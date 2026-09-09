# EP4 | 两个不可能的 Bug：OpenAI 如何用流行病学思维破解神秘崩溃

- 音频文件：`/workspace/algorithm/zhouwg_project/chatGPT-fm/chatgpt-fm/content/openai/engineering/audio/2026-06-30-Core dump epidemiology - fixing an 18-year-old bug.mp3`
- 时长：28 分 20 秒

## Shownotes（复制到小宇宙）

OpenAI 工程团队在 Rockset 服务里发现了一种神秘崩溃：普通的 C++ 函数在返回时跳到了空指针，或者栈指针寄存器凭空偏移了 8 字节。他们花了数周时间，最终发现背后藏着两个完全不相关的 bug——一个是云端物理机的静默硬件错误，另一个是 GNU libunwind 库里潜伏了整整十八年的竞态条件。本期详细拆解整个调查过程，以及那个关键的方法论转变。

- 为什么 C++ 的内存不安全让崩溃调试变得格外棘手，以及 OpenAI 如何用 core dump 来追踪生产故障
- 两类诡异崩溃的技术细节：返回到空指针，以及栈指针寄存器的 8 字节偏移究竟意味着什么
- 从"医生模式"到"流行病学家模式"的方法论转变，以及如何用自动化管线建立高质量的全量崩溃数据集
- 静默硬件错误：云端 CPU 可以在没有任何报警的情况下算出错误结果
- GNU libunwind 十八年老 bug 的完整机制：一条指令宽的竞态窗口，百皮秒级的时间窗，以及三个因素的乘积如何让它从不可见变为可见
- 对基础设施工程师的实践启示：如何建立更好的崩溃分析体系，以及哪些系统设计选择会放大这类风险

---

原文：Core dump epidemiology: fixing an 18-year-old bug
链接：https://openai.com/index/core-dump-epidemiology-data-infrastructure-bug
发表时间：2026-06-30
本期解读由模型（claude-sonnet-4-6）生成，音频由 edge-tts 合成。
