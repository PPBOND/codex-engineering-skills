# Contract and asynchronous ownership

Read this file for a public API, Env, callback, buffer, Reactor, or state-machine
change. It records the decisions that are easiest to break while simplifying code.

## Truth labels before edits

Use four labels in notes and review comments:

- **Confirmed**: visible in the current source, CMake, or a passing command.
- **User-requested**: a desired contract or correction; it is not proof that code
  already implements it.
- **Inferred**: a design consequence that still needs agreement or a test.
- **Unverified**: a claim for which the required source or build evidence is missing.

Never use a design document, an adjacent worktree, or an old commit as proof of the
current checkout without checking the current symbols and revision.

## Integer error contract

The database uses a plain integer for both admission and final error reporting:

```text
ret == 0  -> success (or, for an admission call, the request was accepted)
ret < 0   -> negative errno failure
```

For an asynchronous `Begin*`/`Submit*`, the immediate `ret == 0` means that one
request was accepted and owns one later completion; it does not skip the final
callback result. The callback's integer follows the same `0`/negative-errno rule.

Use standard negative errno values such as `-EINVAL`, `-EAGAIN`, `-ENOMEM`, `-ENOENT`,
`-EILSEQ`, and `-EIO` according to the existing path. A result member may be named
`status` for API readability, but its type and meaning remain `int`; do not invent a
custom status enum, `error_status`, or a positive “failure” code. Preserve the local
rule that a rejected admission creates no request and therefore no user callback
unless the current API explicitly says otherwise.

An enum that only reports scheduler progress (for example, submitted I/O,
backpressure, or callback-ready) is not an error status and may remain when it makes
the state transition clearer. Keep the actual failure value as the plain negative
`int` carried by the operation result.

When changing this contract, search all declarations, implementations, tests, tools,
and documentation before editing. Public ABI, serialization, and callback consumers
must move together.

## Poll and callback ownership

The current boundary is:

```text
caller -> Begin*/Submit* (validate, reserve, register only)
poller -> env.Poll() -> AsyncDatabase::Poll()
        -> submit Env I/O / advance state / dispatch user callback
```

Do not call `Env::Poll()` from Database, wait in a loop, or invoke a user callback
directly from an Env completion stack. A successful Env submission owns exactly one
completion obligation. Keep the buffer, borrowed `void*` context, callback pointer,
and request slot alive until that completion has returned; clear or transfer callback
ownership before a re-entrant callback can submit another request.

Raw pointers are acceptable for a borrowed callback context or a C callback bridge when
the comment states non-null rules, owner, Reactor thread, and lifetime. Do not replace a
well-defined borrow with a speculative ownership class.

## State-machine discipline

Keep a state value only when it marks a real I/O, parse/publish, visibility, rollback,
or resource boundary. If `IoPurpose`, a result flag, a cursor, or an owned buffer already
proves the same fact, reuse it. Conversely, do not merge states whose completion or
persistence semantics differ. Preserve established function names and callback-driven
progress unless the user explicitly accepts a contract change.

## Comment shape

Write comments for the next reviewer, in plain language:

- why the state changes here;
- who owns the buffer/lease/request now;
- what callback or completion triggers the next step;
- when the resource is released and what remains visible after a failure.

Do not translate an `if` line into prose. For a difficult path, start with a tiny
example (for example, sequence 100 write, sequence 101 tombstone, sequence 102 new
write), then name the real symbols and limits.
