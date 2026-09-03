# SwiftRoute Current Visual Sources

## Blueprint vs implemented scope

```mermaid
flowchart LR
    subgraph Proposed[Original broader blueprint — proposed]
      P1[Web / mobile clients]
      P2[Auth + RBAC]
      P3[PostgreSQL]
      P4[Courier integrations]
      P5[Documents / payments / notifications]
      P6[Customer portal]
    end

    subgraph Implemented[2026-08-30 local slice — implemented]
      I1[Python JSON HTTP API] --> I2[Validation]
      I2 --> I3[Idempotent order creation]
      I3 --> I4[(SQLite WAL)]
      I3 --> I5[Supervisor approve / reject]
      I5 --> I4
      I5 --> I6[Transactional audit events]
      I6 --> I4
    end
```

The broader blueprint remains design scope. The implemented slice proves only the order-state boundary represented on the right.

## Order-state machine

```mermaid
stateDiagram-v2
    [*] --> PENDING: order created
    PENDING --> APPROVED: supervisor approves
    PENDING --> REJECTED: supervisor rejects with reason
    APPROVED --> APPROVED: conflicting second review rejected (HTTP 409)
    REJECTED --> REJECTED: conflicting second review rejected (HTTP 409)
```

## Idempotency and audit boundary

```mermaid
flowchart LR
    A[POST /orders + Idempotency-Key] --> B[Validate payload]
    B --> C{Key exists?}
    C -->|No| D[Store canonical request hash]
    D --> E[Create one order]
    E --> F[Write audit event in same transaction]
    C -->|Yes, same hash| G[Return existing order]
    C -->|Yes, different hash| H[Reject conflict]
```

## Stress-remediation story

```mermaid
flowchart LR
    A[Initial local stress profiles] --> B[Baseline passed]
    B --> C[Contention / burst showed connection resets]
    C --> D[Diagnose small TCP accept backlog]
    D --> E[Set request_queue_size = 256]
    E --> F[Re-run deterministic tests + all profiles]
    F --> G[8/8 tests + 3/3 stress profiles pass]
```

This is local loopback evidence only; it is not production capacity or SLA evidence.
