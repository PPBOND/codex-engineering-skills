---
name: cpp-storage-review
description: Review C++ distributed-storage changes for correctness, concurrency, memory, asynchronous I/O, recovery, compatibility, and design conformance.
---

# C++ Storage Code Review

Review a local diff, commit range, or merge request. Report only actionable findings
supported by source evidence.

## Establish Scope

1. Resolve the base and head revisions.
2. Read repository review rules and linked design/spec documents.
3. Group changes by behavior rather than file extension.
4. Trace modified interfaces to callers, implementations, and tests.

## Review Dimensions

### Correctness

- boundary conditions, overflow, partial results, stale state;
- error propagation and retry behavior;
- idempotency and duplicate requests;
- persistence versus in-memory success.

### Concurrency and Async I/O

- lock ordering and data races;
- callback execution context;
- object and buffer lifetime;
- cancellation, shutdown, and callback-after-destruction;
- blocking work on event-loop or consensus threads.

### Memory

- unbounded containers and queues;
- hot-path allocation churn;
- large captures, copies, and retained buffers;
- missing pooling or capacity limits.

### Recovery and Compatibility

- replay, restart, leader change, snapshot, and partial commit;
- wire, metadata, and configuration compatibility;
- rolling upgrade and downgrade assumptions.

### Operability

- stable metrics, log identifiers, tracing, and error codes;
- actionable failure messages without secrets.

### Tests

- happy path plus boundary, failure, concurrency, recovery, and compatibility cases;
- assertions that prove state, not just return codes.

## Severity

- P0: security, data loss, or system-wide outage.
- P1: likely correctness, availability, or compatibility defect.
- P2: meaningful risk or missing coverage.
- P3: localized maintainability issue.

Each finding must include severity, file and line, impact, triggering scenario, and
the smallest credible fix. If no actionable finding exists, say so and list residual
test risk.

