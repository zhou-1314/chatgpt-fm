# EP10 | WebSocket 让 AI 智能体提速四成：OpenAI Responses API 的架构演进实录

- 音频文件：`/workspace/algorithm/zhouwg_project/chatGPT-fm/chatgpt-fm/content/openai/engineering/audio/2026-04-22-Speeding up agentic workflows with WebSockets in the Responses API.mp3`
- 时长：30 分 30 秒

## Shownotes（复制到小宇宙）

本期我们深度拆解一篇来自 OpenAI 工程团队的技术博文，聊聊他们如何通过引入 WebSocket 持久连接，把智能体工作流的端到端延迟砍掉了整整四成。这背后不是简单地"换个协议"，而是一次从架构层面重新思考 AI API 设计的工程实践。

- WebSocket 如何解决 HTTP 模式下每次请求都要重处理完整对话历史的冗余问题
- 为什么推理速度从每秒 65 个 token 提升到近 1000 个 token 之后，API 开销突然成了新瓶颈
- OpenAI 的原型版本 vs 生产版本：技术最优解和开发者友好性之间如何取舍
- 连接级内存缓存缓存了什么，为什么能让安全分类器和 tokenization 都变快
- Vercel、Cline、Cursor 的真实生产数据：最高 40% 的延迟下降意味着什么
- 开发者迁移 WebSocket 模式需要注意哪些坑：重连逻辑、状态依赖、连接复用边界

---

原文：Speeding up agentic workflows with WebSockets in the Responses API
链接：https://openai.com/index/speeding-up-agentic-workflows-with-websockets
发表时间：2026-04-22
本期解读由模型（claude-sonnet-4-6）生成，音频由 edge-tts 合成。
