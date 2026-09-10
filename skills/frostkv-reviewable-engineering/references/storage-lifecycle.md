# Storage lifecycle, publication, and threading

Read this file for Open/replay, checkpoint, compact, Position Index GC, file deletion,
recovery, or any proposal to move maintenance to another thread.

## Current ownership map

- `src/internal/core/` owns request admission and Reactor progression.
- `src/internal/open/` owns Open, Root loading, and replay.
- `src/internal/checkpoint/`, `src/internal/compact/`, and `src/internal/index_gc/`
  own maintenance paths.
- `src/internal/*_format.*` owns on-disk encoding and strict parsing.
- The published Root, Directory Chunk metadata, and Position Page contents are
  immutable snapshots. Only the Position Page cache is LRU-evictable in the current
  design; ordinary writes append Data Records and do not edit a published page.

Verify these facts in the current checkout before copying them into a new design.

## Every maintenance change must answer five questions

1. What durable object is the source of truth after a restart?
2. In what order do body, locator/metadata, in-memory install, and cleanup become
   visible?
3. What does each crash window leave on disk, and how does Open recover it?
4. Which owner holds each buffer, reader, lease, catalog entry, and callback?
5. Exactly when is an old Data File, Root, Segment, or index page safe to delete?

An old object is not reclaimable merely because a new object was written. Require a
durable locator/catalog update, a successful publication, a reference-closure check,
and the existing reader/cache lifetime rules. Logical namespace deletion is a tombstone
first; physical reclaim belongs to checkpoint/compact/GC and must be described
separately.

Validate checksums before parsing cold Directory Chunks or other disk input. A malformed
or inconsistent closure must return a negative errno through Poll; it must not escape as
an exception or be silently treated as an empty object.

## Safe two-thread shape (design guidance, not current implementation)

The current FrostKV model is single Reactor/single owner. If a future design needs one
append thread and one maintenance thread, reduce sharing rather than putting locks
around `DatabaseState`:

```text
writer owner                         maintenance owner
active delta + append I/O            FrozenSnapshot (read-only)
        |                                      |
        +-- freeze/cut --> SPSC message ------> build candidate generation
                                                   |
                         SPSC result <------------+
                         foreground owner validates generation
                         and publishes Root/DB Meta, then reclaims
```

“冻结快照” means the writer stops changing one delta at a cut sequence and hands an
immutable view (or ownership of its buffers) to maintenance. New writes go to a new
active delta. Maintenance never reads or mutates the live delta, sequence counters,
catalog, cache, callback queues, or published Root.

“SPSC 消息” means a single-producer/single-consumer queue transfers ownership of the
snapshot and the candidate result; it is not a shared mutable map. “前台唯一发布”
means only the Reactor owner changes visible Root/DB Meta/catalog/cache state after
checking that the candidate generation still follows the current generation. This
keeps races local to the hand-off protocol. Letting the second thread directly touch
the existing state would race on delta/frozen-delta, sequence/frontier, catalog,
resident-byte accounting, LRU/leases, callback lifetime, and old-file deletion.

Small example: writes 100–105 are frozen at cut 105; maintenance builds generation 8
from that snapshot while writes 106–108 enter the new active delta. If generation 8 is
published, reads combine active(106–108) with Root(8). If a newer cut wins, the old
candidate is discarded by generation check; it must never overwrite the newer Root.

Checkpoint is the safer first candidate for this split. Compact additionally needs
relocation visibility, a generation lease, handling for writes that win over copied
records, and delayed source retirement.

## Failure and callback rules

- Queue-full or transient Env errors retain the current stage and retry with a bounded
  budget; do not spin or retry forever.
- After publication succeeds, cleanup failure is not a publication rollback. Keep the
  durable recovery marker, stop new admission if required by the existing lifecycle,
  and let Open finish cleanup on a later restart.
- A callback is dispatched by Poll exactly once, after state/lease ownership is settled.
  Test final visibility and resource retention, not an accidental callback timing.
