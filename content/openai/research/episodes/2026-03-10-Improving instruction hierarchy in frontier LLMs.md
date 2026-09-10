# EP51 | 指令层级失效时 AI 会听谁的？OpenAI 用强化学习给模型立规矩

- 音频文件：`content/openai/research/audio/2026-03-10-Improving instruction hierarchy in frontier LLMs.mp3`
- 时长：23 分 56 秒

## Shownotes（复制到小宇宙）

OpenAI 今年三月发布了一篇重要的安全研究，专门解决"AI 同时收到多方指令、互相冲突时该听谁的"这个问题。他们构建了一个叫做 IH-Challenge 的强化学习训练数据集，训练出的模型不仅在指令层级判断上大幅提升，还顺带改善了安全可操控性和 prompt 注入抵抗力，且核心能力没有明显下滑。

- 什么是指令层级：System、Developer、User、Tool 四层优先级体系，以及它为什么是 AI 安全的基石
- 强化学习训练指令层级的三个经典陷阱：任务混淆、裁判不可靠、过度拒绝捷径
- IH-Challenge 数据集如何用"简单可验证、无捷径"三个原则绕过这些陷阱
- GPT 五 Mini-R 的实测数字：TensorTrust 开发者对用户场景提升 15 个百分点，过度拒绝问题提升 21 个百分点
- 安全的两个连带收益：safety steerability 和 prompt injection 抵抗力为何能同时改善
- 对工程师的实践建议：系统 prompt 写法、agent 系统安全架构、以及一个尚未被解决的研究空白

---

原文：Improving instruction hierarchy in frontier LLMs
链接：https://openai.com/index/instruction-hierarchy-challenge
发表时间：2026-03-10
本期解读由模型（claude-sonnet-4-6）生成，音频由 edge-tts 合成。
