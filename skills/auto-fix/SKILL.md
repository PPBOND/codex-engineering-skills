---
name: auto-fix
description: 基于 Issue、计划或问题描述完成已授权的修复与验证。按需生成本地计划；分支、提交、Issue 评论及 MR 遵循用户和项目授权。
---

# Auto Fix

基于 Issue 或问题描述自动完成修复闭环。支持两类输入：

## Karpathy 修复守则

修复前读取并应用
[`../code-auto/references/karpathy-coding-guardrails.md`](../code-auto/references/karpathy-coding-guardrails.md)。
先把现象、已证实根因或假设、最小修复范围和验收证据分开；不把 Issue 顺带扩展成重构或新能力。能复现时以复现失败后通过为完成条件，不能复现时明确证据缺口和最小可验证替代。

- **类型 1（含方案）**：issue 含修改方案 / 已有 plan 文件 / 用户给 diff → 直接走 `$code-auto`
- **类型 2（仅问题）**：仅问题描述 → 先查明根因，复杂修复用 `$code-plan` 生成本地方案，再走 `$code-auto`；发布方案到 issue 需要单独满足授权。

## Rule 0: 工作区隔离与授权

Step 5 前按 Step 4 确定本任务工作区，保护调用者分支和已有改动。创建命名分支、提交、发布评论、push/MR 必须满足用户及项目授权，不能仅由调用本 Skill 推断许可。

**必须保留的保障：**
- 不在保护分支直接实施，不自动 stash、丢弃、覆盖用户改动。
- 不自动删除/重建同名分支，不强制 rebase 或改写历史；这些动作仍需明确批准。
- 用户明确要求继续原任务时，核对原任务分支、diff 和进度后续作，不以“必须本轮新建”阻止恢复。

base 优先使用用户指定引用或已确认任务基线；新任务按仓库实际远端默认分支确定，不能写死 `origin/master`。多个目标确实无法区分时再询问，不重置已授权的 WIP。

**进入 Step 5 的前置条件：**
1. 当前路径和 HEAD/分支与 Step 4 记录的任务目标一致。
2. 能区分本任务 diff、plan 和进度文件与无关改动；本任务产生的文件不算工作区污染。
3. 如发生路径/基线不符或无法安全保留的重叠修改，先解决隔离问题；只有缺少外部决定时暂停依赖步骤。

## 输入

- GitLab Issue: URL、`#123` 或 `123`
- Jira Issue: `PROJ-1234`
- Plan 文件路径（如 `task_plan-xxx.md`）
- 直接的问题描述或修改方案文本

## Steps

### 1. 输入归一化与拉取

| 输入形式 | 动作 |
|---------|------|
| GitLab issue | `git remote -v` 取 `<group>/<project>`；`glab issue view <n> --repo <g>/<p> --comments` |
| Jira issue | 调用 `$jira` 获取 issue 信息 |
| Plan 文件 | 直接读取，标记类型 1，跳到 Step 4 |
| 用户文本 | 不需拉取，直接进入 Step 2 |

记录：标题、描述、comments、（如有）issue 编号与 `<group>/<project>`。

### 2. 方案完备度判定

扫描 issue body + comments / 用户文本，识别方案信号。

**含方案信号**（任一即可视为类型 1）：
- "修改方案" / "修复方案" / "变更范围" / "修改 N:" 段落
- 含 ` ```diff ` 代码块
- 含具体文件路径 + 修改描述（≥1 处）

**仅问题信号**（视为类型 2）：
- 只有"现象 / 复现步骤 / 报错日志 / 期望行为"
- 没有任何文件路径、代码片段、diff

输入分类由当前 agent 判断；缺少方案时继续诊断，不让用户替工具选择流程类型。只有无法从证据解决的业务语义或范围选择需要澄清。

### 3. 方案准备

#### 类型 1（含方案）

把方案规整成标准 plan 文件 `task_plan-fix-<n>.md`（无 issue 编号则用短 desc）：

- **issue 含方案** → 把 issue 的方案 / 变更范围 / 示例段落映射到 Goal / Requirements / Commits 章节，直接写入文件
- **plan 文件输入** → 直接复用，跳过转换
- **用户给 diff/方案文本** → 调用 `$code-plan`，传入"已有方案文本，仅做规整与拆分"作为指令，避免重新调研

#### 类型 2（仅问题）

1. 调用 `$code-plan`，把问题描述 / issue 内容作为需求生成方案，产出 `task_plan-fix-<task>.md`
2. 复用已有决策；用户明确要求先审 plan 或存在未决重大取舍时保留 review 关卡，其余按修复授权继续。
3. 仅在用户授权发布时把方案落到 issue；否则保留本地计划并继续修复：
   - **已有 issue（B2）** → 直接用 `glab issue note` 把 plan 中的"修改方案"和"使用示例"作为两条 comment 追加到原 issue
     ```bash
     glab issue note <n> --repo <g>/<p> --message "$(cat <<'EOF'
     ## 修改方案
     ... (从 plan 文件 Commits/Approach 章节提取，diff 格式)
     EOF
     )"
     glab issue note <n> --repo <g>/<p> --message "$(cat <<'EOF'
     ## 使用示例
     ... (从 plan 文件 Examples 章节，或基于 Commits 推导)
     EOF
     )"
     ```
   - **无 issue（C）** → 调用 `$proposal`，传入 plan 文件路径，创建新 issue。完成后回填 issue 编号。

### 4. 创建修复分支

> 实施前必须核对工作区。该检查不要求每次重建分支，不把用户已有改动或本任务 plan 当作需要丢弃的内容。

1. **预检**：
   - 按 Rule 0 解析真实 base，用户指定的引用不擅自改成 `origin/X`
   - 新任务需要最新远端基线时，在授权范围内 fetch；恢复 WIP 不强制更新基线
   - 检查 `git status --porcelain` 并分类改动。共享/脏工作区采用独立 worktree 或临时 checkout；保留原目录。将本任务必要源码和计划纳入实际验证，不能只测干净旧版本
   - 记录当前所在分支 `<orig-branch>` 仅用于错误回滚提示，不作为 base
2. 生成分支名：
   - 有 issue 编号：`fix-<issue-number>-<short-desc>`
   - 无 issue：`fix-<short-desc>`
   - 遵守项目分支前缀与用户命名；没有约定时使用 `codex/fix-<short-desc>`
3. 展示 base 和隔离位置；创建分支已获授权时按约定选名，不重复确认。未获命名分支授权时使用本地隔离 checkout 交付 diff，不把分支创建作为修复许可的替代
4. 新命名分支在独立工作区从已确认 `<base-ref>` 创建；已授权继续 WIP 则复用核验后的任务工作区
5. **分支已存在**：保留它，新任务选未占用名称；明确继续原任务则核对后恢复。用户若选择删除/重建或改写历史，仍必须明确批准具体分支和后果
6. **结束检查**：核对路径和 HEAD/分支符合记录；临时 detached checkout 可用于隔离实施，发布时必须有明确目标分支。目标不符时先修正执行路径再继续

### 5. 执行修复

> **前置检查**：按 Rule 0 核对本任务工作区、基线和文件归属；plan/进度文件允许存在。不能自动清空工作树以通过检查。

调用 `$code-auto` 并传入 `<plan-file-path>`。

`$code-auto` 内部完成实施、审查和验证；委派、commit 和 MR 仅执行已授权部分。

### 6. 提交 MR（兜底）

只有 MR 已获授权且门禁通过、尚未发布时才调用 `$mr-submit`；未授权则交付修复和验证结果，不自动创建 MR。

## Output

```
修复完成：
- Input: <原始输入摘要>
- Issue: #<number> <title>（如有，含 B2 追加的 comment 锚点 / C 新建的 issue URL）
- Plan: task_plan-fix-<task>.md
- Branch: <branch-name>
- Commits: <commit list>
- MR: <mr-url>
```

## Notes

- 本地计划提供可追溯依据；类型 2 的 issue 创建/追加 comment 仍以发布授权为前提
- 类型 1 转 plan 文件时，`$code-auto` 仍会做 build/lint 验证，不要直接跳过
- 输入分类不触发确认；实质业务取舍与明确的“先审方案”关卡仍需用户决定
- typo 等范围明确的微小修复可直接编辑并做相称检查，无须制造 plan/issue；工作区保护和发布授权照常适用
- 输入是 plan 文件路径时跳过方案准备，仍执行 Step 4 的工作区核对
