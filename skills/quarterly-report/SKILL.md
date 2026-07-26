---
name: quarterly-report
description: Generate a personal quarterly work summary from calendars, documents, messages, issue trackers, and source-control activity.
---

# Quarterly Report

## Inputs

- reporting period and timezone;
- identity used across connected systems;
- available calendar, document, chat, issue-tracker, and source-control sources;
- preferred report template or audience.

Use only sources the user has authorized. Never infer activity from another person
with a similar name.

## Workflow

1. Resolve the exact date range.
2. Collect activity by source with pagination:
   - meetings and recurring events;
   - authored or substantially edited documents;
   - important project discussions;
   - issues created, resolved, or owned;
   - commits, reviews, and merge requests.
3. Deduplicate the same work item appearing in multiple systems.
4. Group evidence into outcomes rather than activity counts.
5. For each outcome, record contribution, impact, evidence, and collaboration.
6. Separate completed work, ongoing work, operational support, and learning.
7. Call out gaps when a source is unavailable.

## Quality Rules

- Do not claim impact that is not supported by evidence.
- Prefer shipped behavior, resolved risk, performance change, or reduced effort over
  raw meeting/commit counts.
- Avoid copying private messages verbatim unless the user requests quotations.
- Preserve links for traceability but redact secrets and personal data.

## Output

Produce:

1. executive summary;
2. major outcomes with evidence;
3. reliability/quality/operational contributions;
4. collaboration and influence;
5. growth and lessons;
6. next-quarter priorities;
7. source coverage and known gaps.

