---
name: code-review
description: Structured code review for GitLab MRs or local changes in Codex, including spec-conformance review against implementation specs and quality-gate matrices. Use for review, 审查, MR review, commit range review, fix coverage, 按 spec review, 完整 review, 架构约束检查, or GitLab review comments.
---

# Code Review

对代码变更做结构化审查。支持两种输入：

- **MR 模式**：审查 GitLab MR，并把最终 review 发布为 MR comment。
- **本地模式**：审查本地目录的 commit range，并在终端输出结果。

## 完成标准

- 已判断输入模式，并获取完整 diff、MR 信息和项目背景。
- 已按变更规模选择轻量审查或拆分审查。
- 已覆盖正确性、异常处理、生命周期、性能、可维护性和测试覆盖风险。
- 如果存在 spec 或用户要求按 spec review，已检查 RCT、生命周期、touchpoint、边界错误、运行时不变式和文档范围一致性。
- CRITICAL 结论已做交叉验证，无法验证的结论已降级为 NOTE。
- MR 模式已发布 1 条完整 comment 并回读验证；本地模式已输出完整 markdown。
- 临时文件已清理。

## 使用方式

```bash
$code-review <project> <mr_number>
$code-review <gitlab_mr_url>
$code-review <path> [commit_range]
```

- `path`: 源码目录路径。
- `commit_range`: 可选，默认 `master...HEAD`。

## Step 0: 初始化与模式判断

1. 解析用户参数，按优先级判断模式：
   - 参数包含 `merge_requests`：MR 模式。URL 路径格式为 `.../<group>/<repo>/-/merge_requests/<mr_number>`，提取 `<repo>` 和 `<mr_number>`，仓库目录默认 `~/github/<repo>`；目录不存在时提示用户提供 `<project> <mr_number>`。
   - 第二个参数是纯数字：MR 模式，`project` 为第一个参数，`mr_number` 为第二个参数。
   - 其他情况：本地模式，`path` 为第一个参数，`commit_range` 为第二个参数或 `master...HEAD`。
2. MR 模式确认 `~/github/<project>` 存在，并运行 `glab auth status` 确认 GitLab 认证有效；认证失败时提示用户检查 token 并终止。
3. 读取项目说明文件：MR 模式读取 `~/github/<project>/CLAUDE.md`，本地模式读取 `<path>/CLAUDE.md` 或向上查找；若不存在，再读取 `AGENTS.md`、`README.md` 等项目说明。
4. 如果项目说明引用 review-rule 文件，例如 `docs/code_review_checklist.md`，也读取对应文件。
5. 判断是否启用 **Spec-Conformance Review**：用户说“按 spec review / 完整 review / 架构约束”，diff 修改 `docs/spec/`，MR 描述提供 spec，或仓库内能找到与 feature 同名的 spec。

## Step 1: 获取变更与基础信息

### MR 模式

执行以下命令获取信息：

```bash
cd ~/github/<project> && glab mr view <mr_number>
cd ~/github/<project> && glab mr diff <mr_number> > /tmp/mr-<project>-<mr_number>.patch
cd ~/github/<project> && wc -l < /tmp/mr-<project>-<mr_number>.patch
```

从 MR 信息中提取：

- MR title、description、labels。
- 关联 Issue 号：从 description、commit message、branch name 中提取 `#123`、`issue-123`、`fix/123`、`Closes #123`。
- Fix 检测：title 或 labels 包含 `fix`、`bugfix`、`hotfix`、`bug`、`修复`（不区分大小写）时设置 `is_fix=true`，后续启用 T（测试覆盖）维度。

### 本地模式

```bash
cd <path> && git diff <commit_range> > /tmp/local-review.patch
cd <path> && wc -l < /tmp/local-review.patch
```

本地模式跳过 Issue 根因分析、设计文档独立评审和自动发布，只做代码审查并输出到终端。

### 规模判定

| 变更量 | 策略 |
|--------|------|
| < 200 行 | 轻量模式：读取 patch 后直接审查，跳过 Step 2、Step 3、Step 4，进入 Step 5 |
| 200 - 5000 行 | 拆分模式：按文件拆分 patch，走 Step 2 和 Step 3 |
| > 5000 行 | 提醒用户建议拆分 MR，但仍按拆分模式尝试审查 |

轻量模式下，设计文档变更由代码审查一并覆盖，不单独启动设计文档评审。

## Step 2: 拆分 Diff、检测模式、规划模块

拆分模式下，把 patch 按文件拆分到临时目录。

```bash
python3 -c "
import re, os
patch_file = '<patch_file_path>'
out_dir = '<out_dir>'  # MR: /tmp/mr-splits-<project>-<mr_number>; local: /tmp/local-review-splits
os.makedirs(out_dir, exist_ok=True)
patch = open(patch_file).read()
if re.search(r'^diff --git ', patch, flags=re.MULTILINE):
    files = re.split(r'(?=^diff --git )', patch, flags=re.MULTILINE)
else:
    files = re.split(r'(?=^--- (?!--))', patch, flags=re.MULTILINE)
for i, f in enumerate(files):
    if not f.strip():
        continue
    first_line = f.split('\n')[0]
    if first_line.startswith('diff --git'):
        m = re.search(r'b/(.+)', first_line)
        name = m.group(1).replace('/', '_') if m else f'unknown_{i}'
    elif first_line.startswith('--- '):
        name = first_line[4:].strip().lstrip('a/').replace('/', '_')
    else:
        name = f'unknown_{i}'
    open(f'{out_dir}/{name}.patch', 'w').write(f)
"
```

### 模式检测

扫描 diff，识别需要重点审查的类别：

| 检测信号 | 类别 | 审查重点 |
|----------|------|----------|
| `[=]`, `[&]`, `[this]`, `std::function`, lambda 作为参数 | Lambda 安全 | 捕获列表、异步、跨线程生命周期 |
| 热路径文件变更 | 性能 | 内存分配、锁、系统调用、拷贝 |
| `new`, `delete`, `shared_ptr`, `unique_ptr`, `weak_ptr` | 内存安全 | 所有权、生命周期、泄漏 |
| `std::mutex`, `std::atomic`, `std::thread` | 并发 | 竞态、死锁、内存序 |
| 新增或修改公共 API | API 设计 | 易用性、错误处理、抽象边界 |
| `*_test.cpp`, `TEST(`, `BENCHMARK(` | 测试/基准 | 覆盖率、场景完整性 |

### 模块规划

- 将相关文件按目录或功能合并为模块，每个模块控制在 200-500 行 diff。
- 排序：数据结构 -> 对外接口影响 -> 核心逻辑 -> 辅助模块。
- 测试文件和配置文件归为低优先级模块，做轻量审查。
- 识别跨模块关注点：资源泄漏、计数器配对、状态机完整性、异步生命周期、版本兼容。
- Fix MR 中，标注包含 fix 变更但 diff 无测试文件的模块，这些模块必须启用 T 维度。
- 为每个模块生成 checklist，每项标注维度（D/I/E/F/P/Q/T），并融入模式检测命中的类别。
- 按风险排序：P0（数据安全和核心逻辑）-> P1（业务逻辑）-> P2（辅助/测试/配置）。

展示 review 计划后直接进入审查，不要二次询问是否继续。

### 设计文档检测（仅 MR 模式 + 拆分模式）

从 diff 中识别需要额外评审的 markdown 文件：路径包含 `docs/`，并且路径关键词或文档头部命中设计信号词。

```bash
cd ~/github/<project> && python3 - <<'PYEOF'
import re
patch = open('/tmp/mr-<project>-<mr_number>.patch').read()
files = set(re.findall(r'^\+\+\+ b/(.+?)\s*$', patch, flags=re.MULTILINE))
PATH_SIG = re.compile(r'design|analysis|swdd|spec|prd|architect|方案|架构', re.I)
HEAD_SIG = re.compile(r'^#+ .*(design|analysis|swdd|spec|prd|architect|方案|架构|详细设计|概要设计)', re.I | re.M)
DOCS_PATH = re.compile(r'(^|/)docs/')
out = []
for f in sorted(files):
    if not f.endswith('.md') or not DOCS_PATH.search(f):
        continue
    if PATH_SIG.search(f):
        out.append(f)
        continue
    try:
        if HEAD_SIG.search(open(f).read()[:2000]):
            out.append(f)
    except FileNotFoundError:
        pass
open('/tmp/mr-<project>-<mr_number>-design-docs.txt', 'w').write('\n'.join(out))
print(f'{len(out)} design doc(s):')
print('\n'.join(out) if out else '(none)')
PYEOF
```

清单为空则跳过设计文档独立评审；非空则在 Step 3 并行或串行完成设计文档评审。

### Spec-Conformance 检测

启用条件满足时，确定 spec 路径：

1. 用户显式提供的 spec path 优先。
2. MR/local diff 中的 `docs/spec/**/*.md` 次之。
3. 否则按 feature、branch、MR title 在 `docs/spec/` 和 `docs/design/` 下搜索。

如果找不到 spec，输出 NOTE 说明“未找到 spec，无法做 conformance review”，但继续普通代码审查。找到 spec 后，读取其中的 §Q 质量门禁矩阵、Requirement-Code-Test triples、stage 验收命令；必要时读取对应 analysis/SWDD 做范围一致性对照。

## Step 3: 执行审查

优先在不混淆上下文的前提下拆分审查：

- 可用 Codex sub-agent 且模块之间无依赖时，每批最多 4 个 reviewer 并行。
- 不能并行时，由当前 agent 按同一 checklist 串行审查。
- 小变更（< 200 行）不拆分模块，直接审查完整 patch。

### 模块审查提示模板

```markdown
你是 Senior Code Reviewer，审查模块 N: <模块名>。

项目背景：<从项目说明文件提取的关键信息>
审查范围：<文件列表>
检测到的特殊类别：<Lambda 安全 / 并发 / 性能 等>
Diff 文件路径：
- /tmp/<splits-dir>/<file1>.patch
- /tmp/<splits-dir>/<file2>.patch

Checklist：
1. [D] ...
2. [E] ...
3. [P] <来自模式检测的额外检查项>

要求：
- 先读 diff patch 了解变更内容。
- 需要上下文时，只读取源文件变更行附近内容，不要读取整个文件。
- 源码目录的 working tree 可能不等于 MR source 或 target branch；证据链以 patch 为准，源文件只作辅助参考。
- 若源文件内容与 patch 的修改后状态对不上，视为 working tree 漂移，不要把“源文件未找到新增内容”当作 finding。
- 每条非 PASS 结论必须引用具体文件、行号和代码。
- 输出结论只使用 PASS / CRITICAL / MAJOR / MINOR / NOTE。
- 非 PASS 时给出修复方案；CRITICAL 必须给出完整证据链。
```

### 必查项

#### C++ 继承关系

涉及类方法时必须验证：

- 同一 `.h` 文件可能定义多个类，不得因搜索命中某行就假设文件中只有一个类。
- 必须确认目标方法所在行号落在哪个类定义区间内，再判断继承关系。
- CRITICAL finding 必须包含 `类名 -> 基类 -> 方法签名 -> 行号 -> 冲突点`，缺少任一环节则降级为 NOTE。

#### RAII 对称性

diff 涉及 `Init/Fini`、`Open/Close`、构造/析构等生命周期方法时必须验证：

- 改了初始化方法，就读取对应清理方法。
- 每个操作都要有对应逆操作，且清理顺序应与初始化顺序相反。
- 新增成员变量时，检查构造、析构、Init、Fini、Reset 是否同步处理。
- 初始化中途失败时，检查已完成步骤是否按逆序回滚。

#### 性能影响

涉及运行时代码的模块必须扫描下列风险；纯文档、纯配置、纯断言测试可标注“不涉及运行时路径”并跳过：

1. **Polling / 热路径 / 周期任务**：事件循环、调度器 tick、reactor poll、状态扫描、worker 主循环、新增 timer 或心跳线程中，是否新增堆分配、字符串拷贝、容器扩容、系统调用、锁获取、跨线程同步；是否可以移出热路径、预分配或无锁化；新增周期任务频率是否合理，空闲时是否仍持续唤醒 CPU。
2. **算法与数据结构**：是否把 O(1) 操作变成 O(n)；新增字段是否显著增大结构体或引入 false sharing。
3. **日志 / 统计 / 埋点**：热路径新增 log 或 metrics 是否缺少 debug 级别、采样或限流。

轮询密集型架构中，每秒数千到数万次调用会放大小开销；这类 P 维度问题优先使用 MAJOR/MINOR，不要轻易降为 NOTE。

#### 测试覆盖（Fix MR only）

`is_fix=true` 时，对每个 fix 变更点执行：

1. 在 diff 中搜索对应测试文件变更，如 `*_test.cc`、`*_test.cpp`、`test_*.py`。
2. 若 diff 无测试变更，搜索项目测试目录中与修复函数/类相关的已有测试。
3. 判断推荐覆盖方式：

| 测试类型 | 适用场景 | 判断依据 |
|----------|----------|----------|
| UT | 逻辑错误、边界条件、计算 bug、数据结构问题、单函数/单类行为修复 | 修复点可隔离，不依赖外部组件或复杂初始化 |
| Smoke/Integration | 集成问题、多组件交互 bug、配置错误、接口协议变更 | 修复涉及跨模块调用，需要真实环境或多进程协作 |
| 长跑平台 | 竞态条件、内存泄漏、资源耗尽、时序依赖 bug、压力相关问题 | 修复涉及并发、锁、引用计数，或需要长时间运行才能复现 |

输出 test coverage finding：有测试则 `PASS [T]`；无测试但应该有则 `MINOR [T]` 或 `MAJOR [T]`，并给出推荐测试类型和测试思路。

### 设计文档评审

设计文档清单非空时，使用 `$design-review` 的方法论评审设计文档。评审与代码审查保持独立，避免上下文互相干扰。

评审要求：

- 读取 `/tmp/mr-<project>-<mr_number>-design-docs.txt` 中的文件列表。
- 读取对应 patch：`/tmp/mr-splits-<project>-<mr_number>/<sanitized_path>.patch`，其中 `/` 替换为 `_`。
- 源文件只作辅助参考，行号和结论以 patch 为准。
- 按 `$design-review` 的 4 层 checklist、7 个漏洞角度和措辞信号映射表审查。
- 每条 finding 必须落到 `<file>:<line>` 或章节锚点；没有证据的条目剔除。
- 不修改文档，只输出评审报告。
- 不重复代码审查已覆盖的代码层 finding。
- 报告末尾追加 `<!-- design-review-stats: P0=N P1=N P2=N P3=N -->`。
- 将完整报告写入 `/tmp/mr-<project>-<mr_number>-design-review.md`，供 Step 5 整合。

### Spec-Conformance Review

找到 spec 时，在普通代码审查之外单独执行：

1. **RCT 对照**：逐行检查 Requirement-Code-Test triples，标记 code present / missing、test present / missing、validation command plausible / missing。
2. **Lifecycle 对照**：逐行核对 create/update/delete/unlink/reclaim/report/stats/cold-start/failure 的代码路径和测试。
3. **Touchpoint 对照**：对 feature bit / proto / enum / RPC / cache hook，检查声明、handler、fetch/cache、mutation hook、删除/回收和测试是否齐全。
4. **Boundary/error 对照**：检查 non-dir、root、foreign owner、out-of-range、missing、unlinked、invalid config 的服务层校验和测试。
5. **Runtime invariant 对照**：检查 COW commit boundary、snapshot same-window、overflow/saturation、cache notification order、异常路径回滚。
6. **Doc drift 对照**：grep follow-up / out-of-scope / 已实现 / 已确定 / TBD / 待确认，确认文档没有把后续项写成本 MR 验收。

元数据分片模块额外检查：
- 需要 routed shard 拥有对象的 mutating RPC，优先验证 `invalid_local_ino()` 语义；`invalid_ino()` 只能用于不校验 owner 的范围/类型检查。
- task 生命周期的 `do_prepare`、`handle_cancel`、`handle_apply`、`encode` 必须对称。
- 持久化更新必须先于 cache notification，例如先 `apply_update_*`，再 `on_feat_change` / cache hook。
- unlink/reclaim 必须清理 runtime state，或明确该 state 不归当前 feature 拥有。

将结果写入 `/tmp/<mode>-spec-conformance.md`，供 Step 5 整合。

## Step 4: Issue 根因分析（仅 MR 模式 + 有关联 Issue）

如果 Step 1 提取到关联 Issue 号：

1. 使用 `glab api projects/:fullpath/issues/<issue_number>` 获取 Issue 详情。
2. 分析：
   - 当前修改是否直接解决 Issue 描述的问题。
   - 修改是针对根本原因，还是只修复表象。
   - 是否可能引入新问题或副作用。
   - 是否存在更简洁高效的替代方案。
3. 将结论纳入最终 review 的 `Issue Root Cause Analysis`。

## Step 5: 汇总与发布

本步骤是终点动作。完成汇总、去重和 CRITICAL 交叉验证后，MR 模式立即发布 comment，不在发布前要求用户预览或确认。即使存在 CRITICAL，也照常发布；严重程度由 Stats 表展示。只有 GitLab API 返回错误时才向用户说明。

1. 合并所有模块 findings 和设计文档评审结果。
2. 去重：同一位置同一问题只保留一条。
3. 执行 CRITICAL 交叉验证：
   - 文件不存在：降级 NOTE，说明“文件未找到，疑似 working tree 漂移”。
   - 符号不存在：降级 NOTE，说明“符号未定位”。
   - 文件和符号都存在：保留 CRITICAL。
4. 按严重程度排序：CRITICAL -> MAJOR -> MINOR -> NOTE。
5. 整理为 Review 输出格式。
6. 若存在设计文档评审，将 `/tmp/mr-<project>-<mr_number>-design-review.md` 整段嵌入 `## Design Doc Review`；解析末行 stats，把 P0/P1 计数累加到 Stats 表的 CRITICAL/MAJOR 行，不重复列出 finding。
7. 若存在 spec-conformance 结果，将缺失行为、生命周期 stale state、owner 校验缺失等按严重程度并入主 findings，并额外输出 `## Spec Conformance` 表。

### MR 模式发布与回读验证

使用稳定参数发布 MR comment：

```bash
glab api --method POST projects/:fullpath/merge_requests/<mr_number>/notes -f body=<review_md>
```

不要用 `--input -` 传 JSON，避免 Content-Type 或转义导致 body 残缺。

发布后回读验证：

```bash
glab api projects/:fullpath/merge_requests/<mr_number>/notes/<note_id>
```

检查返回 body 长度。若小于提交内容的 80%，删除该 note 并重发一次；只重试一次，仍失败则报告用户。

发布完成后清理：

- `/tmp/mr-<project>-<mr_number>.patch`
- `/tmp/mr-<project>-<mr_number>-design-docs.txt`（如存在）
- `/tmp/mr-<project>-<mr_number>-design-review.md`（如存在）
- `/tmp/mr-splits-<project>-<mr_number>/`

### 本地模式输出

直接在终端输出 markdown review，并清理：

```bash
rm -f /tmp/local-review.patch
rm -rf /tmp/local-review-splits
```

## Review 维度

| 缩写 | 维度 | 关注点 |
|------|------|--------|
| D | 设计符合性 | 架构、数据结构选型、状态机设计、RAII 对称性 |
| I | 现有流程影响 | 对热路径、生命周期、已有接口的影响 |
| E | 异常处理 | 错误传播、资源泄漏、边界条件 |
| F | 流程流转 | 状态转换完整性、死锁/活锁、进度保证 |
| P | 性能影响 | 热路径开销、内存占用、算法复杂度、轮询路径 CPU 开销、周期任务频率、新增系统调用/分配/锁竞争 |
| Q | 代码质量 | 命名、选型、项目编码规范 |
| T | 测试覆盖 | Fix 是否有对应测试，适合 UT / Smoke / 长跑覆盖 |

T 维度仅在 MR 为 fix 类型时启用。

## 严重程度

| 级别 | 含义 | 响应 |
|------|------|------|
| CRITICAL | 数据安全或正确性问题 | 阻塞合入 |
| MAJOR | 可靠性、性能或 spec conformance 风险 | 强烈建议修复；必需行为缺失、生命周期状态可能陈旧、mutating RPC 缺 owner 校验时阻止继续实现下一阶段 |
| MINOR | 代码质量或可维护性问题 | 建议修复 |
| NOTE | 设计讨论或疑问 | 需要确认 |

## Review 输出格式

```markdown
# Code Review Summary

> MR !<mr_number> | N files, ~M lines | <date>
> Issue: #<issue_number> - <title>

## Stats

| Level | Count |
|-------|-------|
| CRITICAL | N |
| MAJOR | N |
| MINOR | N |
| NOTE | N |

## CRITICAL
### C1. <title>
**File**: `<file>:<line>` | **Dim**: <D/I/E/F/P/Q/T>
<description with code reference>
**Fix**: <suggestion>

## MAJOR
### M1. <title>
...

## MINOR
| # | Dim | Issue | File |
|---|-----|-------|------|

## NOTE
...

## Issue Root Cause Analysis
(MR 模式，有关联 Issue 时)

## Highlights
<positive feedback>

## Design Doc Review

> 仅当 MR 修改了 `docs/` 下的设计文档时生成。以下 P0/P1 已计入上方 Stats 的 CRITICAL/MAJOR 计数，不重复列出。

<嵌入设计文档评审报告>

## Spec Conformance

> 仅当找到 spec 或用户要求按 spec review 时生成。

| Spec row | Code | Test | Result | Notes |
|---|---|---|---|---|
| R-001 | yes/no | yes/no | PASS/FAIL | ... |

Missing RCT rows: N
Lifecycle gaps: N
Touchpoint gaps: N
Doc drift items: N

## Test Coverage (Fix MR only)

| # | Fix 点 | 已有测试 | 推荐方式 | 说明 |
|---|--------|----------|----------|------|
| T1 | `<file>:<line>` <fix 描述> | yes/no | UT / Smoke / 长跑 | <测试建议> |

**未覆盖 Fix 汇总**：N 个 fix 点中 M 个缺少测试覆盖，建议补充。

---
*Generated by Codex Code Review*
```

如果某个级别没有发现，省略对应 section。`Test Coverage` 仅在 `is_fix=true` 时生成；如果所有 fix 点都有测试覆盖，仍输出该 section 并标注全部 PASS。`Design Doc Review` 仅在检测出设计文档时生成；`Spec Conformance` 仅在找到 spec 或用户要求按 spec review 时生成。

## 横切关注点

- 资源泄漏：分配和释放是否配对，所有权转移是否明确。
- 计数器/引用计数：递增和递减是否在成功、失败、取消路径都正确。
- 状态机完整性：转换是否覆盖所有状态，是否存在死循环。
- 异步交互：回调是否在正确上下文执行，关闭后是否安全。
- 版本兼容：持久化格式变更是否前后兼容。
- RAII 对称性：Init/Fini、Open/Close、Register/Unregister 等操作是否对称。
- Fix 测试覆盖：修复是否有配套测试，测试类型是否匹配修复性质。

## Finding 示例

```markdown
### C1. Init/Fini 不对称：新增 timer_ 初始化但 Fini 中未销毁
**File**: `src/volume/volume_manager.cc:245` | **Dim**: D
Init() 新增 `timer_ = TimerManager::Create(...)`，但 Fini() 未销毁。timer_ 仍在运行时对象被释放，可能导致 use-after-free。
**Fix**: 在 Fini() 中按初始化逆序销毁 timer_，确保 timer 回调依赖的资源仍然有效。
```

## 注意

- 只审查代码，不修改代码。
- CRITICAL 和 MAJOR 必须引用具体行号和代码片段。
- 正向反馈必须保留在 `Highlights`。
- 所有 findings 整合为一条输出：MR comment 或终端 markdown。
