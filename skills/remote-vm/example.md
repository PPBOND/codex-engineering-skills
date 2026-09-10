# Example

Build one CMake target and run its registered test on a configured remote VM.

Required inputs:

- `<vm>`: SSH target;
- `<repository>`: remote checkout;
- `<worktree>`: isolated working directory when needed;
- `<target>`: CMake target;
- `<test-regex>`: registered test selector;
- `<build-dir>`: configured build directory.

Example command shapes:

```bash
ssh <vm> 'cmake --build <build-dir> --target <target> --parallel <jobs>'
ssh <vm> 'ctest --test-dir <build-dir> -R <test-regex> --output-on-failure'
```
