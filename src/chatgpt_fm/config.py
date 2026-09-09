"""全局配置：数据源、模型、音色、时长目标。"""

import os
from pathlib import Path

# 项目根目录（src/chatgpt_fm/config.py -> 上三级）
ROOT = Path(__file__).resolve().parents[2]

CONTENT_DIR = ROOT / "content"
SAMPLES_DIR = CONTENT_DIR / "samples"
STATE_FILE = CONTENT_DIR / "state.json"
PROMPT_FILE = ROOT / "prompts" / "interpret.md"


def _load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key.startswith("export "):
            key = key.removeprefix("export ").strip()
        if not key:
            continue
        if (
            len(value) >= 2
            and value[0] == value[-1]
            and value[0] in {'"', "'"}
        ):
            value = value[1:-1]
        os.environ.setdefault(key, value)


def _env(name: str, default: str) -> str:
    return os.getenv(name, default).strip()


_load_env(ROOT / ".env")

# ── 数据源 ────────────────────────────────────────────────────────────────
# openai.com 的文章全部落在 https://openai.com/index/<slug>，靠 URL 前缀分不了源，
# 所以改用官方 RSS 的 <category> 来分：news/rss.xml 一次给出全站 1100+ 篇的
# 标题、链接、分类和**权威发表日期**（claude-fm 那种从 HTML 正则猜日期的活儿省了）。
# RSS 偶尔漏掉个别老文章，再用分类 sitemap 兜底补齐。
OPENAI_RSS = "https://openai.com/news/rss.xml"
OPENAI_SITEMAP = "https://openai.com/sitemap.xml"
ARTICLE_PREFIX = "https://openai.com/index/"

# 五个源。前四个逐篇做深度解读，news 按周聚合成「一周快讯」。
# dir 是该源在 content/ 下的子目录。
SOURCES = {
    "engineering": {
        "dir": "openai/engineering",
        "label": "🛠️ Engineering",
        "categories": ["Engineering", "API"],
    },
    "research": {
        "dir": "openai/research",
        "label": "🔬 Research",
        "categories": ["Research", "Publication"],
    },
    "product": {
        "dir": "openai/product",
        "label": "🚀 Product",
        "categories": ["Product", "Release", "ChatGPT"],
    },
    "safety": {
        "dir": "openai/safety",
        "label": "🛡️ Safety",
        "categories": ["Safety", "Safety & Alignment", "Security"],
    },
    "news": {
        "dir": "openai/news",
        "label": "📰 News 周报",
        # 公司动态、政策、客户故事等；单篇信息量薄，按周聚合更合适
        "categories": [
            "Company", "Global Affairs", "Story", "Startup", "AI Adoption",
            "Applied AI", "OpenAI Academy", "Guides", "Webinar",
            "Intelligence Age", "OpenAI on OpenAI",
        ],
    },
}

# 按周聚合成「一周快讯」的源（其余源逐篇深度解读）
DIGEST_SOURCE = "news"

# RSS <category> → 源名。未在表内或没有 category 的文章归入 news。
CATEGORY_SOURCE = {
    cat: name for name, src in SOURCES.items() for cat in src["categories"]
}
DEFAULT_SOURCE = "news"

# RSS 兜底：分类 sitemap 的名字 → 等价的 RSS category。
# 仅用于补齐 RSS 里没有的少量老文章（dall-e-2、introducing-gpt-4-5 等）。
SITEMAP_CATEGORIES = {
    "engineering": "Engineering",
    "api": "API",
    "research": "Research",
    "publication": "Publication",
    "product": "Product",
    "release": "Release",
    "milestone": "Product",
    "safety": "Safety",
    "security": "Security",
    "company": "Company",
    "global-affairs": "Global Affairs",
}


def source_of_category(category: str) -> str:
    """RSS 分类名 → 源名；未知分类归 news。"""
    return CATEGORY_SOURCE.get(category.strip(), DEFAULT_SOURCE)


def source_dir(source: str) -> Path:
    return CONTENT_DIR / SOURCES.get(source, {}).get("dir", source)


def article_path(source: str, base: str) -> Path:
    return source_dir(source) / "articles" / f"{base}.md"


def script_path(source: str, base: str) -> Path:
    return source_dir(source) / "scripts" / f"{base}.md"


def audio_path(source: str, base: str) -> Path:
    return source_dir(source) / "audio" / f"{base}.mp3"


def episode_path(source: str, base: str) -> Path:
    return source_dir(source) / "episodes" / f"{base}.md"


def ensure_source_dirs(source: str) -> None:
    for sub in ("articles", "scripts", "audio", "episodes"):
        (source_dir(source) / sub).mkdir(parents=True, exist_ok=True)


# ── 解读模型 ──────────────────────────────────────────────────────────────
# 实际值从 .env 读取；没有 .env 时使用这些默认值。
INTERPRET_PROVIDER = _env("INTERPRET_PROVIDER", "codex").lower()

# Codex Responses（读 ~/.codex/auth.json，走本机 codex login 的 ChatGPT OAuth）
CODEX_MODEL = _env("CODEX_MODEL", "gpt-5.5")
CODEX_REASONING_EFFORT = _env("CODEX_REASONING_EFFORT", "high")
CODEX_TIMEOUT = 1200

# Claude CLI 备用（claude -p 无头模式，走订阅）
CLAUDE_MODEL = _env("CLAUDE_MODEL", "claude-sonnet-4-6")
CLAUDE_TIMEOUT = 1200  # 单篇解读超时（秒）；开深度思考后更慢，放宽到 20 分钟
# 推理强度：Claude CLI 靠 prompt 里的触发词分配思考预算（环境变量无效）。
# 取值：""=关闭、"think hard"=较深、"ultrathink"=最深。会附加到每次解读 prompt 末尾。
CLAUDE_REASONING_EFFORT = _env("CLAUDE_REASONING_EFFORT", "ultrathink")

# DeepSeek API（OpenAI 兼容格式）
DEEPSEEK_API_KEY = _env("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = _env("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = _env("DEEPSEEK_MODEL", "deepseek-v4-pro")
DEEPSEEK_REASONING_EFFORT = _env("DEEPSEEK_REASONING_EFFORT", "high")
DEEPSEEK_THINKING = _env("DEEPSEEK_THINKING", "enabled")
DEEPSEEK_TIMEOUT = 1200


def interpret_model() -> str:
    if INTERPRET_PROVIDER == "codex":
        return CODEX_MODEL
    if INTERPRET_PROVIDER == "deepseek":
        return DEEPSEEK_MODEL
    return CLAUDE_MODEL


# ── TTS ───────────────────────────────────────────────────────────────────
# 运行 `chatgpt-fm voices` 生成试听样品后，把选中的音色填到这里。
# TTS_VOICE 用于音色试听样品；正式合成在 TTS_VOICES 里轮换，避免一个声音听腻。
TTS_VOICE = "zh-CN-XiaoxiaoNeural"
TTS_VOICES = [
    "zh-CN-YunxiNeural",     # 男声，轻快
    "zh-CN-YunyangNeural",   # 男声，播报腔
]
TTS_RATE = "+0%"  # 语速微调，如 "+10%" / "-5%"
VOICE_CANDIDATES = {
    "zh-CN-YunxiNeural": "男声，自然轻快",
    "zh-CN-YunyangNeural": "男声，新闻播报腔",
    "zh-CN-XiaoxiaoNeural": "女声，最通用",
    "zh-CN-XiaoyiNeural": "女声，柔和",
}

# ── 播客发布（全部托管在 GitHub Pages 上，不需要自己的服务器）────────────
# 站点产物（feed.xml + 目录页 + 封面 + 全部音频）发布到独立的 gh-pages 分支，
# main 分支只留代码和文字稿，clone 依然轻量。
#
# 音频为什么不能放 GitHub Release：Release 的下载地址返回
#   content-type: application/octet-stream
#   content-disposition: attachment; filename=EP1.mp3
# attachment 是致命的——它告诉客户端"这是要下载保存的附件"，播放器据此拒绝
# 内联播放，Apple Podcasts 上表现为「无法播放」。Pages 对 .mp3 返回
# audio/mp3、不带 content-disposition、支持 Range，才是播客要的。
#
# 代价：Pages 单站点上限 1GB，按单集约 9MB 算大概 111 集封顶。超了就把音频
# 挪到对象存储，改 AUDIO_BASE_URL 一个变量即可，feed 逻辑不用动。
GITHUB_OWNER = _env("GITHUB_OWNER", "zhou-1314")
GITHUB_REPO = _env("GITHUB_REPO", "chatgpt-fm")
PAGES_BRANCH = _env("PAGES_BRANCH", "gh-pages")

# Pages 站点根：feed.xml、index.html、cover.jpg 都在这
FEED_BASE_URL = _env(
    "FEED_BASE_URL", f"https://{GITHUB_OWNER}.github.io/{GITHUB_REPO}"
)
# 音频前缀：站点下的 audio/ 子目录
AUDIO_BASE_URL = _env("AUDIO_BASE_URL", f"{FEED_BASE_URL}/audio")

# 本地站点构建目录（不入库，publish 时同步到 gh-pages 分支）
SITE_DIR = ROOT / ".site"
# 封面源图放在仓库里，publish 时复制进站点
COVER_SOURCE = ROOT / "assets" / "cover.jpg"

PODCAST_TITLE = "ChatGPT FM"
PODCAST_DESCRIPTION = (
    "把 OpenAI 官网的前沿技术内容做成中文解读：模型发布、Codex 与智能体工程、"
    "对齐与安全研究、产品与 API 更新……通勤、健身随时听，用碎片时间积累最前沿的 AI 知识。"
    "原文版权归 OpenAI，中文解读由 AI 模型生成，仅供学习。"
)
PODCAST_AUTHOR = "ChatGPT FM"
PODCAST_EMAIL = "liguangpeng9495@gmail.com"
PODCAST_COVER = f"{FEED_BASE_URL}/cover.jpg"     # docs/cover.jpg，1400×1400
PODCAST_CATEGORY = "Technology"
PODCAST_LANGUAGE = "zh-cn"

# 时长告警阈值（分钟）。这是**异常检测**，不是质量门槛——超了不用管，
# 只是提醒去看一眼是不是模型输出崩了。
#
# 别把它设窄：实测前 10 集时长均值 26.3 分钟、标准差 2.9 分钟
# （汉字数 5583-7960，均值 6854）。模型对 prompt 里的字数指令只在均值上
# 服从，单集方差压不下去，把区间设成 22-28（宽度 6 分钟，比 ±1σ 还窄）
# 的结果是 10 集里 6 集误报。放到约 ±2σ，才只在真出问题时响。
DURATION_MIN = 20
DURATION_MAX = 32

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
# curl_cffi 的浏览器指纹档位。openai.com 挂了 Cloudflare 机器人校验，普通
# httpx/curl 会吃 403，必须用真实 Chrome 的 TLS 指纹才拿得到正文。
IMPERSONATE = "chrome"


def audio_asset_name(episode_no: int) -> str:
    """音频在 GitHub Release 里的附件名。

    不能直接用 slug：slug 里有空格、中文和 ’ 这类字符，GitHub 上传时会自己改名，
    改完的下载地址对不上 feed 里写的 URL。用集号最稳——ASCII、唯一、集号一旦
    分配就不再变。
    """
    return f"EP{episode_no}.mp3"


def audio_url(episode_no: int) -> str:
    return f"{AUDIO_BASE_URL}/{audio_asset_name(episode_no)}"


def ensure_dirs() -> None:
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
