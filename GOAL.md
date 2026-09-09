# GOAL：打造 ChatGPT FM 仓库

> 参考 `../claude-fm` 的设计，做一个面向 **OpenAI 官网博客** 的中文播客流水线仓库。
> 本文件记录目标拆解与推进进度，供随时回看。

## 一、目标

把 [openai.com](https://openai.com) 官网发布的博客内容，逐篇转成口语化中文解读稿 + 中文音频，
整理成一档可订阅的播客（RSS），并在仓库内保留全部文字稿与英文原文。

**硬约束**：所有内容来源必须是 OpenAI 官网（`openai.com`），不引入第三方转载源。

## 二、与 claude-fm 的对照

沿用 claude-fm 的技术选型与目录结构，只替换「数据源」这一层：

| 维度 | claude-fm | chatgpt-fm |
|---|---|---|
| 内容来源 | anthropic.com sitemap + claude.com/blog 列表页 | **openai.com/news/rss.xml**（主）+ openai.com 分类 sitemap（补） |
| 发表日期 | 从文章 HTML 正则锚点猜 | **RSS `pubDate` 权威给出**，HTML 仅作兜底 |
| 分类 | URL 前缀天然分源 | RSS `<category>` 映射到 5 个源 |
| 正文抓取 | httpx → curl | httpx → curl → **curl_cffi（Chrome TLS 指纹）** |
| 解读/TTS/RSS/目录 | 同 | 同（逐文件移植，改包名与文案） |

## 三、数据源设计

发现层：`https://openai.com/news/rss.xml`（1100+ 篇，含 title / link / category / pubDate），
外加 11 个分类 sitemap 兜底补齐 RSS 漏掉的少量老文章。

RSS 分类 → 本仓库的源：

| 源 | 目录 | RSS 分类 | 处理方式 |
|---|---|---|---|
| `engineering` | `content/openai/engineering` | Engineering, API | 单篇深度解读（~25 分钟） |
| `research` | `content/openai/research` | Research, Publication | 单篇深度解读 |
| `product` | `content/openai/product` | Product, Release, ChatGPT | 单篇深度解读 |
| `safety` | `content/openai/safety` | Safety, Safety & Alignment, Security | 单篇深度解读 |
| `news` | `content/openai/news` | Company, Global Affairs, Story, Startup… 及未分类 | 按周聚合成「一周快讯」 |

## 四、任务拆解与状态

- [x] T1 摸清 claude-fm 结构、流水线、状态机与命名风格
- [x] T2 摸清 openai.com 可用接口：sitemap / rss.xml / 文章页反爬情况
- [x] T3 验证 `curl_cffi` 可绕过 openai.com 的 Cloudflare 指纹校验（200 + trafilatura 提取正常）
- [x] T4 仓库骨架：pyproject / .env.example / .gitignore / 目录
- [x] T5 `config.py`：5 源定义、分类映射、播客元信息
- [x] T6 `sources.py`：RSS 发现 + sitemap 兜底 + 分类路由
- [x] T7 `fetch.py`：三级抓取回退 + 正文清洗 + frontmatter 落盘
- [x] T8 移植 `interpret.py` / `tts.py` / `episode.py` / `digest.py` / `feed.py` / `catalog.py` / `state.py`
- [x] T9 `cli.py`：discover / run / autorun / news / weekly / feed / catalog / voices / status
- [x] T10 prompts：`interpret.md` / `news_digest.md` 改写为 OpenAI 语境
- [x] T11 `tests/`：纯函数单测（stdlib unittest，无新依赖）
- [x] T12 README + 本文件
- [x] T13 验证：构建、单测、真实 discover / 抓取 / 目录 / RSS 端到端

## 五、验证记录

全部在本机实跑过（2026-09-08）：

| 验证项 | 命令 / 方式 | 结果 |
|---|---|---|
| 包可安装、CLI 可用 | `uv pip install -e .` + `chatgpt-fm --help` | ✅ 9 个子命令齐全 |
| 单元测试 | `python -m unittest discover -s tests` | ✅ **67 passed** |
| 真实发现 | `chatgpt-fm discover` | ✅ engineering 33 / research 228 / product 172 / safety 140 / news 541 |
| 真实抓取 + 分源 | 四个深度源各抓一篇最新文章 | ✅ 正文 6.9K–19K 字符，日期与 RSS 分类一致 |
| 解读 prompt 渲染 | `interpret.build_prompt` 灌真实文章 | ✅ 占位符全替换，中文日期正常 |
| TTS 合成 | `tts.synthesize` 跑样例文本 | ✅ 199 KB mp3 / 33.2 秒 |
| 上传包 → 目录 → RSS | `tests/test_packaging.py`（临时目录，不污染仓库） | ✅ EP 标题、CATALOG、README 集数、feed.xml 全对 |
| CLI 空库运行 | `status` / `catalog` / `feed` | ✅ 均正常退出 |

**没能在本机验证的一环**：`interpret` 真正调模型生成解读稿——需要 `codex login` /
`claude` 订阅 / DeepSeek API key，本机都没有。除了"真的发一次请求"以外，该环节的
其余逻辑都用假的 `run_llm` 覆盖到了：三段式输出解析、解析失败重试、短稿加长重写、
限额异常原样上抛、解读稿落盘格式（`tests/test_interpret.py`）。

## 六、与 claude-fm 相比的几处改动（都是被 openai.com 的实际情况逼出来的）

1. **`net.py`（新增）**：claude-fm 在 `sources.py` 和 `fetch.py` 里各抄了一份
   `_get_with_retries`；这里抽成一个模块，并加了第三级 `curl_cffi` 兜底。
2. **发现层换成 RSS**：openai.com 文章全在 `/index/<slug>` 下，URL 分不了类，
   改用官方 RSS 的 `<category>` 分源，同时白拿权威 `pubDate`。
3. **`_extract_published` 只认结构化字段**：openai.com 文章页底部有推荐位，
   页面上到处是日期，按 claude-fm 那种"找页面上第一个 Mon D, YYYY"会抓错。
4. **五个源而不是四个**：OpenAI 的 Safety / Preparedness 内容量大且有知识含量，
   单独成源；`config.SOURCES` 驱动全部下游（catalog、cli、feed 都不写死源名）。

---

## 七、GitHub 部署（2026-09-09）

仓库：**<https://github.com/zhou-1314/chatgpt-fm>**（公开）

托管分工，按各自的容量上限来定：

| 放什么 | 放哪 | 上限 |
|---|---|---|
| 代码、中文解读稿、英文原文 | 仓库本体 | 纯文本，几 MB |
| `feed.xml`、网页目录页 | GitHub Pages（`main` 分支 `/docs`） | 站点 1GB，我们只用几十 KB |
| 单集音频 mp3 | GitHub Release 附件（tag `audio`） | 单文件 2GB，总量不限 |

音频不能用 slug 命名：slug 里有空格、中文和 `’`，GitHub 上传时会自己改名，
改完的下载地址和 feed 里写的对不上。改用集号 `EP<n>.mp3`——ASCII、唯一、
集号一旦分配就不再变。

### 部署验证记录

| 验证项 | 结果 |
|---|---|
| 仓库创建 + 推送 | ✅ 3 个 commit 已上 main |
| Pages 开启（main `/docs`） | ✅ build status = `built`，耗时 23.5s |
| 目录页 `https://zhou-1314.github.io/chatgpt-fm/` | ✅ HTTP 200 |
| RSS `https://zhou-1314.github.io/chatgpt-fm/feed.xml` | ✅ HTTP 200，合法 XML，channel 元信息正确 |
| Release `audio` 创建 + `gh` 读写 | ✅ 可创建、可列附件 |
| **音频 URL 全链路** | ✅ 传 `EP0.mp3` → 用 `config.audio_url(0)` 下载 → 199440 字节**逐字节一致**，验证后已删除 |
| 单元测试 | ✅ **79 passed**（新增 12 个覆盖 publish） |

### 已知的一处小风险

GitHub Release 下载返回的 `Content-Type` 是 `application/octet-stream` 而不是
`audio/mpeg`。播客客户端主要认 RSS `<enclosure type="audio/mpeg">`，小宇宙、
Pocket Casts 这类都能正常播；但 Apple Podcasts 的提交校验对此偶有挑剔。
真上架 Apple 时如果被拒，退路是把音频挪到自建服务器或对象存储（改
`AUDIO_BASE_URL` 一个变量即可，feed 逻辑不用动）。

### 还差两步（需要你做）

1. **封面图**：放一张 ≥1400×1400 的 `docs/cover.jpg` 再提交。播客 App 强制要求，没有封面上不了架。
2. **跑第一批内容**：本机 `codex login`（或在 `.env` 配 DeepSeek key）后
   `chatgpt-fm autorun --source engineering` → `chatgpt-fm publish` → 提交推送。
