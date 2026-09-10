---
name: mr-comments
description: Fetch merge-request discussions or a specific review note and evaluate each comment against the current code and design.
---

# Merge-Request Comment Evaluation

## Karpathy Comment-Review Guardrail

Read and apply
[`../code-auto/references/karpathy-coding-guardrails.md`](../code-auto/references/karpathy-coding-guardrails.md).
Classify comments from current diff/source/design evidence, keep unverified claims as clarification requests, and propose only the smallest task-relevant fix; do not turn a valid localized comment into a broad refactor or unrelated cleanup.

## Inputs

- merge-request URL;
- optional note or discussion anchor;
- optional local checkout.

Use the Git provider connector or authenticated CLI. Parse the host, project path,
MR number, and optional note ID from the supplied URL; do not assume a host.

## Workflow

1. Fetch the selected note or all unresolved discussions.
2. Read the exact diff and current file version.
3. Classify each comment:
   - valid defect;
   - valid improvement;
   - already fixed;
   - stale after later changes;
   - incorrect;
   - needs clarification.
4. Support the classification with source locations, tests, or design text.
5. Propose the smallest fix for valid comments.
6. Do not reply, resolve, or modify the MR unless the user explicitly asks.

## Output

For each note, report author, location, concern, assessment, evidence, and suggested
action. Highlight comments that could cause correctness, security, data, or
compatibility issues.
