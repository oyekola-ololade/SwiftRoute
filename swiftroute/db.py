from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


class SwiftRouteError(Exception):
    """Base exception for expected domain failures."""


class ValidationError(SwiftRouteError):
    pass


class NotFoundError(SwiftRouteError):
    pass


class IdempotencyConflict(SwiftRouteError):
    pass


class StateConflict(SwiftRouteError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class Repository:
    """SQLite-backed order and audit repository.

    Every write uses an immediate transaction so the state change and its audit
    event either commit together or roll back together.
    """

    def __init__(self, database_path: str | Path):
        self.database_path = str(database_path)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(
            self.database_path,
            timeout=30,
            isolation_level=None,
            check_same_thread=False,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 30000")
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
        with self.connect() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute("PRAGMA synchronous = NORMAL")
            connection.executescript(schema)

    @staticmethod
    def _canonical_hash(payload: dict[str, Any]) -> str:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _insert_event(
        connection: sqlite3.Connection,
        order_id: str,
        event_type: str,
        actor: str,
        details: dict[str, Any],
        created_at: str,
    ) -> None:
        connection.execute(
            """
            INSERT INTO audit_events
                (id, order_id, event_type, actor, details_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                order_id,
                event_type,
                actor,
                json.dumps(details, sort_keys=True, separators=(",", ":")),
                created_at,
            ),
        )

    def create_order(
        self,
        payload: dict[str, Any],
        idempotency_key: str,
        actor: str = "api-client",
    ) -> tuple[dict[str, Any], bool]:
        clean = validate_order(payload)
        key = idempotency_key.strip()
        if not 8 <= len(key) <= 160:
            raise ValidationError("Idempotency-Key must contain 8 to 160 characters")

        request_hash = self._canonical_hash(clean)
        now = _utc_now()
        order_id = str(uuid.uuid4())
        reference = f"SWR-{uuid.uuid4().hex[:10].upper()}"

        with self.connect() as connection:
            try:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute(
                    """
                    INSERT INTO orders (
                        id, reference, idempotency_key, request_hash,
                        customer_name, origin, destination, cargo_description,
                        weight_kg, status, version, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending_review', 1, ?)
                    """,
                    (
                        order_id,
                        reference,
                        key,
                        request_hash,
                        clean["customer_name"],
                        clean["origin"],
                        clean["destination"],
                        clean["cargo_description"],
                        clean.get("weight_kg"),
                        now,
                    ),
                )
                self._insert_event(
                    connection,
                    order_id,
                    "order.created",
                    actor,
                    {"status": "pending_review", "reference": reference},
                    now,
                )
                connection.execute("COMMIT")
                return self.get_order(order_id), True
            except sqlite3.IntegrityError:
                connection.execute("ROLLBACK")
                existing = connection.execute(
                    "SELECT * FROM orders WHERE idempotency_key = ?", (key,)
                ).fetchone()
                if existing is None:
                    raise
                if existing["request_hash"] != request_hash:
                    raise IdempotencyConflict(
                        "Idempotency-Key was already used with a different request"
                    )
                return dict(existing), False

    def get_order(self, order_id: str) -> dict[str, Any]:
        with self.connect() as connection:
            order = connection.execute(
                "SELECT * FROM orders WHERE id = ?", (order_id,)
            ).fetchone()
        if order is None:
            raise NotFoundError("Order not found")
        return dict(order)

    def list_orders(self, limit: int = 50, status: str | None = None) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 200))
        with self.connect() as connection:
            if status:
                rows = connection.execute(
                    "SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                    (status, limit),
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM orders ORDER BY created_at DESC LIMIT ?", (limit,)
                ).fetchall()
        return [dict(item) for item in rows]

    def review_order(
        self,
        order_id: str,
        decision: str,
        reviewer: str,
        reason: str | None = None,
    ) -> dict[str, Any]:
        decision = decision.strip().lower()
        reviewer = reviewer.strip()
        reason = reason.strip() if isinstance(reason, str) else None
        if decision not in {"approved", "rejected"}:
            raise ValidationError("decision must be approved or rejected")
        if not 2 <= len(reviewer) <= 120:
            raise ValidationError("reviewer must contain 2 to 120 characters")
        if decision == "rejected" and not reason:
            raise ValidationError("reason is required when rejecting an order")
        if reason and len(reason) > 500:
            raise ValidationError("reason must not exceed 500 characters")

        now = _utc_now()
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            order = connection.execute(
                "SELECT * FROM orders WHERE id = ?", (order_id,)
            ).fetchone()
            if order is None:
                connection.execute("ROLLBACK")
                raise NotFoundError("Order not found")
            if order["status"] != "pending_review":
                connection.execute("ROLLBACK")
                raise StateConflict(
                    f"Order is already {order['status']} and cannot be reviewed again"
                )
            connection.execute(
                """
                UPDATE orders
                SET status = ?, reviewed_at = ?, reviewed_by = ?,
                    review_reason = ?, version = version + 1
                WHERE id = ? AND status = 'pending_review'
                """,
                (decision, now, reviewer, reason, order_id),
            )
            self._insert_event(
                connection,
                order_id,
                f"order.{decision}",
                reviewer,
                {"from": "pending_review", "to": decision, "reason": reason},
                now,
            )
            connection.execute("COMMIT")
        return self.get_order(order_id)

    def list_events(self, order_id: str) -> list[dict[str, Any]]:
        self.get_order(order_id)
        with self.connect() as connection:
            events = connection.execute(
                """
                SELECT id, order_id, event_type, actor, details_json, created_at
                FROM audit_events WHERE order_id = ? ORDER BY created_at, id
                """,
                (order_id,),
            ).fetchall()
        return [
            {**dict(event), "details": json.loads(event["details_json"])}
            for event in events
        ]

    def evidence_counts(self) -> dict[str, int]:
        with self.connect() as connection:
            counts = {
                "orders": connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
                "pending_review": connection.execute(
                    "SELECT COUNT(*) FROM orders WHERE status = 'pending_review'"
                ).fetchone()[0],
                "approved": connection.execute(
                    "SELECT COUNT(*) FROM orders WHERE status = 'approved'"
                ).fetchone()[0],
                "rejected": connection.execute(
                    "SELECT COUNT(*) FROM orders WHERE status = 'rejected'"
                ).fetchone()[0],
                "created_events": connection.execute(
                    "SELECT COUNT(*) FROM audit_events WHERE event_type = 'order.created'"
                ).fetchone()[0],
                "review_events": connection.execute(
                    "SELECT COUNT(*) FROM audit_events WHERE event_type IN ('order.approved', 'order.rejected')"
                ).fetchone()[0],
            }
        return counts


def validate_order(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValidationError("JSON body must be an object")
    fields = {
        "customer_name": (2, 120),
        "origin": (2, 160),
        "destination": (2, 160),
        "cargo_description": (3, 500),
    }
    clean: dict[str, Any] = {}
    for field, (minimum, maximum) in fields.items():
        value = payload.get(field)
        if not isinstance(value, str):
            raise ValidationError(f"{field} must be a string")
        value = " ".join(value.split())
        if not minimum <= len(value) <= maximum:
            raise ValidationError(
                f"{field} must contain {minimum} to {maximum} characters"
            )
        clean[field] = value

    weight = payload.get("weight_kg")
    if weight is not None:
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise ValidationError("weight_kg must be a number")
        if not 0 < float(weight) <= 100_000:
            raise ValidationError("weight_kg must be greater than 0 and at most 100000")
        clean["weight_kg"] = float(weight)
    return clean
