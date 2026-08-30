from __future__ import annotations

import argparse
import json
import platform
import tempfile
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from swiftroute.api import build_server


PROFILES = {
    "baseline": {"creates": 150, "replays": 30, "reviews": 75, "conflicts": 15, "concurrency": 8},
    "contention": {"creates": 400, "replays": 80, "reviews": 200, "conflicts": 40, "concurrency": 32},
    "burst": {"creates": 800, "replays": 160, "reviews": 400, "conflicts": 80, "concurrency": 64},
}


def percentile(values: list[float], percent: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int((len(ordered) - 1) * percent)))
    return round(ordered[index], 2)


def call(base: str, method: str, path: str, body: dict[str, Any], headers=None):
    started = time.perf_counter()
    request = urllib.request.Request(
        base + path,
        data=json.dumps(body).encode(),
        method=method,
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status
            payload = json.loads(response.read())
    except urllib.error.HTTPError as error:
        status = error.code
        payload = json.loads(error.read())
    except Exception as error:
        status = 0
        payload = {"error": str(error)}
    return status, payload, (time.perf_counter() - started) * 1000


def payload(index: int) -> dict[str, Any]:
    cities = ["Lagos", "Abuja", "Kano", "Ibadan", "Port Harcourt", "Enugu"]
    return {
        "customer_name": f"Synthetic Customer {index:05d}",
        "origin": cities[index % len(cities)],
        "destination": cities[(index + 2) % len(cities)],
        "cargo_description": f"Synthetic sealed freight batch {index:05d}",
        "weight_kg": float(10 + index % 990),
    }


def run_profile(name: str, config: dict[str, int]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        server = build_server("127.0.0.1", 0, Path(directory) / f"{name}.db")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_port}"
        started = time.perf_counter()
        latencies: list[float] = []
        unexpected: list[dict[str, Any]] = []
        order_ids: list[str] = [""] * config["creates"]

        def create(index: int):
            result = call(
                base,
                "POST",
                "/orders",
                payload(index),
                {"Idempotency-Key": f"{name}-create-{index:06d}"},
            )
            return index, result

        with ThreadPoolExecutor(max_workers=config["concurrency"]) as executor:
            for index, (status, body, latency) in executor.map(create, range(config["creates"])):
                latencies.append(latency)
                if status == 201:
                    order_ids[index] = body["order"]["id"]
                else:
                    unexpected.append({"phase": "create", "index": index, "status": status, "body": body})

        def replay(index: int):
            return index, call(
                base,
                "POST",
                "/orders",
                payload(index),
                {"Idempotency-Key": f"{name}-create-{index:06d}"},
            )

        with ThreadPoolExecutor(max_workers=config["concurrency"]) as executor:
            for index, (status, body, latency) in executor.map(replay, range(config["replays"])):
                latencies.append(latency)
                if status != 200 or body.get("created") is not False or body["order"]["id"] != order_ids[index]:
                    unexpected.append({"phase": "replay", "index": index, "status": status, "body": body})

        def review(index: int):
            decision = "approved" if index % 2 == 0 else "rejected"
            body = {"decision": decision, "reviewer": f"Synthetic Supervisor {index % 7}"}
            if decision == "rejected":
                body["reason"] = "Synthetic policy rejection"
            return index, call(base, "POST", f"/orders/{order_ids[index]}/review", body)

        with ThreadPoolExecutor(max_workers=config["concurrency"]) as executor:
            for index, (status, body, latency) in executor.map(review, range(config["reviews"])):
                latencies.append(latency)
                if status != 200:
                    unexpected.append({"phase": "review", "index": index, "status": status, "body": body})

        def competing_review(index: int):
            return index, call(
                base,
                "POST",
                f"/orders/{order_ids[index]}/review",
                {"decision": "rejected", "reviewer": "Competing Reviewer", "reason": "Synthetic race"},
            )

        with ThreadPoolExecutor(max_workers=config["concurrency"]) as executor:
            for index, (status, body, latency) in executor.map(competing_review, range(config["conflicts"])):
                latencies.append(latency)
                if status != 409:
                    unexpected.append({"phase": "conflict", "index": index, "status": status, "body": body})

        duration = time.perf_counter() - started
        counts = server.repository.evidence_counts()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    expected_counts = {
        "orders": config["creates"],
        "pending_review": config["creates"] - config["reviews"],
        "approved": (config["reviews"] + 1) // 2,
        "rejected": config["reviews"] // 2,
        "created_events": config["creates"],
        "review_events": config["reviews"],
    }
    invariant_errors = {
        key: {"expected": expected, "actual": counts.get(key)}
        for key, expected in expected_counts.items()
        if counts.get(key) != expected
    }
    total = sum(config[key] for key in ("creates", "replays", "reviews", "conflicts"))
    return {
        "profile": name,
        "configuration": config,
        "requests": total,
        "duration_seconds": round(duration, 3),
        "throughput_requests_per_second": round(total / duration, 2),
        "latency_ms": {
            "p50": percentile(latencies, 0.50),
            "p95": percentile(latencies, 0.95),
            "p99": percentile(latencies, 0.99),
            "max": round(max(latencies), 2),
        },
        "database_counts": counts,
        "unexpected_response_count": len(unexpected),
        "unexpected_response_samples": unexpected[:10],
        "invariant_errors": invariant_errors,
        "passed": not unexpected and not invariant_errors,
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# SwiftRoute Synthetic Stress Simulation Report",
        "",
        f"> Generated: **{report['generated_at']}**",
        "",
        "These are local synthetic simulations against the included Python HTTP API and SQLite database. They are not production load tests, customer traffic, deployment evidence, or capacity guarantees.",
        "",
        "## Results",
        "",
        "| Profile | Requests | Concurrency | Result | Req/s | p50 | p95 | p99 |",
        "|---|---:|---:|---|---:|---:|---:|---:|",
    ]
    for item in report["profiles"]:
        latency = item["latency_ms"]
        lines.append(
            f"| {item['profile']} | {item['requests']} | {item['configuration']['concurrency']} | "
            f"{'PASS' if item['passed'] else 'FAIL'} | {item['throughput_requests_per_second']} | "
            f"{latency['p50']} ms | {latency['p95']} ms | {latency['p99']} ms |"
        )
    lines.extend([
        "", "## Verified invariants", "",
        "- Replayed idempotency keys returned the original order without creating duplicates.",
        "- A reviewed order could not transition a second time; competing transitions returned HTTP 409.",
        "- Every committed order had exactly one `order.created` audit event.",
        "- Every committed review had exactly one matching approval or rejection audit event.",
        "- Stored order counts and status counts matched each simulation's expected values.",
        "", "## Environment", "",
        f"- Python: `{report['environment']['python']}`",
        f"- Platform: `{report['environment']['platform']}`",
        "- Database: SQLite in WAL mode, one temporary database per profile",
        "- Transport: local loopback HTTP using `ThreadingHTTPServer`",
        "", "## Reproduce", "", "```bash", "python -m scripts.stress_simulation", "```", "",
        "The JSON companion contains the full configurations, database counts, latencies, and unexpected-response samples.", "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run reproducible SwiftRoute stress simulations")
    parser.add_argument("--profiles", nargs="+", choices=PROFILES, default=list(PROFILES))
    parser.add_argument("--output-json", default="evidence/stress-report.json")
    parser.add_argument("--output-md", default="evidence/stress-report.md")
    args = parser.parse_args()
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "scope": "local synthetic simulation; not production capacity evidence",
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "profiles": [run_profile(name, PROFILES[name]) for name in args.profiles],
    }
    report["passed"] = all(item["passed"] for item in report["profiles"])
    json_path = Path(args.output_json)
    markdown_path = Path(args.output_md)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
