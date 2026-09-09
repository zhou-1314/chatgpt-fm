# EP6 | 给 AI 编程 Agent 造一把安全锁：Codex Windows 沙盒设计全记录

- 音频文件：`/workspace/algorithm/zhouwg_project/chatGPT-fm/chatgpt-fm/content/openai/engineering/audio/2026-05-13-Building a safe, effective sandbox to enable Codex on Windows.mp3`
- 时长：24 分 56 秒

## Shownotes（复制到小宇宙）

OpenAI 工程师 David Wiesen 详细记录了他如何在 Windows 上从零为 Codex 编程 agent 构建沙盒机制。文章坦诚地展示了多条死路以及最终四层架构的形成过程，是难得的真实工程决策记录。

- Codex 在 Mac/Linux 上有成熟沙盒，但 Windows 既无 Seatbelt 也无 seccomp，三种现有方案（AppContainer、Windows Sandbox、强制完整性控制）各有根本性缺陷
- 第一版无需提权的原型：合成 SID + 写受限令牌精细控制文件写入；用代理环境变量"劝阻"网络，但本质上可被绕过
- 第二版高级沙盒：创建两个专属 Windows 系统用户，配合防火墙规则实现真正的网络硬隔离
- Windows 权限壁垒（CreateProcessAsUserW）催生了 codex-command-runner.exe，专门负责在正确边界内铸造受限令牌并启动子进程
- 最终架构分四层：主程序、提权安装程序、命令运行器、受限子进程，各司其职互不越界
- 核心教训：agent 安全和传统应用安全需求不同；网络隔离必须做到操作系统层，环境变量只是劝阻而非强制

---

原文：Building a safe, effective sandbox to enable Codex on Windows
链接：https://openai.com/index/building-codex-windows-sandbox
发表时间：2026-05-13
本期解读由模型（claude-sonnet-4-6）生成，音频由 edge-tts 合成。
