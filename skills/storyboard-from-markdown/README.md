# Storyboard From Markdown Skill

把 Markdown 文档整理成“先提炼核心信息，再纯模型出图”的工作流：

1. 解析文档
2. 生成页面 spec
3. 导出 prompt pack
4. 用内置模型逐页出图
5. 合并成 PDF

这个版本不再依赖 API 出图，也不再局限于设计文档。

## 目录

```text
storyboard_from_markdown_skill/
├── SKILL.md
├── README.md
├── requirements.txt
├── scripts/
│   ├── parse_markdown.py
│   ├── build_story_spec.py
│   ├── render_prompt_pack.py
│   ├── images_to_pdf.py
│   └── run_pipeline.py
├── example/
│   ├── design.md
│   ├── general.md
│   └── config.example.json
└── output/
```

## 依赖安装

建议 Python 3.10+。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 最简运行

```bash
python scripts/run_pipeline.py \
  --input-md example/design.md \
  --config example/config.example.json
```

或直接对通用 Markdown 做核心信息提炼：

```bash
python scripts/run_pipeline.py \
  --input-md example/general.md
```

输出结果会在：

```text
example/storyboard/design/
├── parsed_outline.json
├── story_spec.json
├── prompt_pack.md
├── storyboard_run.json
└── images/
```

接下来按 `prompt_pack.md` 用内置模型逐页出图，保存到同目录下的 `images/`，文件名保持：

```bash
001_cover.png
002_xxx.png
003_xxx.png
...
```

全部图片就位后，合并 PDF：

```bash
python scripts/images_to_pdf.py \
  --input-dir example/storyboard/design/images \
  --output example/storyboard/design/design_storyboard.pdf
```

## 配置说明

`example/config.example.json` 里的主要字段：

- `generate_cover`: 是否自动生成封面
- `style`: 全局风格描述
- `max_pages`: 最多生成多少页，避免文档太长时一次性生成过多
- `selection_mode`: `auto` / `core` / `all`
- `core_page_target`: 提炼核心页时最多保留多少个章节
- `auto_core_threshold`: 章节数不超过这个阈值时，`auto` 模式默认全部保留
- `include_titles`: 只保留指定章节，适合长文档先出核心页
- `skip_titles`: 排除不重要章节，例如“变更记录”“错误码”“可观测性”
- `title_visual_types`: 按标题强制指定页面类型，避免自动判断跑偏
- `title_hint_overrides`: 按标题直接覆写页面要点，适合长文档核心页
- `title_prompt_extras`: 给单页补额外提示
- `include_page_number_hint`: 是否在 prompt 中保留页码提示
- `default_visual_type`: 自动判断失败时的兜底页面类型

## 输出位置

默认不再把中间文件放到 skill 目录。

- 默认输出目录：`<文档目录>/storyboard/<文档名>/`
- 如果显式传 `--workdir`，则按指定路径输出
- `storyboard_run.json` 会记录输入、配置、过程文件、图片目录和建议 PDF 路径

## 推荐做法

任意 Markdown 通常都不适合把所有章节都做成图。更实用的做法是：

1. 先保留封面和 4-8 个核心页
2. 用 `title_visual_types` 固定关键页的表达方式
3. 非关键信息直接跳过，不单列成页

不同类型文档，优先保留的内容通常是：

- 摘要 / 结论
- 背景 / 目标 / 范围
- 关键决策 / 方案 / 架构
- 流程 / 计划 / 时间线
- 风险 / 问题 / 对比
- 行动项 / Next steps / Owner

通常不优先出图：

- Changelog
- 兼容性
- 附录
- 错误码
- 可观测性明细
- 原始日志
- 长参考资料

例如：

- `评审摘要` -> `summary slide`
- `设计方案` -> `architecture diagram`
- `核心流程` -> `flow diagram`
- `接口定义` -> `API contract slide`
- `UT 和 Integration 用例设计` -> `test plan slide`
- `里程碑计划` -> `timeline slide`
- `风险与阻塞` -> `risk matrix`
- `行动项` -> `action checklist`

## 推荐落地方式

如果你是给 Codex / 内部 agent 用：

- 把整个目录作为一个 skill / tool package
- 让 agent 读 `SKILL.md`
- 先跑 `scripts/run_pipeline.py`
- 再按 `prompt_pack.md` 用内置模型逐页出图
- 最后用 `scripts/images_to_pdf.py` 合并

## 可扩展方向

- 支持从 Markdown front matter 读取风格参数
- 支持自动生成“核心页建议”
- 支持目录页 / 页脚 / 页码
- 支持为每页生成讲解摘要
