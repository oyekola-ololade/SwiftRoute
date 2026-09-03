# SwiftRoute Blueprint v1.0 — Proposed System Architecture

> **Status:** DESIGN / PROPOSED SCOPE · not current implementation.

```mermaid
flowchart TB
    A[Web / Mobile Portal] --> B[REST / GraphQL Application API]
    B --> C[Authentication / RBAC]
    C --> D[Order / Shipment Domain]
    C --> E[Document / PDF Domain]
    C --> F[Payment Domain]
    D --> G[(PostgreSQL)]
    E --> G
    F --> G
    D --> H[n8n Orchestration]
    H --> I[Courier Integrations]
    H --> J[Email / WhatsApp]
    G --> K[Dashboards / Analytics]
    G --> L[Customer Visibility]
```

The blueprint describes the wider intended freight/logistics ecosystem. Only a bounded order-control subset is implemented in the current v0.1 local slice.
