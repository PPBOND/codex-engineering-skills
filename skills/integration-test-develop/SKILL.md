---
name: integration-test-develop
description: Design, implement, build, deploy, run, and diagnose integration tests for a multi-service project locally or on remote test hosts.
---

# Integration Test Development

Use this skill for either test-case design or end-to-end test execution.

## Discover the Project Contract

Before acting, inspect:

- build-system files and repository instructions;
- existing integration-test directories and test runners;
- service startup, health-check, and cleanup scripts;
- CI configuration and artifact locations;
- available local or remote test environments.

Treat these files as the source of truth. Do not assume command names, container
layouts, ports, or host addresses.

## Mode A: Design Test Cases

1. Read the code change or specification.
2. Identify observable behavior at public interfaces.
3. Cover:
   - happy path;
   - boundary conditions;
   - restart and recovery;
   - partial failure and retry;
   - concurrency and ordering;
   - compatibility or rolling upgrade when relevant.
4. Define setup, action, expected result, cleanup, and evidence for each case.
5. Prefer deterministic waits on health or state over fixed sleeps.

## Mode B: Build and Run

1. Resolve the exact build and test commands from the repository.
2. Build only required targets first.
3. Deploy to an isolated environment.
4. Record configuration, commit, binaries, and service versions.
5. Run the narrowest relevant suite with verbose logging.
6. Preserve logs and artifacts before cleanup.
7. Diagnose the first failure and rerun only after identifying what changed.

For remote execution, obtain the target and project directory from the user or
environment configuration. Never hard-code hosts.

## Safety

- Avoid reusing a shared environment without confirming ownership.
- Do not terminate unrelated processes.
- Verify paths before cleanup.
- Keep cleanup recoverable and scoped to resources created by the test.

## Output

Report the environment, commands, cases, results, artifact locations, root cause of
failures, and remaining gaps.

