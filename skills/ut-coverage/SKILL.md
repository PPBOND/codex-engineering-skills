---
name: ut-coverage
description: Analyze a coverage report, select effective test strategies for uncovered behavior, implement tests, and verify coverage locally or on a remote build environment.
---

# Unit-Test Coverage Improvement

## Inputs

- coverage report or artifact;
- source scope;
- build and test instructions;
- local or remote execution environment;
- coverage target or acceptance rule.

Discover commands from repository instructions and CI configuration. Do not assume a
build system, build directory, remote host, or package registry.

## Workflow

1. Map uncovered lines and branches to functions and behaviors.
2. Exclude generated code only when the repository policy permits it.
3. Read existing tests and identify the nearest stable test seam.
4. Classify each gap:
   - ordinary input;
   - boundary or state matrix;
   - dependency outcome;
   - asynchronous ordering;
   - system or allocation failure;
   - defensive/unreachable path.
5. Select direct, parameterized, mock/fake, integration, or fault-injection coverage.
6. Implement the smallest behavior-focused tests.
7. Build and run the narrow test target.
8. Regenerate coverage using the repository's documented command.
9. Confirm the intended gap closed and run related tests.

## Remote Execution

When the build must run remotely, use `$remote-vm` and obtain the SSH target,
repository path, and commands from configuration. Preserve unrelated remote changes.

Generic command shapes:

```bash
<configure-with-coverage>
<build-test-target>
<run-test-target>
<generate-coverage-report>
```

## Quality Rules

- Assert returned values, state transitions, side effects, and error propagation.
- Do not add brittle timing sleeps when a deterministic event can be awaited.
- Do not weaken production checks to make a line reachable.
- Treat increased line coverage without behavioral assertions as insufficient.

## Output

Report uncovered behavior, selected strategy, tests added, commands and results,
before/after coverage, remaining gaps, and justified exclusions.
