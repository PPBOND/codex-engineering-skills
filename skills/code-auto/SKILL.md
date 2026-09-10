---
name: code-auto
description: Execute an authorized coding plan or spec through implementation, focused validation, and no-MAJOR+ review gates. Preserve project rules for delegation, commits, and publication; run those steps only when authorized.
---

# Code Auto

## Karpathy 共享守则

对非平凡的实现 stage，先读取并应用
[`references/karpathy-coding-guardrails.md`](references/karpathy-coding-guardrails.md)。
它补充本 skill 的复用/简化门禁：显式区分事实与有影响的假设、只做可追溯的最小改动，并以可执行验证闭环；不得削弱既有 C++17、可靠性或安全约束。

## C++17 Agent Standards（实现门禁）

当 plan/spec 或待改文件涉及 C++、CMake、编译参数或 C/C++ ABI 时，必须先读取 `references/cpp17-agent-standards.md` 指向的规范正文，并在每个 phase/stage 的 preflight 和验收记录中应用它。

- 核对本次改动及实际 target 的 C++17 配置。新增不兼容语法、库 API 或编译选项按 `CRITICAL [Q]` 修复，修复只能使用 C++17；不得把“发现可修复问题”当作结束任务。范围外旧问题记录证据，只有确实阻塞当前验收时才暂停依赖步骤。
- 采用 RAII、Rule of Zero/Five，并根据项目的所有权模型选择裸指针、智能指针、引用或句柄；指针类型本身不构成违规。涉及资源所有权、`new`/`delete`、`malloc`/`free`、异步边界或跨线程保存时，必须在代码/设计中说明所有权、销毁/回收、异常安全和线程约束。
- 性能改动必须先建立可复现 baseline，再用 profiler/benchmark 定位热点；不得提交“看起来更快”的伪优化。优化后必须跑 correctness、相关回归/并发测试，并在同一 workload、硬件和编译配置下对比结果、方差、峰值内存和回归场景。
- 将 Per.1–Per.19（上游定义的 Per.1–Per.7、Per.10–Per.19）作为性能变更清单，检查 cache locality、AoS/SoA、布局/padding、false sharing、间接层和关键路径分配；Per.8/Per.9 不自行虚构规则。
- `std::string_view` 只能用于生命周期明确的非拥有观察；强类型、const-correctness、锁/原子内存序、数据竞争和错误传播必须在 coder 自检、review 和测试记录中闭环。

根据 plan/spec 完成用户授权的编码与验证。提交、push、创建 issue/MR 和发布评论分别遵循用户及项目的明确授权；Skill 自动选中不构成授权，也不要求用户主动打断才能避免发布。后文所有提交和 MR 步骤都受此边界约束，已有同范围批准时直接执行。

## 完成标准

- 输入文件已识别为 `plan` 或 `spec`，待完成项清单明确。
- 每个阶段都有实现、审查、构建/测试结果；失败项已修复或明确需要用户决定。
- 每个阶段已完成复用与简化检查：优先删除或复用已有代码/标准库，共享可变状态和副作用已收敛，新抽象、继承与测试均有当前需求支撑。
- Spec 模式下，每个 stage 必须通过 `$code-review` spec-conformance review，且无未解决 MAJOR+ 后才能进入下一 stage。
- 代码格式已处理（clang-tidy 在 build 内执行，不再单独 lint）。
- 提交已获授权时，每组相关改动用 `$code-commit` 单独提交；否则交付已验证 diff，spec 状态注明未提交，不为获得提交许可阻塞实施交付。
- 进度文件与输入文件状态一致；全部完成后仅清理本任务拥有的临时进度文件，用户要求保留或仍需恢复时保留。
- 提交 MR 前已通过完整 `$code-review`（覆盖整段分支 diff），且无未解决 MAJOR+。
- issue 关联默认关闭；只有用户明确提供 issue 时才关联。MR 已获授权且门禁通过后调用 `$mr-submit`；未要求发布时交付本地结果，缺少 issue/MR 不影响实施完成。

## 全局规则

- 先检查 `git status --short`，保护用户已有改动；不要回退不属于本次任务的变更。
- 优先使用 `rg` / `rg --files` 搜索文件和文本。
- 编码前读取并应用 [`references/reuse-and-simplicity-principles.md`](references/reuse-and-simplicity-principles.md)。这些原则适用于所有语言，是实现和 review 的决策门禁，不是机械指标；不得为了单一职责或复用而制造过碎函数、单实现接口、无现实调用方的通用层或假想扩展点。
- 优先使用项目适用的现有本地工具链；本地不适用且远端验证已在授权范围内时使用 `$remote-vm`。遵守“仅静态分析”等限制，不为文档改动强制远端构建。
- 使用 `$code-commit` 创建提交；不要同时混用手写 `git commit` 规则。
- 只有用户/项目的多 Agent 开关允许且子任务独立时，才使用 sub-agent；给 worker 明确文件归属。同一工作树只有一个 writer，角色名或 `[PARALLEL]` 标注不能绕过该约束。
- 子任务存在共享文件、顺序依赖或风险不清时，由当前 agent 串行完成。
- 同一失败连续 3 轮无进展时停止重复同一策略，汇总证据并检查已授权的替代诊断。存在可行下一步则继续；确需外部决定/权限或存在不安全操作时才暂停依赖步骤，不降低质量门禁。

## 角色语义

角色是职责边界，不绑定具体工具名：

| 角色 | 职责 |
|------|------|
| leader | 当前 agent，负责拆分阶段、分配任务、处理阻塞、记录进度和决定下一步 |
| coder | 修改代码、补测试、按授权提交边界整理变更。注释优先解释 WHY，并保留项目要求的职责、参数、单位、错误及生命周期契约；避免逐句翻译和依赖会话历史的注释。修改行为时同步更新注释。 |
| reviewer | 独立审查改动，重点检查正确性、边界条件、错误处理、并发安全、可维护性和冗余注释。**冗余注释按 ❌ 阻塞**（不放行作为 ⚠️ 累积到下一 commit），判定标准：未来 reader 没有 PR / review / commit 上下文时该注释是否仍有效，无效就要求删 |
| builder | 使用适用且获授权的本地或隔离远端工具链执行 build/test/format，报告实际结果；只有确认 build 已执行 clang-tidy 才记为通过 |

- 多 Agent 已开启时 coder/reviewer 分开；单 Agent 模式由当前 agent 先实现再自审，不因缺少独立 reviewer 而停工。
- builder 是验证职责，不是独立 Agent 或远端环境的强制要求；构建、测试、format、clang-tidy 分别以实际命令结果为准。
- reviewer 发现阻塞问题时，先修复并复审，再交给 builder 验证。

## 进度文件

使用本任务的 `<progress-file>` 断点恢复，默认是仓库根目录 `.code-auto-progress.json`。

```json
{
  "input": "docs/spec/example_spec.md",
  "mode": "spec",
  "completed_phases": [],
  "completed_stages": ["stage-1"],
  "current_stage": "stage-2",
  "validated_commands": [],
  "review_iterations": [
    {"stage": "stage-1", "review_head": "<commit>", "major_plus": 0, "notes": []}
  ],
  "last_updated": "2026-04-30T12:00:00+08:00"
}
```

- `mode=plan` 时只使用 `completed_phases`。
- `mode=spec` 时使用 `completed_stages`、`current_stage`、`validated_commands` 和 `review_iterations`。
- 默认文件属于其他输入/任务时保留它，使用未占用的 `.code-auto-progress.<task>.json`，将其作为本任务 `<progress-file>`；无需询问是否覆盖无关进度。

## Step 0: Preflight

1. 读取用户给出的输入文件；若未给出且只有一个明显候选，可使用该候选，否则询问用户。
2. 判断模式：文件名匹配 `*_spec.md` 或路径包含 `docs/spec/` 时为 `spec`，否则为 `plan`。
3. 读取 `<progress-file>`，只跳过与当前输入文件和模式匹配且有对应验证证据的已完成项。
4. 检查架构约束：在 4 层内搜索 `arch-constraints*`、`arch_constraints*`、`architecture-constraints*`、`architecture_constraints*`、`ARCHITECTURE*.md`；若发现 plan/spec 与约束冲突，先让用户选择调整方案或继续豁免。
5. 读取 `.clang-format` 和 `.clang-tidy`；若 plan/spec 里的示例代码不符合项目规则，记录提醒，实际实现以项目配置为准。
6. 根据输入拆出待执行阶段，并为每个阶段确定变更文件、提交边界和验证命令。
7. 对每个阶段做最小实现扫描：查找现有实现/调用方和标准库替代，识别共享可变状态、副作用与对象生命周期，确认新增模块、接口、继承、依赖和测试都有当前需求支撑；无须为该检查另建文档，只在阶段记录中保留结论。
8. **Issue 关联（可选）**：默认将 `<ISSUE_ID>` 设为空，不询问用户、不从分支名或 commit 信息推断 issue，也不因无 issue 阻塞编码或 MR。只有用户明确提供 Jira key（如 `XSTOR-1234`）或 GitLab issue 号（如 `#42`）时，才将其传给 coder，并按 `$mr-submit` 约定在 commit/MR 中保留引用；未提供时使用 `$code-commit` 默认标题格式，MR 不添加 issue 链接。

## PLAN MODE

### P1. 读取 Plan

- 若 plan 含 `## Subtasks` 且用户要求执行整份计划，读取链接的子计划并按依赖继续实施；单 Agent 模式顺序执行。仅用户要求列计划/审阅时止于报告，缺失的必要子计划只阻塞依赖它的工作。
- 否则提取所有 Phase，以及每个 Phase 的 `[PARALLEL]` / `[SEQUENTIAL]` 标注。
- 跳过 `completed_phases` 中已完成的 Phase。

### P2. 执行 Phase

对每个待执行 Phase：

1. 明确目标、文件范围、提交边界和验证命令。
2. `[PARALLEL]` 仅表示依赖关系；多 Agent 开关已开启且文件所有权隔离时才按项目并发上限委派，否则当前 agent 顺序处理。
3. 完成代码后做审查：多 Agent 已授权且可用时使用独立 reviewer，否则由当前 agent 按正确性、边界条件、并发安全、错误处理、可维护性及复用/简化原则逐项检查。
4. 审查有阻塞问题时修复后复审；非阻塞建议记录在总结中。
5. 使用适用工具链执行该 Phase 的 format/build/test；需要隔离远端时按 `$remote-vm` 同步并核验相关文件，失败则修复后重新执行受影响的检查。
6. 提交已授权时用 `$code-commit` 提交已验证的相关改动，按原子行为划分边界；未授权时保留 diff，不以提交作为验证前置条件。
7. 通过后把 Phase 写入 `completed_phases`，更新时间戳。

### P3. 全量验证

所有 Phase 完成后执行一次完整验证：

- plan 指定了测试命令时，按 plan 执行。
- plan 未指定时，执行项目默认 build 和默认测试。
- Crash、断言失败、测试失败都不能忽略。

### P4. Format

核对实际 build 是否包含 clang-tidy；未执行时不得宣称 lint 已通过。按项目要求补充适用检查。

1. 使用项目工具格式化本次改动文件；仅在用户要求或项目工具必需时做全量 format，保护无关改动。
2. 若 format 产生改动，用 `$code-commit` 单独提交。
3. format 后再次确认 `git status --short`，避免遗漏未提交改动。

### P5. 收尾

- 输出变更文件、提交列表、验证结果和未处理建议。
- MR 已获授权时执行《提交 MR 前的最终复审》，通过后调用 `$mr-submit`，无需重复确认；否则交付已验证结果。仅在用户明确提供 `<ISSUE_ID>` 时关联 issue。

## SPEC MODE

### S1. 读取 Spec

- 从 `📦 实施状态表` 提取所有 stage 及状态：`⬜` 未开始、`🔄` 进行中、`✅` 已完成。
- 读取 §Q 质量门禁矩阵和 Requirement-Code-Test triples；把每个 stage 关联到对应 RCT 行、验证命令和预期文件清单。
- 结合 `completed_stages` 跳过已完成 stage。
- 若所有 stage 已完成，核对验证证据后进入 S3 收尾；发布按已确认授权执行，不能从状态表完成标记推断发布许可。

### S2. 执行 Stage

对每个待执行 stage 严格执行质量门禁：

1. **Stage preflight**：提取该 stage 的 RCT 行、文件清单、commit 边界、并行/串行标注、验收命令和 out-of-scope 说明；确认 tracked worktree 状态，列出与本 stage 无关的未跟踪文件并忽略。
2. **限制范围**：只修改 stage 文件清单内的文件；确需新增文件时，先记录原因并更新 stage 文件清单。
3. **实现与自审**：按 commit 列表执行，流程同 PLAN MODE P2，并应用复用/简化原则；审查阻塞项修复后再继续。
4. **格式、构建、聚焦测试**：先按项目命令 format，再 build，再执行 RCT 中列出的 focused tests；没有明确命令时执行默认 build 和默认测试。
5. **提交 stage 代码**：通过验证后，用 `$code-commit` 提交该 stage 的代码和测试；不要把 spec 瘦身、状态表或文档范围清扫混入代码提交。
6. **Spec-conformance review**：对 stage diff 或当前分支运行 `$code-review`，要求按 spec 检查 RCT、lifecycle、touchpoint、boundary/error、runtime invariant 和 doc drift。
7. **MAJOR+ 处理**：若 review 存在 CRITICAL/MAJOR，修复代码或测试，重新 format/build/focused tests，提交修复，再次运行 `$code-review`；直到 MAJOR+ 为 0。
8. **记录闭环**：把 validation commands 和 review 结果写入 `<progress-file>` 的 `review_iterations[]`，并维护 review closure table。
9. **Spec 瘦身**：使用 `$design-to-spec` 的 spec 瘦身规则做该 stage 的瘦身，只删除已实施细节，保留接口、验收标准、剩余 stage 和必要背景；瘦身改动单独用 `$code-commit` 提交。
10. **状态更新**：已验证 stage 标为 `✅` 并记录验证证据；提交已授权时关联实际 commit hash，否则明确“已验证、未提交”，不编造 hash。
11. **推进条件**：只有 build/test 通过、review MAJOR+ 为 0、进度文件已记录时，才把该 stage 写入 `completed_stages` 并进入下一 stage。

### S3. 全部完成

- 清理本任务拥有且已不再需要的 `<progress-file>`。
- 输出 stage 状态、提交列表、验证结果、review iterations、closure table 和剩余风险。
- MR 已获授权时执行《提交 MR 前的最终复审》，通过后调用 `$mr-submit`，无需重复确认；否则交付已验证结果。仅在用户明确提供 `<ISSUE_ID>` 时关联 issue。

## 提交 MR 前的最终复审

只有提交 MR 已在用户授权范围内时，PLAN MODE P5 / SPEC MODE S3 才进入本节。提交 MR 前仍必须审查整段分支 diff；只有新增修改、失败或未解决风险才重复已完成的全量复审。

1. 计算分叉点：`git merge-base HEAD origin/master`（或 `origin/main`，取目标分支），记为 `<BASE>`；用 merge-base 而非目标分支当前 tip，避免把无关上游变更纳入 review 范围。
2. 调用 `$code-review` 的本地模式审查 `. <BASE>..HEAD`，并应用 [`references/reuse-and-simplicity-principles.md`](references/reuse-and-simplicity-principles.md)。多 Agent 已授权时使用独立 reviewer；否则由主 Agent 按完整 checklist 复审，不为使用 sub-agent 请求额外批准。
3. 根据结果处理：
   - 无 CRITICAL / MAJOR：把 MINOR / SUGGESTION 写入收尾摘要后，使用 `$mr-submit` 提交 MR。
   - 有 CRITICAL / MAJOR：coder 修复后用 `$code-commit` 单独提交；若修复触及编译/测试相关文件，由 builder 通过 `$remote-vm` 重新 build/test 通过后，**回到第 2 步对整段 diff 重跑完整 review**，不允许只 review 增量 fix。
4. 同一类 MAJOR+ 问题连续 3 轮无进展时停止重复同一修复策略，按全局规则检查替代诊断并报告真实阻塞；不因次数耗尽而降级 finding 或带未解决阻塞项发布。

SPEC MODE 下，本节的复审与 S2 step 6 的 stage spec-conformance review 是不同环节：前者是全量出口门禁（按整段分支 diff），后者是 stage 内部门禁（按 stage diff），不能互相替代。

## 阻塞处理

需要用户决定时，只给可执行选项：

- 调整实现方案后继续。
- 接受明确风险继续。
- 暂停并保留当前分支状态。

不要把未验证完成的变更当作完成交付。
