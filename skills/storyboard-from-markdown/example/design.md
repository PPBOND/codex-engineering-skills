# AI 分布式存储系统设计说明

本文档用于生成一组连续的设计图，最后汇总成 PDF。

## 背景

目标：说明 AI 训练场景中的 IO 痛点。

要求：
- 体现 GPU 集群、训练任务、数据加载、checkpoint 写入
- 强调元数据热点、随机小读、TB 级大写入
- 页面风格要简洁、企业技术感、蓝白配色

## 系统架构

目标：展示整体架构。

要求：
- 包含 Client、Metadata Service、Storage Nodes、Cache Layer
- 用箭头表示请求与数据流
- 尽量图标化

## 数据流

目标：展示读写流程。

要求：
- 显示 read path 与 write path
- 标注 cache hit / miss
- 强调 write-back 和 consistency tradeoff

## 关键设计点

目标：展示设计亮点。

要求：
- 列出 Tier-0 cache
- append-only log structured backend
- directory sharding
- polling / RTC
- QoS isolation

## 总结

目标：做一页总结页。

要求：
- 用简洁方式回顾方案价值
- 适合放在 PDF 最后一页
