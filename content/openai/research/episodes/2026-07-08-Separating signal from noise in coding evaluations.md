# EP39 | 当评测工具本身就错了：OpenAI 揭露 SWE-Bench Pro 三成任务存缺陷

- 音频文件：`content/openai/research/audio/2026-07-08-Separating signal from noise in coding evaluations.mp3`
- 时长：23 分 08 秒

## Shownotes（复制到小宇宙）

OpenAI 研究团队对代码能力基准测试 SWE-Bench Pro 展开深度审查，结果令人警醒：估计约三成任务存在根本性缺陷。这意味着当我们看到某个模型在这个评测上取得高分时，很可能是"考卷"本身先坏了——不是模型更强了，而是测试失真了。本期我们拆解这份报告，聊聊评测失真究竟有多深，以及对工程师日常判断 AI 能力意味着什么。

**本期要点**

- OpenAI 审查 SWE-Bench Pro 七三一个任务，估计约三成存在根本性缺陷
- 四类问题：测试标准过严、题目描述不清、测试覆盖率不足、误导性提示
- 三层审查流程：自动化过滤 → Codex 调查员智能体深度分析 → 五名资深工程师人工标注
- 人类审查员比 AI 智能体更倾向于判定任务有问题，两者重叠率七成四
- 低覆盖率测试是人机分歧最大的类别：人工标注占九点四成，智能体仅识别四点一成
- OpenAI 撤回此前对 SWE-Bench Pro 的使用推荐，呼吁行业构建专为测试模型能力而设计的新基准

---

原文：Separating signal from noise in coding evaluations
链接：https://openai.com/index/separating-signal-from-noise-coding-evaluations
发表时间：2026-07-08
本期解读由模型（claude-sonnet-4-6）生成，音频由 edge-tts 合成。
