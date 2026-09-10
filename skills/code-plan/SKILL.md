---
name: code-plan
description: Generate a reviewable coding plan from requirements and repository evidence. Use for explicit planning requests or complex implementation planning; respect project delegation and publication boundaries.
---

# Code Plan

根据需求生成结构化编码计划，供 `$code-auto` 执行。

## Karpathy 规划守则

规划非平凡任务前读取并应用
[`../code-auto/references/karpathy-coding-guardrails.md`](../code-auto/references/karpathy-coding-guardrails.md)。
计划必须分开已证实事实、会影响范围/行为的假设和待决选择；选择当前需求支持的最小方案；每个 phase 要把需求、改动范围和可执行验收一一对应。

## 复用与简化门禁

开始规划前必须读取并应用 [`../code-auto/references/reuse-and-simplicity-principles.md`](../code-auto/references/reuse-and-simplicity-principles.md)，与 `$code-auto` 使用同一套原则。方案按“不写代码/删除 → 复用仓库已有实现 → 标准库或平台能力 → 最小局部实现 → 有现实依据的新抽象”的顺序选择。

- 单一职责、显式输入、最小共享状态、本地化副作用、不可变优先、组合优于继承和高价值测试必须在方案中体现。
- 不得为了潜在复用设计过碎函数、单实现接口、无现实调用方的公共模块、假想扩展点或手写标准库替代品。
- 新接口、继承、模块、依赖、共享可变状态或兼容层必须说明当前调用方、真实变化轴和不可替代原因；说明不成立时从计划中删除。

## 文件命名
- 计划文件：`task_plan-<task>.md`（kebab-case）
- 发现文件：`findings-<task>.md`（如需要）
- 文件已存在则添加序号：`-2`, `-3`

## 流程

### 1. 需求分析
- 解析需求并先核对代码、配置和已有决策；仅对无法自行查明且影响范围/契约的选择澄清，其余说明假设后继续
- 确定文件名，写入 Goal/Requirements
- 先判断需求能否由删除代码、现有行为、配置或已有实现完成；只有确需新增代码时才进入实现规划

### 2. 代码研究
- 当前 agent 探索相关模块；只有项目多 Agent 开关已允许时才委派 explorer，缺少 Agent 不阻塞规划
- 优先检查可用的本地依赖代码；确需且已授权时按 `$remote-vm` 查询远端
- 搜索现有实现、调用方、标准库/平台替代，以及相关状态、所有权、副作用和测试边界
- 记录到 findings 文件

### 3. 审查与拆分
当前 agent 完成以下检查；独立 reviewer 仅在多 Agent 已授权且可用时使用，不固定特定模型：
- 审查方案可行性/完整性/最优性
- 按复用与简化原则审查每个方案，明确哪些代码可以删除/复用，并拒绝没有当前需求支撑的抽象、继承、共享状态、依赖和测试
- 确认遵循 `.clang-format` 和 `.clang-tidy` 规范
- **按 commit 拆分**：每个 commit 是原子性变更（≤500 LOC）
  - 格式：`[commit N] <type>: <scope> - <description>`
  - type: feat/fix/refactor/test/docs
  - 包含：修改文件列表、关键代码变更点
- 标注依赖：[PARALLEL]/[SEQUENTIAL]
- 大任务（>5 commits）拆分为子任务文件

### 4. 持久化输出
由当前负责输出的 agent 写入文件；这不要求额外 sub-agent。

**Prompt 模板**：
```
将以下计划完整写入 `{file_path}`，遵循当前环境的文件编辑工具约定：

---
# Goal
{goal_content}

# Requirements
{requirements_content}

# Approach
{approach_content}

# Reuse and Simplicity Decisions
{reuse_and_simplicity_decisions}

# Commits
{commits_content}

## Dependency
{dependency_info}

# Status
**Ready for Execution**
---
```

### 5. 代码规范检查
持久化后，先复核方案门禁，再对计划中的示例代码进行规范检查：

1. **复用与简化复核**
   - 确认计划已记录复用/标准库选择、共享状态与副作用边界、对象可变性、新抽象依据和最小有效测试
   - 发现可删除的代码、单实现接口、无调用方扩展点或重复实现时，先收敛计划再继续

2. **提取示例代码**
   - 从 task_plan 文件中提取所有 C++ 代码块
   - 创建临时文件保存示例代码（使用合适的扩展名 .cpp/.h）

3. **执行检查**
   - **格式检查**: 使用适用的项目工具执行 `clang-format --dry-run`；本地不适用且已授权时才使用 `$remote-vm`
   - **静态检查**: 对每个代码片段执行基本的 clang-tidy 规则检查（如命名、格式等）
   - **注意**: 这是静态检查，不需要完整编译环境

4. **修正问题**
   - 发现格式问题：自动修正示例代码格式
   - 发现 clang-tidy 问题：在计划中添加 TODO 标记或修正明显问题
   - 使用 Edit 工具更新 task_plan 文件中的代码

5. **验证**
   - 重新检查修正后的代码
   - 确保方案通过复用与简化门禁，且所有示例代码符合规范

只要求制定计划时交付计划和执行入口 `$code-auto task_plan-<task>.md`。若上游已授权完成实施，本计划是内部步骤，继续执行；用户要求先审计划时仍须等待该批准。
