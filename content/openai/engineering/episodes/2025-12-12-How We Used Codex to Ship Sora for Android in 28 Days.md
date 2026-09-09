# EP18 | 四人团队加 Codex：OpenAI 如何在二十八天内把 Sora 搬上安卓

- 音频文件：`/workspace/algorithm/zhouwg_project/chatGPT-fm/chatgpt-fm/content/openai/engineering/audio/2025-12-12-How We Used Codex to Ship Sora for Android in 28 Days.mp3`
- 时长：23 分 08 秒

## Shownotes（复制到小宇宙）

二〇二五年十一月，OpenAI 仅用四名工程师和 AI 编程工具 Codex，在二十八天内将 Sora 视频生成应用从原型推上了 Android 全球上线，首日登顶 Play Store 榜首，二十四小时内用户生成视频超过一百万条。这篇工程复盘详细拆解了他们与 Codex 协作的工作流：如何让 AI 长时间无监督运行、如何把 iOS 代码库变成 Android 的"活体规格书"，以及为什么 AI 辅助开发不是降低了对工程师的要求，而是提高了。

- 把 Codex 当成"刚入职的资深工程师"——它需要被告知偏好、展示范例，而不只是接收需求
- 先建架构骨架和代表性功能，再放 Codex 进来填充——85% 的代码由 Codex 完成，但人定骨架
- 引入"规划前置"循环：理解现有系统 → 制定实施计划 → 分步执行，让 Codex 可无监督运行超过二十四小时
- AGENTS.md 文件是最低成本、最高收益的投资——相当于给每个 AI 会话的"员工手册"
- 并行运行多个 Codex 会话如同管理一支工程团队，瓶颈从写代码转移到决策与审查
- iOS 已有实现 → Codex 跨语言语义翻译 → Android：比 React Native 还彻底的"跨平台方案"

---

原文：How We Used Codex to Ship Sora for Android in 28 Days
链接：https://openai.com/index/shipping-sora-for-android-with-codex
发表时间：2025-12-12
本期解读由模型（claude-sonnet-4-6）生成，音频由 edge-tts 合成。
