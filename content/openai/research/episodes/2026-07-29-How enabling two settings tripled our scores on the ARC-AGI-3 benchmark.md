# EP37 | 两个设置让得分翻三倍：基准测试到底在测什么

- 音频文件：`content/openai/research/audio/2026-07-29-How enabling two settings tripled our scores on the ARC-AGI-3 benchmark.mp3`
- 时长：23 分 45 秒

## Shownotes（复制到小宇宙）

本期我们深度拆解 OpenAI 在二〇二六年七月发表的一篇研究文章：他们发现，只需开启两个 API 设置——保留推理和压缩——就让 GPT 五点六 Sol 在 ARC-AGI-3 基准测试上的得分提升到原来的三倍，同时输出 token 减少了六倍。这不只是一个调参技巧，它揭示了一个行业共性问题：我们每天看的那些基准分数，到底在测什么？

- 什么是 ARC-AGI-3：要求 AI 在没有说明书的情况下探索 2D 游戏、自己推断规则的通用智能基准测试
- 低分背后的真相：评测框架丢弃了模型的私密推理消息，还用滚动截断不断删除早期记忆
- 保留推理的意义：让模型在每次操作后依然能看到自己之前的思考，而不是每步从零重建
- 压缩 vs 截断：压缩通过智能摘要保留关键信息，截断只是粗暴地删掉最老的内容
- 实验结果：开启两个设置后，得分约提升三倍，输出 token 减少六倍
- 对开发者的实践建议：改用 Responses API、开启推理保留、用压缩代替滚动截断

---

原文：How enabling two settings tripled our scores on the ARC-AGI-3 benchmark
链接：https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores
发表时间：2026-07-29
本期解读由模型（claude-sonnet-4-6）生成，音频由 edge-tts 合成。
