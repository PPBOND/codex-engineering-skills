# C++17 Review Reference

仅在审查 C++、CMake、Conan、编译参数或 C/C++ ABI 变更时读取。以仓库约束优先；没有明确约束时，把 C++17 作为最高语言标准。内容改编自 [VoltAgent cpp-pro](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/02-language-specialists/cpp-pro.md)，已移除 C++20/C++23 专属要求。

## 1. 项目与构建基线

- 检查 `CMakeLists.txt`、toolchain、Conan profile、CI、编译器版本、目标平台和 CPU 架构；确认 `CMAKE_CXX_STANDARD`、GNU 扩展、RTTI、异常、可见性和优化选项一致。
- 检查新增依赖、静态/动态链接、符号可见性、ODR、头文件暴露、模板实例化和 ABI 兼容风险。
- 关注交叉编译、大小端、指针宽度、对齐、结构体布局、序列化格式以及不同编译器行为。
- 不假设某项工具可用；优先复用仓库现有构建、lint、sanitizer、coverage 和 benchmark 命令。

## 2. C++17 语言边界

- 允许并按需检查：`if constexpr`、fold expression、结构化绑定、类模板参数推导、`std::optional`、`std::variant`、`std::any`、`std::string_view`、`std::filesystem`、内联变量和并行 STL。
- 检查 `constexpr`、type traits、SFINAE、variadic template、template-template parameter、CRTP、expression template 和静态多态是否保持可读性，并避免错误重载、实例化爆炸及晦涩诊断。
- 检查类型安全、const-correctness、窄化转换、符号/无符号混用、对象生命周期、临时对象和求值顺序。
- 禁止把 C++20/C++23 能力作为修复要求，包括 concepts/constraints、ranges/views/projections、coroutines、modules、`<=>`、标准 designated initializers、`std::expected`、标准 contracts、reflection 或 metaclass。

## 3. 内存、所有权与资源

- 检查 RAII 或明确的生命周期管理、指针/句柄选型、裸指针的拥有或非拥有语义、move 后状态、copy/move 构造与赋值、Rule of Zero/Five 以及异常路径释放。
- 检查自定义 allocator、内存池、placement new、对齐、对象重用、析构调用和分配器传播规则。
- 区分栈与堆的生命周期和容量风险；检查悬空引用、double free、泄漏、越界、use-after-free 和未初始化读取。
- 检查不必要的动态分配、复制、共享所有权与引用计数；验证 copy elision 和 move 优化不会改变语义。

## 4. 错误处理与接口契约

- 检查 basic/strong/nothrow exception guarantee、`noexcept` 正确性、错误码传播、断言边界和失败回滚。
- 资源清理必须依赖 RAII 或明确对称的生命周期；不得用 C++23 `std::expected` 作为 C++17 项目的整改要求。
- 公共接口需明确所有权、单位、有效范围、线程上下文、同步/异步语义、回调生命周期和持久化影响。
- 检查 C API、系统 API、网络协议或跨语言接口的 ABI、调用约定、错误转换和异常越界传播。

## 5. 并发与异步

- 检查 `std::thread`、`std::async`、condition variable、thread pool 的启动、停止、join、取消和异常路径。
- 检查 atomic 的内存序是否建立所需 happens-before；不能仅因使用 atomic 就判定无竞态。
- 检查锁顺序、锁粒度、递归调用、回调重入、死锁、活锁、饥饿、ABA 和 false sharing。
- lock-free 结构必须验证对象回收、内存序和进度保证；不得把 coroutine 作为 C++17 修复方案。

## 6. 性能与低层行为

- 检查算法复杂度、容器/迭代器选择、容量增长、哈希退化、缓存局部性、结构体膨胀和热路径分配。
- 对 SIMD、内联汇编、prefetch、cache-line padding、NUMA、huge page、PGO 和 LTO，仅在目标平台与性能证据支持时建议。
- 检查向量化阻碍、分支密度、循环中的锁/系统调用/日志、无谓复制和零拷贝机会。
- 网络或存储路径额外检查 buffer 所有权、scatter/gather、异步 I/O 生命周期、大小端、包边界和 short I/O。
- 嵌入式、实时、DMA 或中断路径额外检查静态分配、栈预算、阻塞调用、内存屏障、设备所有权和确定性延迟。

## 7. STL、算法与可维护性

- 按访问模式、复杂度、引用稳定性和分配行为检查容器；确认 iterator invalidation 不会产生悬空引用。
- 检查标准算法、range-based for、execution policy、自定义 iterator 和 allocator-aware 类型的前置条件。
- 避免“零开销抽象”口号替代测量；模板、CRTP 或表达式模板必须比直接实现更清晰或有可验证收益。
- 公共类型、模板接口和复杂生命周期应有准确注释；注释解释契约与原因，不复述代码。

## 8. 验证建议

按变更风险和仓库能力选择验证，不要求无关工具全部执行：

- 编译：使用项目 C++17 配置，关注 `-Wall -Wextra` 或等价 MSVC 警告及新增 warning。
- 静态检查：优先项目已有 clang-tidy/cppcheck 规则，避免对全仓历史问题作无关扩张。
- 动态检查：内存、生命周期或 UB 风险使用 ASan/UBSan；线程竞态使用 TSan；适用时使用 Valgrind。
- 测试与覆盖：运行相关 UT/集成测试；按项目使用 gcov/llvm-cov，不把覆盖率数字替代行为覆盖。
- 性能：对性能 finding 提供 benchmark、profile、硬件计数器或前后对比方案；检查缓存、NUMA 或汇编前先证明热点。
- 兼容性：公共 ABI、持久化格式、网络格式或跨平台代码变更需要兼容性测试或明确迁移策略。
