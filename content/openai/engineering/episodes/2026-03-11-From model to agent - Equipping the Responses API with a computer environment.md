# EP22 | 从模型到真正会干活的 AI：OpenAI 如何为 Responses API 装上执行引擎

- 音频文件：`content/openai/engineering/audio/2026-03-11-From model to agent - Equipping the Responses API with a computer environment.mp3`
- 时长：25 分 26 秒

## Shownotes（复制到小宇宙）

本期我们拆解一篇 OpenAI 工程博客文章，主题是如何通过 shell 工具、托管容器、上下文压缩和技能包，把 Responses API 从问答接口升级成端到端的任务执行平台。发表于 2026 年 3 月，这套架构描述了"从模型到智能体"的完整工程思路，距今约六个月，对今天的 agent 开发者依然有很强的参考价值。

- 为什么"用模型"和"用智能体"是两种本质不同的 AI 使用模式
- Shell tool 是什么，为什么比旧版代码解释器的能力宽泛得多
- Responses API 的 agent 执行循环如何运作：并行执行与输出上限控制
- Context compaction 如何解决长任务的上下文溢出问题，以及 Codex 自举开发的精彩故事
- 容器工作空间的三层结构：文件系统、SQLite 数据库、受控网络访问与密钥注入
- Agent skills 如何把重复性工作流变成可复用、版本可控的标准操作手册

---

原文：From model to agent: Equipping the Responses API with a computer environment
链接：https://openai.com/index/equip-responses-api-computer-environment
发表时间：2026-03-11
本期解读由模型（claude-sonnet-4-6）生成，音频由 edge-tts 合成。
