---
name: code-analyze
description: Analyze code step-by-step based on user requirements. Explains control flow, highlights error-prone areas, generates flowcharts, and saves analysis to files. Use when user wants to understand code logic or trace execution paths.
---

# Code Analyze

按问题所需深度分析代码并给出证据；简单解释直接回答。只有用户要求文档或实施任务需要持久化分析时写文件，复杂流程才配图。

## Karpathy 分析守则

分析非平凡问题前读取并应用
[`../code-auto/references/karpathy-coding-guardrails.md`](../code-auto/references/karpathy-coding-guardrails.md)。
输出中区分已验证事实、有限假设与未解问题；只扩展到回答当前问题所需的调用链，并给出能验证分析结论的代码位置、测试或剩余不确定性。

## 文件命名

- 分析文件：`docs/analysis-<topic>.md`（kebab-case）
- 同一主题的后续分析追加到同一文件

## 流程

### 1. 需求理解

- 解析用户的代码范围和问题
- 确定分析主题名称
- 检查是否存在同主题的历史分析文件

### 2. 生成分析计划

根据问题复杂度，生成结构化计划：

| 模块 | 文件 | 分析重点 | 执行方式 |
|------|------|----------|----------|
| 模块A | file_a.cpp | 入口逻辑 | [PARALLEL] |
| 模块B | file_b.cpp | 数据处理 | [PARALLEL] |
| 模块C | file_c.cpp | 结果汇总 | [SEQUENTIAL] |

**可并行**：独立模块、不同分支、独立组件
**必须串行**：存在调用链依赖、需要前序分析结果

### 3. 执行分析

- **[PARALLEL]**：表示任务独立；多 Agent 开关已允许时才启动 sub-agent，否则主 agent 顺序完成
- **[SEQUENTIAL]**：按顺序执行
- 收集结果后合并、去重、生成全局视图

### 4. 详细分析

**执行流程** - 逐步解析：

```
### Step N: [步骤名称]
**代码位置**: `file.cpp:123-130`
**执行内容**: 描述做了什么，涉及的变量和状态变化
```

**易错点标注** - 识别容易理解错误的部分：

```
### N. [易错点标题]
**位置**: `file.cpp:150`
**表象**: 看起来像是...
**实际**: 但实际上是...
**正确理解**: 应该这样理解...
```

常见易错类型：隐式类型转换、指针/引用语义、异步执行顺序、作用域生命周期、运算符优先级、资源所有权转移

**流程图** - 使用 ASCII art（放在 `text` 代码块中）：

```text
┌─────────┐     ┌─────────┐     ┌─────────┐
│  开始   │────▶│ 条件判断 │────▶│  结束   │
└─────────┘     └─────────┘     └─────────┘
```

使用 `┌ ┐ └ ┘ ─ │ ▼ ▲ ► ◄ ├ ┤ ┬ ┴ ┼` 绘制

### 5. 输出结果

文件结构：

```markdown
# <主题> 代码分析

## 分析记录

### [日期时间] - [子主题/问题]

#### 分析目标
[用户的分析需求]

#### 涉及文件
- `path/to/file1.cpp`

#### 执行流程
[逐步分析内容]

#### 易错点
[易错点标注]

#### 流程图
[ASCII 流程图]

#### 总结
[简要总结和关键结论]

---
```

## 规范

1. **分析计划**：包含模块划分、依赖关系、`[PARALLEL]/[SEQUENTIAL]` 标注
2. **委派边界**：遵守项目多 Agent 手动开关；缺少授权或能力时由主 agent 完成，不因此停下或索取委派许可
3. **每个 Step**：说明代码位置、执行内容、状态变化
4. **易错点**：说明表象 vs 实际、为什么容易错、正确理解方式
5. **持续分析**：同一主题追加而非覆盖，用分隔线区分
