# SwiftRoute

> **Evidence status: Early implementation — tested local vertical slice, not production**

SwiftRoute is an emerging freight-operations platform. This repository contains a working first slice for validated order intake, idempotent creation, supervisor approval/rejection, SQLite persistence, and transactional audit-event recording.

The wider shipment, courier, document, payment, notification, customer-portal, authentication, and PostgreSQL architecture remains proposed work.

[Open the visual project page](./index.html)

<p align="center"><img src="assets/local-scope-and-stress.svg" width="100%" alt="SwiftRoute implemented local scope and synthetic stress evidence"></p>

## Table of contents

- [What is implemented](#what-is-implemented)
- [Version / scope history](#version--scope-history)
- [Implemented architecture](#implemented-architecture)
- [API surface](#api-surface)
- [Run locally](#run-locally)
- [Verification](#verification)
- [Evidence boundary](#evidence-boundary)
- [Next engineering gate](#next-engineering-gate)
- [Author](#author)

### Version / architecture quick links

| Record | Status | README | Architecture |
|---|---|---|---|
| Blueprint v1.0 | Proposed broad platform design | [open](versions/blueprint-v1.0/README.md) | [diagram](versions/blueprint-v1.0/ARCHITECTURE.md) |
| v0.1 | **Current implemented / verified locally** | [open](versions/v0.1/README.md) | [diagram](versions/v0.1/ARCHITECTURE.md) |
| v0.2 | Proposed next engineering gate | [open](versions/v0.2-proposed/README.md) | [diagram](versions/v0.2-proposed/ARCHITECTURE.md) |

## What is implemented

| Capability | Evidence | Status |
|---|---|---|
| JSON HTTP API | `swiftroute/api.py` | Implemented and locally tested |
| Order validation | `swiftroute/db.py` | Implemented |
| Idempotent creation | unique key + canonical request hash | Implemented and concurrency-tested |
| Supervisor review | PENDING → APPROVED/REJECTED | Implemented and tested |
| Audit events | same transaction as state change | Implemented and invariant-tested |
| SQLite persistence | `swiftroute/schema.sql` in WAL mode | Implemented for the local slice |
| Unit + HTTP tests | `tests/` | 8 tests passing |
| Synthetic stress | `scripts/stress_simulation.py`, `evidence/` | three profiles passing locally |
| Container packaging | `Dockerfile` | build definition present; image not published |

## Version / scope history

### Blueprint v1.0
A broad freight/logistics system design covering web/mobile interfaces, APIs, auth/RBAC, PostgreSQL, n8n, couriers, documents, payments, notifications and analytics. It is design evidence, not implemented scope.

### v0.1 current local slice
The actual implemented boundary is deliberately narrower:

`order intake → validation → idempotent creation → supervisor review → transactional audit event`

This boundary has source, tests and local synthetic stress evidence.

### v0.2 proposed
The next engineering gate is authentication + RBAC around the existing API, followed by PostgreSQL migration while preserving the v0.1 idempotency/state/audit invariants.

Each record has its own README and architecture page under [`versions/`](versions/).

## Implemented architecture

```mermaid
flowchart TD
    C[API client] --> H[Python HTTP boundary]
    H --> V[Validation + idempotency]
    V --> O[Order service]
    O --> R{Supervisor decision}
    R -->|Approve| A[Approved]
    R -->|Reject with reason| X[Rejected]
    O --> DB[(SQLite order state)]
    A --> DB
    X --> DB
    O --> E[Transactional audit event]
    A --> E
    X --> E
    E --> DB
```

See [architecture](docs/architecture.md), [current visual sources](docs/current-visuals.md), [release manifest](docs/RELEASE_MANIFEST.md), and [changelog](CHANGELOG.md).

## API surface

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/health` | service health |
| `GET` | `/metrics` | current local database counts |
| `POST` | `/orders` | validate/create order; requires `Idempotency-Key` |
| `GET` | `/orders` | list orders |
| `GET` | `/orders/{id}` | fetch order |
| `POST` | `/orders/{id}/review` | approve/reject pending order |
| `GET` | `/orders/{id}/events` | read audit trail |

## Run locally

Requirements: Python 3.11+.

```bash
cp .env.example .env
python -m swiftroute.api
```

Default address: `http://127.0.0.1:8080`. The database is created at `data/swiftroute.db`.

## Verification

```bash
python -m unittest discover -s tests -v
python -m scripts.stress_simulation
```

Current deterministic result: **8 tests passed**.

Verified final local stress run on 2026-08-30:

| Profile | Requests | Concurrency | Result | Throughput | p95 latency |
|---|---:|---:|---|---:|---:|
| Baseline | 270 | 8 | PASS | 380.62 req/s | 82.62 ms |
| Contention | 720 | 32 | PASS | 349.14 req/s | 432.93 ms |
| Burst | 1,440 | 64 | PASS | 330.13 req/s | 836.31 ms |

Across all **2,430 synthetic requests**, the final run recorded zero unexpected responses. Replayed keys did not create duplicate orders, competing second reviews returned HTTP 409, and stored order/audit counts matched the expected invariants.

These are **local loopback simulations using SQLite**. They are not production load tests, deployment evidence, an SLA, or a capacity guarantee. See [stress report](evidence/stress-report.md), [raw JSON](evidence/stress-report.json), and [remediation log](evidence/REMEDIATION.md).

## Evidence boundary

This repository does **not** claim:

- production deployment or a public hosted API;
- authentication, authorization, tenant isolation, or PostgreSQL support;
- real courier, WhatsApp, email, document, payment, or storage integrations;
- web/mobile customer applications;
- real shipments, users, clients, revenue, uptime, or business outcomes;
- security certification or production performance.

## Next engineering gate

Authentication + role-based access around the existing review boundary, followed by PostgreSQL migration and integration tests. External courier writes stay out of scope until idempotency, webhook verification, reconciliation, and provider-failure handling are implemented.

## Author

**Oyekola Ololade**  
AI Systems & Integration Engineer

- [GitHub](https://github.com/oyekola-ololade)
- [LinkedIn](https://www.linkedin.com/in/ololade-oyekola-5b1797397/)
- [Email](mailto:oyekolaololade69@gmail.com)
