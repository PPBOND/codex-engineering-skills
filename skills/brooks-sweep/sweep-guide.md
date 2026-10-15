# Brooks-Lint — Full Sweep Guide

Sequential pipeline: **review → test → debt → audit**. Apply authorized fixes,
verify affected behavior, and report residuals. All severity levels share a bounded
re-scan budget. A request to fix selected findings uses only the relevant dimensions.

Every finding follows the Iron Law: **Symptom → Source → Consequence → Remedy**.

---

### Step 0 — Scope, authorization, and baseline

0a. Read applicable project instructions and inspect `git status --short` and the
   relevant diff before editing. Enumerate tracked and relevant untracked source
   files with the available file tools; exclude generated and vendor output.

0b. Briefly state the scope and verification approach. An explicit sweep-and-fix
   or repair request, including earlier authorization in this task, is enough to
   proceed within that scope. A report-only request remains read-only. If the
   intended deliverable is unclear, finish safe diagnosis and ask only for the
   decision needed before edits. Do not ask again at every dimension or phase.

0c. Preserve dirty work in place. Capture task-owned pre-edit hunks when needed
   for rollback; do not require a commit or stash. Do not restore entire files,
   use destructive Git resets, or clean unrelated artifacts. Commits, branches,
   publication, and remote/system changes follow the user's and project's authority.

0d. Identify the relevant existing validation commands and baseline evidence. Run
   a focused baseline when needed to distinguish existing failures. If a new issue
   changes public contracts, data safety, or scope beyond the approved task, prepare
   the concrete finding and options before asking; continue independent safe work.

---

### Step 1 — Scope enumeration and state init

1a. Apply Auto Scope Detection from `../_brooks-lint/common.md` if the user did not
   specify files or a directory. Otherwise honor the user's explicit scope.

1b. Read `.brooks-lint.yaml` from the project root if present. Apply `disable`,
   `severity`, `ignore`, `focus`, and `custom_risks` per common.md. Record the
   applied config values and reuse them across all iteration rounds — do not
   re-read the file in Step 6 even if files were modified.

1c. Initialize pipeline state (persists across all rounds):

   - **`unresolvable`** (set): findings retired after at most 3 distinct failed attempts; key by `(file, symbol, risk_code, signature)` so shifted line numbers do not reset the budget.
   - **`rescan_rounds`** (int, 0): counts all re-scan rounds after the initial pass, regardless of severity.
   - **`fix_log`** (list): each fix with file, line range, risk code, description, and outcome (`applied` / `reverted` / `retired`).

1d. Record the final scope file list in the Fix Report output buffer for Step 8.

---

### Step 2 — brooks-review pass (R1–R6 code decay)

Scan every file in scope against all R-series risks defined in
`../_brooks-lint/decay-risks.md`.

2a. For each R-risk, apply its symptom checklist. Record each hit as a finding
   with: risk code, file + approximate line range, Symptom, Source,
   Consequence, Remedy, Severity (Critical / Warning / Suggestion), and
   **Fix-Class** (see Step 2b).

2b. Assign Fix-Class per finding:

   | Class | Criteria |
   |-------|----------|
   | **Safe** | Fully local change with proven purpose and suitable validation, such as removing confirmed dead code or clarifying a private name. File count alone does not establish safety; preserve behavior, ownership, and error contracts. |
   | **Extended-Safe** | Bounded multi-file change within authorization, with known callers, suitable baseline evidence, and focused validation of affected behavior. |
   | **Residual** | A required design decision, unsupported assumption, missing essential validation, or public/persistent/lifecycle change beyond authorization. Report the concrete reason; severity does not grant authority. |

2c. Skip any finding that matches an entry in the `unresolvable` set.

2d. Apply every Safe and Extended-Safe fix in this dimension, lowest risk
   within each severity tier first. For each fix: apply a focused patch, then append
   one row to `fix_log` with outcome `applied`. If two fixes touch overlapping
   line ranges in the same file, apply higher-severity first, re-read the file,
   then apply the next.

2e. Run focused validation appropriate to the change (for C++ use real CMake/CTest
   targets and the repository's configured toolchain). On failure, diagnose the
   first actionable cause against the baseline. Fix a task-caused regression or
   undo only task-owned hunks while preserving user and concurrent edits. Mark an
   undone fix `reverted` and report its residual. Do not run repeated full suites
   after already-passing checks without a new change or unresolved concern.
   If required validation cannot run, report the limitation rather than claiming
   the change is verified. Documentation-only changes need suitable static checks.

2f. Record dimension summary: N scanned, M Safe applied, K Extended-Safe applied,
   R reverted, P Residual.

---

### Step 3 — brooks-test pass (T1–T6 test decay)

Scan test files (and untested production code) against T-series risks defined
in `../_brooks-lint/test-decay-risks.md`.

Follow the same sub-steps as Step 2 (classify → apply → verify → summarize),
using T-prefix risk codes. Confirm behavior lacks coverage before reporting T5;
missing adjacent test files is not sufficient evidence. Add meaningful tests for
the demonstrated risk rather than empty scaffolds or assertions mirroring the
implementation. New test infrastructure needs an actual task requirement.

---

### Step 4 — brooks-debt pass (tech debt accumulation)

Re-classify R-findings through a debt lens — same symptoms at accumulation scale:
repeated duplication, layered workarounds, stale `TODO`/`FIXME` clusters, dead
flags. Score each with **Pain (1–3) × Spread (1–3)**; total 7–9 = Critical,
4–6 = Warning, 1–3 = Suggestion. Apply a severity bump for pattern-level
occurrences (isolated Suggestion → 4+ modules Warning).

Follow the same sub-steps as Step 2. Debt findings often span multiple files
and are more likely to land in Extended-Safe or Residual than Safe.

---

### Step 5 — brooks-audit pass (architecture integrity)

Scan the full scope for architecture-level issues. The dependency-direction
symptoms (inverted dependencies, circular imports, cross-domain coupling) are
defined in `../_brooks-lint/decay-risks.md` Risk 5 — use that checklist. Step 5
additionally covers architecture-only concerns that R5 does not: missing
abstraction layers, god modules, leaked infrastructure inside domain code,
and seam-boundary violations.

Most architecture findings are **Residual** by definition — they require human
judgment on module boundaries. A few are Extended-Safe (e.g. extract a shared
constant used in 3+ modules into a new module that nothing else imports yet).
Do not auto-refactor module layouts, rename packages, or change public exports.

Follow the same sub-steps as Step 2.

---

### Step 6 — Iteration loop

**Goal:** Re-scan what the fixes touched and converge. Stop on clean round,
cap, or no progress.

6a. Build the re-scan scope:
   - every file modified in Steps 2–5 of the current round, PLUS
   - every file in the same module as a modified file, PLUS
   - every file that statically imports from a modified file.

   Do not re-scan files whose dependencies were not touched. On monorepos
   where a "module" may span hundreds of files, narrow the same-module bucket
   to files that import from or are imported by a modified file (direct
   dependency graph only).

6b. Re-scan only the affected scope, incrementing `rescan_rounds` once. Reuse
   verified findings and skip `unresolvable` entries. Order actionable findings
   by severity and apply Steps 2–5 only where the new evidence warrants work.

6c. Stop when the scan is clean, no meaningful progress is possible, required
   authority or evidence is missing, or `rescan_rounds` reaches
   `sweep.max_iterations` (default 3). The cap applies to Critical findings too.
   Report every remaining finding and the stopping reason; a capped run is not
   equivalent to a fully remediated codebase.

6d. Attempt a failed fix again only with a new causal hypothesis. Retire a finding
   after at most 3 failed attempts, or earlier for a repeated unchanged blocker.
   Do not requeue a known residual merely because its line numbers moved.

---

### Step 7 — Residual aggregation

Collect everything that was NOT fixed in place, de-duplicated:

- All Residual-class findings from Steps 2–5 (first round + re-scan rounds)
- All `unresolvable` entries with their retirement reason
- All iteration-cap residuals from Step 6c

Sort Critical → Warning → Suggestion. Within each severity, list file path,
risk code, Symptom (one line), Remedy (one line), and the reason it was not
applied (`public API break` / `no test coverage` / `3-retry budget` /
`iteration cap`).

---

### Step 8 — Sweep report

Output the final report. Use the standard Report Template from
`../_brooks-lint/common.md` with these additions:

```
# Brooks-Lint — Full Sweep Report
Mode: Full Sweep | Scope: <files or directory>
Config: .brooks-lint.yaml applied (strictness: <preset>, N risks disabled, M paths ignored)   # omit if no config

## Dimension Summary
| Dimension | Scanned | Safe Applied | Extended Applied | Reverted | Residual |
|-----------|---------|--------------|------------------|----------|----------|
| Review (R1–R6) | ... | ... | ... | ... | ... |
| Test (T1–T6)   | ... | ... | ... | ... | ... |
| Debt           | ... | ... | ... | ... | ... |
| Audit          | ... | ... | ... | ... | ... |

## Iteration History
Round 1: <classification — clean / critical-only / mixed>, <N> new findings
Round 2: ...
Stopped at: clean round | iteration cap | no progress | required input or validation

## Fix Log
| # | File | Lines | Risk | Outcome  | Change |
|---|------|-------|------|----------|--------|
| 1 | ...  | ...   | R2   | applied  | Extract repeated constant |
| 2 | ...  | ...   | T4   | reverted | Test regression; promoted to Residual |
...

## Health Score Delta
Before: <estimated score>/100  →  After: <estimated score>/100
(Use $brooks-health for a fresh heuristic assessment of the inspected scope.)

## Residual Items  (<K> not applied)
<Iron Law entries, sorted Critical → Suggestion, with "Not applied because: ..." line>

## Summary
- Total findings detected: <N>
- Fixed this sweep: <M>
- Residual (needs human review): <K>
- Unresolvable (3-retry exhausted): <U>
```

If there are zero residual items and zero unresolvable entries, state that no
actionable findings remain in the inspected scope and list validation limits.
Do not claim the entire codebase is defect-free.

**Mode line in report:** `Full Sweep`
