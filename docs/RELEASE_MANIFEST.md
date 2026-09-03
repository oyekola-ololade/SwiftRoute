# SwiftRoute Current Release Manifest

## Classification

**Early implementation — tested local vertical slice, not production.**

## Included implementation

- `swiftroute/api.py` — JSON HTTP API boundary.
- `swiftroute/db.py` — repository/state logic.
- `swiftroute/schema.sql` — SQLite schema and WAL-oriented persistence.
- `tests/` — deterministic unit/HTTP/concurrency coverage.
- `scripts/stress_simulation.py` — local synthetic stress runner.
- `evidence/stress-report.json` — machine-readable final test output.
- `evidence/stress-report.md` — human-readable test report.
- `evidence/REMEDIATION.md` — failure diagnosis and remediation record.
- `Dockerfile` — container build definition.
- `.env.example` — placeholder-only local configuration.

## Verified behavior

- valid order intake;
- field validation;
- idempotent replay;
- conflict on reused idempotency key with different payload;
- controlled PENDING → APPROVED / REJECTED transition;
- conflict on competing second review;
- transactional audit-event invariants;
- 40 concurrent submissions sharing one idempotency key;
- final three-profile local stress run.

## Explicitly not included

- authentication / RBAC;
- PostgreSQL runtime;
- real courier writes;
- real notification providers;
- document/payment workflows;
- customer portal/mobile app;
- production deployment or production security controls.

## Promotion rule

A future release must update this manifest whenever code, architecture, externally visible behavior, data contracts, security boundary, or verified test evidence materially changes.
