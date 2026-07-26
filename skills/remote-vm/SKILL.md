---
name: remote-vm
description: Build, test, lint, debug, or run a project on a remote VM when the local environment is unsuitable.
---

# Remote VM Workflow

## Inputs

- SSH target;
- remote repository or worktree path;
- requested build/test/run command;
- branch or commit;
- required environment or container context.

Read these from user input, repository documentation, or environment configuration.
Never embed host addresses, passwords, package remotes, or repository paths.

## Workflow

1. Verify SSH connectivity and the resolved remote path.
2. Inspect remote Git status before changing anything.
3. Confirm the intended branch/commit and preserve unrelated changes.
4. Use the repository's documented build wrapper, presets, or package manager.
5. Run the narrowest relevant configure/build/test command.
6. Capture command, exit code, key output, and artifacts.
7. On failure, diagnose the first actionable cause.

## Worktrees

Use a separate worktree when the remote checkout is shared or dirty. Resolve all
paths before creation or cleanup, and never delete a worktree without explicit scope.

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

