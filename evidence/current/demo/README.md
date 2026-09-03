# SwiftRoute v0.1 — Current Demo Placeholder

**Status:** NO CURRENT TERMINAL/API DEMO RECORDING PUBLISHED YET.

The source/tests/stress reports are real evidence, but this location is reserved for a concise current demonstration.

## Minimum demo

A useful current recording should show:

1. start the local API;
2. health check;
3. create a valid order with an idempotency key;
4. replay the same key and show no duplicate order;
5. attempt a conflicting idempotency payload;
6. approve or reject a pending order;
7. attempt a conflicting second review and show HTTP 409;
8. read the order's audit events;
9. optionally run the deterministic tests;
10. clearly state that the environment is local Python/SQLite, not production.

Replace this placeholder only with evidence from the current implementation generation.