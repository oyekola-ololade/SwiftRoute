# SwiftRoute — Repository Index

> **Current truth:** early local Python/SQLite implementation with verified order-state/idempotency/audit behavior and local synthetic stress evidence. The broader logistics platform remains proposed.

## Start here

- [Main README](README.md)
- [Version / scope archive](versions/INDEX.md)
- [Architecture](docs/architecture.md)
- [Current visual sources](docs/current-visuals.md)
- [Release manifest](docs/RELEASE_MANIFEST.md)
- [Stress report](evidence/stress-report.md)
- [Raw stress results](evidence/stress-report.json)
- [Remediation record](evidence/REMEDIATION.md)
- [Security policy](SECURITY.md)
- [Changelog](CHANGELOG.md)
- `swiftroute/` — implemented Python package
- `tests/` — unit/integration tests
- `scripts/stress_simulation.py` — local synthetic stress harness

## Version / scope model

| Record | Meaning | Status |
|---|---|---|
| Blueprint v1.0 | broad freight/logistics ecosystem | DESIGN / PROPOSED |
| v0.1-style local snapshot | bounded order-control vertical slice | **CURRENT IMPLEMENTED / VERIFIED LOCALLY** |
| v0.2 proposed | auth/RBAC + PostgreSQL migration gate | PROPOSED NEXT |

See [`versions/`](versions/INDEX.md).

## Current verified evidence

- JSON HTTP API;
- order validation;
- idempotent creation;
- create/list/read order;
- supervisor approve/reject;
- conflicting second review rejected;
- transactional audit events;
- SQLite WAL persistence;
- 8/8 tests passed after remediation;
- three local stress profiles, 2,430 synthetic requests total;
- accept-backlog problem preserved, diagnosed, remediated with `request_queue_size = 256`, then rerun successfully.

This is local loopback/SQLite evidence, **not production capacity or SLA evidence**.

## Media rule

The current v0.1-style snapshot has architecture/stress SVG evidence but no genuine terminal/API demo recording and no curated runtime screenshot set, so placeholders are visible:

- [Demo placeholder](evidence/current/demo/README.md)
- [Screenshot placeholder](evidence/current/screenshots/README.md)

Blueprint/proposed records do not receive empty media folders.