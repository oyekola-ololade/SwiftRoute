# SwiftRoute Blueprint v1.0

**Status:** DESIGN / PROPOSED SCOPE

## What the blueprint describes

The original blueprint defines a much broader freight/logistics ecosystem including concepts such as:

- web/mobile operational and customer interfaces;
- REST/GraphQL-style application APIs;
- authentication/RBAC;
- order/shipment/document/payment domains;
- PostgreSQL;
- n8n orchestration;
- courier integrations;
- document/PDF operations;
- email/WhatsApp notifications;
- dashboards/analytics and customer visibility.

## What is actually implemented today

Only a bounded subset of that blueprint was implemented in the v0.1-style local slice. See [`../v0.1/README.md`](../v0.1/README.md).

## Why the scope was reduced

The implementation deliberately focused first on a state-management boundary that could be tested rigorously:

`order intake → validation → idempotent creation → supervisor review → transactional audit event`

That choice produced inspectable source/tests/evidence instead of a large unverified mock system.

## Evidence boundary

The blueprint proves design thinking and intended system decomposition. It does not prove courier/payment/document/portal integrations, production hosting or shipment operations.

## Media

Design/historical scope record. No demo/screenshot placeholders.