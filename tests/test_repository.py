import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from swiftroute.db import IdempotencyConflict, Repository, StateConflict, ValidationError


def payload(suffix: str = "1") -> dict:
    return {
        "customer_name": f"Test Customer {suffix}",
        "origin": "Lagos",
        "destination": "Abuja",
        "cargo_description": f"Sealed test cartons {suffix}",
        "weight_kg": 25,
    }


class RepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Repository(Path(self.temp.name) / "test.db")
        self.repo.initialize()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_create_and_audit_event_commit_together(self) -> None:
        order, created = self.repo.create_order(payload(), "idem-key-0001")
        self.assertTrue(created)
        self.assertEqual(order["status"], "pending_review")
        events = self.repo.list_events(order["id"])
        self.assertEqual([event["event_type"] for event in events], ["order.created"])

    def test_same_idempotency_request_returns_same_order(self) -> None:
        first, created = self.repo.create_order(payload(), "idem-key-0002")
        second, replay_created = self.repo.create_order(payload(), "idem-key-0002")
        self.assertTrue(created)
        self.assertFalse(replay_created)
        self.assertEqual(first["id"], second["id"])
        self.assertEqual(self.repo.evidence_counts()["orders"], 1)

    def test_reusing_key_for_different_request_conflicts(self) -> None:
        self.repo.create_order(payload("A"), "idem-key-0003")
        with self.assertRaises(IdempotencyConflict):
            self.repo.create_order(payload("B"), "idem-key-0003")

    def test_review_transition_is_single_use_and_audited(self) -> None:
        order, _ = self.repo.create_order(payload(), "idem-key-0004")
        reviewed = self.repo.review_order(order["id"], "approved", "Supervisor One")
        self.assertEqual(reviewed["status"], "approved")
        self.assertEqual(reviewed["version"], 2)
        with self.assertRaises(StateConflict):
            self.repo.review_order(order["id"], "rejected", "Supervisor Two", "Changed mind")
        events = self.repo.list_events(order["id"])
        self.assertEqual(len(events), 2)
        self.assertEqual(events[-1]["event_type"], "order.approved")

    def test_rejection_requires_reason(self) -> None:
        order, _ = self.repo.create_order(payload(), "idem-key-0005")
        with self.assertRaises(ValidationError):
            self.repo.review_order(order["id"], "rejected", "Supervisor One")

    def test_concurrent_idempotent_requests_create_one_order(self) -> None:
        def submit(_: int):
            return self.repo.create_order(payload(), "idem-concurrent-0001")
        with ThreadPoolExecutor(max_workers=12) as executor:
            results = list(executor.map(submit, range(40)))
        self.assertEqual(sum(1 for _, created in results if created), 1)
        self.assertEqual(len({order["id"] for order, _ in results}), 1)
        self.assertEqual(self.repo.evidence_counts()["created_events"], 1)


if __name__ == "__main__":
    unittest.main()
