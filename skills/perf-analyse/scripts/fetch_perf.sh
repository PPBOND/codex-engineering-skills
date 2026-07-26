#!/usr/bin/env bash
set -euo pipefail

: "${PROMETHEUS_URL:?Set PROMETHEUS_URL}"
: "${START:?Set START}"
: "${END:?Set END}"
: "${STEP:=15s}"

if [[ "$#" -eq 0 ]]; then
  echo "usage: PROMETHEUS_URL=... START=... END=... STEP=... $0 '<promql>' [...]" >&2
  exit 2
fi

for query in "$@"; do
  echo "== query: ${query} =="
  curl --fail --silent --show-error --get \
    --data-urlencode "query=${query}" \
    --data-urlencode "start=${START}" \
    --data-urlencode "end=${END}" \
    --data-urlencode "step=${STEP}" \
    "${PROMETHEUS_URL%/}/api/v1/query_range"
  echo
done
