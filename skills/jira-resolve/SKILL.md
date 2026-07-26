---
name: jira-resolve
description: Resolve or advance a Jira issue using merge-request information by adding a traceable comment and applying an available workflow transition.
---

# Resolve a Jira Issue

This skill performs external writes. Use it only when the user explicitly asks to
resolve, close, transition, or "walk through" an issue.

## Inputs

- Jira issue key or URL;
- merge-request URL or project plus MR number;
- target workflow outcome, if the user specified one.

Obtain `JIRA_BASE_URL`, Git provider host, and authentication from configured tools
or the environment. Never hard-code them.

## Workflow

1. Read the issue, its current status, and available transitions.
2. Resolve the exact merge request and verify title, state, source branch, target
   branch, and URL.
3. Check whether an equivalent MR comment already exists.
4. Add one concise comment containing the MR title and canonical URL.
5. Select only a transition exposed by Jira:
   - use the user's requested target when available;
   - otherwise choose the narrowest transition consistent with "resolved";
   - stop and ask if multiple materially different outcomes remain.
6. Re-read the issue and verify the final status and comment.

Do not reopen, close, or reassign unrelated issues. Avoid duplicate comments and
idempotently handle retries.

## Output

Report the issue, MR, comment result, transition applied, and verified final status.

