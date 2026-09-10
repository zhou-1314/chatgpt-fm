<div align="center">

# ChatGPT FM 📻

**把 OpenAI 官网发布的技术博客，做成中文音频解读**

用碎片时间听懂最前沿的 AI

![episodes](https://img.shields.io/badge/已更新-52%20集-1DB954)
![update](https://img.shields.io/badge/更新频率-每周日-FF8800)
![language](https://img.shields.io/badge/语言-简体中文-blue)

</div>

---

## 🎧 收听

用**任意播客 App**（小宇宙、Apple Podcasts、Pocket Casts…）粘贴下面的地址订阅：

```
https://zhou-1314.github.io/chatgpt-fm/feed.xml
```

也可以直接打开网页版目录 👉 **<https://zhou-1314.github.io/chatgpt-fm/>**

## 💡 这是什么

[OpenAI 官网](https://openai.com)持续发布大量高质量内容——模型发布、Codex 与智能体工程实践、
对齐与安全研究、产品与 API 更新，平常没时间逐篇读。

这个项目把它们**逐篇做成约 25 分钟的口语化中文解读**，配上音频，按发表时间排成一条
AI 技术演进的时间线。通勤、健身、做家务的时候听一听就跟上了。

> 所有内容源均来自 **openai.com 官网**，不收录任何第三方转载。
> 中文解读由 AI 模型生成，仅供学习参考，请以英文原文为准。

## 📚 更新进度

| 来源 | 集数 | 内容 |
|---|:---:|---|
| 🛠️ Engineering | 32 | 工程实践（Codex、harness、基础设施…） |
| 🔬 Research | 20 | 研究与论文（推理、评测、可解释性…） |
| 🚀 Product | 0 | 模型与产品发布（GPT 系列、API、ChatGPT…） |
| 🛡️ Safety | 0 | 安全与对齐（Preparedness、威胁情报…） |
| 📰 News 周报 | 0 | 「一周快讯」，速览每周官方动态 |
| | **52 集** | 每周日更新 |

前四个源逐篇做深度解读；news 类内容（公司动态、政策、客户故事）多为公告，
按周聚合成几分钟的「一周快讯」。

### 最新单集

<!-- LATEST:START -->

- 🔬 `EP33` · 2026-09-08 · [AI 用八十八小时攻克九十年数学悬案：OpenAI 解开流体力学千年大奖之谜](content/openai/research/scripts/2026-09-08-On%20the%20Navier%E2%80%93Stokes%20Millennium%20Prize%20Problem.md)
- 🔬 `EP34` · 2026-09-06 · [OpenAI内部实录：AI研究算力已是人类三倍，自动化科研背后两起安全警报](content/openai/research/scripts/2026-09-06-Research%20acceleration%20-%20The%20view%20inside%20OpenAI.md)
- 🔬 `EP35` · 2026-09-03 · [GPT 六 Astra 全面解析：计算机操控、网络安全与 AI 对齐的新一代突破](content/openai/research/scripts/2026-09-03-GPT-6%20Astra%20-%20A%20new%20generation%20of%20intelligence.md)
- 🛠️ `EP1` · 2026-08-25 · [OpenAI 首款自研芯片 Jalapeño 实测：推理效率与速度全面刷新行业基准](content/openai/engineering/scripts/2026-08-25-Jalape%C3%B1o%E2%80%99s%20first%20results%20show%20industry-leading%20speed%20and%20efficiency%20in%20AI%20inference.md)
- 🛠️ `EP2` · 2026-08-03 · [六个月打造实时语音AI：OpenAI全双工架构工程内幕](content/openai/engineering/scripts/2026-08-03-How%20we%20built%20a%20realtime%20system%20for%20responsive%20voice%20AI%20in%20six%20months.md)
- 🔬 `EP36` · 2026-08-01 · [AI 如何解开十道数学百年难题，以及这对我们意味着什么](content/openai/research/scripts/2026-08-01-Ten%20advances%20in%20mathematics%20and%20theoretical%20computer%20science.md)
- 🔬 `EP37` · 2026-07-29 · [两个设置让得分翻三倍：基准测试到底在测什么](content/openai/research/scripts/2026-07-29-How%20enabling%20two%20settings%20tripled%20our%20scores%20on%20the%20ARC-AGI-3%20benchmark.md)
- 🛠️ `EP3` · 2026-07-29 · [让模型优化模型：GPT 五点六如何同时拿下前沿智能与前沿效率](content/openai/engineering/scripts/2026-07-29-How%20GPT-5.6%20fuses%20frontier%20intelligence%20with%20frontier%20efficiency.md)

<!-- LATEST:END -->

📋 **完整 52 集目录（可点开每集文字稿）** 👉 **[CATALOG.md](CATALOG.md)**

## 📖 也可以直接读文字版

不方便听？每集的中文解读全文都在仓库里，点开即读。
文字稿按来源存放在 [`content/`](content/) 下：

- `content/openai/<源>/scripts/` — 中文解读稿（含 shownotes）
- `content/openai/<源>/articles/` — 抓取到的英文原文

## 🔧 自己跑一份

```bash
uv venv --python 3.11 && uv pip install -e .
cp .env.example .env          # 配解读后端：codex / claude / deepseek 三选一

chatgpt-fm weekly             # 抓取 → 解读 → TTS → 上传包 → 刷新目录
chatgpt-fm publish            # 构建站点并推到 gh-pages，Pages 托管
```

流水线每篇走四步：**抓取原文 → 模型生成解读稿 → edge-tts 合成音频 → 生成上传包**。
进度记在 `content/state.json`，全程幂等——中断后重跑会跳过已完成的阶段。

换成你自己的仓库：改 `config.py` 里的 `GITHUB_OWNER` / `GITHUB_REPO`，
或用同名环境变量覆盖。

> 📘 数据源发现机制、部署细节、全部命令、踩坑备忘 👉 **[DEVELOPMENT.md](DEVELOPMENT.md)**

## 🙏 致谢

本项目脱胎于 **[yuc16/claude-fm](https://github.com/yuc16/claude-fm)** —— 一档把
Anthropic 官方博客做成中文音频解读的播客。整条流水线的设计思路
（抓取 → 模型解读 → TTS → 上传包 → RSS → 目录）、状态机与幂等策略、
prompt 框架、目录结构和命名风格都沿用自它，本项目主要替换了数据源那一层，
把 anthropic.com 换成了 openai.com。

感谢原作者把这套做法完整地开源出来。如果你关注 Anthropic 的内容，推荐直接去听
[Claude FM](https://github.com/yuc16/claude-fm)。

---

<div align="center">

本项目为个人**非商业**的学习用途整理，**与 OpenAI 无任何官方关联**。<br>
所有原文版权归 [OpenAI](https://openai.com) 所有。

</div>
