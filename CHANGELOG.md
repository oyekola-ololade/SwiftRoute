# Changelog

## 2026-08-30 — v0.1-style local implementation slice

### Added

- Python JSON HTTP API.
- Order validation.
- Idempotent order creation with canonical request hashing.
- SQLite persistence in WAL mode.
- Supervisor approve/reject state transitions.
- Transactional audit-event recording.
- Unit and HTTP integration tests.
- Synthetic local stress profiles.
- Dockerfile and Makefile.

### Verification

- 8 deterministic tests passed.
- Baseline: 270 requests, concurrency 8, 380.62 req/s, p95 82.62 ms.
- Contention: 720 requests, concurrency 32, 349.14 req/s, p95 432.93 ms.
- Burst: 1,440 requests, concurrency 64, 330.13 req/s, p95 836.31 ms.
- 2,430 total local synthetic requests with zero unexpected responses in the final run.

### Remediation

An earlier contention/burst run exposed connection resets. Diagnosis identified the local server's small TCP accept backlog. The queue size was increased to 256 and the full deterministic/stress suite was rerun successfully.

### Boundary

These results are local synthetic loopback evidence using SQLite. They are not production load tests, throughput guarantees, uptime evidence, or SLA measurements.

## Proposed next release — v0.2

Planned, not implemented:

- authentication;
- role-based authorization;
- PostgreSQL migration;
- corresponding integration/security tests;
- only after those gates, external courier-write design and verification.
