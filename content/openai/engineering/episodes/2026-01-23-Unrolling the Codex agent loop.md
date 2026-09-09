# EP15 | OpenAI 首次公开：生产级 AI agent 循环的工程内幕

- 音频文件：`/workspace/algorithm/zhouwg_project/chatGPT-fm/chatgpt-fm/content/openai/engineering/audio/2026-01-23-Unrolling the Codex agent loop.mp3`
- 时长：29 分 28 秒

## Shownotes（复制到小宇宙）

本期节目深度拆解 OpenAI 工程博客文章《Unrolling the Codex agent loop》，这是 Codex 团队首次系统性地公开构建世界级软件 agent 过程中积累的硬核工程经验。我们将从最基础的 agent 循环结构讲起，逐层深入到 prompt 构建、流式响应处理、prompt 缓存优化、以及上下文窗口管理策略，并结合实际工程场景给出可以直接上手的操作建议。

- - Codex agent loop 的完整运转机制：从用户输入到最终响应的每一个环节
- - Responses API 的 prompt 构建细节：instructions、tools 与 input 三字段的工程设计
- - 为什么选择不用 previous_response_id：无状态设计与零数据留存合规的权衡
- - Prompt caching 如何把推理成本从平方降到线性，以及 MCP 工具顺序不一致导致缓存失效的真实 bug
- - /responses/compact 自动压缩接口如何解决上下文窗口管理难题
- - 六条可直接应用于你自己 agent 项目的工程实践建议

---

原文：Unrolling the Codex agent loop
链接：https://openai.com/index/unrolling-the-codex-agent-loop
发表时间：2026-01-23
本期解读由模型（claude-sonnet-4-6）生成，音频由 edge-tts 合成。
