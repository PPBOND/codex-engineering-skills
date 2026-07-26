# Codex Engineering Skills

A reusable collection of 35 Codex skills for software design, implementation,
review, testing, CI diagnosis, documentation, and engineering operations.

The repository contains no organization-specific hostnames, project names, fixed
machine addresses, credentials, or private repository paths. Infrastructure values
are supplied by the user, environment, repository instructions, or connected tools.

## Layout

```text
skills/
  <skill-name>/
    SKILL.md
    agents/       # optional UI metadata
    scripts/      # optional helpers
    references/   # optional reference material
    assets/       # optional assets
```

## Included Skills

### Coding and Review

- `auto-fix` — drive a problem from issue analysis through implementation and MR.
- `code-analyze` — explain control flow, risk, and behavior.
- `code-auto` — implement a plan or specification in validated stages.
- `code-commit` — create a focused, well-formed Git commit.
- `code-plan` — turn requirements into an implementation plan.
- `code-review` — review local changes or merge requests.
- `code-review-new-feature` — structure a deep review of a large feature.
- `cpp-storage-review` — review C++ storage code for correctness and lifecycle risk.
- `mr-comments` — evaluate merge-request review comments.
- `mr-submit` — create and verify a GitLab merge request.

### Design and Documentation

- `design-analysis` — create a detailed design from requirements and code evidence.
- `design-review` — cross-review design, specification, and product documents.
- `design-to-spec` — convert a design into an implementation-ready specification.
- `design-to-swdd` — convert design analysis into a software design document.
- `plan-to-design` — elevate an implementation plan into an architecture document.
- `proposal` — extract and publish a structured proposal.
- `quarterly-report` — summarize work from connected activity sources.
- `retro` — draft or review an incident, project, or decision retrospective.
- `storyboard-from-markdown` — generate storyboard images and a PDF from documents.
- `test-handover` — produce a test-handover and acceptance document.

### Build, Test, CI, and Performance

- `cicd-check` — diagnose pipeline, test, crash, timeout, and runner failures.
- `cmake-ut-compile` — configure, build, and run CMake targets and tests.
- `cpp-ut-coverage` — improve C++ coverage with appropriate test seams.
- `integration-test-develop` — design and run multi-service integration tests.
- `perf-analyse` — analyze Prometheus-compatible performance metrics.
- `remote-vm` — build and test safely on a remote VM.
- `ut-coverage` — improve behavior-oriented unit-test coverage.

### Architecture and Storage Operations

- `deployment-log-analyze` — correlate logs across service instances.
- `distributed-storage-arch-constraints` — apply storage architecture constraints.
- `metadata-shard-develop` — guide metadata-shard design and implementation.
- `small-file-compaction-develop` — develop a small-file packing subsystem.
- `storage-system-doctor` — diagnose distributed storage deployments.

### External Systems

- `feishu-doc` — create or update Feishu/Lark documents.
- `jira` — fetch and analyze Jira resources.
- `jira-resolve` — comment and transition Jira issues using MR information.

## 各 Skill 工作流程

下面描述的是每个 skill 的默认工作流。目标仓库中的 `AGENTS.md`、
构建配置、设计规范和安全规则始终拥有更高的项目事实优先级。

### 编码与 Review

#### `auto-fix`

- 触发场景：用户提供 Issue、缺陷描述或明确的问题，并希望得到完整修复。
- 输入：问题描述、Issue 链接、目标仓库、验收标准以及可用的测试环境。
- 工作流程：
  1. 读取问题和相关代码，判断现有方案是否足以直接实现。
  2. 如果方案缺少边界、接口或验收标准，先补齐实现方案并记录决策。
  3. 建立独立分支，调用分阶段编码流程完成修改。
  4. 执行格式化、构建、测试和代码审查，修复阻塞问题。
  5. 创建 MR，并关联原始问题和验证结果。
- 产出：实现提交、验证证据、MR 链接以及尚未解决的风险。

#### `code-analyze`

- 触发场景：解释代码逻辑、追踪调用链、理解状态机或定位高风险路径。
- 输入：文件、类、函数、模块或用户关心的业务场景。
- 工作流程：
  1. 确定分析入口、调用方、实现方和关键数据结构。
  2. 逐步追踪正常路径、错误路径、异步回调和状态变化。
  3. 标注线程上下文、对象生命周期、持久化点和外部依赖。
  4. 找出容易出错的边界、隐含假设和缺少测试的位置。
  5. 在关系复杂时生成流程图或时序图。
- 产出：带源码位置的控制流说明、风险清单、图示和待确认问题。

#### `code-auto`

- 触发场景：已有 plan 或 spec，需要 Codex 按阶段完成编码任务。
- 输入：计划或规格文件、目标阶段、验收命令和分支范围。
- 工作流程：
  1. 校验计划是否包含文件范围、接口、测试和完成条件。
  2. 按依赖顺序拆分阶段，每阶段只修改约定范围。
  3. 完成实现后运行该阶段的最小构建和测试。
  4. 审查正确性、边界、并发、错误处理和可维护性。
  5. 记录进度并创建阶段提交；全部阶段完成后执行整体验证。
  6. 如用户要求，创建最终 MR。
- 产出：分阶段代码、提交、进度记录、测试结果和最终审查结论。

#### `code-commit`

- 触发场景：用户要求提交当前改动。
- 输入：工作树状态、期望提交范围和仓库提交规范。
- 工作流程：
  1. 检查状态和 diff，区分任务改动与无关改动。
  2. 仅暂存当前任务需要的文件。
  3. 在提交前运行适当的快速验证。
  4. 根据实际 diff 生成简洁、可追踪的提交信息。
  5. 创建提交并再次检查工作树。
- 产出：提交 SHA、提交信息、包含文件以及未提交改动说明。

#### `code-plan`

- 触发场景：需求已经明确，但还缺少可以直接编码的实现计划。
- 输入：需求、相关代码范围、约束条件和验收目标。
- 工作流程：
  1. 探索入口、调用关系、数据结构、构建目标和现有测试。
  2. 明确当前行为、目标行为和不在本次范围内的内容。
  3. 按依赖拆成可独立验证的阶段。
  4. 为每阶段写出文件、接口、实现步骤、测试和验收命令。
  5. 复核遗漏、并行冲突和回滚风险。
- 产出：可交给编码 agent 直接执行的分阶段计划。

#### `code-review`

- 触发场景：审查本地 diff、提交范围或 MR。
- 输入：base/head、MR 链接、设计或规格以及仓库 Review 规则。
- 工作流程：
  1. 固定审查范围并建立变更清单。
  2. 将实现与需求、设计、接口和测试矩阵对齐。
  3. 追踪修改接口的调用方、实现方和错误传播。
  4. 检查正确性、并发、生命周期、兼容性、资源边界和可观测性。
  5. 验证测试是否覆盖正常、边界、失败和恢复路径。
  6. 对每个 finding 进行严重度分级并复核证据。
- 产出：按严重度排序、带文件和行号的 actionable findings。

#### `code-review-new-feature`

- 触发场景：新增功能改动较大，无法可靠地逐文件顺序审查。
- 输入：提交范围或 MR、设计文档和重点关注维度。
- 工作流程：
  1. 按行为和职责建立变更清单。
  2. 拆成 API、状态、执行、恢复、可观测性和测试等逻辑模块。
  3. 为每个模块生成专项 checklist。
  4. 分模块审查，再单独检查跨模块不变量和生命周期。
  5. 合并重复 finding，解决冲突结论并复核高严重度问题。
- 产出：模块化 Review 报告、汇总 finding 和未覆盖风险。

#### `cpp-storage-review`

- 触发场景：审查 C++ 高性能或分布式存储代码。
- 输入：代码范围、架构设计、线程模型和测试结果。
- 工作流程：
  1. 确认持久化真相源、线程上下文和异步完成语义。
  2. 检查锁顺序、数据竞争、回调生命周期和关闭路径。
  3. 检查热路径分配、无界队列、大对象复制和缓冲区持有。
  4. 检查重试、幂等、部分成功、重启恢复和版本兼容。
  5. 检查故障、并发、恢复和兼容性测试。
- 产出：按 P0～P3 分级的存储专项 finding 和残余风险。

#### `mr-comments`

- 触发场景：分析 MR 中的某条评论或全部未解决讨论。
- 输入：MR URL、可选 note/discussion 锚点和本地代码。
- 工作流程：
  1. 获取指定评论及其对应 diff。
  2. 对照最新代码、测试和设计判断评论是否仍然有效。
  3. 分类为缺陷、合理改进、已修复、已过期、不正确或需澄清。
  4. 为有效评论给出最小修复建议。
  5. 只有用户明确要求时才回复或解决线上讨论。
- 产出：逐条评论的判断、证据和建议动作。

#### `mr-submit`

- 触发场景：把当前分支提交为 GitLab MR。
- 输入：源分支、目标仓库、默认分支和已完成验证。
- 工作流程：
  1. 检查工作树、提交范围和远端配置。
  2. 推送源分支并检查是否已有同源 MR。
  3. 根据提交和 diff 生成标题、摘要、测试和风险说明。
  4. 创建一次 MR，不自动附加未请求的 reviewer、label 或 auto-merge。
  5. 读取远端结果，验证源分支、目标分支和 MR 状态。
- 产出：规范化 MR 和可访问的 canonical URL。

### 设计与文档

#### `design-analysis`

- 触发场景：从需求出发进行详细设计、架构方案比较或复杂功能分析。
- 输入：需求、现有代码、架构约束、竞品材料和用户确认。
- 工作流程：
  1. 将需求拆成目标、非目标、参与者、状态和验收标准。
  2. 用源码位置验证关键架构前提和现有行为。
  3. 枚举候选方案并比较正确性、内存、性能、复杂度和兼容性。
  4. 定义真相源、生命周期、线程模型、错误处理和恢复。
  5. 估算规模、RPC、内存和写放大，补充时序图。
  6. 记录已确认、待确认和已拒绝决策，并经过独立评审收敛。
- 产出：包含方案选择、接口、状态机、风险和测试策略的详细设计。

#### `design-review`

- 触发场景：评审 design、analysis、SWDD、spec 或 PRD。
- 输入：待评审文档、相关代码和上游/下游文档。
- 工作流程：
  1. 验证文档对当前代码和系统事实的描述。
  2. 交叉检查需求、设计、接口、状态、错误码和测试的一致性。
  3. 扫描生命周期、并发、恢复、兼容性和范围承诺盲区。
  4. 判断是否达到进入 spec 或编码阶段的门槛。
  5. 将问题按 P0～P3 分级并给出修订建议。
- 产出：可执行 todo list、阻塞项和评审结论。

#### `design-to-spec`

- 触发场景：把已经收敛的设计转换为 Codex 可直接编码的规格。
- 输入：设计文档、代码事实、接口定义和仓库 spec 规范。
- 工作流程：
  1. 提取已确认范围、术语、状态、接口和不变量。
  2. 为 Proto、数据结构、类和函数给出实现级签名或骨架。
  3. 为每个 hook 指定稳定源码锚点和语义。
  4. 按依赖拆分阶段，定义每阶段文件范围和质量门禁。
  5. 建立需求—代码—测试映射和端到端验收命令。
  6. 运行 spec lint 或等价检查，清理 TODO、旧术语和矛盾。
- 产出：无需回跳设计即可执行的 implementation spec。

#### `design-to-swdd`

- 触发场景：把设计分析整理成团队软件设计文档。
- 输入：analysis、需求、接口材料、测试策略和文档模板。
- 工作流程：
  1. 提取背景、目标、范围和承诺状态。
  2. 组织总体方案、核心流程、接口、数据结构和状态机。
  3. 汇总错误处理、日志、指标、配置和兼容性。
  4. 将测试拆成 UT、集成功能、故障与稳定性三类。
  5. 明确 current scope、follow-up 和 out-of-scope。
  6. 执行章节完整性和术语一致性检查。
- 产出：适合团队评审和转测输入的 SWDD。

#### `plan-to-design`

- 触发场景：已有实现计划，但需要长期维护的正式架构文档。
- 输入：plan、代码上下文和架构约束。
- 工作流程：
  1. 从计划中提取目标、约束、组件和阶段依赖。
  2. 补充现状架构和关键源码证据。
  3. 将步骤提升为组件职责、接口、数据流和部署关系。
  4. 增加方案比较、质量属性、风险和演进策略。
  5. 检查文档能否独立解释为什么这样设计。
- 产出：正式 Architecture Design Document。

#### `proposal`

- 触发场景：从计划或方案中提取一份可评审、可追踪的 Proposal。
- 输入：plan 文件、目标代码范围和 GitLab 项目信息。
- 工作流程：
  1. 提取背景、问题、目标、非目标和推荐方案。
  2. 整理方案比较、实施阶段、风险和验收方式。
  3. 生成结构化 Issue 正文及必要的分节评论。
  4. 在创建前检查重复 Issue 和用户授权。
  5. 创建后读取远端内容验证完整性。
- 产出：GitLab Issue/Proposal URL 和本地摘要。

#### `quarterly-report`

- 触发场景：生成个人季度工作总结。
- 输入：季度范围、用户身份、日历、文档、消息、Issue 和代码活动。
- 工作流程：
  1. 按统一时间范围从已授权数据源采集活动。
  2. 对同一工作在多个系统中的记录去重。
  3. 将活动整理为结果、影响、证据和协作，而不是简单计数。
  4. 区分已完成、进行中、运营支持和成长学习。
  5. 标记缺失数据源和无法验证的影响。
- 产出：管理层摘要、主要成果、质量贡献、成长和下季度计划。

#### `retro`

- 触发场景：起草或评审故障、反复缺陷、项目或决策复盘。
- 输入：时间线、日志、Issue、会议材料、修复记录和现有复盘。
- 工作流程：
  1. 构建事实时间线并区分事实、假设和未知问题。
  2. 区分直接触发因素、根因、促成因素和影响扩大因素。
  3. 区分 workaround 与根因修复。
  4. 检查检测、响应、决策和沟通中的系统性缺口。
  5. 将行动项写成有 owner、期限和验收方式的任务。
  6. Review 模式下按 P0～P3 输出修订清单。
- 产出：无责、证据驱动、可追踪行动项的复盘文档。

#### `storyboard-from-markdown`

- 触发场景：把长文档、截图或设计材料转成故事板和 PDF。
- 输入：Markdown，或可先转换成 Markdown 的图片/文档。
- 工作流程：
  1. 解析标题、章节、关键结论、流程和视觉重点。
  2. 将内容压缩为有叙事顺序的页面规格。
  3. 为每页生成视觉提示词和一致的风格约束。
  4. 使用图像模型生成最终页面，而非仅靠本地文字渲染。
  5. 检查文字可读性、顺序、重复内容和视觉一致性。
  6. 合并图片并生成紧凑 PDF。
- 产出：页面规格、提示词包、最终图片和 PDF。

#### `test-handover`

- 触发场景：准备转测、测试澄清或发布验收文档。
- 输入：需求、设计、代码范围、UT/集成测试结果和部署信息。
- 工作流程：
  1. 从提交和文档确定精确发布范围。
  2. 汇总行为、接口、配置、数据和兼容性变化。
  3. 将需求和设计分支转换为测试矩阵。
  4. 为已执行测试记录命令、环境、结果和证据。
  5. 列出未覆盖路径、限制、回滚条件和监控方式。
  6. 逐章检查 current scope、follow-up 和 out-of-scope。
- 产出：可用于转测和验收的完整 handover 文档。

### 构建、测试、CI 与性能

#### `cicd-check`

- 触发场景：流水线、UT、集成测试、超时、崩溃或 core dump 失败。
- 输入：Pipeline/Job URL、日志、测试名、产物目录或远程 runner。
- 工作流程：
  1. 固定 pipeline、job、stage、commit 和 runner。
  2. 找到第一个失败阶段，区分基础设施与代码/测试问题。
  3. 读取相关日志和产物，优先寻找 assertion、signal、sanitizer 和退出码。
  4. 检查超时、OOM、磁盘、网络、容器和 runner 故障。
  5. 对 crash 使用匹配的二进制和调试符号生成调用栈。
  6. 将失败映射到源码和最近变更，并给出最小修复。
- 产出：根因分类、证据、置信度、修复和验证命令。

#### `cmake-ut-compile`

- 触发场景：配置、编译或运行一个或多个 CMake target/测试。
- 输入：target、test regex、构建模式和可用 build 目录。
- 工作流程：
  1. 读取仓库构建说明、CMake、preset 和包管理配置。
  2. 定位 target 声明和测试注册。
  3. 复用兼容 build 目录，必要时执行配置。
  4. 优先只编译请求的 target。
  5. 通过 `ctest` 或仓库规定方式运行测试。
  6. 失败时报告首个编译、链接或运行原因。
- 产出：配置、命令、target、测试结果和产物位置。

#### `cpp-ut-coverage`

- 触发场景：补充 C++ 未覆盖行或分支。
- 输入：覆盖率报告、源码范围、现有测试和构建环境。
- 工作流程：
  1. 将缺口映射到具体行为和分支条件。
  2. 分类为正常输入、边界、依赖结果、异步、系统失败或防御代码。
  3. 选择 direct、parameterized、mock、fault injection 或 async 测试。
  4. 编写带状态和副作用断言的测试。
  5. 编译运行最小 target，重新生成覆盖率。
  6. 确认目标缺口关闭，并运行相邻回归测试。
- 产出：测试改动、策略说明、前后覆盖率和合理排除项。

#### `integration-test-develop`

- 触发场景：设计或执行多服务集成测试。
- 输入：代码变更、服务部署方式、测试环境和验收目标。
- 工作流程：
  1. 从仓库发现构建、启动、健康检查、测试和清理入口。
  2. 设计正常、边界、重启恢复、部分失败、并发和兼容性用例。
  3. 构建最小目标并部署到隔离环境。
  4. 记录提交、配置、服务版本和工作负载。
  5. 运行最小相关套件并保留日志和产物。
  6. 定位首个失败后再决定是否重跑。
- 产出：测试矩阵、环境、命令、结果、产物和失败根因。

#### `perf-analyse`

- 触发场景：分析延迟、吞吐、错误率、抖动或性能回退。
- 输入：Prometheus-compatible endpoint、时间范围、workload、labels 和 metric mapping。
- 工作流程：
  1. 校验时间窗口，识别预热、稳态和收尾阶段。
  2. 获取请求率、完成率、错误、重试、延迟、队列和资源指标。
  3. 将客户端、服务端、队列和设备层对齐到同一时间轴。
  4. 找到最早随症状变化或达到饱和的层。
  5. 多次运行比较时按并发、请求大小和持续时间归一化。
  6. 明确是回退、抖动、饱和还是证据不足。
- 产出：关键指标、瓶颈证据、置信度、查询和下一步实验。

#### `remote-vm`

- 触发场景：本机环境不适合构建、测试、lint 或运行项目。
- 输入：SSH target、远端仓库路径、分支/提交和目标命令。
- 工作流程：
  1. 验证连接和远端路径。
  2. 检查 Git 状态，保护无关改动。
  3. 必要时使用独立 worktree。
  4. 运行仓库规定的最小构建和测试命令。
  5. 收集退出码、关键输出和产物。
  6. 失败时定位首个可行动原因，避免修改机器级配置。
- 产出：远端 revision、完整命令、结果、产物和下一步。

#### `ut-coverage`

- 触发场景：对任意语言或构建系统进行行为导向的 UT 覆盖率提升。
- 输入：覆盖率报告、源码范围、仓库测试规则和目标阈值。
- 工作流程：
  1. 将未覆盖内容映射到行为，而不是只看行号。
  2. 识别普通、边界、依赖、异步、系统失败和不可达路径。
  3. 选择最稳定的测试层级和 seam。
  4. 实现最小测试并验证真实状态或副作用。
  5. 重新生成报告并运行相关回归。
  6. 对无法覆盖内容给出可审计的排除理由。
- 产出：测试、验证结果、覆盖率变化和剩余缺口。

### 架构与存储运维

#### `deployment-log-analyze`

- 触发场景：分析多实例服务部署日志和跨节点故障链。
- 输入：日志根目录、实例清单、时间范围和请求/对象标识。
- 工作流程：
  1. 盘点实例角色、版本、重启时间和时区。
  2. 从症状附近提取窄时间窗口。
  3. 用请求或对象 ID 串联跨实例生命周期。
  4. 找到最早异常事件并区分主故障与重试/清理噪声。
  5. 关联进程重启、OOM、磁盘、网络和内核事件。
- 产出：跨实例时间线、证据、根因、影响范围和修复建议。

#### `distributed-storage-arch-constraints`

- 触发场景：设计或评审高性能分布式存储功能。
- 输入：目标设计、代码架构和项目特定参数。
- 工作流程：
  1. 检查传输、协议、编排、共识、持久化和设备访问分层。
  2. 检查线程上下文、锁顺序和异步生命周期。
  3. 检查热路径内存、池化、队列和 cache 上限。
  4. 明确 accepted、persisted、replicated、acknowledged 等状态。
  5. 检查真相源、重放、快照、leader change 和版本兼容。
  6. 用生命周期、可观测性和测试门禁判断设计完整度。
- 产出：架构约束清单和设计缺口。

#### `metadata-shard-develop`

- 触发场景：修改元数据分片、路由、放置、复制、迁移或恢复。
- 输入：模块代码、协议、设计文档和测试。
- 工作流程：
  1. 定位源码、协议、设计和测试入口。
  2. 确认 routing key、shard identity、ownership 和 replicated truth。
  3. 追踪生命周期操作到持久化和调用方。
  4. 检查 split/merge、迁移、leader change 和 stale epoch。
  5. 检查幂等、重启恢复、兼容性和测试 target。
- 产出：基于仓库事实的实现或评审结果。

#### `small-file-compaction-develop`

- 触发场景：设计、实现或审查小文件打包/归并子系统。
- 输入：对象生命周期、索引模型、持久化和回收需求。
- 工作流程：
  1. 定义 source object、container file、索引和状态机。
  2. 比较 append-only、size-tiered 和 time-window 等策略。
  3. 评估内存、读写放大、删除成本和恢复。
  4. 定义原子 commit 点、幂等重试和 restart reconciliation。
  5. 限制队列、索引内存、批次和并发任务。
  6. 覆盖 crash、删除、校验失败、并发读取和 GC 测试。
- 产出：设计、实现建议、测试矩阵或专项 Review finding。

#### `storage-system-doctor`

- 触发场景：诊断分布式存储服务健康、容量、延迟、崩溃或资源异常。
- 输入：主机、SSH 访问、部署/日志目录、组件名和时间范围。
- 工作流程：
  1. 明确受影响主机、时间和症状。
  2. 读取部署清单和服务定义。
  3. 收集负载、内存、磁盘、inode、服务和内核错误。
  4. 定位组件日志并按时间、请求或分片标识关联。
  5. 区分事实、可能原因和未解问题。
  6. 给出最小安全动作和验证命令。
- 产出：主机/组件范围、证据、根因置信度、缓解和长期修复。

### 外部系统

#### `feishu-doc`

- 触发场景：创建、追加或发布飞书/Lark 云文档。
- 输入：目标文档或目录、正文内容、标题和可用认证方式。
- 工作流程：
  1. 检查连接和身份，解析目标 token 或目录。
  2. 新建文档或读取必要的结构信息。
  3. 将内容按标题、段落、列表、表格等块追加。
  4. 避免 fetch—本地改写—整体覆盖造成并发内容丢失。
  5. 读取文档元信息或追加结果验证写入成功。
- 产出：文档链接、写入范围和验证结果。

#### `jira`

- 触发场景：读取和分析 Jira Issue、Filter、Board 或 JQL 结果。
- 输入：Issue key/URL、Filter ID、Board ID 或 JQL。
- 工作流程：
  1. 从用户输入解析资源类型。
  2. 使用已配置 connector、CLI 或 REST API 获取最小数据集。
  3. 对搜索结果处理分页。
  4. 汇总状态、优先级、负责人、验收标准、评论和依赖。
  5. 默认只读，除非用户明确要求修改。
- 产出：Issue/查询摘要、阻塞项、风险和建议下一步。

#### `jira-resolve`

- 触发场景：用户明确要求关联 MR 并流转、解决或关闭 Jira Issue。
- 输入：Issue key/URL、MR URL 和期望工作流结果。
- 工作流程：
  1. 读取当前状态和可用 transitions。
  2. 验证 MR 标题、状态、源/目标分支和 canonical URL。
  3. 检查是否已有等价 MR 评论。
  4. 添加一条可追踪、幂等的 MR 评论。
  5. 选择 Jira 实际暴露且符合用户意图的 transition。
  6. 再次读取 Issue 验证评论和最终状态。
- 产出：Issue、MR、评论结果、transition 和最终状态。

## Installation

For a repository-local skill, copy one directory to:

```text
<target-repository>/.agents/skills/<skill-name>/
```

For a personal Codex skill, copy one directory to:

```text
%USERPROFILE%/.codex/skills/<skill-name>/
```

On macOS or Linux, use:

```text
~/.codex/skills/<skill-name>/
```

Start a new Codex task after installation. Invoke a skill explicitly with
`$<skill-name>` or let its `description` trigger it from natural language.

## Configuration

Skills that use Git providers, issue trackers, document systems, SSH, CI runners, or
metrics services expect those tools to be installed and authenticated separately.
Never add credentials or fixed private endpoints to a skill.

## Validation

Before publishing changes:

1. ensure every `skills/<name>/SKILL.md` has matching `name` frontmatter;
2. scan for credentials, private hostnames, addresses, and repository paths;
3. verify referenced scripts and local resources exist;
4. test the skill in a fresh Codex task.
