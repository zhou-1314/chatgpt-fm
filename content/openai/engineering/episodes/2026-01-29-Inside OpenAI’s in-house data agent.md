# EP14 | OpenAI 内部数据 agent 全拆解：七层上下文如何让 AI 真正读懂企业数据

- 音频文件：`/workspace/algorithm/zhouwg_project/chatGPT-fm/chatgpt-fm/content/openai/engineering/audio/2026-01-29-Inside OpenAI’s in-house data agent.mp3`
- 时长：24 分 37 秒

## Shownotes（复制到小宇宙）

OpenAI 在内部用 GPT 五点二、Codex、Evals API 和 Embeddings API 构建了一个专属数据 agent，让三千五百名员工能用自然语言在几分钟内从六百拍字节、七万个数据集里得到可靠答案。本期节目拆解这个 agent 的七层上下文体系、自我纠错推理机制、黄金 SQL 评估方法，以及团队在构建过程中总结的三条关键工程教训。

- 为什么元数据和文档不够：表的真正含义藏在生产它的管道代码里，而不是列名里
- Codex 如何读懂数据管道代码，自动区分看起来相似但含义截然不同的表
- 记忆系统专门用于积累"踩坑知识"，让 agent 从每次纠正中进化
- 黄金 SQL + Evals API 评估方案：用模型判断结果等价性，而非字符串匹配
- 工程教训：精简工具集、高层级指引优于步骤规定、代码胜过文档
- 对工程师和数据团队的实践建议：从哪一层开始、如何避免常见陷阱

---

原文：Inside OpenAI’s in-house data agent
链接：https://openai.com/index/inside-our-in-house-data-agent
发表时间：2026-01-29
本期解读由模型（claude-sonnet-4-6）生成，音频由 edge-tts 合成。
