---
name: Basic Block Placement for Hot Path Fall-Through
source: perf-book Ch.11, Section 11-3 Basic Block Placement
layers: [microarchitecture]
platforms: [arm, x86]
keywords: [basic block, layout, fall-through, branch, taken branch, not taken, likely, unlikely, __builtin_expect, cold path, hot path, I-cache, uop-cache, DSB, code placement]
---

## Problem

By default, compilers lay out basic blocks in source order. When error-handling or rarely-executed code sits between hot code sections, the hot path requires a taken branch to skip over the cold code. This causes three distinct penalties:

1. **Fetch block waste**: The CPU Frontend fetches contiguous aligned blocks (16-64 bytes depending on architecture). After a taken branch, the remaining bytes in the fetch block between the jump and the branch target are unused, reducing effective fetch throughput.

2. **Taken branch cost**: Not-taken branches are cheaper than taken branches. On Intel Skylake, the CPU can execute two untaken branches per cycle but only one taken branch every two cycles.

3. **I-cache and uop-cache fragmentation**: Cold code interleaved with hot code occupies cache lines that could hold useful hot instructions. The uop-cache (DSB) caches based on the underlying code layout, so fragmented hot code wastes DSB entries as well.

```cpp
// Hot path with cold error handling in between
if (cond)       // cond is rarely true
  coldFunc();   // error handling -- rarely executed
// hot path continues
```

With default layout, the compiler places `coldFunc()` inline. The hot fall-through path must jump over it, wasting fetch bandwidth and cache capacity.

## Detection

**Source-level indicators:**
- `if/else` blocks where one path is error handling, logging, or exception-related
- Branches guarding `throw`, `abort()`, `exit()`, `assert()`, or diagnostic output
- No profile-guided layout or C++17-compatible compiler-hint evidence for branches with obvious hot/cold asymmetry

**Profile-level indicators:**
- TMA: `Frontend_Bound` > 10%, with `ICache_Misses` or `DSB_Coverage` submetrics elevated
- Branch profile data showing a branch is taken < 5% of the time, yet the taken path is laid out as fall-through

**Disassembly clues:**
- Hot code separated by `jmp` instructions that skip over cold blocks
- Unconditional jumps (`jmp`, ARM `b`) appearing immediately after a conditional branch in the hot path, indicating the compiler placed cold code inline and needs a jump to rejoin the hot path

## Transformation

### C++20: `[[likely]]` and `[[unlikely]]` attributes (禁用)

These attributes are not available under the C++17-only policy. Do not add
them as an optimization. First verify the branch profile and compiler layout;
use the C++17-compatible `__builtin_expect` wrapper below only when the
project already permits compiler extensions and measurement justifies it.

### Pre-C++20: `__builtin_expect`

```cpp
#define LIKELY(EXPR)   __builtin_expect((bool)(EXPR), true)
#define UNLIKELY(EXPR) __builtin_expect((bool)(EXPR), false)

if (UNLIKELY(errorCondition)) {
    handleError();
}
// hot path continues
```

### What the compiler does with a C++17 hint

When the project permits `__builtin_expect`, the compiler may use the hint to
place the likely path as fall-through and separate cold code. Verify the
generated layout and branch behavior; do not assume a macro improves code.

## Expected Impact

- **Fetch throughput**: Eliminating taken branches on the hot path recovers wasted bytes in fetch blocks. On a 32-byte fetch width, a taken branch in the middle wastes up to 16 bytes per fetch cycle.
- **Branch throughput**: On Intel Skylake, converting a taken branch to not-taken doubles the branch throughput from 1 taken/2 cycles to 2 untaken/cycle.
- **I-cache utilization**: Contiguous hot code means every byte in a fetched cache line is useful, rather than being wasted on interleaved cold code.
- **Typical speedup**: 1-5% on code with many branches and error-handling paths. Larger gains possible when combined with function splitting.

## Caveats

- **Only useful when branch bias is known**: If a branch is close to 50/50, there is no clearly "unlikely" path. Annotating incorrectly can make performance worse by putting the actually-hot path out of line.
- **PGO supersedes manual hints**: Profile-Guided Optimization provides measured branch frequencies to the compiler, making manual `__builtin_expect` hints unnecessary for branches that PGO covers.
- **Compiler may already get it right**: Modern compilers use heuristics (e.g., branches guarding `throw` or `__builtin_unreachable()` are assumed unlikely). Check the disassembly before adding annotations.
- **Excessive hints harm readability**: Add a C++17 compiler-hint wrapper only for measured, performance-critical branches with clear hot/cold asymmetry.
