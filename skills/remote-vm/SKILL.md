---
name: remote-vm
description: Build, test, lint, debug, or run a project on a remote VM when the local environment is unsuitable.
---

# Remote VM Workflow

## Connection Configuration

Resolve the SSH target, user, and key from the user's request or authorized local
SSH configuration. This published skill does not provide a default server.
Prefer key-based authentication. Do not put credentials on a process command line.
If the configured key is unavailable or rejected, ask for an approved connection
method rather than silently falling back to password authentication.

## Inputs

- SSH target and authentication method;
- remote repository or worktree path;
- requested build/test/run command;
- branch or commit;
- required environment or container context.

Read these from user input, repository documentation, or environment configuration.
Do not embed host addresses, passwords, private-key locations, or private repository
paths in the published skill. Never expose credentials in output.

## Workflow

Use the existing request and project policy to determine whether remote validation
is authorized. Verify the host/path with tools; do not turn every "confirm" below
into a user prompt. Once the target and scoped build/test operation are authorized,
continue dependent commands and safe diagnostics. Static-only requests prohibit
remote builds; shared-service and system changes keep the explicit Safety gates.

1. Verify SSH connectivity and the resolved remote path.
2. Inspect remote Git status before changing anything.
3. Confirm the intended branch/commit and preserve unrelated changes.
4. Use the repository's documented build wrapper, presets, or package manager.
5. Run the narrowest relevant configure/build/test command.
6. Capture command, exit code, key output, and artifacts.
7. On failure, diagnose the first actionable cause and fix task-owned build/test issues when implementation is authorized. Continue safe independent checks; if credentials, a user decision, or new authority are required, report the exact blocker and resumption step. A failed command is not by itself task completion.

## Worktrees

Prefer reusing an existing idle isolated directory or worktree. Before reuse, check
its resolved path, Git status, running build/test commands and process working
directories, plus any task ownership markers. A dated directory name alone does not
prove it is unused. Preserve unrelated source changes and existing result artifacts.

Use a separate worktree when the remote checkout is shared or dirty. Create a new
isolated directory only when no suitable idle one exists or the user requests one.
Resolve all paths before creation or cleanup, and never delete a worktree without
explicit scope.

Generic pattern:

```bash
ssh <vm> 'cd <repository> && git status --short --branch'
ssh <vm> 'cd <worktree> && <project-build-command>'
ssh <vm> 'cd <worktree> && <project-test-command>'
```

## Safety

- Keep commands scoped to the requested repository.
- Do not modify global Git configuration.
- Do not overwrite remote changes.
- Avoid exposing environment variables or credentials in output.
- Ask before restarting shared services or changing machine-wide packages.

## Output

Return remote revision, commands, result, artifact paths, root cause of failures, and
the next safe step.
