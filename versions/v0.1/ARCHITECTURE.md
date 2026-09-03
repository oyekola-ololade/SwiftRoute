# SwiftRoute v0.1 — Implemented Local Architecture

> **Status:** CURRENT IMPLEMENTED / VERIFIED LOCALLY.

```mermaid
flowchart TD
    A[API client] --> B[Python JSON HTTP API]
    B --> C[Validation]
    C --> D[Idempotency key + canonical request hash]
    D --> E[Order service]
    E --> F[(SQLite WAL persistence)]
    E --> G{Supervisor review}
    G -->|Approve| H[APPROVED]
    G -->|Reject + reason| I[REJECTED]
    H --> F
    I --> F
    E --> J[Transactional audit event]
    H --> J
    I --> J
    J --> F
    K[Unit + HTTP integration tests] --> B
    L[Synthetic local stress harness] --> B
```

## Scope boundary

This is the architecture that the current code/tests support. Authentication/RBAC, PostgreSQL, courier integrations, n8n orchestration, documents, payments, notifications and customer applications are not part of v0.1.

Measured stress evidence is local loopback/SQLite evidence, not production capacity.
