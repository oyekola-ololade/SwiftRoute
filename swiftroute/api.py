from __future__ import annotations

import argparse
import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .db import IdempotencyConflict, NotFoundError, Repository, StateConflict, ValidationError


MAX_BODY_BYTES = 64 * 1024
ORDER_PATH = re.compile(r"^/orders/([0-9a-f-]{36})$")
EVENT_PATH = re.compile(r"^/orders/([0-9a-f-]{36})/events$")
REVIEW_PATH = re.compile(r"^/orders/([0-9a-f-]{36})/review$")


class SwiftRouteHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 256

    def __init__(self, server_address: tuple[str, int], repository: Repository):
        super().__init__(server_address, SwiftRouteHandler)
        self.repository = repository


class SwiftRouteHandler(BaseHTTPRequestHandler):
    server: SwiftRouteHTTPServer
    protocol_version = "HTTP/1.1"

    def _json(self, status: int, payload: dict[str, Any] | list[Any], **headers: str) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for name, value in headers.items():
            self.send_header(name.replace("_", "-"), value)
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict[str, Any]:
        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            raise ValidationError("Content-Length is required")
        try:
            length = int(raw_length)
        except ValueError as error:
            raise ValidationError("Content-Length is invalid") from error
        if length <= 0 or length > MAX_BODY_BYTES:
            raise ValidationError("JSON body must contain 1 to 65536 bytes")
        try:
            value = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise ValidationError("Request body must be valid UTF-8 JSON") from error
        if not isinstance(value, dict):
            raise ValidationError("JSON body must be an object")
        return value

    def _dispatch(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        if self.command == "GET" and path == "/health":
            self._json(200, {"status": "ok", "service": "swiftroute", "version": "0.1.0"})
            return
        if self.command == "GET" and path == "/metrics":
            self._json(200, self.server.repository.evidence_counts())
            return
        if self.command == "GET" and path == "/orders":
            query = parse_qs(parsed.query)
            try:
                limit = int(query.get("limit", ["50"])[0])
            except ValueError as error:
                raise ValidationError("limit must be an integer") from error
            status = query.get("status", [None])[0]
            if status and status not in {"pending_review", "approved", "rejected"}:
                raise ValidationError("status filter is invalid")
            orders = self.server.repository.list_orders(limit=limit, status=status)
            self._json(200, {"items": orders, "count": len(orders)})
            return
        if self.command == "POST" and path == "/orders":
            key = self.headers.get("Idempotency-Key", "")
            actor = self.headers.get("X-Actor", "api-client")[:120]
            order, created = self.server.repository.create_order(self._body(), key, actor)
            self._json(
                201 if created else 200,
                {"order": order, "created": created},
                Idempotency_Replayed="false" if created else "true",
            )
            return
        order_match = ORDER_PATH.match(path)
        if self.command == "GET" and order_match:
            self._json(200, {"order": self.server.repository.get_order(order_match.group(1))})
            return
        event_match = EVENT_PATH.match(path)
        if self.command == "GET" and event_match:
            events = self.server.repository.list_events(event_match.group(1))
            self._json(200, {"items": events, "count": len(events)})
            return
        review_match = REVIEW_PATH.match(path)
        if self.command == "POST" and review_match:
            body = self._body()
            order = self.server.repository.review_order(
                review_match.group(1),
                str(body.get("decision", "")),
                str(body.get("reviewer", "")),
                body.get("reason"),
            )
            self._json(200, {"order": order})
            return
        self._json(404, {"error": {"code": "not_found", "message": "Route not found"}})

    def _handle(self) -> None:
        try:
            self._dispatch()
        except ValidationError as error:
            self._json(400, {"error": {"code": "validation_error", "message": str(error)}})
        except NotFoundError as error:
            self._json(404, {"error": {"code": "not_found", "message": str(error)}})
        except (IdempotencyConflict, StateConflict) as error:
            self._json(409, {"error": {"code": "conflict", "message": str(error)}})
        except Exception:
            self._json(500, {"error": {"code": "internal_error", "message": "Unexpected server error"}})

    do_GET = _handle
    do_POST = _handle

    def log_message(self, fmt: str, *args: object) -> None:
        if os.environ.get("SWIFTROUTE_ACCESS_LOG") == "1":
            super().log_message(fmt, *args)


def build_server(host: str, port: int, database_path: str | Path) -> SwiftRouteHTTPServer:
    repository = Repository(database_path)
    repository.initialize()
    return SwiftRouteHTTPServer((host, port), repository)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the SwiftRoute early implementation API")
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8080")))
    parser.add_argument("--database", default=os.environ.get("SWIFTROUTE_DATABASE", "data/swiftroute.db"))
    args = parser.parse_args()
    database = Path(args.database)
    database.parent.mkdir(parents=True, exist_ok=True)
    server = build_server(args.host, args.port, database)
    print(f"SwiftRoute listening on http://{args.host}:{server.server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
