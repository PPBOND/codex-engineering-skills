---
name: perf-analyse
description: Fetch and analyze end-to-end performance metrics from Prometheus-compatible APIs, including latency, throughput, errors, saturation, and cross-layer bottlenecks.
---

# End-to-End Performance Analysis

Analyze one run or compare multiple runs without assuming metric names or endpoints.

## Inputs

- Prometheus-compatible base URL;
- start/end time and step;
- workload description;
- labels that identify a run, host, service, operation, or device;
- metric mapping for latency, throughput, errors, and resources.

Read dashboards, recording rules, and application instrumentation to discover metric
names. Never hard-code infrastructure endpoints.

## Workflow

1. Validate the time range and workload phase.
2. Identify comparable windows and exclude warm-up or teardown unless requested.
3. Fetch:
   - request rate and completion rate;
   - error, timeout, and retry rate;
   - latency percentiles or histograms;
   - queue depth and concurrency;
   - CPU, memory, network, and device utilization.
4. Align layers on the same time axis.
5. Distinguish client-observed latency from server processing and queueing.
6. Find the earliest layer whose latency or saturation changes with the symptom.
7. For comparisons, normalize by workload, concurrency, object size, and duration.
8. State whether evidence shows regression, jitter, saturation, or insufficient data.

## Fetch Helper

`scripts/fetch_perf.sh` executes arbitrary range queries:

```bash
PROMETHEUS_URL='https://<metrics-host>' \
START='<rfc3339-or-unix-time>' \
END='<rfc3339-or-unix-time>' \
STEP='15s' \
bash scripts/fetch_perf.sh \
  'rate(requests_total[1m])' \
  'histogram_quantile(0.99, sum by (le) (rate(request_latency_seconds_bucket[5m])))'
```

Queries are examples only; replace them with metrics verified in the target system.

## Output

Include:

- workload and time windows;
- headline throughput, errors, and latency;
- bottleneck hypothesis with cross-layer evidence;
- confidence and data gaps;
- recommended experiment or configuration change;
- exact queries used.
