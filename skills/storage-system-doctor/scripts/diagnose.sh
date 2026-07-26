#!/usr/bin/env bash
set -euo pipefail

: "${SSH_TARGET:?Set SSH_TARGET to <user>@<host>}"
: "${LOG_ROOT:?Set LOG_ROOT to the remote log directory}"
: "${PROCESS_PATTERN:?Set PROCESS_PATTERN to a service or process pattern}"

ssh "${SSH_TARGET}" bash -s -- "${LOG_ROOT}" "${PROCESS_PATTERN}" <<'REMOTE'
set -euo pipefail
log_root="$1"
process_pattern="$2"

echo "== host =="
hostname
date --iso-8601=seconds
uptime

echo "== memory =="
free -h

echo "== storage =="
df -h
df -i

echo "== processes =="
pgrep -af -- "${process_pattern}" || true

echo "== recent system errors =="
journalctl --since "1 hour ago" -p warning..alert --no-pager 2>/dev/null | tail -n 200 || true

echo "== recent component log lines =="
find "${log_root}" -type f -mmin -60 -print0 2>/dev/null \
  | xargs -0r tail -n 80 2>/dev/null \
  | tail -n 400 || true
REMOTE
