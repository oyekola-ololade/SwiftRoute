# SwiftRoute API Contract

## Implemented routes

All bodies are JSON. Mutating order creation requires an `Idempotency-Key` header containing 8–160 characters.

### `POST /orders`

```json
{
  "customer_name": "Demo Exporter",
  "origin": "Lagos",
  "destination": "Abuja",
  "cargo_description": "Sealed textile cartons",
  "weight_kg": 120
}
```

- `201`: new order created
- `200`: exact idempotent replay; `created` is false
- `400`: validation or missing/invalid key
- `409`: key reused for a different normalized payload

### `GET /orders?status=pending_review&limit=50`

Returns at most 200 orders. Status may be `pending_review`, `approved`, or `rejected`.

### `GET /orders/{id}`

Returns one order or `404`.

### `POST /orders/{id}/review`

Approval:

```json
{"decision":"approved","reviewer":"Supervisor One"}
```

Rejection:

```json
{
  "decision":"rejected",
  "reviewer":"Supervisor One",
  "reason":"Required documentation is incomplete"
}
```

Only a `pending_review` order may transition. A repeated or competing review returns `409`.

### `GET /orders/{id}/events`

Returns the order's ordered audit events.

### `GET /health`

Returns service name, version, and current health status.

### `GET /metrics`

Returns current local counts for orders, statuses, creation events, and review events. This is a diagnostic endpoint, not a production monitoring system.

## Error envelope

```json
{
  "error": {
    "code": "validation_error",
    "message": "customer_name must be a string"
  }
}
```

Expected codes are `validation_error`, `not_found`, `conflict`, and `internal_error`.

## Proposed routes

Authentication, customers, shipments, documents, courier callbacks, payments, notifications, and portal routes remain design work. They should not be treated as implemented until source, tests, and evidence are added.
