"""抓取文章正文 → content/<源>/articles/<slug>.md（frontmatter + markdown 正文）。"""

import re
from datetime import datetime

import trafilatura
import yaml

from . import config, net
from .sources import ArticleRef

_MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}
_HUMAN_DATE = r"([A-Z][a-z]{2,8})\.?\s+(\d{1,2}),\s+(\d{4})"


def _parse_english_date(text: str) -> str:
    """'Feb 11, 2026' / 'February 11, 2026' -> '2026-02-11'，解析失败返回空。"""
    m = re.search(_HUMAN_DATE, text)
    if not m:
        return ""
    mon = _MONTHS.get(m.group(1)[:3])
    if not mon:
        return ""
    return f"{m.group(3)}-{mon:02d}-{int(m.group(2)):02d}"


# 页面套话。注意：trafilatura 往往不保留文章自身的小节标题，不能按
# "标题到下一个标题"删整节，只能按段落精确剔除。
_BOILERPLATE_HEADING = re.compile(
    r"^#{1,6}\s*(Related (articles|posts|research)|Read more|More news|"
    r"Newsletter|Subscribe.*|Stay informed|Footnotes|Share this)\s*$",
    re.I,
)
_BOILERPLATE_TEXT = re.compile(
    r"(Delivered monthly to your inbox|"
    r"^Sign up (for|to) .{0,60}newsletter|"
    r"^(Switch to|Explore more) .{0,40}$)",
    re.I | re.M,
)


def _clean_markdown(markdown: str) -> str:
    paragraphs = re.split(r"\n\s*\n", markdown)
    out: list[str] = []
    drop_next = False
    for p in paragraphs:
        stripped = p.strip()
        if _BOILERPLATE_HEADING.match(stripped):
            drop_next = True  # 套话标题后紧跟的一段一并删
            continue
        if _BOILERPLATE_TEXT.search(stripped):
            drop_next = False
            continue
        if drop_next:
            drop_next = False
            continue
        out.append(stripped)
    return "\n\n".join(out).strip()


def _extract_published(html: str) -> str:
    """从 HTML 里提取发表日期，返回 'YYYY-MM-DD' 或 ''。

    只在 RSS 没给日期时才走这里（sitemap 兜底来的那几篇）。openai.com 的文章页
    上有多处日期（正文旁 + 页脚推荐位），所以优先认结构化字段，不认页面上
    随便一个 "Mon D, YYYY"，避免抓到推荐文章的日期。
    """
    # 锚点 1：JSON-LD / Next.js 数据里的结构化发表时间，最可靠
    m = re.search(r'"(?:datePublished|publishedAt|publish_date)"\s*:\s*"(\d{4}-\d{2}-\d{2})', html)
    if m:
        return m.group(1)
    # 锚点 2：<time datetime="2026-02-11...">
    m = re.search(r'<time[^>]+datetime="(\d{4}-\d{2}-\d{2})', html)
    if m:
        return m.group(1)
    # 锚点 3：og:published_time 之类的 meta
    m = re.search(r'<meta[^>]+(?:published_time|article:published)[^>]+content="(\d{4}-\d{2}-\d{2})', html)
    if m:
        return m.group(1)
    # 都没有就返回空（宁可标未知，不取页面随机日期瞎猜）
    return ""


def fetch_article(ref: ArticleRef) -> dict:
    """抓取并解析一篇文章，返回 {title, published, markdown, slug}。"""
    html = net.get_text(ref.url, timeout=60)

    markdown = trafilatura.extract(
        html,
        output_format="markdown",
        include_tables=True,
        include_links=False,
        favor_recall=True,
    )
    if not markdown or len(markdown) < 300:
        raise RuntimeError(f"正文提取失败或过短: {ref.url}")
    markdown = _clean_markdown(markdown)

    meta = trafilatura.extract_metadata(html)
    title = ref.title or (meta.title if meta and meta.title else "")
    if not title:
        m = re.search(r"<title>(.*?)</title>", html, re.S)
        title = m.group(1) if m else ref.url
    # 去掉站点名后缀，如 "标题 | OpenAI"
    title = re.sub(r"\s*[\\|]\s*OpenAI\s*$", "", title).strip()

    # RSS 的 pubDate 是官方发表时间，优先用；兜底才去 HTML 里找
    published = ref.published or _extract_published(html)

    return {
        "title": title,
        "published": published,
        "markdown": markdown,
        "slug": make_base(published, title),
    }


def make_base(published: str, title: str) -> str:
    """文件名：发表日期-文章完整标题（替换文件系统非法字符）。"""
    safe = re.sub(r'[\\/:*?"<>|]', " - ", title)
    safe = re.sub(r"\s+", " ", safe).strip().rstrip(".")
    return f"{published or '0000-00-00'}-{safe}"


def save_article(ref: ArticleRef, data: dict) -> None:
    frontmatter = {
        "title": data["title"],
        "url": ref.url,
        "source": ref.source,
        "category": ref.category,
        "published": data["published"],
        "fetched": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False).strip()
    path = config.article_path(ref.source, data["slug"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{fm}\n---\n\n{data['markdown']}\n", encoding="utf-8")


def read_with_frontmatter(path) -> tuple[dict, str]:
    """读取带 frontmatter 的 md 文件，返回 (meta, body)。"""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n+(.*)$", text, re.S)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)) or {}, m.group(2)
