# 开发与运维笔记

面向要自己跑这条流水线、或者想改数据源的人。用户向的介绍在 [README](README.md)。

## 目录

- [环境与后端](#环境与后端)
- [全部命令](#全部命令)
- [内容源是怎么发现的](#内容源是怎么发现的)
- [部署](#部署)
- [本地验证](#本地验证)
- [踩坑备忘](#踩坑备忘)

## 环境与后端

```bash
uv venv --python 3.11
uv pip install -e .
cp .env.example .env
```

解读后端三选一（`.env` 里配 `INTERPRET_PROVIDER`）：

| 后端 | 取值 | 认证方式 |
|---|---|---|
| Codex（默认） | `codex` | 本机 `codex login`，读 `~/.codex/auth.json` |
| Claude CLI | `claude` | 本机 `claude` 订阅登录 |
| DeepSeek API | `deepseek` | `.env` 里填 `DEEPSEEK_API_KEY` |

只有 DeepSeek 能搬进 CI——Codex 走的是本机 `codex login` 的 OAuth，
Claude 走订阅登录，都拿不到可移植的凭证。

## 全部命令

```bash
chatgpt-fm discover                             # 列出各源文章数与新文章
chatgpt-fm run --source engineering --limit 3   # 端到端跑几篇
chatgpt-fm autorun --source research            # 无人值守，撞限额自动等重置续跑
chatgpt-fm news                                 # 把上一周的 news 打包成「一周快讯」
chatgpt-fm weekly                               # 每周日一条命令：四源增量 + news 周报 + 目录
chatgpt-fm publish                              # 构建站点并推到 gh-pages
chatgpt-fm feed                                 # 只生成 RSS
chatgpt-fm catalog                              # 只刷新 CATALOG.md 与 README 进度
chatgpt-fm voices                               # 生成音色试听样品
chatgpt-fm status                               # 查看各篇进度
```

流水线每篇四步：**抓取原文 → 模型生成解读稿 → edge-tts 合成音频 → 生成上传包**。
进度记在 `content/state.json`，全程幂等，中断后重跑跳过已完成的阶段。

## 内容源是怎么发现的

OpenAI 官网的文章全部落在 `https://openai.com/index/<slug>`，靠 URL 前缀分不了类，所以：

- **主发现**：官方 RSS `https://openai.com/news/rss.xml`，一次给出全站一千多篇的
  标题、链接、分类和**权威发表日期**（省掉了从 HTML 正则猜日期的活儿）；
- **兜底**：11 个分类 sitemap（`https://openai.com/sitemap.xml/<分类>/`），
  补齐 RSS 偶尔漏掉的少量老文章（`dall-e-2`、`introducing-gpt-4-5` 之类）；
- **分源**：按 RSS `<category>` 映射到五个源，映射表在
  `src/chatgpt_fm/config.py` 的 `SOURCES`，改这一处即可调整分类。

抓取层 `net.py` 依次尝试 **httpx → curl → curl_cffi（Chrome TLS 指纹）**。
openai.com 的文章页有 Cloudflare 机器人校验，前两级一律吃 403，
正文实际由 `curl_cffi` 拿到，所以它是必需依赖。

## 部署

全部托管在 GitHub 上，不需要自己的服务器：

| 放什么 | 放哪 | 为什么 |
|---|---|---|
| 代码、中文解读稿、英文原文 | `main` 分支 | 纯文本，几百 KB，clone 很快 |
| `feed.xml`、目录页、封面、**全部音频** | `gh-pages` 分支，由 Pages 提供 | 站点产物单独一个分支，不污染 main 的历史 |

### 音频为什么不能放 GitHub Release

Release 的下载地址返回：

```
content-type: application/octet-stream
content-disposition: attachment; filename=EP1.mp3
```

`attachment` 是致命的——它告诉客户端"这是要下载保存的附件"，播放器据此拒绝内联播放，
在 Apple Podcasts 上就表现为「无法播放」。Pages 对 `.mp3` 返回 `audio/mp3`、
不带 `content-disposition`、支持 Range（206），才是播客客户端要的。

音频在站点里一律按集号命名（`EP12.mp3`）：slug 里有空格、中文和 `’`，直接做 URL
要转义，集号是 ASCII、唯一、分配后不再变。

> ⚠️ **容量上限**：Pages 单站点 1GB，按单集约 9MB 算大概 **111 集封顶**。
> `publish` 在站点音频超过 900MB 时会告警。超了就把音频挪到对象存储
> （Cloudflare R2 免费额度 10GB 且不收出站流量），改 `AUDIO_BASE_URL` 一个变量即可，
> feed 逻辑不用动。

### 每周更新流程

```bash
chatgpt-fm weekly     # 抓取 → 解读 → TTS → 上传包 → 刷新 CATALOG 与 README 进度
chatgpt-fm publish    # 构建站点（feed + 目录页 + 封面 + 音频）并推到 gh-pages
git add -A && git commit -m "weekly update" && git push   # main 只提交文字稿
```

`publish` 幂等：音频同名同大小就跳过，只同步新增或重新合成过的那几集，
不会让 git 认为几百个文件都变了。加 `--dry-run` 可以先看它打算做什么。
gh-pages 用 `git worktree` 操作，不碰主工作区——流水线正在跑的时候也能发布。

### 首次部署

1. 仓库 Settings → Pages → Source 选 `Deploy from a branch`，分支 `gh-pages`、目录 `/`；
2. 放一张 ≥1400×1400 的正方形封面到 `assets/cover.jpg`（播客 App 强制要求）；
3. 改 `config.py` 的 `GITHUB_OWNER` / `GITHUB_REPO`（或用同名环境变量覆盖）。

## 本地验证

```bash
uv run python -m unittest discover -s tests     # 单测，不联网、不调模型
chatgpt-fm discover                             # 真实联网发现
chatgpt-fm run --source engineering --limit 1   # 跑通一整篇（这步会真的调模型）
```

## 踩坑备忘

- **文章页 403**：openai.com 有 Cloudflare 机器人校验，一定要装上 `curl_cffi`
  （已在依赖里），否则只有 `sitemap.xml` / `rss.xml` 能拿到，正文全军覆没。

- **环境里设了 `ALL_PROXY=socks5://...`**：httpx 会要求额外的 socks 支持，报
  `Using SOCKS proxy, but the 'socksio' package is not installed`。抓取层会自动
  降级到 curl / curl_cffi 不受影响，但**解读后端（codex / deepseek）走的是 httpx，
  会直接失败**。二选一：`uv pip install "httpx[socks]"`，或跑命令前
  `unset ALL_PROXY all_proxy`（HTTP 代理变量保留即可）。实测 unset 之后抓取
  从 97 秒降到 3.5 秒——不用每次都退到 curl_cffi 兜底了。

- **抓着抓着整站连不上**：openai.com 会按出口 IP 限流。抓太密时文章页、sitemap、
  RSS 会一起变成连接被 RST（`SSL_ERROR_SYSCALL`），几分钟后自动恢复。
  `net.py` 内置 2 秒最小请求间隔 + 连续失败 3 篇熔断来躲这个；网络环境更敏感就把
  `net.MIN_REQUEST_INTERVAL` 调大。**这种时候 edge-tts 往往也一起挂，
  别误判成 TTS 坏了。**

- **codex 撞周限额**：ChatGPT Pro 的周限额一撞就是好几天（响应体里的
  `resets_in_seconds` 实测有 51 万秒 ≈ 6 天）。autorun 会识别出来直接停下而不是
  睡等，这时候把 `.env` 的 `INTERPRET_PROVIDER` 换成 `claude` 或 `deepseek`
  继续跑就行，已完成的阶段不会重做。

- **Pages 切换分支后资源 404**：切 Pages source 之后 CDN 会缓存一段时间的 404
  （响应头里能看到 `x-cache: HIT` 和很大的 `age`）。
  `gh api -X POST repos/<owner>/<repo>/pages/builds` 触发一次重建即可。

- **别在流水线跑着的时候手改 `content/state.json`**：autorun 全程持有 state 的
  内存副本，它下一次 save 会把整个字典写回，你手上的修改会被静默抹掉。
  实测标了 3 篇 skipped，几分钟后全没了。要改就先停流水线。
  同理，不要并发跑两个 autorun——后 save 的那个会覆盖另一个的进度。

- **集数显示不对**：`weekly` 和 `publish` 都会自动刷新 CATALOG.md 与 README 进度。
  只跑了 `autorun` 的话进度不会动，手动补一条 `chatgpt-fm catalog` 即可。
