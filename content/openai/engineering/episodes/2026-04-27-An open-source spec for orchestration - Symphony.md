# EP9 | 把工单变成指挥中心：OpenAI 用一份规范文档让 coding agent 自主运转

- 音频文件：`/workspace/algorithm/zhouwg_project/chatGPT-fm/chatgpt-fm/content/openai/engineering/audio/2026-04-27-An open-source spec for orchestration - Symphony.mp3`
- 时长：21 分 55 秒

## Shownotes（复制到小宇宙）

本期聊的是 OpenAI 工程团队于二零二六年四月发布的一篇实战总结：他们如何构建了一个叫 Symphony 的 agent 编排系统，把 Linear 这样的项目管理工具变成了 coding agent 的调度大脑，让某些团队的 PR 合并量在三周内增长了五倍。更出人意料的是，Symphony 的核心不是一套复杂框架，而是一个叫做 SPEC.md 的 Markdown 规范文档。

- 为什么工程师管理 coding agent 会撞上"注意力天花板"，三到五个会话是临界点
- Symphony 的核心设计：让 issue tracker 变成 agent 的状态机，彻底解耦"任务"和"会话"
- DAG 并行执行：agent 如何根据依赖关系自动排队开工，以 React 升级依赖 Vite 迁移为例
- SPEC.md 哲学：为什么一份写得好的规范文档，比一套复杂框架更有生命力
- Codex App Server 无界面模式：JSON-RPC 接口让 agent 编排真正可编程
- 实践指南：上手 Symphony 需要哪些基础设施、什么任务适合委托、review 文化怎么调整

---

原文：An open-source spec for orchestration: Symphony
链接：https://openai.com/index/open-source-codex-orchestration-symphony
发表时间：2026-04-27
本期解读由模型（claude-sonnet-4-6）生成，音频由 edge-tts 合成。
