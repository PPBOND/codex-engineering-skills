---
name: code-auto
description: Execute coding tasks from a plan or spec file in Codex with staged implementation, validation, commits, and no-MAJOR+ review gates. Use for implementing coding plans/specs, running spec-driven stages, updating progress, validating build/test/format, coordinating sub-agents, or submitting GitLab MRs.
---

# Code Auto

根据 plan 文件或 spec 文件完成编码、验证、提交和自动 MR。目标是把任务拆成可验证的小步，每步都先确认代码正确，再进入下一步；用户若不想提交 MR，需在流程中途主动打断。

## 完成标准

- 输入文件已识别为 `plan` 或 `spec`，待完成项清单明确。
- 每个阶段都有实现、审查、构建/测试结果；失败项已修复或明确需要用户决定。
- Spec 模式下，每个 stage 必须通过 `$code-review` spec-conformance review，且无未解决 MAJOR+ 后才能进入下一 stage。
- 代码格式已处理（clang-tidy 在 build 内执行，不再单独 lint）。
- 每组相关改动已用 `$code-commit` 单独提交，spec 瘦身和状态更新不混入代码提交。
- 进度文件与输入文件状态一致；全部完成后删除临时进度文件。
- 提交 MR 前已通过完整 `$code-review`（覆盖整段分支 diff），且无未解决 MAJOR+。
- 在 Step 0 已采集 `<ISSUE_ID>`，coder commit 标题已带 issue 前缀；编码 + format + 完整 review 全部通过后自动调用 `$mr-submit`，不再询问用户。

## 全局规则

- 先检查 `git status --short`，保护用户已有改动；不要回退不属于本次任务的变更。
- 优先使用 `rg` / `rg --files` 搜索文件和文本。
- 使用 `$remote-vm` 完成远程 build、test、format（clang-tidy 已在 build 内执行）；不要在本 skill 重复维护远程 VM 连接细节。
- 使用 `$code-commit` 创建提交；不要同时混用手写 `git commit` 规则。
- 子任务能并行且文件范围互不重叠时，才使用 Codex sub-agent；给每个 worker 明确文件归属，并说明不要回退他人改动。
- 子任务存在共享文件、顺序依赖或风险不清时，由当前 agent 串行完成。
- 自动修复最多 3 轮；仍失败时停止并向用户说明可选方案。

## 角色语义

角色是职责边界，不绑定具体工具名：

| 角色 | 职责 |
|------|------|
| leader | 当前 agent，负责拆分阶段、分配任务、处理阻塞、记录进度和决定下一步 |
| coder | 修改代码、补测试、按提交边界整理变更；不负责最终验证结论。**注释规范**：只写 WHY（约束/决策/坑），不写 WHAT（well-named identifier 已说明）；禁止过程性描述（"之前是 X 现在 Y"/"按 review 反馈"/"P12 后改为"）、review-driven 锚点（`TODO(#fix-after-PXX)` / `// per xpfs-bot` / 指向 commit hash / followup PR 的引用）和删除轨迹——这些都属 commit message body 或 plan 文档，代码里的 reader 看不到 PR / review 上下文。改/删代码时同步清旧注释，不留中间态痕迹。 |
| reviewer | 独立审查改动，重点检查正确性、边界条件、错误处理、并发安全、可维护性和冗余注释。**冗余注释按 ❌ 阻塞**（不放行作为 ⚠️ 累积到下一 commit），判定标准：未来 reader 没有 PR / review / commit 上下文时该注释是否仍有效，无效就要求删 |
| builder | 专职通过 `$remote-vm` 执行 build、test、format（clang-tidy 已在 build 内），并报告可复现结果 |

- coder 和 reviewer 不应是同一个 sub-agent。
- builder 语义必须保留：build/test/format 的结论只以 `$remote-vm` 结果为准（clang-tidy 已在 build 内）。
- reviewer 发现阻塞问题时，先修复并复审，再交给 builder 验证。

## 进度文件

使用仓库根目录 `.code-auto-progress.json` 断点恢复。

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
- 输入文件或模式不匹配当前任务时，不复用旧进度；询问用户是覆盖还是保留。

## Step 0: Preflight

1. 读取用户给出的输入文件；若未给出且只有一个明显候选，可使用该候选，否则询问用户。
2. 判断模式：文件名匹配 `*_spec.md` 或路径包含 `docs/spec/` 时为 `spec`，否则为 `plan`。
3. 读取 `.code-auto-progress.json`，只跳过与当前输入文件和模式匹配的已完成项。
4. 检查架构约束：在 4 层内搜索 `arch-constraints*`、`arch_constraints*`、`architecture-constraints*`、`architecture_constraints*`、`ARCHITECTURE*.md`；若发现 plan/spec 与约束冲突，先让用户选择调整方案或继续豁免。
5. 读取 `.clang-format` 和 `.clang-tidy`；若 plan/spec 里的示例代码不符合项目规则，记录提醒，实际实现以项目配置为准。
6. 根据输入拆出待执行阶段，并为每个阶段确定变更文件、提交边界和验证命令。
7. **采集 issue 号**：本流程末尾会自动调用 `$mr-submit`（不再询问用户是否提交），因此必须在编码开始前就拿到关联 issue。提示用户提供本次任务的 Jira key（如 `XSTOR-1234`）/ GitLab issue 号（如 `#42`），或确认「无关联 issue」。把结果记为 `<ISSUE_ID>`：非空时传给 coder，coder 在每个 commit 标题加 issue 前缀（格式参考 `$mr-submit`：`[feat #42] module: msg` 或 `[feat XSTOR-1234] module: msg`）；为空时按 `$code-commit` 默认格式，最终由 `$mr-submit` 自身规则补 issue。`$mr-submit` 会从已有 commit 标题自动提取 issue 引用，前置采集就是为了让 commit 一开始就带上引用，避免最后再追问。

## PLAN MODE

### P1. 读取 Plan

- 若 plan 含 `## Subtasks` 且是主协调文件，只列出子任务执行顺序并停止，不直接编码。
- 否则提取所有 Phase，以及每个 Phase 的 `[PARALLEL]` / `[SEQUENTIAL]` 标注。
- 跳过 `completed_phases` 中已完成的 Phase。

### P2. 执行 Phase

对每个待执行 Phase：

1. 明确目标、文件范围、提交边界和验证命令。
2. `[PARALLEL]` 且文件范围不重叠时，可启动最多 3 个 worker 并行处理；否则串行处理。
3. 完成代码后做审查：优先用独立 reviewer sub-agent；不可用时由当前 agent 按正确性、边界条件、并发安全、错误处理、可维护性逐项检查。
4. 审查有阻塞问题时修复后复审；非阻塞建议记录在总结中。
5. 用 `$code-commit` 提交该 Phase 的相关代码改动；单次改动超过 500 LOC 时按模块拆成多个提交。
6. 用 `$remote-vm` 执行该 Phase 的 build/test；由 `$remote-vm` 负责远端工作区同步，失败则修复并重复审查、提交、验证。
7. 通过后把 Phase 写入 `completed_phases`，更新时间戳。

### P3. 全量验证

所有 Phase 完成后执行一次完整验证：

- plan 指定了测试命令时，按 plan 执行。
- plan 未指定时，执行项目默认 build 和默认测试。
- Crash、断言失败、测试失败都不能忽略。

### P4. Format

clang-tidy 已在 build 内执行，无需单独 lint 阶段。

1. 用 `$remote-vm` 跑全量 format，不做按文件 format。
2. 若 format 产生改动，用 `$code-commit` 单独提交。
3. format 后再次确认 `git status --short`，避免遗漏未提交改动。

### P5. 收尾

- 输出变更文件、提交列表、验证结果和未处理建议。
- **不再询问用户是否提交 MR**：自动执行《提交 MR 前的最终复审》，通过后调用 `$mr-submit`。Step 0 已采集 `<ISSUE_ID>` 并写入 commit 标题，`$mr-submit` 不会回头追问 issue。用户若不想提 MR，需在编码完成前主动打断流程。

## SPEC MODE

### S1. 读取 Spec

- 从 `📦 实施状态表` 提取所有 stage 及状态：`⬜` 未开始、`🔄` 进行中、`✅` 已完成。
- 读取 §Q 质量门禁矩阵和 Requirement-Code-Test triples；把每个 stage 关联到对应 RCT 行、验证命令和预期文件清单。
- 结合 `completed_stages` 跳过已完成 stage。
- 若所有 stage 已完成，直接进入 S3 收尾：删除 `.code-auto-progress.json`，输出状态，并自动执行《提交 MR 前的最终复审》；通过后调用 `$mr-submit`，不再询问用户。

### S2. 执行 Stage

对每个待执行 stage 严格执行质量门禁：

1. **Stage preflight**：提取该 stage 的 RCT 行、文件清单、commit 边界、并行/串行标注、验收命令和 out-of-scope 说明；确认 tracked worktree 状态，列出与本 stage 无关的未跟踪文件并忽略。
2. **限制范围**：只修改 stage 文件清单内的文件；确需新增文件时，先记录原因并更新 stage 文件清单。
3. **实现与自审**：按 commit 列表执行，流程同 PLAN MODE P2；审查阻塞项修复后再继续。
4. **格式、构建、聚焦测试**：先按项目命令 format，再 build，再执行 RCT 中列出的 focused tests；没有明确命令时执行默认 build 和默认测试。
5. **提交 stage 代码**：通过验证后，用 `$code-commit` 提交该 stage 的代码和测试；不要把 spec 瘦身、状态表或文档范围清扫混入代码提交。
6. **Spec-conformance review**：对 stage diff 或当前分支运行 `$code-review`，要求按 spec 检查 RCT、lifecycle、touchpoint、boundary/error、runtime invariant 和 doc drift。
7. **MAJOR+ 处理**：若 review 存在 CRITICAL/MAJOR，修复代码或测试，重新 format/build/focused tests，提交修复，再次运行 `$code-review`；直到 MAJOR+ 为 0。
8. **记录闭环**：把 validation commands 和 review 结果写入 `.code-auto-progress.json.review_iterations[]`，并维护 review closure table。
9. **Spec 瘦身**：使用 `$design-to-spec` 的 spec 瘦身规则做该 stage 的瘦身，只删除已实施细节，保留接口、验收标准、剩余 stage 和必要背景；瘦身改动单独用 `$code-commit` 提交。
10. **状态更新**：在 `📦 实施状态表` 中把该 stage 标为 `✅ <slim-commit-hash>`，状态更新再单独用 `$code-commit` 提交；不要把状态表更新混入瘦身提交。
11. **推进条件**：只有 build/test 通过、review MAJOR+ 为 0、进度文件已记录时，才把该 stage 写入 `completed_stages` 并进入下一 stage。

### S3. 全部完成

- 删除 `.code-auto-progress.json`。
- 输出 stage 状态、提交列表、验证结果、review iterations、closure table 和剩余风险。
- **不再询问用户是否提交 MR**：自动执行《提交 MR 前的最终复审》，通过后调用 `$mr-submit`。Step 0 已采集 `<ISSUE_ID>` 并写入 commit 标题，`$mr-submit` 不会回头追问 issue。用户若不想提 MR，需在编码完成前主动打断流程。

## 提交 MR 前的最终复审

PLAN MODE P5 和 SPEC MODE S3 都自动触发本节（不再以用户确认为前置条件）。即使每个 Phase / stage 的审查都已通过，提交 MR 前仍必须做一次覆盖整段分支 diff 的完整复审，以补齐跨文件一致性、整体设计权衡、累计变更后才显现的接口/状态问题。

1. 计算分叉点：`git merge-base HEAD origin/master`（或 `origin/main`，取目标分支），记为 `<BASE>`；用 merge-base 而非目标分支当前 tip，避免把无关上游变更纳入 review 范围。
2. 调用 `$code-review`，输入 `. <BASE>..HEAD`（本地模式 + 全量变更范围）；reviewer 必须是独立 sub-agent，不复用 stage 内的 reviewer 上下文。
3. 根据结果处理：
   - 无 CRITICAL / MAJOR：把 MINOR / SUGGESTION 写入收尾摘要后，使用 `$mr-submit` 提交 MR。
   - 有 CRITICAL / MAJOR：coder 修复后用 `$code-commit` 单独提交；若修复触及编译/测试相关文件，由 builder 通过 `$remote-vm` 重新 build/test 通过后，**回到第 2 步对整段 diff 重跑完整 review**，不允许只 review 增量 fix。
4. 同一类 MAJOR+ 问题反复 3 轮未清零 → 停止并向用户说明可选方案（继续修 / 降级理由说明 / 带问题强提 MR）。

SPEC MODE 下，本节的复审与 S2 step 6 的 stage spec-conformance review 是不同环节：前者是全量出口门禁（按整段分支 diff），后者是 stage 内部门禁（按 stage diff），不能互相替代。

## 阻塞处理

需要用户决定时，只给可执行选项：

- 调整实现方案后继续。
- 接受明确风险继续。
- 暂停并保留当前分支状态。

不要把未验证完成的变更当作完成交付。
