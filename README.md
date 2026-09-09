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
https://zhou-1314.github.io/chatgpt-fm/feed.xml
```

也可以直接打开网页版目录：**<https://zhou-1314.github.io/chatgpt-fm/>**

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
chatgpt-fm feed                           # 生成播客 RSS docs/feed.xml
chatgpt-fm publish                        # 发布到 GitHub：音频→Release，feed+目录页→Pages
chatgpt-fm catalog                        # 生成 CATALOG.md 并刷新 README 集数
chatgpt-fm voices                         # 生成音色试听样品
chatgpt-fm status                         # 查看各篇进度
```

流水线每篇走四步：**抓取原文 → 模型生成解读稿 → edge-tts 合成音频 → 生成上传包**。
进度记在 `content/state.json`，全程幂等——中断后重跑会跳过已完成的阶段。

### 部署：全部托管在 GitHub 上，不需要自己的服务器

| 放什么 | 放哪 | 为什么 |
|---|---|---|
| 代码、中文解读稿、英文原文 | 仓库本体 | 纯文本，几 MB |
| `feed.xml`、网页目录页 | GitHub Pages（`main` 分支的 `docs/`） | 几十 KB，随仓库一起提交 |
| 单集音频 mp3 | GitHub Release 附件（tag `audio`） | Pages 单站点上限 1GB，几百集音频装不下；Release 附件单文件上限 2GB、总量不限 |

音频附件一律按集号命名（`EP12.mp3`）。slug 里有空格、中文和 `’`，GitHub 上传时会自己
改名，改完的下载地址会和 feed 里写的对不上；集号是 ASCII、唯一、分配后不再变。

每周更新的完整流程就两条命令：

```bash
chatgpt-fm weekly     # 抓取 → 解读 → TTS → 上传包 → 刷新 CATALOG
chatgpt-fm publish    # 音频传 Release，重写 docs/feed.xml 与 docs/index.html
git add -A && git commit -m "weekly update" && git push
```

`publish` 是幂等的：附件同名同大小就跳过，只传新增或重新合成过的那几集，
所以中断后重跑不会把已上传的音频再传一遍。先看看它打算做什么可以加 `--dry-run`。

换成你自己的仓库/域名，改 `config.py` 里的 `GITHUB_OWNER` / `GITHUB_REPO`
（也可以用同名环境变量或 `.env` 覆盖），或直接设 `FEED_BASE_URL` / `AUDIO_BASE_URL`。

**首次部署还要做两件事**：
1. 仓库 Settings → Pages → Source 选 `Deploy from a branch`，分支 `main`、目录 `/docs`；
2. 放一张 ≥1400×1400 的封面图到 `docs/cover.jpg`（播客 App 要求，没有封面上不了架）。

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
uv run python -m unittest discover -s tests   # 67 个单测，不联网、不调模型
chatgpt-fm discover                           # 真实联网发现（约 1 分半，含 sitemap 兜底）
chatgpt-fm run --source engineering --limit 1 # 跑通一整篇（这步会真的调模型）
```

### 踩坑备忘

- **文章页 403**：openai.com 有 Cloudflare 机器人校验，一定要装上 `curl_cffi`
  （已在依赖里），否则只有 `sitemap.xml` / `rss.xml` 能拿到，正文全军覆没。
- **环境里设了 `ALL_PROXY=socks5://...`**：httpx 会要求额外的 socks 支持，报
  `Using SOCKS proxy, but the 'socksio' package is not installed`。抓取层会自动
  降级到 curl / curl_cffi 不受影响，但**解读后端（codex / deepseek）走的是 httpx，
  会直接失败**。解决办法二选一：`uv pip install "httpx[socks]"`，或者跑命令前
  `unset ALL_PROXY all_proxy`（HTTP 代理变量保留即可）。实测 unset 之后抓取
  从 97 秒降到 3.5 秒——因为不用每次都退到 curl_cffi 兜底了。
- **抓着抓着整站连不上**：openai.com 会按出口 IP 限流。抓太密时文章页、
  sitemap、RSS 会一起变成连接被 RST（`SSL_ERROR_SYSCALL`），几分钟后自动恢复。
  `net.py` 已经内置 2 秒最小请求间隔 + 连续失败 3 篇熔断来躲这个；如果你的
  网络环境更敏感，把 `net.MIN_REQUEST_INTERVAL` 调大即可。
  顺带一提，这种时候 edge-tts 往往也一起挂，别误判成 TTS 坏了。
- **codex 撞周限额**：ChatGPT Pro 的周限额一撞就是好几天（响应体里的
  `resets_in_seconds` 实测有 51 万秒 ≈ 6 天）。autorun 会识别出来直接停下
  而不是睡等，这时候把 `.env` 里的 `INTERPRET_PROVIDER` 换成 `claude` 或
  `deepseek` 继续跑就行，已完成的阶段不会重做。

---

<div align="center">

## 关于版权

本项目为个人**非商业**的学习用途整理，**与 OpenAI 无任何官方关联**。<br>
所有原文版权归 [OpenAI](https://openai.com) 所有；中文解读由当前配置的 AI 模型生成，仅供学习参考，请以英文原文为准。

</div>
