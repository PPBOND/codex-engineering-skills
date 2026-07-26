---
name: code-plan
description: Generate coding plan from requirements. Uses Opus for review and phase splitting.
---

# Code Plan

根据需求生成结构化编码计划，供 `$code-auto` 执行。

## 文件命名
- 计划文件：`task_plan-<task>.md`（kebab-case）
- 发现文件：`findings-<task>.md`（如需要）
- 文件已存在则添加序号：`-2`, `-3`

## 流程

### 1. 需求分析
- 解析需求，模糊处向用户澄清
- 确定文件名，写入 Goal/Requirements

### 2. 代码研究
- 用 explorer sub-agent 探索相关模块
- 外部依赖代码：使用 `$remote-vm` 在远程 VM 查询
- 记录到 findings 文件

### 3. Opus 审查与拆分
**单次** 规划型 sub-agent 调用，完成：
- 审查方案可行性/完整性/最优性
- 确认遵循 `.clang-format` 和 `.clang-tidy` 规范
- **按 commit 拆分**：每个 commit 是原子性变更（≤500 LOC）
  - 格式：`[commit N] <type>: <scope> - <description>`
  - type: feat/fix/refactor/test/docs
  - 包含：修改文件列表、关键代码变更点
- 标注依赖：[PARALLEL]/[SEQUENTIAL]
- 大任务（>5 commits）拆分为子任务文件

### 4. 持久化输出
让 sub-agent 写入文件。

**Prompt 模板**：
```
将以下计划写入文件 `{file_path}`，使用 Write 工具，不要遗漏任何内容：

---
# Goal
{goal_content}

# Requirements
{requirements_content}

# Approach
{approach_content}

# Commits
{commits_content}

## Dependency
{dependency_info}

# Status
**Ready for Execution**
---
```

### 5. 代码规范检查
持久化后，对计划中的示例代码进行规范检查：

1. **提取示例代码**
   - 从 task_plan 文件中提取所有 C++ 代码块
   - 创建临时文件保存示例代码（使用合适的扩展名 .cpp/.h）

2. **执行检查**
   - **格式检查**: 使用 `$remote-vm` 执行 `clang-format --dry-run` 检查格式
   - **静态检查**: 对每个代码片段执行基本的 clang-tidy 规则检查（如命名、格式等）
   - **注意**: 这是静态检查，不需要完整编译环境

3. **修正问题**
   - 发现格式问题：自动修正示例代码格式
   - 发现 clang-tidy 问题：在计划中添加 TODO 标记或修正明显问题
   - 使用 Edit 工具更新 task_plan 文件中的代码

4. **验证**
   - 重新检查修正后的代码
   - 确保所有示例代码符合规范

完成后告知用户：`$code-auto task_plan-<task>.md`
