---
name: plan-to-design
description: Transform implementation plan into formal Architecture Design Document. Use when you need to elevate a coding plan to architecture-level documentation for review and long-term maintenance.
---

# Plan to Design

将实现型设计文档（plan）重构为正式的架构设计文档。

## 使用方式

```
$plan-to-design <plan-file-path>
```

## 输出

`docs/design-<topic>.md`（同名则添加 `-v2` 后缀）

## 角色

资深分布式系统架构师，将"如何实现"升级为：
- 为什么这样设计
- 整体架构视角
- 关键权衡与决策

面向：架构评审、长期维护、团队协作

## 流程

### 1. 读取与分析

- 读取 plan 文件，提取主题
- 识别核心问题、设计决策、隐含假设
- 信息不足时用 explorer sub-agent 补充上下文

### 2. 生成架构设计文档

按以下 8 章结构输出：

| 章节 | 内容要点 |
|------|----------|
| 1. 设计背景与目标 | 问题背景、核心问题、非目标 |
| 2. 总体架构概览 | 组件划分、依赖假设、架构图(ASCII) |
| 3. 核心模块设计 | 职责边界、接口、数据模型、并发/一致性语义 |
| 4. 关键流程与时序 | Happy Path、异常路径、时序图 |
| 5. 设计决策与权衡 | 可选方案对比、选择理由、放弃代价 |
| 6. 一致性与可靠性 | 一致性模型、崩溃恢复、重试语义 |
| 7. 可扩展性与演进 | 扩展边界、瓶颈、预留设计 |
| 8. 风险与待验证点 | 高风险点、待验证假设 |

可选附录：术语表、参考文档

### 3. 写入文件

Write 到 `docs/design-<topic>.md`，告知用户位置

## 写作规范

- 聚焦架构，不复述实现步骤
- 逻辑级描述，不输出代码
- 多用架构语言：权衡、边界条件、失败语义
- 信息不足时标注"设计假设"
- 图表用 ASCII art
