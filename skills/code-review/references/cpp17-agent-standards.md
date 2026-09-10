# C++17 Agent Standards

本参考把 `affaan-m/ecc` 的 C++ Core Guidelines 适配版、C++ Core Guidelines 的 Per.1–Per.19 性能条目，以及 `PatrickJS/awesome-cursorrules` 的 C++ 规则提炼为 Codex 可执行的审查清单。它只服务于 C++17；项目自己的 `AGENTS.md`、`CLAUDE.md`、接口契约和既有风格优先。

来源：

- [ECC C++ Coding Standards](https://github.com/affaan-m/ecc/blob/main/skills/cpp-coding-standards/SKILL.md)
- [C++ Core Guidelines](https://github.com/isocpp/CppCoreGuidelines/blob/master/CppCoreGuidelines.md)
- [awesome-cursorrules C++ rules](https://github.com/PatrickJS/awesome-cursorrules/tree/main/rules)
- [cursor.directory/cpp](https://cursor.directory/cpp)（社区规则入口；具体条目以可审计的 GitHub mirror 为准）

## C++17 硬门禁

- 最高标准固定为 C++17；检查 `CMAKE_CXX_STANDARD`、toolchain、Conan/profile、CI 和编译命令是否一致。
- 不得新增或推荐 C++20/23 语法、库或构建标准：`concepts/requires`、ranges/views、coroutines、modules、`<=>`、designated initializers、`consteval`、`constinit`、`std::span`、`std::jthread`、`std::stop_token`、`std::barrier`/`latch`/semaphore、`std::atomic_ref`、`std::format`、`std::source_location`、`std::bit_cast`、`std::endian`、`std::expected` 等。
- C++17 可用能力包括 `std::optional`、`std::variant`、`std::string_view`、`std::filesystem`、`std::scoped_lock`、结构化绑定和 `if constexpr`；不得把这些能力升级为更高标准的替代品。
- 发现禁用能力或 `-std=c++20`/更高配置时，审查输出 `CRITICAL [Q]` 并阻止继续实现/合入；修复只能使用 C++17。

## Core Guidelines 基线

- 直接表达意图，优先静态类型检查；使用 `enum class`、强类型包装（单位、ID、状态）和命名常量，避免魔法数字、隐式窄化和不必要的强制转换。
- 默认不可变：对象、参数和成员函数尽量使用 `const`/`constexpr`；接口明确区分输入、输出和所有权。
- 函数只做一个逻辑操作，保持短小；廉价值类型按值传递，昂贵输入按 `const&`，消耗型参数可按值接收并移动；多结果优先返回结构体/值。
- 能用标准库算法表达的遍历、查找和变换不要手写重复控制流；复杂逻辑拆成命名函数，避免深层嵌套和隐含副作用。
- 构造函数建立完整不变量；单参数构造函数默认 `explicit`；优先 Rule of Zero，确需资源管理时完整遵守 Rule of Five；多态基类析构函数必须为 public virtual 或 protected non-virtual，覆写使用 `override`/`final`。
- 优先组合而非继承；接口和公共类型写清不变量、单位、错误语义与生命周期，注释解释调用契约和设计原因。
- 头文件自包含，禁止头文件全局 `using namespace`，遵守 ODR；命名和格式以仓库现有风格为准，社区规则只作 fallback。

## 所有权、生命周期和内存安全

- 资源生命周期必须可证明；优先使用 RAII，但裸 `new`/`delete`、`malloc`/`free`、智能指针、引用或第三方句柄均不因类型本身自动违规。
- 根据项目的所有权模型选择指针或句柄表示；`std::unique_ptr`/`std::shared_ptr` 只是可选工具，不要求为了形式统一而替换已有裸指针。
- 裸指针或引用可以表示非拥有观察关系，也可以在项目明确的所有权/回收协议下参与资源管理；不得无契约地跨异步边界保存、指向已结束生命周期的对象或让回收责任不明。异步回调必须说明对象生命周期。
- 使用底层 allocator、placement-new 或第三方句柄时，必须在同一变更中说明所有权、销毁/回收路径、异常安全和线程约束。
- 不得对非平凡类型使用 `memset`/`memcpy`；避免悬空引用、双重释放、部分初始化和异常路径泄漏。

## 类型安全与接口

- 使用 `std::optional` 表示“可能没有值”，使用项目约定的错误码/结果类型表示预期失败；不要引入 C++23 `std::expected`。
- `std::string` 拥有字符序列；`std::string_view` 只作非拥有观察，调用期间 owner 必须存活，不能从临时字符串构造后跨越表达式/异步回调保存。
- 通过参数对象或返回结构体表达多字段契约；避免 `void f(T&, U&)` 式隐式输出参数和无单位的 primitive obsession。
- 公开 API 的单位、范围、空值、错误语义、持久化影响、同步/异步行为和所有权必须在注释或类型中明确。

## Per.1–Per.19 性能门禁

上游当前定义 Per.1–Per.7、Per.10–Per.19；Per.8/Per.9 没有独立规则，不能自行虚构规则编号。对每个性能改动逐项核对：

| 条目 | 审查/实现要求 |
|---|---|
| Per.1 | 没有明确用户影响、SLO 或资源问题，不做优化。 |
| Per.2 | 不做提前优化；先保持清晰、可验证的实现。 |
| Per.3 | 只优化已证明的性能关键路径，不改非热点代码。 |
| Per.4 | 不假设复杂/“聪明”的代码一定更快；先测量再决定。 |
| Per.5 | 不假设低层代码一定优于高层抽象；比较真实构建产物和端到端结果。 |
| Per.6 | 任何性能收益声明必须有可复现的 benchmark/profile/硬件计数器或前后对比。 |
| Per.7 | 设计应保留可优化边界：稳定接口、可替换策略、局部化低层技巧，并避免臆测式泛化。 |
| Per.8/Per.9 | 上游未定义；按仓库约束和 Per.7/Per.10 的证据要求处理，不创建伪规则。 |
| Per.10 | 依赖静态类型系统表达约束，减少运行时分支、字符串分派和不安全转换。 |
| Per.11 | 仅在有证据且不改变语义时把稳定计算移到编译期（C++17 `constexpr`/`if constexpr`）。 |
| Per.12 | 消除不必要的别名、复制和临时视图；先证明它们位于热点。 |
| Per.13 | 消除冗余指针追踪和间接层；不得以裸指针所有权换取假想收益。 |
| Per.14 | 减少分配/释放次数，使用预留、复用或批处理；必须验证峰值内存和线程安全。 |
| Per.15 | 关键分支不得临时分配；把分配移出热路径或采用已有 RAII 池/arena 封装。 |
| Per.16 | 使用紧凑数据结构，权衡 padding、对齐、可读性、ABI 和随机访问代价。 |
| Per.17 | 时间关键结构体可按访问频率安排成员，但必须有布局/性能证据并评估 ABI 影响。 |
| Per.18 | 空间占用会影响缓存和带宽；压缩布局必须通过 profile 和正确性测试证明收益。 |
| Per.19 | 优先可预测、连续、局部的内存访问；检查 AoS/SoA、指针追踪、cache miss、NUMA 和 false sharing。 |

### 性能证据闭环

1. 记录优化前 baseline：输入规模、数据分布、编译器/选项、硬件、线程数、热身、重复次数和统计方法。
2. 用 profiler/benchmark 定位热点，保存命令和原始结果；“看起来更快”不是证据。
3. 每次只改变一个可归因因素，先验证功能、边界、并发和资源生命周期，再比较同一 workload 的结果。
4. 记录收益、方差、峰值内存、回归场景和结论；无法复现时不得声称优化成功。

无 profiling 或 baseline 的性能改写：审查通常为 `MAJOR [P]`（可能改变正确性/资源/并发时）或 `MINOR [P]`（低风险且易回滚），并要求先补证据；实现流程必须暂停性能改动而保留正确性修复。

## Cache、并发与测试

- 热点容器优先连续存储；比较 AoS 与 SoA 时记录访问模式，不凭经验拆分结构体。避免在共享热字段旁引入 false sharing；对齐/填充调整须有架构和 ABI 依据。
- 共享可写状态越少越好；使用命名的 `std::lock_guard`/`std::unique_lock`/`std::scoped_lock`，条件变量必须带谓词；不在锁内调用未知回调。`volatile` 不是线程同步工具，lock-free 只在必要且有模型/基准证明时使用。
- 原子操作必须说明 happens-before 和 memory order；除非有必要性、无锁算法证明和基准证据，不引入 lock-free 结构。
- 修复或性能改动必须覆盖边界、错误、并发和回归场景；优先单元测试（Arrange–Act–Assert），跨模块行为补集成/长稳测试，benchmark 与 correctness 测试分离。

## 质量结论

- Review：违反 C++17 硬门禁为 `CRITICAL [Q]`；无证据优化按上文 `P` 维度分级；所有权/生命周期/数据竞争/ABI 风险按实际影响升级。
- Auto-code：实现前确认 C++17 配置并读取本参考；性能改动先 baseline/profile，改动后跑 correctness、相关测试和同 workload 对比；任何未解决的 `CRITICAL`/`MAJOR` 都禁止进入下一阶段或提交。
