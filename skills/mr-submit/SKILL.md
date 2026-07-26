---
name: mr-submit
description: Create a GitLab merge request from the current branch to the repository default branch, generating a concise title and body from the committed diff.
---

# Submit a Merge Request

Use for GitLab.com or self-managed GitLab through an authenticated connector or
`glab`.

## Preconditions

1. Confirm the working tree and branch.
2. Verify commits intended for submission.
3. Resolve the default target branch from the remote.
4. Ensure the source branch is pushed.
5. Check whether an open MR already exists for the source branch.

## Create

Generate:

- title describing the primary behavior change;
- summary of important implementation changes;
- validation commands and results;
- risks, compatibility, and follow-up work;
- links to issues or specs supplied by the user.

Create one MR against the default branch. Do not enable auto-merge, assign reviewers,
or change labels unless requested.

## Verification

Read back the canonical MR URL, title, source, target, and state. Return the URL and
any CI status available immediately after creation.
