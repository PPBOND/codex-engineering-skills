---
name: test-handover
description: Generate a test-handover document from requirements, design, implementation scope, test evidence, risks, and deployment information.
---

# Test Handover Document

## Inputs

Use all available sources:

- requirement or product document;
- design, architecture, or implementation specification;
- merge request or commit range;
- unit and integration test results;
- deployment/configuration changes;
- known limitations and risk decisions.

Treat links, hosts, and artifact paths as user-provided values. Never embed internal
domains, addresses, passwords, or fixed log roots.

## Workflow

1. Establish the exact release scope from commits and linked documents.
2. Summarize user-visible behavior and affected components.
3. Enumerate interfaces, configuration, data-format, and compatibility changes.
4. Convert requirements and design branches into testable scenarios.
5. Record completed tests with command, environment, result, and artifact.
6. Identify untested paths, known limitations, rollback conditions, and monitoring.
7. Distinguish current scope, follow-up work, and out-of-scope items.
8. Cross-check every claim against code or evidence.

## Required Sections

1. background and objective;
2. release scope and code range;
3. architecture and interface changes;
4. configuration and deployment;
5. test matrix;
6. completed validation and evidence;
7. risk, compatibility, recovery, and rollback;
8. observability and troubleshooting;
9. known issues and exclusions;
10. acceptance checklist.

## Test Matrix

For each scenario include:

- identifier and requirement;
- preconditions;
- steps or workload;
- expected result;
- coverage level: unit, integration, system, manual;
- execution status and evidence;
- owner or follow-up.

## Quality Gate

Do not mark a test as passed without evidence. Do not present planned or follow-up
work as current acceptance scope. Redact credentials and personal information from
logs before linking them.

