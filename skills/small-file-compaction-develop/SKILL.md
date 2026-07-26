---
name: small-file-compaction-develop
description: Design, implement, test, and review a generic small-file compaction or packing subsystem for a storage service.
---

# Small-File Compaction Development

Use for systems that combine many small objects into larger container files while
preserving lookup, deletion, recovery, and lifecycle correctness.

## Required Model

Define:

- source object identity and immutable metadata;
- container-file identity and layout;
- index mapping from object to container offset and length;
- states such as pending, compacting, committed, reclaimable, and deleted;
- authoritative state versus rebuildable cache;
- ownership of scheduling, execution, commit, and garbage collection.

## Design Workflow

1. Read existing object lifecycle, metadata, and recovery code.
2. Establish invariants before selecting data structures.
3. Compare at least:
   - append-only packing;
   - size-tiered compaction;
   - time-window compaction.
4. Evaluate memory overhead, write amplification, read amplification, crash recovery,
   and deletion cost.
5. Specify the atomic commit point and restart reconciliation.
6. Bound queues, index memory, batch size, and concurrent jobs.
7. Define metrics, logs, tracing identifiers, and operator controls.

## Implementation Rules

- Keep container construction separate from metadata publication.
- Treat retries as normal and make all commit operations idempotent.
- Never reclaim source data before the new mapping is durable and visible.
- Validate offsets and checksums on read.
- Pool frequently allocated I/O-path objects when the host project provides a pool.
- Avoid unbounded per-object metadata in memory.

## Tests

Cover:

- empty, minimum, maximum, and mixed-size batches;
- duplicate scheduling and idempotent retry;
- crash before and after each durable transition;
- source deletion during compaction;
- checksum or truncated-container failure;
- concurrent reads, deletes, and compaction;
- restart, replay, and garbage collection.

## Review Output

Report violated invariants, unsafe transitions, memory growth, recovery gaps, and
missing tests with concrete source locations.

