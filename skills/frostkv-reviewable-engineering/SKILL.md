---
name: frostkv-reviewable-engineering
description: "Use when working on the FrostKV/partial_cached_kv C++17 storage engine, especially async API or Env contracts, state machines, checkpoint/compact/recovery/index GC, comments, tests, performance, or behavior-preserving refactors. It turns repository evidence and user-confirmed requirements into a small, reviewable, verifiable change; it is not a generic database tutorial and does not grant permission to publish changes."
---

# Frostkv Reviewable Engineering

Use this skill to keep FrostKV changes easy to understand, safe to recover, and honest
about what was actually verified. The entry file is a router, not a copy of the whole
project rulebook.

## Route every task

1. Read the repository `AGENTS.md` and the relevant source before proposing a change.
   Start with `git status --short --branch`, the public headers, the real call path,
   CMake target, and focused tests. Preserve unrelated dirty and untracked files.
2. Write a short task anchor: Goal, Done When, Boundaries, and the current `Current ->
   Target` mapping. Label each claim as `confirmed`, `user-requested`, `inferred`, or
   `unverified`.
3. Load only the route that can change the next action:

   | If the task concerns | Read |
   | --- | --- |
   | public API, `int` errors, callbacks, buffers, Reactor, or state values | [contract-and-async.md](references/contract-and-async.md) |
   | Open/replay, checkpoint, compact, index GC, publication, reclaim, or a second thread | [storage-lifecycle.md](references/storage-lifecycle.md) |
   | comments, naming, explanation, refactor scope, or review findings | [review-and-explain.md](references/review-and-explain.md) |
   | build, CTest, benchmark, commit, or remote publication | [validation-and-release.md](references/validation-and-release.md) |

4. If the user is asking whether a design is reasonable, analyze and show the
   boundaries first; edit only after the user clearly authorizes implementation.
   Prefer deletion and reuse over a new class, enum, tick loop, or abstraction. Keep
   one writer per working tree and one owner for mutable Reactor state.
5. Work in small verifiable steps until the complete authorized outcome is met;
   one step passing is not completion if required work remains. Keep refactors
   behavior-preserving, and implement requested behavior changes explicitly. Run
   the narrowest real target that proves the change; do not treat format/fallback
   results as recovery, native SPDK, or production performance evidence.
6. Close the task: inspect the diff, re-check the task anchor, scan for a newly learned
   general rule, and report exact files/symbols, commands, results, and uncovered paths.
   Report reusable lessons if helpful; edit skills or memories only when explicitly
   requested, and never turn a session transcript into a reference file.

## FrostKV boundaries that must survive refactors

- C++17, one Reactor owner, asynchronous Database API, and no hidden synchronous drain.
- Error state is a plain `int`: `0` is success and a value `< 0` is a negative errno
  failure. Do not add a project-specific `status`/`error_status` type or use a positive
  value as success. For an async admission call, `0` means accepted; the later
  callback still reports the operation's own `0`/negative result. Keep both meanings
  explicit at each API.
- `Begin*`/`Submit*` perform synchronous admission; `AsyncDatabase::Poll()` submits
  Env I/O and dispatches user callbacks. An Env completion only advances internal
  state. Buffers, callback contexts, and request slots live through completion, and a
  callback is delivered exactly once.
- Build dependencies used by the project are fixed in the repository's `third_party/`
  tree; do not make configure or a normal build fetch an unpinned external copy.
- Published index objects are immutable. Name the durable source of truth, publication
  order, crash window, recovery action, and the point at which an old file becomes
  reclaimable before changing checkpoint, compact, or GC code.
- Treat disk bytes as untrusted: verify the complete checksum before strict parsing and
  close malformed input with a negative errno through the existing asynchronous path.

## Maintenance of this skill

Keep `SKILL.md` short and keep rules separate from procedures. Add a reference only
when it has an independent task-time loading reason and changes the next action. Merge
or delete stale rules when evidence shows they are no longer useful. Automatic checks
prove structure; source review and focused tests prove semantics.

The historical prompt mapping and the distinction between FrostKV rules and
FlexDB/tool-specific lessons live in the repository document
`docs/analysis/cross-session-guidance.md`.
