# SwiftRoute Synthetic Stress Simulation Report

> Generated: **2026-08-30T21:11:58.173724Z**

These are local synthetic simulations against the included Python HTTP API and SQLite database. They are not production load tests, customer traffic, deployment evidence, or capacity guarantees.

## Results

| Profile | Requests | Concurrency | Result | Req/s | p50 | p95 | p99 |
|---|---:|---:|---|---:|---:|---:|---:|
| baseline | 270 | 8 | PASS | 380.62 | 4.29 ms | 82.62 ms | 231.81 ms |
| contention | 720 | 32 | PASS | 349.14 | 6.74 ms | 432.93 ms | 938.66 ms |
| burst | 1440 | 64 | PASS | 330.13 | 21.33 ms | 836.31 ms | 1532.98 ms |

## Verified invariants

- Replayed idempotency keys returned the original order without creating duplicates.
- A reviewed order could not transition a second time; competing transitions returned HTTP 409.
- Every committed order had exactly one `order.created` audit event.
- Every committed review had exactly one matching approval or rejection audit event.
- Stored order counts and status counts matched each simulation's expected values.

## Environment

- Python: `3.12.13`
- Platform: `Linux-6.18.35-x86_64-with-glibc2.39`
- Database: SQLite in WAL mode, one temporary database per profile
- Transport: local loopback HTTP using `ThreadingHTTPServer`

## Reproduce

```bash
python -m scripts.stress_simulation
```

The JSON companion contains the full configurations, database counts, latencies, and unexpected-response samples.
