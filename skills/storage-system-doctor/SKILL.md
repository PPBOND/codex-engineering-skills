---
name: storage-system-doctor
description: Diagnose distributed storage deployments from one or more hosts. Use for service health, capacity, latency, crash, disk, network, process, and log investigations.
---

# Distributed Storage System Doctor

Diagnose a storage deployment without assuming a specific product, repository layout,
service name, or host address.

## Inputs

Collect or infer:

- one or more hosts;
- SSH user and access method;
- deployment root and log root;
- component names or process patterns;
- incident time range;
- expected and observed behavior.

Never invent missing endpoints or credentials. Prefer existing project documentation,
environment variables, and deployment manifests.

## Workflow

1. Establish the time window and affected hosts.
2. Read deployment manifests and service definitions before choosing commands.
3. Collect lightweight global health data:
   - uptime and load;
   - memory and swap pressure;
   - disk capacity, inode usage, and mount state;
   - failed services and recent restarts;
   - kernel I/O, filesystem, OOM, and network errors.
4. Identify storage components from manifests or running processes.
5. Inspect component logs within the incident window.
6. Correlate events across hosts by timestamp and request, shard, volume, or trace ID.
7. Separate confirmed facts, likely causes, and unresolved questions.
8. Recommend the smallest safe next action and a verification command.

For multiple hosts, parallelize only when each host can be inspected independently.
Never run mutating recovery commands unless the user explicitly requests them.

## Command Template

Use `scripts/diagnose.sh` as a starting point:

```bash
SSH_TARGET='<user>@<host>' \
LOG_ROOT='<remote-log-root>' \
PROCESS_PATTERN='<service-pattern>' \
bash scripts/diagnose.sh
```

All values are required inputs or explicitly documented defaults. Do not embed host
addresses in the skill.

## Report

Return:

1. scope and time window;
2. affected hosts/components;
3. evidence with timestamps and source files;
4. root-cause assessment and confidence;
5. immediate mitigation, long-term fix, and validation steps.
