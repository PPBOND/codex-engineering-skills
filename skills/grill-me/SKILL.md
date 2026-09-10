---
name: grill-me
description: >
  Interview the user one question at a time to stress-test a plan, design, or
  requirement until decisions, constraints, edge cases, and acceptance criteria
  are explicit. Use when the user says "grill me", asks to be challenged, wants
  a plan or design pressure-tested, or faces a consequential implementation.
  Do not invoke for trivial, already-specified changes or when the user asks to
  skip questions.
---

# Grill Me

Adapted for Codex from [RobMitt/grill-me-skill](https://github.com/RobMitt/grill-me-skill).
It is an alignment interview, not an implementation engine: resolve the decision
tree first, then hand the clarified result to the appropriate planning or coding
workflow.

## Contract

- Ask exactly one focused question per turn. Do not bundle a questionnaire into
  one message.
- Always put the question directly in the visible assistant message. Never call
  `request_user_input` or place the question inside a tool call, status block,
  or collapsible UI card.
- When choices help, show 2-3 concrete, mutually exclusive options as a
  numbered list, put the recommended option first, and allow a free-form answer.
- End the message with one clear instruction such as `Choose 1, 2, or give your
  own answer`, then wait for the user's reply.
- Inspect the repository, files, existing configuration, and available evidence
  yourself when they can answer a question. Do not ask the user for facts that
  can be discovered safely.
- Acknowledge the previous answer in at most two short sentences, record the
  decision mentally, and immediately ask the next highest-value question.
- Do not edit files, implement code, create issues, or commit changes while the
  interview is running unless the user explicitly asks for that action.
- Respect repository instructions, existing specifications, and user decisions;
  grilling challenges ambiguity, not settled constraints.
- If the user says to proceed, stop asking questions. State unresolved
  assumptions and risks explicitly, then hand off to the requested workflow.

## Workflow

1. Restate the requested outcome in one sentence and identify the first
   unresolved decision with the largest downstream impact.
2. Build a small decision map while interviewing. Cover only the branches that
   affect the result:
   - goal, users, and non-goals;
   - inputs, outputs, interfaces, and ownership;
   - constraints, compatibility, scale, and performance targets;
   - state, lifecycle, failure, recovery, and concurrency behavior;
   - security, observability, rollout, and migration boundaries;
   - acceptance criteria and the smallest useful verification.
3. Ask the next question based on prior answers. Prefer concrete scenarios,
   trade-offs, and edge cases over abstract requests for more detail.
4. Do not revisit a resolved branch unless a later answer creates a direct
   contradiction. Surface contradictions plainly and ask which decision wins.
5. Finish when every material branch has an explicit decision or a named
   assumption with an owner and a follow-up trigger.

## Question quality

- Ask questions that change the design. Skip cosmetic preferences until the
  core behavior is settled.
- Offer realistic alternatives, not artificial yes/no choices. Include an
  "other" path when the space is genuinely open.
- Use examples from the user's actual code or domain when available.
- For a bug or operational issue, first establish the expected behavior,
  affected scope, reproduction, and evidence before discussing a fix.
- For a design, explicitly test the negative path: what is out of scope, what
  happens on invalid input, what happens during restart or partial failure, and
  what is the rollback boundary.

## Completion summary

When the interview is complete, output a concise handoff with:

1. Confirmed goal and non-goals.
2. Decisions made, including important rejected alternatives.
3. Constraints, invariants, interfaces, and lifecycle assumptions.
4. Acceptance criteria and verification plan.
5. Open risks or assumptions, each with a trigger or owner.
6. The next action, such as `design-analysis`, `code-plan`, `design-to-spec`,
   or implementation.

Do not claim that the design is complete merely because the user answered many
questions. It is complete only when the remaining ambiguity cannot change the
implementation or its acceptance criteria.
