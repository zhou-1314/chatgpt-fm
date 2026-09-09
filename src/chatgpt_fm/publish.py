"""发布到 GitHub Pages：站点产物（feed + 目录页 + 封面 + 音频）推到 gh-pages 分支。

为什么音频也走 Pages 而不是 Release：Release 的下载地址带
`content-disposition: attachment` 且 content-type 是 application/octet-stream，
播放器会当成"要下载的附件"而拒绝内联播放（Apple Podcasts 上就是「无法播放」）。
Pages 对 .mp3 返回 audio/mp3、不带 disposition、支持 Range，才是播客要的。

站点单独放 gh-pages 分支，main 保持纯文本，clone 不会被几百 MB 音频拖累。
音频在站点里一律按集号命名（EP12.mp3）：slug 里有空格、中文和 ’，直接做 URL
要转义，集号是 ASCII、唯一、分配后不再变。
"""

import shutil
import subprocess
import tempfile
from html import escape
from pathlib import Path

from . import config, state


class GitHubCliError(RuntimeError):
    """git / gh 子命令失败。"""


def _repo() -> str:
    return f"{config.GITHUB_OWNER}/{config.GITHUB_REPO}"


# ── 收集音频 ─────────────────────────────────────────────────────────────

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


def sync_audio(site_dir: Path, dry_run: bool = False) -> tuple[int, int]:
    """把本地音频按集号复制进站点的 audio/。返回 (新增或更新数, 跳过数)。

    同名同大小就跳过——几百集全量复制一遍既慢又会让 git 认为文件都变了。
    """
    audio_dir = site_dir / "audio"
    if not dry_run:
        audio_dir.mkdir(parents=True, exist_ok=True)
    copied = skipped = 0
    for e in collect_audio(state.load()):
        dest = audio_dir / config.audio_asset_name(e["ep"])
        size = e["path"].stat().st_size
        if dest.exists() and dest.stat().st_size == size:
            skipped += 1
            continue
        print(f"  + EP{e['ep']:<5} {dest.name:<12} {size / 1024 / 1024:6.1f} MB  {e['slug'][:42]}")
        if not dry_run:
            shutil.copyfile(e["path"], dest)
        copied += 1
    return copied, skipped


# ── 推送到 gh-pages 分支 ─────────────────────────────────────────────────

def push_site(site_dir: Path, branch: str, message: str) -> str:
    """把 site_dir 的内容提交并推送到 branch。

    用 git worktree 挂一个独立工作区，不碰主工作区（流水线可能正在写 content/）。
    分支不存在就建成 orphan，历史从头开始。
    """
    worktree = Path(tempfile.mkdtemp(prefix="chatgpt-fm-pages-"))
    worktree.rmdir()  # git worktree add 要求目标不存在
    remote_exists = _git("ls-remote", "--heads", "origin", branch).strip() != ""
    try:
        if remote_exists:
            _git("fetch", "origin", f"{branch}:{branch}", check=False)
            _git("worktree", "add", str(worktree), branch)
        else:
            _git("worktree", "add", "--detach", str(worktree))
            _git("-C", str(worktree), "checkout", "--orphan", branch)
            _git("-C", str(worktree), "rm", "-rf", "--quiet", ".", check=False)

        _mirror(site_dir, worktree)
        _git("-C", str(worktree), "add", "-A")
        status = _git("-C", str(worktree), "status", "--porcelain")
        if not status.strip():
            return "站点内容没有变化，跳过提交"
        _git("-C", str(worktree), "-c", "user.name=zhou-1314",
             "-c", "user.email=zhouwg1314@gmail.com", "commit", "-q", "-m", message)
        _git("-C", str(worktree), "push", "-q", "origin", f"HEAD:{branch}")
        return f"已推送到 {branch}（{len(status.strip().splitlines())} 个文件变更）"
    finally:
        _git("worktree", "remove", "--force", str(worktree), check=False)
        shutil.rmtree(worktree, ignore_errors=True)


def _mirror(src: Path, dest: Path) -> None:
    """把 src 的内容同步到 dest，删掉 dest 里多余的文件（.git 除外）。"""
    for item in dest.iterdir():
        if item.name == ".git":
            continue
        shutil.rmtree(item) if item.is_dir() else item.unlink()
    for item in src.iterdir():
        target = dest / item.name
        shutil.copytree(item, target) if item.is_dir() else shutil.copyfile(item, target)


def _git(*args: str, check: bool = True) -> str:
    proc = subprocess.run(["git", *args], capture_output=True, text=True, cwd=config.ROOT)
    if check and proc.returncode != 0:
        raise GitHubCliError(
            f"git {' '.join(args[:4])} 失败（exit {proc.returncode}）：\n"
            f"{(proc.stderr or proc.stdout).strip()[:600]}")
    return proc.stdout


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
    """生成站点：feed.xml、index.html、封面、.nojekyll。返回 (站点目录, 集数)。"""
    from . import catalog, feed

    config.SITE_DIR.mkdir(parents=True, exist_ok=True)
    _, n = feed.write_feed()
    by_src = catalog._all(state.load())
    (config.SITE_DIR / "index.html").write_text(build_index(by_src), encoding="utf-8")
    # 没有这个文件 Pages 会用 Jekyll 处理站点，下划线开头的资源会被吞掉
    (config.SITE_DIR / ".nojekyll").touch()
    if config.COVER_SOURCE.exists():
        shutil.copyfile(config.COVER_SOURCE, config.SITE_DIR / "cover.jpg")
    return config.SITE_DIR, n
