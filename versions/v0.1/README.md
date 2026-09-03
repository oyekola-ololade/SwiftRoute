# SwiftRoute v0.1 — Local Order-Control Snapshot

[← Main README](../../README.md) · [Implemented architecture](ARCHITECTURE.md)

**Status:** **CURRENT IMPLEMENTED / VERIFIED LOCALLY**  
**Date:** 2026-08-30 evidence snapshot

## Contents

- [Implemented scope](#implemented-scope)
- [Architecture](#architecture)
- [Verification evidence](#verification-evidence)
- [Failure / remediation story](#preserved-failure--remediation-story)
- [Not implemented](#not-implemented-in-v01)
- [Evidence boundary](#evidence-boundary)
- [Media](#media)

## Implemented scope

| Capability | Status |
|---|---|
| JSON HTTP API | implemented + tested |
| Order validation | implemented |
| Idempotent creation | implemented + concurrency-tested |
| Create/list/read order | implemented + tested |
| Supervisor approve/reject | implemented + tested |
| Conflicting second review | rejected and verified |
| Transactional audit event | implemented + invariant-tested |
| SQLite WAL persistence | implemented |
| Synthetic stress harness | implemented |
| Docker build definition | present; image not published |

## Architecture

[Open the v0.1 implemented architecture →](ARCHITECTURE.md)

The diagram matches the bounded Python/SQLite slice represented by the current code and tests.

## Verification evidence

- **8/8 tests passed** after remediation.
- Baseline: 270 requests, concurrency 8, 380.62 req/s, p95 82.62 ms.
- Contention: 720 requests, concurrency 32, 349.14 req/s, p95 432.93 ms.
- Burst: 1,440 requests, concurrency 64, 330.13 req/s, p95 836.31 ms.
- Total: **2,430 local synthetic requests**.

## Preserved failure / remediation story

The initial higher-concurrency local run showed connection/reset behavior. Investigation identified a small server accept backlog. The queue was increased using `request_queue_size = 256`, then unit/integration/stress evidence was rerun successfully.

That remediation record is deliberately preserved rather than deleting the failure and presenting only the final pass.

## Not implemented in v0.1

- authentication / RBAC;
- PostgreSQL;
- n8n orchestration;
- courier writes;
- documents/PDF;
- payments;
- notifications;
- dashboard/web/mobile;
- production hosting/SLA.

## Evidence boundary

The performance numbers are local loopback/SQLite test evidence on one environment. They are **not** production capacity, uptime or SLA claims.

## Media

Current-version media locations:

- [`../../evidence/current/demo/README.md`](../../evidence/current/demo/README.md)
- [`../../evidence/current/screenshots/README.md`](../../evidence/current/screenshots/README.md)
- `../../assets/local-scope-and-stress.svg`

Existing architecture/stress evidence remains explanatory/measured evidence, not a replacement for a genuine current demo.
