# Stress-Test Remediation Log

## Initial discovery

The first three-profile run on 2026-08-30 passed the baseline profile but failed the contention and burst profiles.

- Contention: 2 unexpected responses
- Burst: 20 unexpected responses
- Primary symptom: local HTTP connections reset under burst acceptance
- Database outcome: unique orders and total audit-event invariants remained intact, but some clients lost their response and later competing reviews became the committed transition

## Root cause and correction

Python's standard `TCPServer` connection backlog is small by default. SwiftRoute's threaded server inherited that default, so the transport could reject bursts before application handling began.

`SwiftRouteHTTPServer.request_queue_size` was explicitly set to `256`.

## Verification after correction

The complete test suite and all three profiles were rerun. The final report records:

- 8 of 8 tests passing
- 2,430 synthetic requests
- Concurrency levels 8, 32, and 64
- Zero unexpected responses
- Zero invariant mismatches

This correction improves the local simulation behavior. It does not convert the standard-library server into a production application server or prove production capacity.
