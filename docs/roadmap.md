# Proposed Implementation Roadmap

All work remains unchecked because SwiftRoute has not been implemented.

## Phase 1 — Bounded vertical slice

- [ ] Define order and audit-event schemas
- [ ] Create PostgreSQL migrations
- [ ] Build authenticated order-intake API
- [ ] Add supervisor review action
- [ ] Record immutable audit events
- [ ] Add unit and integration tests
- [ ] Publish synthetic test evidence

## Phase 2 — Shipment state

- [ ] Add shipment and milestone model
- [ ] Create provider-neutral courier adapter
- [ ] Implement one sandbox courier integration
- [ ] Verify webhook signatures
- [ ] Add reconciliation and retry behavior

## Phase 3 — Documents and notifications

- [ ] Add controlled document storage
- [ ] Implement review/approval flow
- [ ] Add one sandbox notification provider
- [ ] Add failure escalation and delivery records

## Phase 4 — Payments and customer portal

- [ ] Add invoice/payment records
- [ ] Implement manual-payment reconciliation
- [ ] Build customer-scoped tracking portal
- [ ] Test authorization and data isolation

## Upgrade rule

Do not change the project label from **Concept / Specification** until implementation files and executed test evidence support a stronger status.

