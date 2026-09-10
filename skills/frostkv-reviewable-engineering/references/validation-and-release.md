# Validation, performance, and release

Read this file when compiling, testing, benchmarking, committing, or publishing FrostKV.

## Build and test evidence

Use the real CMake target and keep fallback and native SPDK evidence separate. The
typical fallback sequence is:

```bash
cmake -S . -B build-release \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=ON \
  -DPARTIAL_CACHED_KV_BUILD_SPDK_TESTS=OFF
cmake --build build-release --parallel
ctest --test-dir build-release --output-on-failure
```

Native SPDK tests are a separate claim and require the repository's bundled dependency
build plus `PARTIAL_CACHED_KV_BUILD_SPDK_TESTS=ON`. If the local toolchain is missing,
use an isolated remote directory/worktree; synchronization alone is not validation.
Always run `git diff --check` for source/doc changes.

Test the behavior that can regress:

- normal and boundary inputs;
- rejected admission and negative errno propagation;
- malformed/corrupt input and retry/queue-full paths;
- restart/replay and crash windows;
- callback re-entry, close, resource release, and final visibility;
- concurrent in-flight requests within the documented single-owner model.

Do not use one passing format test, parity test, or fallback target to claim all recovery,
compact, GC, or native paths are correct.

## Performance claims

Separate algorithmic complexity from application-level I/O. A statement such as “two
reads” means two logical reads in a stated cache state, not a universal physical-device
guarantee. A theory about single-thread performance is not a benchmark result.

For an A/B number record the same hardware, CPU affinity, build flags, workload/key
distribution, cache warm-up, run count, and metric (throughput, p50/p99, CPU, logical
I/O, physical I/O, or resident memory). Report cold and warm behavior separately and
include variance or bimodal results instead of selecting a favorable run.

## Commits and remote publication

Only commit or push after the user explicitly requests it. Before staging, inspect
tracked, staged, and untracked paths. Keep unrelated drafts, scans, performance files,
and generated documents out of the commit. Split commits by coherent behavior (for
example contract, implementation, tests, docs), inspect the staged diff and exact path
list, then verify the remote branch hash after a normal push. Never force-overwrite a
remote history unless the user explicitly asks for that operation.

## Closure and self-maintenance

The final report must distinguish: changed scope, configure/build target, test filter,
fallback/native/SPDK mode, actual pass count, and uncovered paths. After the main work,
scan for a new general lesson. Record it only if it changes a future decision and has a
source/test/incident to support it; delete or revise rules that no longer match the
current project. Do not add dated session logs to `references/`.
