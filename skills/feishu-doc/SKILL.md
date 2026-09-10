---
name: feishu-doc
description: Guide for creating Feishu/Lark cloud documents via feishu-remote MCP or lark-cli. Triggers when calling mcp__feishu_remote__create_doc or mcp__feishu_remote__update_doc, or using lark-cli docs commands. Also use this skill whenever the user asks to create, write, or publish content to Feishu (飞书), even if they don't mention MCP explicitly — any request involving "写到飞书", "创建飞书文档", "发到飞书", "发布到飞书", "上传到飞书", "feishu doc", or similar phrases.
---

# Feishu Document Publishing Workflow

飞书文档发布流程入口。负责场景路由、发布前检查、执行、发布后验收。
具体文档操作能力由 `$lark-doc` 和 `$lark-whiteboard` skill 提供；若这两个 skill 不可用，直接使用 lark-cli 命令推进。

## Rule 0: 不支持原地替换，修订按"append vs 重发"决策

**最高优先级规则**（仅下文明确列出的 block 级精修例外）。飞书文档富文本元素（whiteboard、lark-table、mention-doc、callout）在 Markdown 往返（fetch → edit → update）中会不可逆损坏。

**绝对禁止：** `+update --mode replace_range / replace_all / overwrite`、`mcp__feishu_remote__update_doc` 非 append 模式、任何 fetch → 本地编辑 → update 的 round-trip。

**唯一允许的更新操作：**
```bash
lark-cli docs +update --doc "<url>" --mode append --markdown '<内容>'
```

### 飞书 docx 表格修订（重要例外）

飞书 docx 表格的 `<tr>` **不是独立 block，没有 block_id**。这意味着：

| 想做的事 | 能不能做 | 怎么做 |
|---------|---------|------|
| 追加 / 删除 / 重排表行 | ❌ 不能用 `block_insert_after` 单独插一行 tr | **只能用 `block_replace` 替换整张 `<table>`**——把整张表的完整 XML（含所有原行 + 新行）作为 `--content`，`--block-id` 指向 `<table>` 自身的 block_id |
| 改某个单元格的文字内容 | ✅ td 内的 `<p>` 有 block_id | 对该 `<p>` 用 `block_replace` |
| 给某个单元格加局部评论 | ✅ td / p 都可锚定 | `drive +add-comment --block-id <td 或 p 的 id>` |

**`block_replace` 整张表的副作用**：飞书重建表后，**表内所有 td / 段落的 block_id 全部失效**。如果之前对某个单元格加了局部评论，评论本身仍然存在，但锚定到的 block 已不存在——评论会变成"游离评论"，不再附着在表格上。

**工作流约束**：先改表 → 再加锚定到表内的评论；不要反过来。如果不得不在改表后保留原评论，需要在新表里手动重新锚定一次。

### `--content @file` 路径限制

`lark-cli docs +update --content @<path>` 只接受**相对当前 cwd 的路径**，不接受绝对路径。

```bash
# ❌ 报错：--file must be a relative path within the current directory
lark-cli docs +update ... --content @/tmp/payload.xml

# ✅ 先 cd 再用相对路径
cd /tmp && lark-cli docs +update ... --content @./payload.xml
```

适用于所有 `docs +update` / `docs +create` 等 shortcut 的 `--content @file` 形式。

### 修订策略决策

修订已有飞书文档时，先评估 diff 大小再决定走哪条路，不要无脑 append：

| 情况 | 推荐策略 | 理由 |
|------|---------|------|
| 单处小修（+1 行变更记录、一小段勘误） | **append 勘误章节** | 改动小，冗余可忽略 |
| 新增 1-2 个独立小章节 | **append 勘误章节** | 可接受的冗余 |
| 重构 / 整章重写 / 多节改动 | **整篇重发（create 新 doc）** | 多次 append 会让同名章节在正文和勘误里重复，视觉混乱 |
| 评审场景需要"当前最新版"入口 | **整篇重发** | 评审者不想翻勘误历史 |

**重发时：**
- 创建新文档，返回新 URL 给用户
- 旧文档由用户手动归档，skill **不得**代为删除或重命名
- 可在新文档变更记录里附上旧版链接作为引用（可选）

### append 勘误章节模板

决定 append 时按下列结构写，避免标题层级冲突和覆盖意图不清：

```markdown
## 勘误与更新（v0.X → v0.Y）

> 本章节为文档创建后的累计勘误。以下内容代表当前最新版本，**请以本章节为准**；正文中"<被覆盖章节 A>、<被覆盖章节 B>"的内容以此处覆盖。

### 变更记录（增量）

| 版本 | 日期 | 作者 | 变更说明 |
| ... |

### <被覆盖 H2 章节的降级替代>   ← 原文 H2 → 勘误里写为 H3

...

#### <被覆盖 H3 子标题的降级替代>   ← 原文 H3 → 勘误里写为 H4

...
```

**降级规则**：原文 H2 整节被覆盖时，在勘误里降为 H3；原文 H3 子标题被覆盖时降为 H4。避免勘误里的章节与原文同级标题冲突造成歧义。

## 发布流程

### Phase 0: 首发 vs 修订判断

在进入路由决策前，先判断当前场景：

- **首次发布**：创建新文档，走 Phase 1+。
- **修订已有文档**：先按 Rule 0 的"修订策略决策"表判断走 **append** 还是 **整篇重发**；确定后再进入 Phase 1+。

**策略确认规则**：修订场景保留 append vs 重发的策略批准要求。用户已明确指定同一文档的策略时直接执行；仅尚未决定、或新修订改变已批准策略时才确认，避免重复审批和章节冗余。

**豁免场景**（无须确认，直接 append）：
- 单行变更记录追加
- typo / 链接修复 / 单句勘误
- 用户已明确指示同一目标“直接 append”（按此策略执行）

以上之外的修订（包括新增章节、重构、整章改写、多节改动），必须满足策略批准后才写入；明确要求重发同一文档也是该策略的批准。等待批准时可继续读取原文、整理修订稿和检查结构。

### Phase 1: 路由决策

| 内容类型 | 路由目标 | 说明 |
|---------|---------|------|
| 纯文档（文字、表格、代码块、简单图表） | `$lark-doc` skill | 大多数场景 |
| 简单流程图、时序图、状态机 | Mermaid 代码块内嵌文档 | 飞书原生渲染 |
| 复杂架构图（多层嵌套、精细布局、需后续编辑） | `$lark-whiteboard` skill | DSL 画板，支持布局和样式 |
| 数据图表（柱状图、折线图、漏斗图等） | `$lark-whiteboard` skill | Mermaid 不支持 |

**Skill 不可用时的 fallback：** 如果 `$lark-doc` 或 `$lark-whiteboard` skill 未加载，自主使用 lark-cli 命令推进：
- 文档：`lark-cli docs +create`、`lark-cli docs +update`、`lark-cli docs +fetch`
- 画板：`lark-cli whiteboard +render`

不要因为 skill 不可用就中断流程或反复询问用户。

### Phase 2: 发布前检查

执行创建/更新前，逐项检查内容：

**链接检查：**
- 相对路径（`./src/foo.cpp`、`../design.md`）在飞书中**不会**生成可点击链接，只显示为纯文本
- 处理：转为行内代码引用（`` `src/foo.cpp` ``），或替换为完整 URL
- 外部链接（GitLab/GitHub）：确认 URL 完整

**转义检查：**
- 去掉所有 Markdown 反斜杠转义（`\_` → `_`、`\*` → `*`、`\\` → `\`）
- 飞书富文本引擎自行渲染，传入的 `\` 会被当作字面字符显示

**格式检查：**
- 有序列表：前必须有空行，项之间不能有空行，格式为 `数字. 空格 内容`
  - 错误：段落后紧跟 `1. xxx`（无空行）→ 飞书渲染为普通文本
  - 错误：列表项之间插入空行 → 列表断开为独立段落
  - 正确：段落后空一行，列表项连续无空行
- Mermaid 节点换行必须用 `<br/>`，不能用 `\n`（`\n` 会原样显示）

**长度检查：**
- 超长内容分段：先 `+create` 写入前半部分，再 `+update --mode append` 追加

### Phase 3: 执行

调用对应工具执行创建/更新。**执行时记录：**
- 返回的文档 URL 和 document token
- API 返回的所有 warnings — 如果 lark-cli 的 stdout/stderr 包含 `warning` 或 `⚠` 字样，提取完整信息留给 Phase 4 处理
- 执行状态（成功/失败/部分成功）

### Phase 4: 发布后验收

#### 回读确认

创建完成后，用 `lark-cli docs +fetch` 回读文档，检查：
- 标题和章节结构完整
- 表格渲染正确（列数、对齐）
- Mermaid 语法正确（无原样展示的代码块）
- 无意外的反斜杠或格式错乱
- **append 场景专项**：grep 勘误章节里每个 H3/H4 标题，看正文中是否已有同名标题；如有，向用户说明重复位置，说明"勘误章节覆盖同名章节"的读法约定，并在下次重大改版时建议改走整篇重发

**发现问题时：** 向用户报告具体差异，不要自动尝试修复（避免在原文档上叠加更多 append 造成混乱）。如果问题可通过 append 勘误章节解决，先征得用户同意。

#### Warning 处理

**API 返回的 warning 必须作为正式结果处理，不允许静默忽略。**

- 无效链接 warning → 标注哪些链接需要用户手动修复
- 格式降级 warning → 说明哪些元素未能完整渲染
- 其他 warning → 原文报告并说明影响

#### 结果汇报

```
文档已创建：<URL>     （首发）
或
文档已更新（append 勘误）：<URL>     （修订）
或
文档已重发（新 URL）：<新 URL>；旧版请用户归档：<旧 URL>     （整篇重发）

[如有 warning]
注意以下问题：
- <warning 描述及影响>
- <需要用户手动处理的事项>

[如 append 后产生同名章节冗余]
注意：本次 append 的 <章节名> 在正文中已存在同名章节（内容以勘误为准）；
建议下次重大改版时走整篇重发，避免冗余累积。
```
