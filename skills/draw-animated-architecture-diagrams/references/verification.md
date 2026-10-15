# 浏览器验收

先构建：

```sh
python <skill>/scripts/build_panel.py --config config.json --out output/architecture.html
```

打开输出，等待 `window.__ready === true`。用已授权的浏览器开发工具执行同目录 `check-panel.js`。通过 localhost HTTP 预览时，可在开发者执行环境中运行：

```javascript
fetch('check-panel.js').then(r => r.text()).then(source => (0, eval)(source))
```

读取该结果；异常或错误意味着检查未通过。检查器返回总览，并覆盖所有图页的124个时间点：

- 步骤号唯一、完整，节点有正文，组件数量与页面配置一致。
- 子对象位于声明的父边界内，连线端点附着正确。
- 正交线之间没有交叉、重合或共用端点，路径避开卡片与标题。
- 标签不盖住连接线；节点文字不越界。
- 动画不切换页面或正文，前后按钮边界正确，光点运动且 `seek(t)` 可重复。

再检查每页实际渲染效果，重点看缩放后的文字、卡片留白、路径方向、折返、平行线间距、箭头、数字与标签位置。程序检查不能判断图是否直观，也不能判断源码语义。

验证窄窗口的按钮可见、SVG 在自己的容器内滚动，正文仍可阅读；用 Enter/Space 激活导航。保存实际页面截图作为预览。HTML 修改后，若 PNG 或截图属于交付物，必须重新导出受影响页。

生成脚本与模板自测：

```sh
python -m unittest discover -s <skill>/scripts -p 'test_*.py'
```

构建成功只证明嵌入过程完成；只有实际浏览器检查成功才能报告交互验证通过。保留当次源码/配置依据，说明未验证的协议、导出格式或平台。
