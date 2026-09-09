# EP11 | 决策瀑布：OpenAI 如何让 Codex 和 Sora 永不断流

- 音频文件：`/workspace/algorithm/zhouwg_project/chatGPT-fm/chatgpt-fm/content/openai/engineering/audio/2026-02-13-Beyond rate limits - scaling access to Codex and Sora.mp3`
- 时长：25 分 22 秒

## Shownotes（复制到小宇宙）

本期我们深读 OpenAI 工程团队发表的技术文章《Beyond rate limits: scaling access to Codex and Sora》，作者 Jonah Cohen 详细拆解了 OpenAI 为何放弃传统速率限制和纯按量计费方案，转而自建一套实时混合访问控制系统，并深入讲解了其中的"决策瀑布"模型、三层数据集架构与可证明正确的计费哲学。这篇文章对所有在构建 AI 产品、后端计费或用量管理系统的工程师都有极高参考价值。

- 速率限制与按量计费各有缺陷，OpenAI 选择自建混合系统
- "决策瀑布"模型：把访问控制从二元判断变为多层顺序扣减
- 为何放弃第三方计量平台：实时性要求与深度可观察性缺一不可
- 三层独立数据集：用量事件、计费事件、余额更新，支撑可证明的计费正确性
- 幂等键与原子事务是分布式计费系统的基础安全阀
- 同步决策加异步结算，超支时自动退款，用户信任优于严格执行

---

原文：Beyond rate limits: scaling access to Codex and Sora
链接：https://openai.com/index/beyond-rate-limits
发表时间：2026-02-13
本期解读由模型（claude-sonnet-4-6）生成，音频由 edge-tts 合成。
