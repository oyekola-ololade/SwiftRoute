# SwiftRoute v0.2 — Proposed Next Architecture

> **Status:** PROPOSED NEXT ENGINEERING GATE · not implemented.

```mermaid
flowchart TD
    A[Authenticated API client] --> B[Authentication]
    B --> C[Role-based authorization]
    C --> D[Existing order-control API]
    D --> E[Validation + idempotent creation]
    D --> F[Supervisor review boundary]
    E --> G[(PostgreSQL)]
    F --> G
    E --> H[Transactional audit events]
    F --> H
    H --> G
    I[Migration + regression tests] --> G
    J[v0.1 idempotency/state/audit test suite] --> D
```

External courier writes, documents, payments, notifications and customer portals remain outside this proposed increment. v0.2 is only promoted after auth/RBAC, PostgreSQL migration and regression evidence exist.
