---
name: cicd-check
description: Diagnose CI/CD, unit-test, integration-test, crash, timeout, and core-dump failures from pipeline links, job IDs, logs, or remote runners.
---

# CI/CD Failure Diagnosis

Determine the first actionable root cause instead of summarizing the last error line.

## Accepted Inputs

- a CI pipeline or job URL;
- a project and job identifier;
- a local log directory;
- a remote runner plus log directory;
- a test binary, core dump, or failing test name.

Use the repository's configured CI provider and authenticated CLI when available.
Never guess organization URLs, runner hosts, or credentials.

## Workflow

1. Resolve the exact pipeline, job, stage, commit, and runner.
2. Identify the earliest failing stage and distinguish infrastructure failure from
   product/test failure.
3. Download or read only the relevant logs and artifacts.
4. Search in this order:
   - explicit assertion, fatal, sanitizer, or exception;
   - process exit code or signal;
   - timeout and deadlock symptoms;
   - OOM, disk-full, network, container, or runner errors;
   - cascading cleanup failures.
5. For test failures, map the failing test to its source and recent changes.
6. For crashes, identify the executable and build ID, then use the matching binary
   and debug symbols for the backtrace.
7. Compare with a successful run only when it can isolate an environmental change.
8. Produce a root-cause statement backed by exact log or source locations.

## Remote Logs

When remote access is required, obtain the host and paths from CI metadata or the
user. Keep commands read-only unless repair was explicitly requested.

Example placeholders:

```bash
ssh <runner> 'find <artifact-root>/<job-id> -maxdepth 2 -type f'
ssh <runner> 'grep -RniE "fatal|assert|segmentation|sanitizer|out of memory" <artifact-root>/<job-id>'
```

## Core Dumps

Verify the core belongs to the expected executable before analysis:

```bash
file <core-file>
gdb -batch -ex 'set pagination off' -ex 'thread apply all bt full' \
  <executable> <core-file>
```

Do not treat an incomplete backtrace as proof. Record missing symbols or binary
mismatches explicitly.

## Output

Return:

- failing stage/job/test;
- classification: code, test, dependency, resource, runner, or unknown;
- primary evidence;
- root cause and confidence;
- smallest repair;
- exact verification command.

