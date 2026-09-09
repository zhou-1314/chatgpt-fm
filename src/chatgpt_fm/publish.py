"""发布到 GitHub：音频传 Release 附件，feed.xml + 目录页写进 docs/ 供 Pages 提供。

为什么这么分：
  - GitHub Pages 单站点上限 1GB，几百集 mp3（claude-fm 同规模约 1.7GB）放不下；
  - Release 附件单文件上限 2GB、总量不设限，正好托音频；
  - 于是 docs/ 只放几十 KB 的 feed.xml 和 index.html，音频走 Release 下载地址。

音频附件一律按集号命名（EP12.mp3）。slug 里有空格、中文和 ’，GitHub 上传时会
自己改名，改完的地址和 feed 里写的对不上；集号是 ASCII、唯一、分配后不再变。
"""

import json
import shutil
import subprocess
import tempfile
from html import escape
from pathlib import Path

from . import config, state


class GitHubCliError(RuntimeError):
    pass


def _gh(*args: str, check: bool = True) -> str:
    """跑一条 gh 命令，返回 stdout。"""
    proc = subprocess.run(
        ["gh", *args], capture_output=True, text=True,
        cwd=config.ROOT,
    )
    if check and proc.returncode != 0:
        raise GitHubCliError(
            f"gh {' '.join(args)} 失败（exit {proc.returncode}）：\n"
            f"{(proc.stderr or proc.stdout).strip()[:600]}"
        )
    return proc.stdout


def _repo() -> str:
    return f"{config.GITHUB_OWNER}/{config.GITHUB_REPO}"


# ── 音频 → Release 附件 ───────────────────────────────────────────────────

def collect_audio(st: dict) -> list[dict]:
    """已打包且音频文件在本地的集，返回 [{ep, source, slug, path}]，按集号排序。"""
    out = []
    records = [(a.get("source"), a) for a in st["articles"].values()]
    records += [(config.DIGEST_SOURCE, d) for d in st.get("digests", {}).values()]
    for source, rec in records:
        if not source or not rec.get("stages", {}).get("packaged") or "episode" not in rec:
            continue
        path = config.audio_path(source, rec["slug"])
        if not path.exists():
            continue
        out.append({"ep": rec["episode"], "source": source,
                    "slug": rec["slug"], "path": path})
    out.sort(key=lambda x: x["ep"])
    return out


def ensure_release(tag: str) -> None:
    """Release 不存在就建一个。已存在则原样保留（附件都挂在它下面）。"""
    proc = subprocess.run(
        ["gh", "release", "view", tag, "--repo", _repo()],
        capture_output=True, text=True, cwd=config.ROOT,
    )
    if proc.returncode == 0:
        return
    _gh("release", "create", tag,
        "--repo", _repo(),
        "--title", f"{config.PODCAST_TITLE} 音频",
        "--notes",
        f"{config.PODCAST_TITLE} 的全部单集音频，按集号命名（EP<n>.mp3）。\n\n"
        f"订阅地址：{config.FEED_BASE_URL}/feed.xml\n\n"
        "音频由 edge-tts 合成，原文版权归 OpenAI。")


def release_assets(tag: str) -> dict[str, int]:
    """Release 上已有的附件 {名字: 字节数}。Release 不存在返回空。"""
    proc = subprocess.run(
        ["gh", "release", "view", tag, "--repo", _repo(), "--json", "assets"],
        capture_output=True, text=True, cwd=config.ROOT,
    )
    if proc.returncode != 0:
        return {}
    assets = json.loads(proc.stdout or "{}").get("assets") or []
    return {a["name"]: a.get("size", 0) for a in assets}


def upload_audio(tag: str, dry_run: bool = False) -> tuple[int, int]:
    """把本地新增/变更的音频传上 Release。返回 (上传数, 跳过数)。"""
    st = state.load()
    episodes = collect_audio(st)
    if not episodes:
        return 0, 0
    if not dry_run:
        ensure_release(tag)
    existing = release_assets(tag)

    uploaded = skipped = 0
    with tempfile.TemporaryDirectory() as tmp:
        for e in episodes:
            name = config.audio_asset_name(e["ep"])
            size = e["path"].stat().st_size
            if existing.get(name) == size:      # 同名同大小，认为已是最新
                skipped += 1
                continue
            print(f"  ↑ EP{e['ep']:<5} {name:<12} {size / 1024 / 1024:6.1f} MB  {e['slug'][:44]}")
            if dry_run:
                uploaded += 1
                continue
            # gh 用文件名当附件名，所以先复制成目标名再传
            staged = Path(tmp) / name
            shutil.copyfile(e["path"], staged)
            _gh("release", "upload", tag, str(staged),
                "--repo", _repo(), "--clobber")
            staged.unlink()
            uploaded += 1
    return uploaded, skipped


# ── Pages 目录页 ─────────────────────────────────────────────────────────

_INDEX_CSS = """
:root { color-scheme: light dark; --fg:#111; --muted:#666; --bg:#fff; --line:#e5e5e5; --accent:#0b7; }
@media (prefers-color-scheme: dark) {
  :root { --fg:#e8e8e8; --muted:#9a9a9a; --bg:#131313; --line:#2c2c2c; --accent:#1db954; }
}
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--fg); font:16px/1.7 -apple-system,BlinkMacSystemFont,
       "Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif; }
.wrap { max-width: 860px; margin: 0 auto; padding: 48px 20px 80px; }
h1 { font-size: 2rem; margin: 0 0 .3em; }
.tagline { color: var(--muted); margin: 0 0 1.6em; }
.sub { background: rgba(127,127,127,.08); border:1px solid var(--line); border-radius:10px;
       padding:16px 18px; margin-bottom:2.2em; }
.sub code { display:block; overflow-x:auto; padding:10px 12px; margin-top:8px;
            background: rgba(127,127,127,.12); border-radius:6px; font-size:.9rem; }
h2 { font-size:1.15rem; margin:2.2em 0 .6em; padding-bottom:.35em; border-bottom:1px solid var(--line); }
ul { list-style:none; padding:0; margin:0; }
li { padding:.45em 0; border-bottom:1px solid var(--line); display:flex; gap:.7em; flex-wrap:wrap; align-items:baseline; }
.ep { color:var(--accent); font-variant-numeric:tabular-nums; font-weight:600; min-width:4.5em; }
.date { color:var(--muted); font-size:.85rem; font-variant-numeric:tabular-nums; }
a { color:inherit; }
a.title { text-decoration:none; border-bottom:1px solid transparent; flex:1; min-width:14em; }
a.title:hover { border-bottom-color:var(--accent); }
.links a { color:var(--muted); font-size:.82rem; text-decoration:none; margin-left:.6em; }
.links a:hover { color:var(--accent); }
footer { margin-top:3em; padding-top:1.4em; border-top:1px solid var(--line); color:var(--muted); font-size:.85rem; }
"""


def _blob(path: str) -> str:
    """仓库文件在 GitHub 上的网页地址。"""
    from urllib.parse import quote
    return f"https://github.com/{_repo()}/blob/main/{quote(path)}"


def build_index(by_src: dict) -> str:
    """用 catalog 的分组数据渲染 Pages 首页。"""
    total = sum(len(v) for v in by_src.values())
    parts = [
        "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">",
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        f"<title>{escape(config.PODCAST_TITLE)}</title>",
        f'<meta name="description" content="{escape(config.PODCAST_DESCRIPTION[:150])}">',
        f'<link rel="alternate" type="application/rss+xml" title="{escape(config.PODCAST_TITLE)}" '
        f'href="{config.FEED_BASE_URL}/feed.xml">',
        f"<style>{_INDEX_CSS}</style></head><body><div class=\"wrap\">",
        f"<h1>{escape(config.PODCAST_TITLE)} 📻</h1>",
        '<p class="tagline">把 OpenAI 官网发布的技术博客，转成中文音频解读。'
        f"目前共 <strong>{total}</strong> 集。</p>",
        '<div class="sub"><strong>用任意播客 App 订阅</strong>（小宇宙、Apple Podcasts、'
        f'Pocket Casts…）：<code>{config.FEED_BASE_URL}/feed.xml</code></div>',
    ]
    for name, src in config.SOURCES.items():
        items = by_src.get(name) or []
        if not items:
            continue
        parts.append(f"<h2>{escape(src['label'])}（{len(items)}）</h2><ul>")
        for e in sorted(items, key=lambda x: (x["date"], x["ep"]), reverse=True):
            links = [f'<a href="{config.audio_url(e["ep"])}">音频</a>']
            # catalog 给的是 quote 过的仓库相对路径，直接拼成 GitHub 网页地址
            links.insert(0, f'<a href="https://github.com/{_repo()}/blob/main/{e["link"]}">中文稿</a>')
            if e.get("article"):
                links.append(f'<a href="https://github.com/{_repo()}/blob/main/{e["article"]}">英文原文</a>')
            parts.append(
                f'<li><span class="ep">EP{e["ep"]}</span>'
                f'<a class="title" href="https://github.com/{_repo()}/blob/main/{e["link"]}">'
                f'{escape(e["title"])}</a>'
                f'<span class="date">{e["date"]}</span>'
                f'<span class="links">{"".join(links)}</span></li>'
            )
        parts.append("</ul>")
    if total == 0:
        parts.append("<p>还没有已发布的单集。先在本地跑 <code>chatgpt-fm weekly</code>，"
                     "再跑 <code>chatgpt-fm publish</code>。</p>")
    parts += [
        f'<footer>本项目为个人非商业的学习用途整理，与 OpenAI 无任何官方关联。'
        f'原文版权归 <a href="https://openai.com">OpenAI</a> 所有；'
        f'中文解读由 AI 模型生成，仅供学习参考。'
        f'<br><a href="https://github.com/{_repo()}">源码与全部文字稿在 GitHub</a>'
        f' · <a href="{config.FEED_BASE_URL}/feed.xml">RSS</a></footer>',
        "</div></body></html>",
    ]
    return "\n".join(parts)


def write_site() -> tuple[Path, int]:
    """生成 docs/feed.xml 与 docs/index.html。返回 (docs 目录, 集数)。"""
    from . import catalog, feed

    config.SITE_DIR.mkdir(parents=True, exist_ok=True)
    _, n = feed.write_feed()
    by_src = catalog._all(state.load())
    (config.SITE_DIR / "index.html").write_text(build_index(by_src), encoding="utf-8")
    # 没有这个文件 Pages 会把 docs/ 当 Jekyll 源码处理，下划线开头的资源会被吞掉
    (config.SITE_DIR / ".nojekyll").touch()
    return config.SITE_DIR, n
