# SwiftRoute v0.2 — Proposed Next Engineering Gate

**Status:** PROPOSED · not implemented

## Proposed scope

The next credible increment is deliberately narrower than the original blueprint:

1. authentication around the existing API boundary;
2. role-based access control for operational/reviewer actions;
3. PostgreSQL migration from the local SQLite evidence store;
4. integration tests proving existing idempotency/state/audit invariants survive the migration.

## Why this comes before courier integrations

External courier writes add another failure/idempotency/reconciliation boundary. The current plan requires identity/authorization and durable shared database behavior to be proven before adding provider-side effects.

## Acceptance requirements

- authenticated requests and explicit unauthorized/forbidden cases;
- roles that distinguish allowed review/admin operations;
- PostgreSQL schema/migrations;
- idempotent creation invariant preserved;
- review conflict invariant preserved;
- transactional audit invariant preserved;
- regression tests from v0.1 rerun;
- current documentation/evidence updated.

## Not included merely because it appears in the blueprint

Courier APIs, documents, payments, notifications and customer portals remain later work unless explicitly implemented.

## Media

Proposed version. No demo/screenshot placeholders until this becomes an implemented current release.