---
name: code-review-new-feature
description: Structure a deep review of a large new feature by splitting changes into logical modules, building checklists, and consolidating findings.
---

# Large New-Feature Review

Use when a change is too large for a reliable file-by-file review.

## Inputs

- local path, commit range, or merge request;
- optional focus such as correctness, concurrency, memory, or compatibility;
- linked design or specification.

## Workflow

1. Resolve the exact diff and read repository review rules.
2. Build a change inventory by behavior and ownership.
3. Split the feature into review modules with minimal overlap, for example:
   - public API and protocol;
   - state and persistence;
   - execution and concurrency;
   - recovery and compatibility;
   - observability and tests.
4. Create a checklist for each module.
5. Trace cross-module invariants and lifecycle transitions separately.
6. Consolidate duplicate findings and resolve contradictory assessments.
7. Verify high-severity findings against current source and tests.

## Checklist

- requirement and design conformance;
- state truth source and lifecycle;
- error propagation, retry, and idempotency;
- thread safety and callback lifetime;
- memory bounds and hot-path allocations;
- partial failure, restart, and recovery;
- wire/data/config compatibility;
- metrics, logs, and operator controls;
- boundary, failure, concurrency, and recovery tests.

## Findings

Use P0 through P3 severity. Every finding must include source location, triggering
scenario, impact, evidence, and smallest credible fix. Finish with residual risk and
unreviewed areas.
