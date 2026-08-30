# SwiftRoute Evidence-Gated Roadmap

## Phase 0 — first vertical slice: complete

- Working Python JSON API
- SQLite schema and repository
- Validated, idempotent order creation
- Supervisor approval and rejection
- Transactional audit events
- Unit and HTTP integration tests
- Three reproducible stress profiles
- Docker build definition

Status may now be described as **early implementation**, not concept-only.

## Phase 1 — access and database foundation

- Authentication and role-based authorization
- Separate operations and supervisor permissions
- PostgreSQL repository with migrations
- Integration tests against PostgreSQL
- Structured request IDs and application logs
- CI workflow for tests and simulation smoke profile

## Phase 2 — shipment vertical slice

- Shipment state model
- Provider-neutral courier adapter contract
- One sandbox courier integration
- Idempotent external writes
- Signed webhook verification
- Reconciliation and exception records

## Phase 3 — documents and notifications

- Controlled document metadata and access
- Approval workflow
- Email or WhatsApp adapter with delivery records
- Retry and dead-letter behavior

## Phase 4 — customer visibility

- Tenant-isolated customer reads
- Authenticated tracking portal
- Shipment milestones and document visibility
- Accessibility and security review

No phase should be marked complete without source, tests, reproducible evidence, and an updated limitation boundary.
