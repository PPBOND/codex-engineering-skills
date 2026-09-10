# Codex 工程 Skills

这是一个面向软件工程、C++、分布式存储和研发流程的 Codex skill 集合。
当前同步了 48 个用户级 skill，包含每个 skill 的 `SKILL.md`、可选的
`agents/` 元数据、脚本、参考资料和资源文件。

## 目录结构

```text
skills/
  <skill-name>/
    SKILL.md          # 触发条件和工作流程
    agents/           # 可选的 Codex UI 元数据
    references/       # 可选的规范和参考资料
    scripts/          # 可选的辅助脚本
    assets/           # 可选的图片或其他资源
```

## Skills 清单

### 编码、审查与质量

- `auto-fix`：从问题分析、实现到验证的完整修复流程。
- `code-analyze`：分析调用链、控制流、状态机和风险路径。
- `code-auto`：按计划或规格分阶段实现并验证代码。
- `code-commit`：检查范围并创建聚焦、可追踪的 Git 提交。
- `code-plan`：将需求整理为可执行的实现计划。
- `code-review`：审查本地改动、提交范围或 Merge Request。
- `cpp-perf`：基于测量分析和优化 C++17 性能。
- `cpp-storage-review`：审查 C++ 存储代码的正确性、并发和生命周期。
- `cpp-ut-coverage`：按行为和分支补充 C++ 测试覆盖率。
- `eval-harness`：构建可重复的 AI 输出评估和质量门禁。
- `frostkv-reviewable-engineering`：面向 FrostKV/partial_cached_kv 的可审查工程流程。
- `grill-me`：对方案、设计和实现进行压力提问与风险暴露。
- `karpathy-guidelines`：约束 AI 避免过度设计、扩大范围和无证据修改。
- `mr-comments`：分析 Merge Request 评论是否仍然有效。
- `mr-submit`：创建并验证 GitLab Merge Request。
- `no-negative-echo`：避免把被否决的方案或过程残留带入最终产物。
- `security-review`：检查认证、授权、输入、密钥和安全边界。

### 设计、架构与文档

- `design-analysis`：结合需求、代码证据和约束完成详细设计。
- `design-review`：交叉评审 design、SWDD、spec 和 PRD。
- `design-to-spec`：将收敛后的设计转换为可直接执行的实现规格。
- `design-to-swdd`：将设计分析整理为团队软件详细设计文档。
- `distributed-storage-arch-constraints`：检查存储系统分层、线程、内存、I/O、恢复和可观测性约束。
- `metadata-shard-develop`：处理元数据分片、路由、放置、复制和恢复。
- `plan-to-design`：将实现计划提升为长期维护的架构设计文档。
- `project-guidelines-example`：提供项目级 AI 协作规范示例。
- `proposal`：从计划或方案生成结构化 Proposal/Issue。
- `retro`：起草或评审故障、项目、决策和功能缺陷复盘。
- `strategic-compact`：在长任务的逻辑阶段建议进行上下文压缩。
- `test-handover`：生成转测、验收和发布交接文档。

### 构建、测试、CI 与运维

- `cicd-check`：诊断流水线、测试、崩溃、超时和 runner 问题。
- `cmake-ut-compile`：配置、编译和运行 CMake target/测试。
- `deployment-log-analyze`：关联多实例部署日志和跨节点故障时间线。
- `integration-test-develop`：设计、部署、运行和诊断集成测试。
- `perf-analyse`：分析 Prometheus 兼容接口的延迟、吞吐和资源指标。
- `remote-vm`：在远程虚拟机上安全构建、测试和运行项目。
- `small-file-compaction-develop`：设计和实现小文件打包/归并子系统。
- `storage-system-doctor`：诊断存储系统健康、容量、网络、磁盘和日志。

### 可视化与外部系统

- `clickhouse-io`：ClickHouse 查询、性能和数据工程实践。
- `draw-layered-engineering-diagrams`：生成分层工程架构、I/O、存储和恢复图。
- `feishu-doc`：创建、编辑和发布飞书/Lark 云文档。
- `jira`：读取和分析 Jira Issue、Filter、Board 或 JQL。
- `jira-resolve`：根据 MR 信息评论并流转 Jira Issue。
- `lark-doc`：读取和编辑飞书文档内容。
- `lark-drive`：管理飞书云盘文件、目录、权限和版本。
- `lark-shared`：处理飞书 CLI 认证、权限和身份问题。
- `lark-wiki`：管理飞书知识空间、节点和成员。
- `quarterly-report`：根据已授权活动生成季度工作总结。
- `storyboard-from-markdown`：将长文档、设计材料转为故事板和 PDF。

## 使用方式

将单个 skill 复制到仓库内：

```text
<目标仓库>/.agents/skills/<skill-name>/
```

或复制到个人 Codex skill 目录：

```text
%USERPROFILE%/.codex/skills/<skill-name>/
```

安装或更新后，启动新的 Codex 任务。可以使用 `$<skill-name>` 显式调用，
也可以让 skill 的 `description` 根据自然语言自动触发。

## 工程约束

仓库中的项目 `AGENTS.md`、构建配置、设计文档、安全规范和实际代码事实，
优先级高于通用 skill 建议。涉及 C++ 存储系统时，应同时关注持久化真相源、
线程上下文、异步缓冲区生命周期、锁顺序、恢复、兼容性和测试证据。

Skill 只描述工作流，不包含账号密码、API 密钥、固定私有地址或项目凭据。
使用 Git、Issue、SSH、飞书、Jira、CI 或指标服务的 skill，需要调用方单独
配置并认证对应工具。

## 发布前检查

1. 每个 `skills/<name>/SKILL.md` 的 frontmatter `name` 与目录名一致。
2. 参考资料、脚本和资源路径均存在。
3. 已扫描凭据、密钥、私有地址和本机路径，未发现实际凭据。
4. 对有副作用的 skill，先在隔离环境完成最小验证。
5. 修改 skill 后启动新的 Codex 任务，确认发现和触发行为正常。

## 同步说明

本仓库用于保存可复用的用户级工程 skills。系统内置的 `.system` skill 不在
本同步范围内；`__pycache__` 等运行时缓存也不纳入版本控制。
