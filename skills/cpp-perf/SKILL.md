---
name: cpp-perf
description: >
  Analyze and optimize C++17 code performance for ARM and x86 targets with
  measurement, profiling, benchmarking, compiler-output inspection, and
  correctness checks. Use when the user asks to optimize C++ performance,
  profile hotspots, improve vectorization or cache behavior, or benchmark C++.
  Do not use for general C++ questions, ordinary code review, non-C++ code, or
  build-only tasks.
---

# C++ Performance Optimization (Codex)

Use this skill only for performance-focused C++ work. Start with the value screen below. Load matching sections of [`cpp-perf.md`](cpp-perf.md), knowledge patterns, profiles, and templates only after they are needed for the current stage; do not read or execute the whole pipeline by default.

## Value-first workflow

1. **Screen before proposing experiments.** Establish actual input sizes, call frequency and hotspot share from code and existing evidence. Estimate the end-to-end saving, including construction, update and reclamation costs. A component occupying 1% of total time and becoming 10x faster saves only about 0.9% of total time. Also consider concrete tail-latency, I/O and resource targets; mean CPU share alone does not describe them.
2. **Reject low-value work early.** If the upper bound is marginal for the user's goal, deliver that conclusion instead of building candidates or a large benchmark matrix. If hotspot evidence is missing, use one bounded, inexpensive observation to decide whether further work is justified. Theory screens proposals; it is not a measured speedup.
3. **Pilot, then promote.** Unless the user specifies otherwise, start with one baseline, one minimal candidate and 1–2 representative cases, reusing existing harnesses. Only a convincing improvement relevant to the overall goal justifies broad performance coverage. Complete explicitly requested comparisons and required correctness tests; these internal stages do not add approval gates.
4. **Stop inconclusive tuning.** Before a targeted rerun, state the hypothesis, the distinguishing measurement and the exit condition. For small deltas/noise, default to at most one such rerun; stop if evidence remains inconclusive. Do not keep changing layouts, adding variants or rerunning full matrices to obtain a favorable result. Preserve failures and neutral results.

Fix fairness conditions before the first run: source snapshot, compiler/options, data distribution, paths, cache state, concurrency and machine load. Keep fixture preparation and correctness checks outside measured work. External edits do not automatically restart the matrix; preserve the comparison snapshot and validate only affected integration paths, without claiming old evidence covers changed code.

Keep token use proportional to the decision: read only relevant functions and skill sections, summarize/filter large tool results before returning them, and reuse prior evidence. The detailed pipeline's broad discovery, sampling and adaptive-repeat recipes are conditional references subordinate to this workflow and the user's requested limits.

## Karpathy Scope and Goal Guardrail

For a non-trivial optimization, read and apply
[`../code-auto/references/karpathy-coding-guardrails.md`](../code-auto/references/karpathy-coding-guardrails.md).
State the measured bottleneck, assumptions, smallest candidate change, and success metric before editing; do not add speculative abstraction or configurability, broaden a diff, or claim an improvement without reproducible evidence.

## Mandatory constraints

- Treat C++17 as the highest permitted language standard. Generated benchmarks and fixes must compile with the project's C++17 configuration.
- Do not introduce or recommend C++20/C++23 syntax, library APIs, compiler modes, or a standard-version upgrade as an optimization. Report such a change as a compatibility blocker.
- Do not claim a speedup from static inspection alone. Separate estimated impact from measured results and state confidence and prerequisites.
- Preserve correctness first: compare baseline and optimized behavior before reporting a performance result. If an optimization regresses or cannot be reproduced, retract it.

## Codex execution rules

1. Parse snippet, file, or diff input and identify the target function and call context.
2. Inspect the workspace's build system and existing compiler flags before choosing commands or profiles.
3. Check for a project-local `cpp-perf-platform.yaml`. If absent, use a local/native build only when the target is clear; do not create project configuration without the user's authorization.
4. Expand context only to the necessary callers, callees, types, includes, and configuration. Use the pipeline's two-level and context-budget limits.
5. Read the measurement methodology before designing a benchmark, and consult compiler optimization reports before asserting that vectorization or inlining was missed.
6. For analysis-only requests, present findings and obtain the user's choice before implementing. An explicit request to implement an optimization already selects that item; continue within that scope without asking again. Ask only about new items or material tradeoffs not covered by the request.
7. Keep generated cases and reports in a scoped temporary directory; do not overwrite project files unless the user explicitly asks to apply the selected change.

## Resource and tool mapping

- Resolve every upstream path such as `skills/cpp-perf/knowledge/...` relative to this installed skill directory, not the user's workspace.
- Map Claude Code tool names in the detailed pipeline as follows: Read/Grep/Glob → `rg` or read-only shell inspection; Write/Edit → `apply_patch`; Bash → `shell_command`.
- On Windows, do not assume Bash, `/tmp`, `g++`, `objdump`, or Linux utilities exist. Prefer the workspace's CMake/toolchain and PowerShell equivalents, or explicitly report the missing dependency.
- Use the bundled templates and profiles from this skill; do not recreate them in the project.

## Remote execution

- When target execution requires SSH or a remote VM, read [`remote-vm`](../remote-vm/SKILL.md) and follow its safety rules.
- Reuse that skill's connection workflow instead of copying credentials into this skill, `cpp-perf-platform.yaml`, generated manifests, process arguments, or logs.
- Never print, echo, commit, or persist a password. Prefer SSH agent, key-based authentication, environment-backed secret storage, or an interactive credential mechanism.
- Verify the exact remote target/worktree and command from the request, configuration, and prior authorization; this is an evidence check, not a mandatory extra prompt. First-use approval still applies if that target/action is not yet authorized. Follow `remote-vm` for shared-service and system-change approvals.

## Required report content

Report the target and platform, hot path, current behavior, estimated cycles or memory effects, confidence, measurement status, correctness status, disassembly/compiler evidence, and any caveats. Distinguish high/medium/low impact from high/medium/low confidence. Negative or negligible results are valid outcomes.
