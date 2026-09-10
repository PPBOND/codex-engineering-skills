---
name: deployment-log-analyze
description: Analyze logs from a multi-instance service deployment, correlating failures, lifecycle transitions, retries, and resource pressure across hosts.
---

# Deployment Log Analysis

## Inputs

- deployment or log root;
- one or more hosts or instances;
- time window;
- symptom, request ID, object ID, or component;
- expected behavior.

Obtain hosts and paths from deployment metadata or the user. Do not embed endpoints.

## Workflow

1. Inventory instances, versions, roles, and restart times.
2. Normalize timestamps and time zones.
3. Search for the symptom and extract a narrow time window.
4. Build a cross-instance timeline.
5. Trace request or object identifiers through lifecycle transitions.
6. Identify the earliest abnormal event, not merely the final error.
7. Correlate with process restarts, OOM, disk, network, and kernel events.
8. Distinguish primary failure from retries and cleanup noise.

Useful generic searches:

```bash
find <log-root> -type f -print
grep -RniE 'fatal|panic|assert|timeout|retry|corrupt|out of memory' <log-root>
grep -Rni '<request-or-object-id>' <log-root>
```

## Output

Return a concise timeline, evidence with file and timestamp, root cause and
confidence, affected scope, mitigation, permanent fix, and missing evidence.
