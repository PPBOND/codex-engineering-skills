---
name: distributed-storage-arch-constraints
description: Architecture constraints reference for high-performance distributed storage systems, covering layering, threading, memory, I/O, consensus, lifecycle, and observability.
---

# Distributed Storage Architecture Constraints

Load this reference when designing or reviewing a storage-system feature. Verify all
project-specific values from source code and configuration.

## Layering

- Keep transport, protocol, orchestration, consensus, persistence, and device access
  behind explicit interfaces.
- Do not let public SDKs depend on server implementation details.
- Place ownership of durable state in one documented component.
- Cross-layer shortcuts require a measured reason and a stable abstraction.

## Threading

- Document the execution context for every callback and completion.
- Never block reactor, event-loop, or consensus threads on slow I/O.
- Define lock ordering and avoid holding locks across callbacks or remote calls.
- Make cancellation, shutdown, and callback-after-destruction behavior explicit.

## Memory

- Prefer bounded or pooled allocations on hot I/O paths.
- Make queue and cache limits configurable and observable.
- Avoid duplicating large payloads; use ownership transfer or views where safe.
- Prefer data structures with predictable overhead when memory is the primary cost.
- Define behavior under memory pressure instead of relying on allocation failure.

## I/O

- State alignment, maximum request size, ordering, and durability requirements.
- Preserve buffer lifetime until asynchronous completion.
- Distinguish accepted, persisted, replicated, and acknowledged states.
- Define partial completion and retry semantics.

## Consensus and Metadata

- Separate authoritative replicated state from rebuildable caches.
- Make terms, epochs, generations, and idempotency keys explicit.
- Specify leader change, replay, snapshot, and version compatibility.
- Never infer durable success solely from an in-memory callback.

## Lifecycle

For each stateful object, define:

- creator and owner;
- valid states and transitions;
- recovery source;
- deletion and tombstone rules;
- restart and rolling-upgrade behavior;
- metrics and diagnostic identifiers.

## Design Gate

A design is incomplete until it identifies the truth source, execution context,
memory bounds, failure recovery, compatibility behavior, observability, and tests.

