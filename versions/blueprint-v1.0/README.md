# SwiftRoute Blueprint v1.0

[← Main README](../../README.md) · [Architecture diagram](ARCHITECTURE.md)

**Status:** DESIGN / PROPOSED SCOPE

## Contents

- [What the blueprint describes](#what-the-blueprint-describes)
- [Architecture](#architecture)
- [What is implemented today](#what-is-actually-implemented-today)
- [Why scope was reduced](#why-the-scope-was-reduced)
- [Evidence boundary](#evidence-boundary)

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

## Architecture

[Open the Blueprint v1.0 architecture →](ARCHITECTURE.md)

The diagram is design evidence only. It must not be mistaken for the current implementation.

## What is actually implemented today

Only a bounded subset of that blueprint was implemented in the v0.1-style local slice. See [`../v0.1/README.md`](../v0.1/README.md).

## Why the scope was reduced

The implementation deliberately focused first on a state-management boundary that could be tested rigorously:

`order intake → validation → idempotent creation → supervisor review → transactional audit event`

That choice produced inspectable source/tests/evidence instead of a large unverified mock system.

## Evidence boundary

The blueprint proves design thinking and intended system decomposition. It does not prove courier/payment/document/portal integrations, production hosting or shipment operations.

Design/historical scope record: no fake runtime demo/screenshot placeholders.
