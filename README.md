<div align="center">

# ChatGPT FM 📻

**把 OpenAI 官网发布的技术博客内容，转化为中文音频解读，让你在碎片时间听懂最前沿的 AI**

![episodes](https://img.shields.io/badge/已更新-0%20集-1DB954)
![update](https://img.shields.io/badge/更新频率-每周日-FF8800)
![language](https://img.shields.io/badge/语言-简体中文-blue)

</div>

---

## 这是什么

[OpenAI](https://openai.com) 在官网持续发布大量高质量的 AI 内容——模型发布、Codex 与智能体工程实践、对齐与安全研究、产品与 API 更新、政策与公司动态，平常没有大量时间逐篇阅读。

**ChatGPT FM 把它们逐篇做成口语化的中文解读**，整理成一档可以随时收听的播客——通勤、健身、做家务的时候听一听，用碎片时间把最前沿的 AI 进展听懂。仓库把 OpenAI 官网的内容按发表时间排成一条 AI 技术演进的时间线，并且每周日持续更新。

> 所有内容源均来自 **openai.com 官网**，不收录任何第三方转载。

## 🎧 收听

用**任意播客 App**（小宇宙、Apple Podcasts、Pocket Casts 等）粘贴下面的 RSS 地址订阅：

```
https://chatgpt-fm.example.com/feed.xml
```

> 部署前请把 `src/chatgpt_fm/config.py` 里的 `FEED_BASE_URL` 换成你自己的域名。

## 📖 也可以直接读文字版

不方便听？每一集的**中文解读全文**都在这个仓库里，点开即读（开头都会注明文章发表时间）。

📋 **完整 0 集目录（可点开每集文字稿）** 👉 **[CATALOG.md](CATALOG.md)**

全部解读稿也在 [`content/`](content/) 下按来源分目录存放（`scripts/` 是中文解读，`articles/` 是英文原文）。

## 📚 内容概览

| 来源 | 集数 | 内容 |
|---|:---:|---|
| 🛠️ Engineering | 0 | 工程实践深度解读（Codex、harness、基础设施…） |
| 🔬 Research | 0 | 研究与论文深度解读（推理、评测、可解释性…） |
| 🚀 Product | 0 | 模型与产品发布深度解读（GPT 系列、API、ChatGPT…） |
| 🛡️ Safety | 0 | 安全与对齐深度解读（Preparedness、威胁情报、安全评估…） |
| 📰 News 周报 | 0 | 「一周快讯」合集，速览每周官方动态 |
| | **0 集** | 每周日更新 |

前四个源逐篇做约 25 分钟的深度解读；news 类内容（公司动态、政策、客户故事）时效性强、多为公告，按周聚合成几分钟的「一周快讯」。

---

## 🔧 本地运行

### 环境

```bash
uv venv --python 3.11
uv pip install -e .
cp .env.example .env      # 按需修改解读后端
```

解读后端三选一（在 `.env` 里配 `INTERPRET_PROVIDER`）：

| 后端 | 取值 | 认证方式 |
|---|---|---|
| Codex（默认） | `codex` | 本机 `codex login`，读 `~/.codex/auth.json` |
| Claude CLI | `claude` | 本机 `claude` 订阅登录 |
| DeepSeek API | `deepseek` | `.env` 里填 `DEEPSEEK_API_KEY` |

### 常用命令

```bash
chatgpt-fm discover                       # 列出各源文章数与新文章
chatgpt-fm run --source engineering --limit 3   # 端到端跑几篇
chatgpt-fm autorun --source research      # 无人值守，撞限额自动等重置续跑
chatgpt-fm news                           # 把上一周的 news 打包成「一周快讯」
chatgpt-fm weekly                         # 每周日一条命令：四源增量 + news 周报 + RSS + 目录
chatgpt-fm feed                           # 生成播客 RSS content/feed.xml
chatgpt-fm catalog                        # 生成 CATALOG.md 并刷新 README 集数
chatgpt-fm voices                         # 生成音色试听样品
chatgpt-fm status                         # 查看各篇进度
```

流水线每篇走四步：**抓取原文 → 模型生成解读稿 → edge-tts 合成音频 → 生成上传包**。
进度记在 `content/state.json`，全程幂等——中断后重跑会跳过已完成的阶段。

### 内容源是怎么发现的

OpenAI 官网的文章全部落在 `https://openai.com/index/<slug>`，靠 URL 前缀分不了类，所以：

- **主发现**：官方 RSS `https://openai.com/news/rss.xml`，一次给出全站一千多篇的标题、链接、分类和**权威发表日期**；
- **兜底**：11 个分类 sitemap（`https://openai.com/sitemap.xml/<分类>/`），补齐 RSS 偶尔漏掉的少量老文章；
- **分源**：按 RSS `<category>` 映射到上表的五个源，映射表在 `src/chatgpt_fm/config.py` 的 `SOURCES`。

> ⚠️ openai.com 的文章页有 Cloudflare 机器人校验，普通 httpx / curl 会吃 403。
> 抓取层 `net.py` 会依次尝试 **httpx → curl → curl_cffi（Chrome TLS 指纹）**，
> 正文实际由 `curl_cffi` 拿到，所以它是必需依赖。

### 本地验证

```bash
python -m unittest discover -s tests -v    # 纯函数单测，不联网
chatgpt-fm discover                        # 真实联网发现（约 20 秒）
```

---

<div align="center">

## 关于版权

本项目为个人**非商业**的学习用途整理，**与 OpenAI 无任何官方关联**。<br>
所有原文版权归 [OpenAI](https://openai.com) 所有；中文解读由当前配置的 AI 模型生成，仅供学习参考，请以英文原文为准。

</div>
