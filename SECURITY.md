# Security Policy

SwiftRoute is an early local implementation and is not ready for sensitive or production data.

## Do not use this version for

- Real customer, shipment, identity, payment, or document data
- Internet-facing deployment without authentication and TLS
- Multi-tenant access
- Production courier or messaging credentials

## Current controls

- Bounded JSON body size
- Field validation
- Idempotent creation
- Controlled order state transitions
- Atomic audit-event writes
- Placeholder-only environment configuration

Authentication, authorization, encryption policy, secret management, rate limiting, PostgreSQL access controls, backup/recovery, and formal security testing are not implemented.

Report security concerns privately to the repository owner rather than including sensitive details in a public issue.
