import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from swiftroute.api import build_server


class APITests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.server = build_server("127.0.0.1", 0, Path(self.temp.name) / "api.db")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp.cleanup()

    def request(self, method: str, path: str, body=None, headers=None):
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(
            self.base + path, data=data, method=method,
            headers={"Content-Type": "application/json", **(headers or {})},
        )
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read())

    def test_health_create_replay_review_and_events(self) -> None:
        status, health = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(health["status"], "ok")
        order_payload = {
            "customer_name": "API Test Customer", "origin": "Lagos",
            "destination": "Kano", "cargo_description": "Synthetic cartons", "weight_kg": 90,
        }
        headers = {"Idempotency-Key": "api-test-key-0001"}
        created_status, created = self.request("POST", "/orders", order_payload, headers)
        replay_status, replay = self.request("POST", "/orders", order_payload, headers)
        self.assertEqual(created_status, 201)
        self.assertEqual(replay_status, 200)
        self.assertEqual(created["order"]["id"], replay["order"]["id"])
        self.assertFalse(replay["created"])
        order_id = created["order"]["id"]
        review_status, reviewed = self.request(
            "POST", f"/orders/{order_id}/review",
            {"decision": "approved", "reviewer": "API Supervisor"},
        )
        self.assertEqual(review_status, 200)
        self.assertEqual(reviewed["order"]["status"], "approved")
        event_status, events = self.request("GET", f"/orders/{order_id}/events")
        self.assertEqual(event_status, 200)
        self.assertEqual(events["count"], 2)

    def test_validation_and_state_conflicts_are_explicit(self) -> None:
        status, error = self.request("POST", "/orders", {}, {})
        self.assertEqual(status, 400)
        self.assertEqual(error["error"]["code"], "validation_error")
        body = {
            "customer_name": "Conflict Customer", "origin": "Lagos",
            "destination": "Ibadan", "cargo_description": "Synthetic parcel",
        }
        _, created = self.request("POST", "/orders", body, {"Idempotency-Key": "api-conflict-0001"})
        order_id = created["order"]["id"]
        first, _ = self.request("POST", f"/orders/{order_id}/review", {"decision": "approved", "reviewer": "Supervisor A"})
        second, error = self.request("POST", f"/orders/{order_id}/review", {"decision": "rejected", "reviewer": "Supervisor B", "reason": "Conflict"})
        self.assertEqual(first, 200)
        self.assertEqual(second, 409)
        self.assertEqual(error["error"]["code"], "conflict")


if __name__ == "__main__":
    unittest.main()
