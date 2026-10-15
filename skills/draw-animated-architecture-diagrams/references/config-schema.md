# 配置格式

直接参考 `examples/example-config.json`。配置只包含可 JSON 序列化的数据；默认画布固定为 2000×1400，位置单位均为画布像素。

## 根对象

- `title`：浏览器标题及工具栏名称。
- `subtitle`：工具栏副标题。
- `sourceNote`：页脚说明源码或教学示例的性质。
- `pages`：非空有序列表，第一项是总览。

## 每页

`id`、`short`、`title`、`subtitle`、`summary`、`note` 是文本。`overview` 为布尔值；总览的 `steps` 为 `[]`。`example: true` 在图例中标明符号值与区间是示例。

- `groups`：父边界先于子边界。每项包含 `id,title,x,y,w,h,color`；`parent` 指向所属 group。可选 `fill` 为六位十六进制颜色，`titleX` 调整标题横坐标以避让路线。
- `nodes`：每项包含 `id,title,lines,x,y,w,h,color`；`parent` 可选。`lines` 是正文行数组。可选 `titleSize`（默认22）、`bodySize`（默认17）。高度不足80的节点用作纯标题条带；较高卡片必须有正文、字段或 widget。
- `steps`：顺序说明，每项 `{who,m,g}` 分别表示执行者、动作和产出/完成条件。编号由数组顺序生成，从1开始。
- `edges`：有向连接，格式见下节。

`color` 使用 `blue,green,orange,purple,gray`。每页 node/group 的 id 唯一，采用字母开头的字母、数字、下划线或短横线组合。

## 数据图形

节点可选 `fields: ["field A", "field B"]`，表示底部并列字段。较复杂图形使用 `widget`，并把 `lines` 留空，避免正文重复。

- 表格：`{"kind":"table","rows":[["字段","值"],["状态","ready"]]}`。
- 条带：`{"kind":"strip","cells":[{"label":"Header","weight":1,"color":"blue"},{"label":"Value","weight":3,"color":"orange"}]}`。
- 区间：`{"kind":"ranges","axis":[0,4,8],"rows":[{"label":"范围","cells":[{"label":"已覆盖","weight":4,"color":"green"},{"label":"未决","weight":4,"color":"gray"}]}]}`。

`weight` 为正值，决定格子宽度。区间 axis 严格递增，首末值定义刻度范围，各行格子覆盖整个范围。可选 `crossed: true` 在失效数据格子内画删除线。文字宽度与行高需经浏览器验证。

## 连接线

每项包含：

```json
{
  "from": "input", "to": "writer",
  "points": [[440,340],[440,500]],
  "color": "blue", "dashed": false,
  "step": 1, "badge": true, "label": [440,420]
}
```

`points` 是正交折线，首尾落在对应节点边界。不同线使用不同端口和通道。总览使用 `step: 0, badge: false`；详细页每条边关联有效 step，同一步只有一条边的 badge 为 true。`label` 是数字圆点中心，即使 badge=false 也保留该字段以便统一编辑。

条件可加 `caption` 与 `captionAt: [x,y]`，后者为文本基线中心。`dashed` 表示条件/控制/回退/提前返回；正常路径设为 false。条件的完整语义同时写进节点结果或步骤，不能只靠颜色猜测。

## 时间与作用域

所有静态信息来自当前页配置；动画只改变光点坐标。`window.seek(t)` 可以先跳到其他时间再回到 t，图形应完全一致。光点同时流动是示意，不代表独立分支同时实际发生或系统有测得的延迟。
