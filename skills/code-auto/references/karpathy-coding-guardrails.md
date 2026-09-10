# Karpathy Coding Guardrails (Codex Adaptation)

This is the shared Codex application of the installed
[`karpathy-guidelines`](../../karpathy-guidelines/SKILL.md) skill. Apply it
proportionately to non-trivial coding, planning, testing, analysis, and review
work; a one-line mechanical correction does not need a ceremony.

## 1. Establish facts before changing code

- Separate verified repository facts, material assumptions, and open decisions.
- Do not silently choose between interpretations that change behavior, public
  contracts, compatibility, data safety, or task scope. Ask a concise question
  when that choice cannot be resolved from the code or user request.
- For a low-risk, bounded ambiguity, state the assumption and proceed instead
  of blocking routine work.
- Resolve checkable facts from source and configuration before asking. Reuse an
  explicit decision or approval for the same action, target, and scope; ask again
  only when those materially change. Continue independent work while a necessary
  clarification is pending.
- Implementation, validation, commit, publication, and shared-system changes have
  distinct authorization boundaries. Skill selection and silence grant no extra
  authority. Preserve explicit approval gates, including user-requested plan review.
- Delegation follows the project's manual switch. Self-review can fulfill a normal
  review step in single-agent mode, but cannot be reported as an explicitly
  requested independent review; disclose that gap and finish unaffected work.

## 2. Prefer the smallest supported solution

- First consider no code change, deletion, existing repository behavior,
  standard-library/platform support, then a local implementation.
- Do not add speculative features, configurability, dependencies, abstractions,
  or extension points without a current caller and requirement.
- Do not invent handling for purely hypothetical cases. This never permits
  removing a credible validation, recovery path, security control, ownership
  rule, or project-mandated error contract.

## 3. Keep changes surgical

- Every changed file and line must trace to the active request or an artifact
  made unused by this change.
- Preserve unrelated user edits, code, comments, and formatting. Match local
  style; report pre-existing cleanup opportunities rather than changing them.
- Remove only imports, variables, helpers, or tests made obsolete by the
  current change.

## 4. Work toward an observable goal

- State the behavior or invariant to establish and the smallest meaningful
  verification before implementation.
- For a bug fix, add or reuse a reproducer when practical, then verify it
  passes after the fix. For a refactor, compare relevant behavior before and
  after.
- Do not claim completion from inspection alone when a focused build, test,
  benchmark, or review can establish the result.
- A minimal implementation must still satisfy the complete requested outcome.
  Continue through authorized dependent steps and child plans; phase boundaries
  are progress markers, not new permission gates.
- After repeated failure, change the diagnostic approach rather than blindly
  retrying. Pause dependent work only for a real missing decision, permission,
  resource, or unsafe next step; report evidence and a concrete resumption path.
- Run checks proportional to the changed behavior and explicit requirements.
  Once required checks pass, repeat them only for new changes, failures, or
  unresolved risks. Optional follow-ups do not block completion.

## Review application

- Findings and recommendations require diff/source/design/test evidence.
- Flag unrequested scope growth, speculative flexibility, and unrelated edits;
  recommend the smallest credible correction rather than a broad rewrite.
- Keep an unverified concern as a question or note, not a fabricated defect.

## Precedence

User requirements, repository instructions, language compatibility rules,
security/reliability contracts, and required validation take precedence over
this reference.
