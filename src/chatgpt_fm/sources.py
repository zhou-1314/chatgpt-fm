"""文章发现：openai.com 官方 RSS（主）+ 分类 sitemap（兜底）。

openai.com 的文章不分路径前缀，全在 https://openai.com/index/<slug>，所以分源
靠的是 RSS 里的 <category>。RSS 一次就给出 title / link / category / pubDate，
发表日期是官方给的，不用再从 HTML 里正则猜。
"""

import re
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime

from . import config, net


@dataclass
class ArticleRef:
    url: str
    source: str
    # RSS 能直接给出的元数据（sitemap 兜底来的那几篇拿不到，抓正文时再补）
    title: str = ""
    published: str = ""  # YYYY-MM-DD
    summary: str = ""    # RSS <description>，一句话摘要
    category: str = ""   # RSS 原始分类，落进 frontmatter 便于回溯


def _cdata(text: str) -> str:
    """去掉 <![CDATA[...]]> 包装并做最基本的实体还原。"""
    m = re.match(r"\s*<!\[CDATA\[(.*?)\]\]>\s*$", text, re.S)
    value = m.group(1) if m else text
    for entity, char in (("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'),
                         ("&#39;", "'"), ("&amp;", "&")):
        value = value.replace(entity, char)
    return value.strip()


def _tag(item: str, name: str) -> str:
    m = re.search(rf"<{name}[^>]*>(.*?)</{name}>", item, re.S)
    return _cdata(m.group(1)) if m else ""


def normalize_url(url: str) -> str:
    """RSS 给的链接没有尾斜杠，sitemap 有；统一成无尾斜杠，避免同一篇算两条。"""
    return url.strip().rstrip("/")


def _rfc822_date(raw: str) -> str:
    """'Wed, 11 Feb 2026 09:00:00 GMT' -> '2026-02-11'，解析失败返回空。"""
    if not raw:
        return ""
    try:
        return parsedate_to_datetime(raw).date().isoformat()
    except (TypeError, ValueError):
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", raw)
        return m.group(0) if m else ""


def parse_rss(xml: str) -> list[ArticleRef]:
    """解析 openai.com/news/rss.xml，返回全部文章（已按分类分好源）。"""
    refs: list[ArticleRef] = []
    for item in re.findall(r"<item>(.*?)</item>", xml, re.S):
        url = normalize_url(_tag(item, "link"))
        if not url.startswith(config.ARTICLE_PREFIX):
            continue
        categories = [_cdata(c) for c in
                      re.findall(r"<category[^>]*>(.*?)</category>", item, re.S)]
        category = categories[0] if categories else ""
        refs.append(ArticleRef(
            url=url,
            source=config.source_of_category(category),
            title=_tag(item, "title"),
            published=_rfc822_date(_tag(item, "pubDate")),
            summary=_tag(item, "description"),
            category=category,
        ))
    return refs


def parse_sitemap_urls(xml: str) -> list[str]:
    """从 sitemap 里挑出 /index/<slug> 文章链接（忽略栏目页和多语言 alternate）。"""
    urls = []
    for loc in re.findall(r"<loc>\s*(.*?)\s*</loc>", xml, re.S):
        url = normalize_url(loc)
        if url.startswith(config.ARTICLE_PREFIX) and "/" not in url[len(config.ARTICLE_PREFIX):]:
            urls.append(url)
    return urls


def discover_rss() -> list[ArticleRef]:
    return parse_rss(net.get_text(config.OPENAI_RSS, timeout=60))


def discover_sitemap_extras(known: set[str]) -> list[ArticleRef]:
    """RSS 会漏掉个别老文章（dall-e-2、introducing-gpt-4-5 等）。
    逐个分类 sitemap 捞一遍，只补 known 里没有的；分类由 sitemap 名字推出。
    单个 sitemap 取不到就跳过，不影响整体发现。"""
    extras: dict[str, ArticleRef] = {}
    for tag, category in config.SITEMAP_CATEGORIES.items():
        try:
            xml = net.get_text(f"{config.OPENAI_SITEMAP}/{tag}/", timeout=60)
        except RuntimeError as exc:
            print(f"  ⚠️ sitemap {tag} 取不到，跳过：{str(exc)[:120]}", flush=True)
            continue
        for url in parse_sitemap_urls(xml):
            if url in known or url in extras:
                continue
            extras[url] = ArticleRef(
                url=url,
                source=config.source_of_category(category),
                category=category,
            )
    return list(extras.values())


def discover_all(with_sitemap: bool = True) -> dict[str, list[ArticleRef]]:
    """返回 {source: [ArticleRef]}，全量（不与 state 求差）。新文章排在前面。"""
    refs = discover_rss()
    if with_sitemap:
        refs += discover_sitemap_extras({r.url for r in refs})

    result: dict[str, list[ArticleRef]] = {name: [] for name in config.SOURCES}
    for ref in refs:
        result.setdefault(ref.source, []).append(ref)
    for items in result.values():
        # 有日期的按日期倒序排前面；sitemap 兜底来的没日期，排到最后
        items.sort(key=lambda r: r.published or "0000-00-00", reverse=True)
    return result


def source_of_url(url: str, refs: dict[str, list[ArticleRef]] | None = None) -> str:
    """给定文章 URL 反查它属于哪个源（`run --url` 用）。查不到归 DEFAULT_SOURCE。"""
    target = normalize_url(url)
    for name, items in (refs or discover_all()).items():
        if any(r.url == target for r in items):
            return name
    return config.DEFAULT_SOURCE


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")
