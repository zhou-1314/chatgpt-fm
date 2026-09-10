# EP48 | OpenAI 开源隐私过滤器：小模型本地运行，PII 检测达到业界顶尖水准

- 音频文件：`content/openai/research/audio/2026-04-22-Introducing OpenAI Privacy Filter.mp3`
- 时长：23 分 46 秒

## Shownotes（复制到小宇宙）

本期我们拆解 OpenAI 在二〇二六年四月发布的 Privacy Filter——一个开源、可本地运行的个人敏感信息检测模型。它以十五亿参数打出顶级 F1 成绩，支持十二万八千 token 的长上下文，覆盖姓名、日期、账号、密码等八类 PII，Apache 2.0 协议商用友好，对需要处理用户数据的 AI 工程师来说，是一个可以立刻集成进训练流水线、日志管道和合规流程的实用工具。

- 传统规则匹配为何永远解决不了"日期"这个类别：PII 检测需要上下文理解的根本原因
- Privacy Filter 的核心架构：双向 token 分类模型 + 受限维特比 span 解码，单次前向传播完成全部标注
- 八个 PII 类别的设计逻辑，以及格式不固定的项目编号为何能被识别为 account_number
- F1 97.43% 背后的故事：他们如何发现并修正了标准测评集本身的标注错误
- 少量数据微调让 F1 从 54% 跳升至 96%，领域适配成本极低
- 工程师实战落地：五个最适合的场景、配置技巧，以及中文数据的现实局限

---

原文：Introducing OpenAI Privacy Filter
链接：https://openai.com/index/introducing-openai-privacy-filter
发表时间：2026-04-22
本期解读由模型（claude-sonnet-4-6）生成，音频由 edge-tts 合成。
