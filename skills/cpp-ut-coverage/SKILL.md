---
name: cpp-ut-coverage
description: Improve C++ unit-test coverage by mapping uncovered lines and branches to behaviors, selecting direct, mock, parameterized, or fault-injection tests, and verifying the result.
---

# C++ Unit-Test Coverage

## Karpathy Test Guardrail

Before adding tests, read and apply
[`../code-auto/references/karpathy-coding-guardrails.md`](../code-auto/references/karpathy-coding-guardrails.md).
Map each test to a concrete uncovered behavior or risk, choose the smallest stable seam, and define the observable assertion and coverage result. Do not add broad fixtures, production hooks, or scenarios unsupported by the current contract merely to raise a metric.

## Workflow

1. Resolve the coverage report to exact source lines and branches.
2. Read surrounding code, callers, error contracts, and existing tests.
3. Classify each gap:
   - normal input or boundary;
   - dependency result requiring a mock;
   - allocation, I/O, or system failure suited to fault injection;
   - asynchronous ordering or callback;
   - defensive/unreachable code;
   - generated or excluded code.
4. Select the smallest stable test seam.
5. Implement tests using repository conventions.
6. Build and run the narrow target.
7. Regenerate coverage and confirm the intended lines or branches changed.
8. Run relevant neighboring tests to detect regressions.

## Strategy Selection

- Direct call: deterministic behavior with accessible inputs.
- Parameterized test: a matrix of boundaries or state transitions.
- Mock/fake: dependency outcomes are part of the public contract.
- Fault injection: failures cannot be reached reliably through normal inputs.
- Async test: ordering, cancellation, callback, or lifetime behavior.

Do not add production-only hooks solely for coverage unless the behavior is otherwise
untestable and the design tradeoff is documented. Avoid assertions that merely
execute a line without checking state or side effects.

## Output

List covered gaps, chosen strategy, files changed, commands run, before/after
coverage, and justified exclusions.
