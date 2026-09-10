---
name: cmake-ut-compile
description: Configure, compile, and run one or more CMake targets or unit tests, including projects that use Conan and a repository build wrapper.
---

# CMake Target Compile and Run

## Discover Before Running

Inspect repository instructions, `CMakeLists.txt`, presets, Conan files, build
wrappers, and existing build directories. Use the project's documented entrypoint.
Resolve build type, generator, container, targets, and parallelism from existing
configuration and task requirements. Ask only when a missing choice affects the
result; do not request values that can be read from presets or CMakeCache.

## Workflow

1. Parse the requested target or test names.
2. Locate their CMake declarations and test registrations.
3. Determine whether a compatible configured build directory exists.
4. If configuration is required, use the repository's wrapper or presets.
5. Build only requested targets first.
6. Run tests through `ctest` when registered; otherwise run the executable using the
   documented environment and working directory.
7. On failure, diagnose the first compile/link/runtime cause. For an implementation task, fix in-scope issues and rerun the affected checks; for a diagnosis-only task, deliver the cause and evidence. After required checks pass, repeat or broaden testing only for new changes, failures, unresolved risks, or explicit project requirements.

Generic command shapes:

```bash
cmake --preset <configure-preset>
cmake --build --preset <build-preset> --target <target> --parallel <jobs>
ctest --preset <test-preset> -R '<test-regex>' --output-on-failure
```

or:

```bash
cmake -S . -B <build-dir> -DCMAKE_BUILD_TYPE=<type>
cmake --build <build-dir> --target <target> --parallel <jobs>
ctest --test-dir <build-dir> -R '<test-regex>' --output-on-failure
```

Use Conan only when the repository declares it. Never invent a package profile.

## Output

Report configuration used, targets built, tests run, elapsed result, artifact path,
and any unresolved failure.
