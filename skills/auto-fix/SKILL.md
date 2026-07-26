---
name: auto-fix
description: 基于 Issue 或问题描述自动修复：判定方案完备度 → 缺方案则先生成方案并提交 issue → 创建分支 → code-auto → MR。
---

# Auto Fix

基于 Issue 或问题描述自动完成修复闭环。支持两类输入：

- **类型 1（含方案）**：issue 含修改方案 / 已有 plan 文件 / 用户给 diff → 直接走 `$code-auto`
- **类型 2（仅问题）**：仅问题描述 → 先 `$code-plan` 生成方案，落到 issue，再走 `$code-auto`

## Rule 0: 分支隔离规则（最高优先级，无例外）

**Step 5（执行修复）前必须由 Step 4 创建一个全新的修复分支并 checkout 到它**，否则 `$code-auto` 会污染调用者所在的旧分支或保护分支。

**绝对禁止：**
- 跳过 Step 4，在当前所在分支（哪怕分支名已经匹配 `fix-*` 模板）直接调用 `$code-auto`
- 在 `master` / `main` / `release-*` 等保护分支上直接干活
- 复用历史 `fix-*` 分支但不重新基于最新 `origin/master`（或显式指定 base）

**默认 base = `origin/master`**。仅当用户在输入中显式指定其它 base（如"基于 release-2.0 切"、"--base xxx"）时使用指定值。不要使用本地 `master`、当前 `HEAD`、上次中断时所在的分支。

**进入 Step 5 的硬性前置条件：**
1. 当前 `HEAD` 所在分支 = Step 4 这一轮新建的分支（用 `git rev-parse --abbrev-ref HEAD` 校验）
2. 该分支刚从 `origin/<base>` checkout 出来，且 worktree clean
3. 任一条不满足 → 停下并向用户报告，不要继续 `$code-auto`

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

判定不确定时向用户确认：含方案 / 仅问题 / 我先看下。

### 3. 方案准备

#### 类型 1（含方案）

把方案规整成标准 plan 文件 `task_plan-fix-<n>.md`（无 issue 编号则用短 desc）：

- **issue 含方案** → 把 issue 的方案 / 变更范围 / 示例段落映射到 Goal / Requirements / Commits 章节，直接写入文件
- **plan 文件输入** → 直接复用，跳过转换
- **用户给 diff/方案文本** → 调用 `$code-plan`，传入"已有方案文本，仅做规整与拆分"作为指令，避免重新调研

#### 类型 2（仅问题）

1. 调用 `$code-plan`，把问题描述 / issue 内容作为需求生成方案，产出 `task_plan-fix-<task>.md`
2. 用户 review plan（`$code-plan` 内含确认环节）
3. 把方案落到 issue：
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

> **本步骤不可跳过**。即便当前已经在某个 `fix-*` 分支上（上一轮中断、用户手动切过、之前测试遗留），也必须重新走完本步骤——根据 Rule 0，`$code-auto` 必须在"本轮新建并基于最新 base"的分支上跑。

1. **预检**：
   - 解析 base 分支：默认 `origin/master`；用户输入若含"基于 X 切"、"--base X"等显式指定 → 改用 `origin/X`
   - `git fetch origin <base>` 拉取最新引用
   - `git status --porcelain` 必须为空；非空则停下，提示用户 stash / commit / 丢弃后重试，**不要在脏 worktree 上创建分支**
   - 记录当前所在分支 `<orig-branch>` 仅用于错误回滚提示，不作为 base
2. 生成分支名：
   - 有 issue 编号：`fix-<issue-number>-<short-desc>`
   - 无 issue：`fix-<short-desc>`
   - 标题转小写、特殊字符替换 `-`、≤30 字符、不含斜杠
3. 向用户确认分支名（同时展示 base 分支，让用户有机会改）
4. 创建：`git checkout -b <branch> origin/<base>`
5. **分支已存在的处理**——必须向用户确认，**默认推荐"基于 origin/<base> 重建"**：
   - **重建（默认推荐）**：`git branch -D <branch> && git checkout -b <branch> origin/<base>`。原分支 commit 会丢弃；用户若想保留请改用其它分支名
   - **恢复 WIP**（仅当用户明确说"继续上次未完成的修复"）：`git checkout <branch>`，随后**必须执行 `git rebase origin/<base>`** 把它对齐到最新 base；rebase 失败则停下报告冲突，不要硬上
   - **改名**：回到 4.2 重新生成
6. **结束断言**：执行 `git rev-parse --abbrev-ref HEAD`，必须等于本轮选定的分支名；输出为字面值 `HEAD`（游离 HEAD 状态）也视为失败。任一不等则停止并报告，不进入 Step 5

### 5. 执行修复

> **前置 assert（来自 Rule 0）**：调用 `$code-auto` 前再次确认 `git rev-parse --abbrev-ref HEAD` = Step 4 创建的分支，且 `git status --porcelain` 为空。任一不满足 → 停止，回到 Step 4 重做，不要默默在错误的分支上跑 `$code-auto`。

调用 `$code-auto` 并传入 `<plan-file-path>`。

`$code-auto` 内部完成：phase 拆分、parallel 执行、commit、build/lint/format、（可选）submit MR。

### 6. 提交 MR（兜底）

如果 `$code-auto` 未自动提交 MR，调用 `$mr-submit`，自动从 commit 提取 issue 引用生成 MR 标题。

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

- 类型 2 的 issue 提交（B2 追加 comment / C 创建新 issue）保证修复方案有可追溯锚点
- 类型 1 转 plan 文件时，`$code-auto` 仍会做 build/lint 验证，不要直接跳过
- 判定模糊时倾向于走类型 2 + 用户确认，不要默默执行不完整方案
- 一行 typo 这类极小修改也走 `$code-auto`；`$code-plan` 会产出极简单的 plan，不会浪费太多步骤
- 输入是 plan 文件路径（Step 1 中"跳到 Step 4"）时也**不能**跳过 Step 4 的分支创建——只是跳过 Step 2/3 的方案准备，分支隔离规则照样生效
