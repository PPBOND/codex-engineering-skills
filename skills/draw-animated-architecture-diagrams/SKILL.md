---
name: draw-animated-architecture-diagrams
description: Create source-grounded architecture and workflow animations as self-contained interactive HTML, with nested ownership, an overview plus focused flow pages, manual previous/next navigation, fixed explanations and deterministic packets on arrows. Use for 动态架构图、流程动态图、可播放 I/O 链路、按参考图制作 HTML 图册. For a static-only diagram use draw-layered-engineering-diagrams; this skill is not a general dashboard or telemetry builder.
---

# 架构与流程动态图

把系统结构与核心流程画成可以持续播放、手动切换的 HTML 图册。复用本 skill 的模板与检查器，先把静态构图画清楚，再让流向动起来。

## 默认交付与交互

- 交付自包含 HTML、唯一源配置 `config.json` 和实际浏览器预览。需要 PNG 时，从同一份图形配置或 SVG 导出。
- 第一页是整体架构；后续每页只展开一条相关流程，包括该流程必要的分支与提前返回。
- 当前页持续播放；只在用户点击“上一张 / 下一张”时切换。流程说明、标题、步骤号和日志类说明保持固定。
- `window.seek(t)` 接收秒数，决定所有光点位置；正常播放由 `requestAnimationFrame` 驱动，`?manual` 停止自动时钟，供确定性检查与截图。遵从浏览器的减少动态效果偏好。
- 光点表示方向，时长不代表延迟。示例 key、区间、计数应标为示例；性能或容量数字要有来源。

## 工作步骤

1. **读参考与源事实。** 按 [构图规范中的参考图索引](references/layout.md) 查看原始截图与已完成的动态 HTML 截图：总览对照整体架构与 HTML 总览，流程页对照单次 I/O 与 HTML 流程，交互呈现再看 HTML 示例。追踪公开入口、对象归属、异步提交/完成、结果类型和持久化顺序；先明确每页要解释的问题。
2. **列页，再画对象。** 保持“总览 → 独立流程”的阅读顺序。整体 I/O 分析还应核对恢复、关闭、销毁、后台维护、checkpoint/GC 等实际存在的路径。数量由源码与请求范围决定。
3. **编辑配置。** 从 [示例配置](examples/example-config.json) 起步，按 [配置说明](references/config-schema.md) 填入真实模块与字段。每页单独选择布局，紧凑嵌套、纵向主路径或独立侧路按语义决定。
4. **生成 HTML。** 用 `scripts/build_panel.py` 嵌入配置。模板已支持嵌套组、字段条、表格、逻辑区间、唯一步骤号、条件箭头与光点；常规任务只编辑配置。
5. **运行与检查。** 使用当前可用的浏览器工具打开 HTML；若工具不接受本地文件协议，通过仅绑定 `127.0.0.1` 的临时 HTTP 服务预览。按 [浏览器验收](references/verification.md) 执行检查器、观察每页，修正配置后重建。
6. **交付。** 链接 HTML 与预览，说明源码依据和实际验证范围。修改既有图册时保留无关页；同时刷新受影响的静态图、预览和打包文件。

```sh
python <skill>/scripts/build_panel.py --config config.json --out architecture.html
```

构建脚本同时把 `check-panel.js` 放到 HTML 旁边。生成过程仅使用 Python 3.10+ 标准库，原生支持 Windows/Linux/macOS；页面在浏览器中运行，不依赖 CDN、构建框架或服务端。

## 不可省略的图形契约

- 每个步骤号在一张图内只出现一次。用 `step` 关联动作，用 `badge` 选择唯一显示编号的主箭头；其他关联线靠路径和简短动作标签说明。
- 正常路径用实线；条件、控制、回退与提前返回用虚线并说明条件或结果。独立接口保持独立分支，提前返回出口靠近判断位置。
- 正文卡片展示具体输入、状态、触发条件、输出或完成条件。纯标题节点收紧为条带；callback 与完成节点应体现实际结果类型和必要字段。
- 先布父边界与子组件，再布连接线。避免穿框、穿标题、线与线交叉/重合、密集平行线和多余折返；留出箭头与标签的空间。
- 动画保持完整图形、正文和唯一编号可读。页面切换负责文字，时间函数只负责运动；不用动画时钟修改流程说明。
- 自动几何检查与逐图目视检查都要做。检查通过只能证明其覆盖的条件，不能代替对结构、美观与源码语义的判断。

## 资源与维护

- 通用示例截图指导绘图：[HTML 总览](assets/reference-html-overview.jpg)、[HTML 详细流程](assets/reference-html-flow.jpg)、[HTML 交互示例](assets/reference-html-interaction.png)。分别展示教学模型的总览、写入和命中/缺页页面，不代表某个生产系统。
- `assets/panel-template.html`：由本次 FlexDB 图册提炼的通用模板。
- `scripts/build_panel.py`、`scripts/check_panel.js`：嵌入生成与浏览器验证。
- `examples/example-config.json`：教学用三页示例，包含总览、写入和命中/缺页分支。
- [来源与许可](references/provenance.md)：live-panel 固定布局、纯时间函数和逐帧验证方法的来源；保留页面中的方法署名。

修改模板或检查器后，至少用示例配置生成并在浏览器运行一次完整检查；已有真实图册适合作为第二个回归样本。构建脚本的检查用 `python -m unittest discover -s <skill>/scripts -p 'test_*.py'`。
