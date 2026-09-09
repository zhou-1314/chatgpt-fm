# EP13 | 解锁 Codex 执行框架：OpenAI 如何为 AI 编程智能体构建稳定集成协议

- 音频文件：`/workspace/algorithm/zhouwg_project/chatGPT-fm/chatgpt-fm/content/openai/engineering/audio/2026-02-04-Unlocking the Codex harness - how we built the App Server.mp3`
- 时长：28 分 20 秒

## Shownotes（复制到小宇宙）

本期我们深度拆解 OpenAI 工程博客上的一篇技术文章，讲 OpenAI 是如何为 Codex——他们的 AI 编程智能体——构建 App Server 这套统一中间层的。从最初为 VS Code 插件临时搭的 JSON-RPC 桥，到如今支撑网页端、桌面端、IDE 插件和命令行的稳定平台级协议，背后有一套值得所有 AI 应用工程师借鉴的架构思路。

- - 文章来自 OpenAI 技术人员 Celia Chen，发表于二〇二六年二月，彼时 AI 编程智能体正进入大规模商业落地阶段
- - Codex harness 是什么：包含智能体循环、线程持久化、配置认证、工具沙箱执行的完整引擎
- - App Server 的三个核心协议原语：Item（原子输入输出单元）、Turn（单次智能体工作单元）、Thread（持久会话容器）
- - 双向 JSON-RPC over stdio 的设计哲学：为何不用 HTTP，以及向后兼容如何让 Xcode 这样的合作伙伴解耦发版周期
- - 五种集成方式横向比较：MCP 服务器、通用智能体协议、App Server、CLI 自动化、TypeScript SDK，各自的适用场景和权衡
- - 对听众的实践启示：如何快速上手 App Server 集成，三个最容易踩的坑，以及远程执行能力的长远意义

---

原文：Unlocking the Codex harness: how we built the App Server
链接：https://openai.com/index/unlocking-the-codex-harness
发表时间：2026-02-04
本期解读由模型（claude-sonnet-4-6）生成，音频由 edge-tts 合成。
