# Review, explanation, and minimal refactoring

Read this file for code cleanup, comments, architecture explanations, naming, or a
review response.

## Before changing code

- Locate the actual symbol and all callers with the repository search tools.
- Draw the short control flow: admission -> I/O -> completion -> next stage -> callback.
- List preserved behavior: API names, state transitions, ordering, limits, error values,
  restart visibility, and callback/re-entry behavior.
- State what is intentionally out of scope. A neighboring module or a future design is
  evidence to inspect, not permission to rewrite.

Prefer a small deletion or helper reuse. Do not introduce a class, enum, scheduler tick,
or new vocabulary merely to make a diagram look cleaner. If a rename is useful, first
prove that the old name is misleading and check every public/documented consumer.

## How to explain a hard path

Use this order:

1. one concrete numeric example;
2. the current code path and owner;
3. the state/visibility change;
4. memory and logical/physical I/O consequences;
5. alternatives, risks, and what remains unverified.

Say “the current checkout implements …”, “the proposed design would …”, or “not tested”
instead of blending those claims. Complexity, logical I/O, physical I/O, CPU, memory,
throughput, and tail latency are separate facts.

## Review checklist

Look for:

- a state or `bool` duplicating an existing cursor/result/`IoPurpose`;
- a callback reachable from both completion and Poll, or a buffer released too early;
- an error swallowed, converted to a default success, or represented by a custom status;
- a parser called before checksum/length/range validation;
- a new mapping published before its locator/catalog is durable;
- an old object deleted before the new reference closure and reader lifetime are safe;
- comments that describe what the code says but not why ownership or ordering matters;
- tests that cover only a happy return value or callback timing;
- claims based on an adjacent branch, estimate, or one fallback test.

Report findings as P0–P3 with file/symbol, concrete failure, smallest safe fix, and a
focused validation command. Do not inflate a style preference into a correctness issue.
