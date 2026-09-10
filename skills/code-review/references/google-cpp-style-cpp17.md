# Google C++ Style Guide — C++17 Profile

审查 C++ 变更时，与 `cpp17-review.md` 一起使用。本文件以 [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html) 为参考，但固定在 C++17：Google 官方当前允许的 C++20 内容不适用于本 profile。

## 规则优先级与 finding 策略

- 始终执行“不允许 C++20+”硬门禁；其余规则按 `AGENTS.md`/`CLAUDE.md`、仓库规范、修改位置的既有风格、本文顺序应用。
- 只审查 diff 引入或直接影响的问题，不要求顺手格式化未修改的历史代码。
- 新增 C++20/23 依赖或语法记为 `CRITICAL [Q]`；会导致正确性、资源、并发或 ABI 问题的风格违规按实际风险升级；纯一致性问题通常为 `MINOR [Q]`。
- Google 特有的组织策略（例如全面禁用异常、特定命名和文件后缀）仅作 fallback，不得覆盖仓库已经明确的约定。

## C++17 硬门禁

- 构建配置不得出现 `CMAKE_CXX_STANDARD 20/23`、`cxx_std_20/23`、`-std=c++2a`、`-std=gnu++20`、`-std=c++20` 或更高版本。
- 不得新增 concepts/`requires`、ranges/views、coroutines、modules、`<=>`、designated initializers、`consteval`、`constinit` 等 C++20+ 语法。
- 不得新增 C++20+ 标准库能力，例如 `std::span`、`std::ranges`、`std::jthread`、`std::stop_token`、`std::barrier`、`std::latch`、`std::counting_semaphore`、`std::binary_semaphore`、`std::atomic_ref`、`std::format`、`std::source_location`、`std::bit_cast` 或 `std::endian`。
- 上述清单不是穷举；以项目在 C++17 模式下编译成功为最终判据。不得用编译器扩展伪装标准兼容性，也不得建议升级标准解决问题。

## 头文件与依赖

- 头文件应可独立编译，具备项目约定的 include guard，并直接包含自己使用的声明；禁止依赖传递 include。
- 禁止前置声明 `std` 中的实体。对项目不拥有的类型优先包含正式头文件；只有在确认语义、ABI 和编译收益后才对自有类型使用前置声明。
- 头文件中的模板和 inline/`constexpr` 定义必须可供实例化且满足 ODR；较长的非模板实现优先放入 `.cc`。
- include 顺序和路径首先服从仓库规则；没有规则时采用关联头、C/POSIX、C++ 标准库、第三方、项目头，并在组内保持稳定排序。

## 作用域、存储期与命名空间

- 将代码放入项目命名空间；禁止 `using namespace` 污染作用域，尤其禁止在头文件中导出 using-directive 或公共 namespace alias。
- 仅在 `.cc` 中用 unnamed namespace 或 `static` 提供内部链接；禁止在头文件中创建内部链接实体。
- 变量应在最窄作用域声明并立即初始化；循环外复用对象前确认这样做不会保留错误状态。
- 审查 static/global/thread-local 的初始化次序、析构顺序、线程安全和退出阶段依赖；非平凡全局对象应有明确必要性和生命周期方案。

## 类、对象与接口

- 单参数构造函数和转换运算符默认使用 `explicit`；复制/移动构造除外。禁止依赖意外的双向隐式转换。
- 公共 API 必须明确类型是 copyable、move-only 还是 neither；检查 Rule of Zero/Five、对象切片和 move 后状态。
- `struct` 用于被动数据；存在跨字段不变量、封装或演进需求时使用 `class`。优先组合而非实现继承。
- 继承通常应为 public；数据成员保持 private。重写虚函数使用 `override` 或 `final`，并验证基类析构和多态删除安全。
- 运算符重载必须符合内置语义且成本不意外；禁止重载 `&&`、`||`、逗号、一元 `&`，避免用户自定义字面量。
- 构造函数、析构函数和生命周期方法不得隐藏可能失败、阻塞或跨线程的工作；必要行为必须写入接口契约。

## 函数、所有权与错误处理

- 优先返回值表达输出；输入通常按值或 `const&`，可空参数用指针并注明 null 语义。需要跨调用保存引用/指针时必须说明生命周期。
- 优先明确且稳定的所有权模型；可按项目约定使用 `std::unique_ptr`、`std::shared_ptr`、裸指针或句柄，并检查所有权转移、回收责任、环和引用计数成本。裸指针的拥有/非拥有语义必须明确。
- 使用 C++ cast；`reinterpret_cast`、`const_cast` 和向下转换必须有明确不变量与证据。禁止 C 风格 cast 掩盖窄化或别名问题。
- `const` 必须准确表达 API 的读写语义；不要把 `const` 等同于线程安全。所有 const 操作并发安全或类注释必须明确 thread-unsafe。
- 错误处理服从项目约定。检查返回码、异常路径、持久化提交边界和回滚；`noexcept` 只能在语义真实且失败应终止时使用。
- 函数保持单一职责；长函数本身不是 finding，只有当复杂度妨碍验证、测试或正确修改时才报告。

## 类型、模板、lambda 与可移植性

- 磁盘、网络和公开格式使用确切宽度类型并检查溢出、符号转换、对齐和大小端；不得假设 `long`、指针或 `size_t` 跨平台等宽。
- 使用 `nullptr` 表示空指针；避免宏，必须使用时保证括号、唯一前缀、无重复求值和跨平台行为。
- `auto`、CTAD、SFINAE、`if constexpr`、fold expression、CRTP 和模板元编程只能在类型仍清晰且收益可验证时使用；检查实例化膨胀和诊断质量。
- lambda 捕获必须使所有权和生命周期可见；异步、跨线程或延迟回调优先显式捕获，禁止悬空引用和无意复制大对象。
- 第三方库和非标准扩展必须确认许可证、维护性、异常/RTTI/ABI 模式、编译器支持及跨平台退化路径。

## 命名、注释与局部一致性

- 命名和格式首先保持仓库及修改位置的一致性；没有既有规则时再采用 Google 风格作为 fallback。
- 名称表达业务含义、单位和所有权；避免含混缩写、类型编码和与标准/系统头冲突的文件名。
- 类和结构注释说明职责、不变量、线程模型和使用边界；函数注释说明输入输出、null、所有权、生命周期、错误、性能和同步语义。
- 实现注释解释“为什么”和不明显约束，不逐句复述代码。复杂布尔参数优先改为 enum/options 结构，而不是依赖调用点注释。
- 历史代码不符合 Google 风格时优先维持局部一致性；除非用户要求，不在功能 MR 中扩张为全文件样式整改。
