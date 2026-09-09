# EP12 | 零行手写代码、百万行产品：OpenAI 的 Agent 工程方法论

- 音频文件：`/workspace/algorithm/zhouwg_project/chatGPT-fm/chatgpt-fm/content/openai/engineering/audio/2026-02-11-Harness engineering - leveraging Codex in an agent-first world.mp3`
- 时长：26 分 55 秒

## Shownotes（复制到小宇宙）

OpenAI 内部工程团队在五个月内，带着"零行手写代码"的极端约束，用 Codex agent 构建出了一款拥有真实日常用户的产品，仓库规模达到大约一百万行代码。这篇文章总结了他们在这个过程中积累的工程方法论——如何设计文档结构、如何用架构约束驯服 agent、如何让 agent 自己做质量验证。如果你正在认真思考如何在团队里落地 AI 驱动开发，而不只是把它当代码补全工具，这是目前为止最有操作价值的一手工程经验之一。

- 核心哲学：人类掌舵，Agent 执行——工程师的产出从写代码变成了设计环境、表达意图、构建反馈循环
- 文档设计：AGENTS.md 应该是目录而非百科全书，用"渐进式披露"管理 agent 的稀缺 context
- 架构约束：刚性的分层依赖规则不是负担，是 agent 高速工作而不产生混乱的基础设施
- 可观测性：把日志、指标、UI 直接暴露给 agent，让它用真实运行时行为来验证自己的改动
- 持续清理：用定期运行的后台 agent 做代码"垃圾回收"，把团队的黄金原则机械化后持续强制执行
- 全流程自动化：从复现 bug 到合并 PR，单次 Codex 运行已经可以端到端完成完整的软件交付流程

---

原文：Harness engineering: leveraging Codex in an agent-first world
链接：https://openai.com/index/harness-engineering
发表时间：2026-02-11
本期解读由模型（claude-sonnet-4-6）生成，音频由 edge-tts 合成。
