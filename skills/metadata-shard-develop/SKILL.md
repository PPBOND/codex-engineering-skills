---
name: metadata-shard-develop
description: Repository entrypoint for metadata-shard development. Use when work touches metadata partitioning, placement, routing, replication, recovery, or shard tests.
---

# Metadata Shard Development

## Karpathy Change Guardrail

Before design or edits, read and apply
[`../code-auto/references/karpathy-coding-guardrails.md`](../code-auto/references/karpathy-coding-guardrails.md).
Separate confirmed shard behavior from assumptions, choose the smallest change supported by the current routing/ownership contract, avoid unrelated refactoring, and define the exact build/test or recovery evidence required to claim completion.

The repository is the source of truth. Before editing:

1. locate metadata-shard source, protocol definitions, design documents, and tests;
2. read the nearest repository instructions and module design;
3. identify routing keys, shard identity, ownership, and replicated truth;
4. trace lifecycle operations through callers and persistence;
5. confirm thread and callback contexts;
6. find existing test targets and build commands.

Pay special attention to shard split/merge, migration, leader change, stale epochs,
idempotency, restart recovery, and compatibility.

Do not invent file paths or command names. If normative module documentation is
missing, state the gap and derive behavior from code with exact references.
