"""chatgpt-fm 命令行入口。

  chatgpt-fm discover                      列出各源文章数与新文章
  chatgpt-fm run [--source X] [--limit N] [--url URL]   端到端流水线
  chatgpt-fm publish                       发布到 GitHub Pages（站点→gh-pages 分支）
  chatgpt-fm voices                        生成音色试听样品
  chatgpt-fm status                        显示各篇进度
"""

import argparse
import sys
from datetime import date, timedelta

from . import config, episode, fetch, interpret, sources, state, tts


# 连续失败到这个数就停手：多半是网络/限流，不是单篇文章的问题
MAX_CONSECUTIVE_FAILURES = 3


def _deep_sources() -> list[str]:
    """逐篇深度解读的源（周报源之外的全部）。"""
    return [s for s in config.SOURCES if s != config.DIGEST_SOURCE]


def _previous_week_window() -> tuple[str, str]:
    """返回上一个完整周日-周六窗口，YYYY-MM-DD。"""
    today = date.today()
    this_sunday = today - timedelta(days=(today.weekday() + 1) % 7)
    start = this_sunday - timedelta(days=7)
    end = this_sunday - timedelta(days=1)
    return start.isoformat(), end.isoformat()


def _in_date_window(published: str, start: str | None, end: str | None) -> bool:
    if not start or not end or not published:
        return True
    day = published[:10]
    return start <= day <= end


def cmd_discover(args) -> None:
    st = state.load()
    known = set(st["articles"].keys())
    all_refs = sources.discover_all()
    print(f"{'源':<14}{'总数':>6}{'新文章':>8}")
    for name, refs in all_refs.items():
        new = [r for r in refs if r.url not in known]
        print(f"{name:<14}{len(refs):>6}{len(new):>8}")
        for r in new[: args.show]:
            print(f"    {r.url}")
        if len(new) > args.show:
            print(f"    ... 还有 {len(new) - args.show} 篇")


def _pipeline_one(
    ref: sources.ArticleRef,
    st: dict,
    published_start: str | None = None,
    published_end: str | None = None,
) -> bool:
    """单篇文章走完 抓取→解读→TTS→上传包，幂等：完成的阶段跳过。"""
    art = state.get_article(st, ref.url)
    art["source"] = ref.source
    stages = art["stages"]

    # 1. 抓取
    if not stages.get("fetched"):
        print(f"  [1/4] 抓取原文 {ref.url}")
        try:
            data = fetch.fetch_article(ref)
        except Exception:
            # get_article 是 setdefault，上面这一步已经把空壳记进 state 了。
            # 抓取失败就把它摘掉，否则 discover 会把这些 URL 当成"已处理过"，
            # 新文章数从此对不上。
            if not art.get("slug"):
                st["articles"].pop(ref.url, None)
            raise
        if not _in_date_window(data["published"], published_start, published_end):
            print(
                f"        跳过，发布日期 {data['published'] or '未知'} 不在 "
                f"{published_start}–{published_end}",
                flush=True,
            )
            st["articles"].pop(ref.url, None)
            return False
        fetch.save_article(ref, data)
        art.update(slug=data["slug"], title=data["title"], published=data["published"])
        stages["fetched"] = True
        state.save(st)
    elif not _in_date_window(art.get("published", ""), published_start, published_end):
        return False
    slug = art["slug"]

    article_path = config.article_path(ref.source, slug)
    meta, body = fetch.read_with_frontmatter(article_path)

    # 2. 解读
    if not stages.get("interpreted"):
        print(f"  [2/4] 模型生成解读稿（{config.interpret_model()}，可能需要几分钟）...")
        result = interpret.interpret(meta, body, slug)
        print(f"        完成，{interpret.han_count(result['script'])} 个汉字")
        stages["interpreted"] = True
        state.save(st)

    script_path = config.script_path(ref.source, slug)
    script_meta, script_body = fetch.read_with_frontmatter(script_path)

    # 3. TTS
    audio_path = config.audio_path(ref.source, slug)
    if not stages.get("synthesized"):
        # 音色轮换：未合成过的文章按全局计数器交替选音色，并记到 state，重跑时沿用
        voice = art.get("voice")
        if not voice:
            idx = st.get("voice_rotation", 0)
            voice = config.TTS_VOICES[idx % len(config.TTS_VOICES)]
            st["voice_rotation"] = idx + 1
            art["voice"] = voice
        print(f"  [3/4] edge-tts 合成（{voice}）...")
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        duration = tts.synthesize(tts.extract_script(script_body), audio_path, voice=voice)
        art["duration_sec"] = round(duration, 1)
        stages["synthesized"] = True
        state.save(st)
        mins = duration / 60
        flag = "" if config.DURATION_MIN <= mins <= config.DURATION_MAX else "  ⚠️ 超出 22-28 分钟目标"
        print(f"        完成，时长 {mins:.1f} 分钟{flag}")

    # 4. 上传包
    if not stages.get("packaged"):
        ep_no = state.assign_episode(st, ref.url)
        episode.write_episode(
            slug=slug,
            episode_no=ep_no,
            episode_title=script_meta.get("episode_title", art.get("title", slug)),
            shownotes=tts.extract_shownotes(script_body),
            article_meta=meta,
            duration_sec=art.get("duration_sec", 0),
        )
        stages["packaged"] = True
        state.save(st)
        ep_rel = config.episode_path(ref.source, slug).relative_to(config.ROOT)
        print(f"  [4/4] 上传包就绪: {ep_rel}（EP{ep_no}）")
    return True


def _collect_refs(
    st,
    source=None,
    limit=None,
    url=None,
    published_start: str | None = None,
    published_end: str | None = None,
) -> list:
    """收集待处理文章（未完成 packaged 的）。"""
    if url:
        # openai.com 文章全在 /index/ 下，URL 本身看不出分类，回 RSS 里反查
        all_refs = sources.discover_all()
        target = sources.normalize_url(url)
        for items in all_refs.values():
            for r in items:
                if r.url == target:
                    return [r]
        return [sources.ArticleRef(url=target, source=config.DEFAULT_SOURCE)]

    all_refs = sources.discover_all()
    refs = []
    for name, source_refs in all_refs.items():
        if source and name != source:
            continue
        # 周报源不走单篇解读（由 `chatgpt-fm news` 按周聚合），
        # 除非显式 --source news 指名要它
        if not source and name == config.DIGEST_SOURCE:
            continue
        refs.extend(
            r for r in source_refs
            if not st["articles"].get(r.url, {}).get("stages", {}).get("packaged")
            and _in_date_window(
                st["articles"].get(r.url, {}).get("published", ""),
                published_start,
                published_end,
            )
        )
    # discover_all 已按发表日期倒序（新文章在前），limit 取最前面的
    return refs[:limit] if limit else refs


def _run_batch(refs, st, published_start: str | None = None, published_end: str | None = None):
    """跑一批文章。返回 (完成数, 失败列表, 限额异常或 None)。
    撞限额时立即停止剩余文章并把 SessionLimitError 上报。"""
    ok, skipped, failed = 0, 0, []
    consecutive = 0
    for i, ref in enumerate(refs, 1):
        print(f"[{i}/{len(refs)}] {ref.url}")
        try:
            if _pipeline_one(ref, st, published_start, published_end):
                ok += 1
            else:
                skipped += 1
            consecutive = 0
        except interpret.SessionLimitError as e:
            kind = "周限额" if e.weekly else "会话限额"
            print(f"  ⏸ 撞{kind}，暂停（重置: {e.reset_raw or '未知'}）", file=sys.stderr)
            return ok, failed, e
        except Exception as e:
            failed.append((ref.url, str(e)))
            print(f"  ❌ 失败: {e}", file=sys.stderr)
            consecutive += 1
            # 连续失败多半是网络/限流这类全局问题（实测 openai.com 会因抓太密
            # 而整站拒连），继续一篇篇试只会加重限流，不如停下等人来看
            if consecutive >= MAX_CONSECUTIVE_FAILURES:
                print(f"  ⛔ 连续失败 {consecutive} 篇，判定为网络或限流问题，"
                      f"本轮提前停止（剩余 {len(refs) - i} 篇未试）", file=sys.stderr)
                break
    if skipped:
        print(f"跳过 {skipped} 篇不在目标日期窗口的文章。", flush=True)
    return ok, failed, None


def cmd_run(args) -> None:
    config.ensure_dirs()
    st = state.load()
    refs = _collect_refs(st, args.source, args.limit, args.url)
    if not refs:
        print("没有待处理的文章。")
        return
    print(f"待处理 {len(refs)} 篇：")
    ok, failed, limit_err = _run_batch(refs, st)
    print(f"\n完成 {ok} 篇，失败 {len(failed)} 篇。")
    if limit_err is not None:
        kind = "周限额" if limit_err.weekly else "会话限额"
        print(f"⏸ 已撞{kind}（重置: {limit_err.reset_raw or '未知'}），剩余未处理。用 autorun 可自动续跑。")
    for url, err in failed:
        print(f"  失败: {url}\n    {err}")


def _seconds_until_reset(reset_raw: str, reset_seconds: int | None = None) -> int:
    """算出该睡多久再续跑。额外加 3 分钟缓冲。

    codex 的错误体里直接带精确秒数（reset_seconds），有就用它；
    claude CLI 只给 '4:50pm' 这种文本，退回按 Asia/Shanghai 推算；
    都拿不到就回退 1 小时。
    """
    if reset_seconds is not None and reset_seconds >= 0:
        return reset_seconds + 180

    import re as _re
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo

    tz = ZoneInfo("Asia/Shanghai")
    now = datetime.now(tz)
    m = _re.match(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", reset_raw.strip(), _re.I)
    if not m:
        return 3600
    hour = int(m.group(1)) % 12
    minute = int(m.group(2) or 0)
    ampm = (m.group(3) or "").lower()
    if ampm == "pm":
        hour += 12
    elif not ampm and hour < 8:  # 没标 am/pm 且是小时数，多为早晨重置
        pass
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return int((target - now).total_seconds()) + 180


def cmd_autorun(args) -> None:
    """无人值守：循环跑流水线，撞限额就自动睡到重置点再续，直到全部完成。"""
    import time
    from datetime import datetime

    config.ensure_dirs()
    round_no = 0
    while True:
        round_no += 1
        st = state.load()
        published_start = getattr(args, "published_start", None)
        published_end = getattr(args, "published_end", None)
        refs = _collect_refs(st, args.source, args.limit, None, published_start, published_end)
        if not refs:
            print(f"[autorun] 全部完成，没有待处理文章。共 {round_no - 1} 轮。")
            return
        print(f"[autorun] 第 {round_no} 轮，待处理 {len(refs)} 篇  "
              f"({datetime.now():%Y-%m-%d %H:%M})", flush=True)
        ok, failed, limit_err = _run_batch(refs, st, published_start, published_end)
        print(f"[autorun] 第 {round_no} 轮完成 {ok} 篇，失败 {len(failed)} 篇", flush=True)
        if limit_err is None:
            # 没撞限额：若本轮零进展，说明剩下的都是持续失败的，停止避免死循环
            if ok == 0:
                print(f"[autorun] 本轮无进展，结束。")
                for url, err in failed:
                    print(f"  失败: {url}  |  {err[:80]}")
                return
            continue  # 有进展，继续下一轮把剩余的做完
        if limit_err.weekly:
            # 周限额重置在数天后，睡等没意义：停下提示换号/等重置
            print(f"[autorun] ⛔ 撞到【每周限额】（重置: {limit_err.reset_raw or '见错误信息'}）。"
                  f"睡等数天不现实，已停止。请换个账号后重新运行 autorun，会自动续传。", flush=True)
            return
        wait = _seconds_until_reset(limit_err.reset_raw,
                                    getattr(limit_err, "reset_seconds", None))
        wake = datetime.now().timestamp() + wait
        print(f"[autorun] 撞会话限额，睡 {wait // 60} 分钟，{datetime.fromtimestamp(wake):%H:%M} "
              f"后自动续跑（重置标记: {limit_err.reset_raw or '未知'}）", flush=True)
        time.sleep(wait)


def cmd_news(args) -> None:
    """news 周报合集：按周（周日为周首）把上一周的 news 打包成一期，无人值守。
    撞会话限额自动等重置续跑，撞每周限额停下提示换号。"""
    import time
    from datetime import datetime
    from . import digest

    config.ensure_dirs()
    published_start = getattr(args, "published_start", None)
    published_end = getattr(args, "published_end", None)
    if not published_start or not published_end:
        published_start, published_end = _previous_week_window()
    target_sunday = digest.week_sunday(published_start)
    print(f"[news] 目标窗口：{published_start}–{published_end}", flush=True)
    # 先同步新增 news 原文（发现→抓取），再按周聚合
    st = state.load()
    n = digest.sync_news(st, published_start, published_end)
    if n:
        print(f"[news] 同步到 {n} 篇新 news", flush=True)
    # 迟到文章落入已完成的周 → 重置该周以重做
    target_weeks = [
        w for w in digest.group_news_weeks(st)
        if w["sunday"] == target_sunday
    ]
    stale = digest.reset_stale_weeks(st, target_weeks)
    if stale:
        print(f"[news] 检测到 {len(stale)} 周有新增文章，将重做: {', '.join(stale)}", flush=True)
    round_no = 0
    while True:
        round_no += 1
        st = state.load()
        weeks = [
            w for w in digest.group_news_weeks(st)
            if w["sunday"] == target_sunday
        ]
        pending = [w for w in weeks
                   if not st.get("digests", {}).get(w["sunday"].isoformat(), {})
                   .get("stages", {}).get("packaged")]
        if args.limit:
            pending = pending[: args.limit]
        if not pending:
            print(f"[news] 全部完成，没有待处理周。共 {round_no - 1} 轮。")
            return
        print(f"[news] 第 {round_no} 轮，待处理 {len(pending)} 周  "
              f"({datetime.now():%Y-%m-%d %H:%M})", flush=True)
        ok, failed, limit_err = 0, [], None
        for i, w in enumerate(pending, 1):
            print(f"[{i}/{len(pending)}] {w['label']}（{len(w['items'])} 条）")
            try:
                digest.process_week(st, w)
                ok += 1
            except interpret.SessionLimitError as e:
                limit_err = e
                kind = "周限额" if e.weekly else "会话限额"
                print(f"  ⏸ 撞{kind}，暂停（重置: {e.reset_raw or '未知'}）", file=sys.stderr)
                break
            except Exception as e:
                failed.append((w["slug"], str(e)))
                print(f"  ❌ 失败: {e}", file=sys.stderr)
        print(f"[news] 第 {round_no} 轮完成 {ok} 周，失败 {len(failed)} 周", flush=True)
        if limit_err is None:
            if ok == 0:
                print(f"[news] 本轮无进展，剩余 {len(failed)} 周均为持续失败，结束。")
                return
            continue
        if limit_err.weekly:
            print(f"[news] ⛔ 撞到【每周限额】（重置: {limit_err.reset_raw or '见错误信息'}）。"
                  f"已停止，请换号后重新运行 news，会自动续传。", flush=True)
            return
        wait = _seconds_until_reset(limit_err.reset_raw,
                                    getattr(limit_err, "reset_seconds", None))
        wake = datetime.now().timestamp() + wait
        print(f"[news] 撞会话限额，睡 {wait // 60} 分钟，{datetime.fromtimestamp(wake):%H:%M} "
              f"后自动续跑", flush=True)
        time.sleep(wait)


def cmd_weekly(args) -> None:
    """每周日一条命令搞定更新：四个深度源增量解读 + news 上周周报。"""
    import argparse as _argparse
    published_start, published_end = _previous_week_window()
    print(f"本次 weekly 只更新上一周：{published_start}–{published_end}", flush=True)
    for src in _deep_sources():
        print(f"\n========== 更新 {src} ==========", flush=True)
        cmd_autorun(_argparse.Namespace(
            source=src,
            limit=None,
            published_start=published_start,
            published_end=published_end,
        ))
    print("\n========== news 周报 ==========", flush=True)
    cmd_news(_argparse.Namespace(
        limit=None,
        published_start=published_start,
        published_end=published_end,
    ))
    print("\n========== 刷新 RSS 与目录 ==========", flush=True)
    cmd_feed(None)
    cmd_catalog(None)
    print("\n✅ 本周更新完成。接着跑 `chatgpt-fm publish` 把站点（feed + 目录页 + 音频）"
          "推到 gh-pages 分支。", flush=True)


def cmd_catalog(args) -> None:
    """生成全集目录 CATALOG.md，并刷新 README 集数。"""
    from . import catalog
    total, counts, _ = catalog.build_catalog()
    print(f"已生成 CATALOG.md（{total} 集：" +
          "，".join(f"{k} {v}" for k, v in counts.items()) + "），README 进度已刷新")


def cmd_feed(args) -> None:
    """生成播客 RSS feed.xml（含全部已打包集），供小宇宙等订阅。"""
    from . import feed
    out, n = feed.write_feed()
    print(f"已生成 {out.relative_to(config.ROOT)}（{n} 集）")
    print(f"提交并推送后，订阅地址：{config.FEED_BASE_URL}/feed.xml")


def cmd_publish(args) -> None:
    """发布到 GitHub Pages：站点（feed + 目录页 + 封面 + 音频）推到 gh-pages 分支。"""
    from . import publish

    branch = args.branch or config.PAGES_BRANCH
    print(f"仓库：{config.GITHUB_OWNER}/{config.GITHUB_REPO}  ·  站点分支：{branch}")
    if args.dry_run:
        print("（--dry-run：只构建本地站点，不推送）")

    print("\n[1/3] 刷新目录、生成 feed 与目录页")
    site, n = publish.write_site()
    print(f"      {site.name}/feed.xml     （{n} 集）")
    print(f"      {site.name}/index.html")

    print("\n[2/3] 同步音频到站点")
    copied, skipped = publish.sync_audio(site, dry_run=args.dry_run)
    total_mb = sum(f.stat().st_size for f in (site / "audio").glob("*.mp3")) / 1024 / 1024 \
        if (site / "audio").exists() else 0
    print(f"      新增/更新 {copied} 个，跳过 {skipped} 个 · 站点音频共 {total_mb:.0f} MB")
    if total_mb > 900:
        print(f"      ⚠️ 接近 GitHub Pages 的 1GB 站点上限，该把音频挪到对象存储了"
              f"（改 AUDIO_BASE_URL 即可）", file=sys.stderr)

    if args.dry_run:
        print(f"\n本地站点已就绪：{site}")
        return

    print(f"\n[3/3] 推送到 {branch} 分支")
    try:
        print("      " + publish.push_site(site, branch, f"发布站点：{n} 集"))
    except publish.GitHubCliError as e:
        print(f"  ❌ {e}", file=sys.stderr)
        return

    print(f"\n订阅地址：{config.FEED_BASE_URL}/feed.xml")
    print(f"目录页　：{config.FEED_BASE_URL}/")


def cmd_voices(args) -> None:
    print("正在为各候选音色生成试听样品（同一段文本）...")
    for voice, desc, dur in tts.make_samples():
        print(f"  {voice:<24}{desc:<12}{dur:.0f}s  content/samples/{voice}.mp3")
    print(f"\n试听后把选中的音色写入 src/chatgpt_fm/config.py 的 TTS_VOICE（当前: {config.TTS_VOICE}）")


def cmd_status(args) -> None:
    st = state.load()
    arts = st["articles"]
    if not arts:
        print("还没有处理过任何文章。先跑 chatgpt-fm run --source engineering --limit 5")
        return
    rows = sorted(arts.items(), key=lambda kv: (kv[1].get("source", ""), kv[1].get("slug", "")))
    print(f"{'EP':<5}{'阶段':<6}{'时长':<8}{'源':<13}文件名")
    stage_names = ["fetched", "interpreted", "synthesized", "packaged"]
    for url, a in rows:
        done = sum(1 for s in stage_names if a.get("stages", {}).get(s))
        dur = a.get("duration_sec")
        dur_s = f"{dur / 60:.1f}m" if dur else "-"
        ep = f"EP{a['episode']}" if "episode" in a else "-"
        print(f"{ep:<5}{f'{done}/4':<6}{dur_s:<8}{a.get('source', '-'):<13}{a.get('slug', url)}")


def main() -> None:
    sys.stdout.reconfigure(line_buffering=True)  # 后台/管道运行时进度实时可见
    parser = argparse.ArgumentParser(prog="chatgpt-fm", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("discover", help="列出各源文章数与新文章")
    p.add_argument("--show", type=int, default=5, help="每个源最多展示几篇新文章 URL")
    p.set_defaults(func=cmd_discover)

    p = sub.add_parser("run", help="端到端流水线：发现→抓取→解读→TTS→上传包")
    p.add_argument("--source", choices=list(config.SOURCES), help="只处理指定源")
    p.add_argument("--limit", type=int, help="最多处理几篇")
    p.add_argument("--url", help="只处理这一篇文章")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("autorun", help="无人值守循环：撞限额自动等重置再续，直到全部完成")
    p.add_argument("--source", choices=list(config.SOURCES), help="只处理指定源")
    p.add_argument("--limit", type=int, help="最多处理几篇")
    p.set_defaults(func=cmd_autorun)

    p = sub.add_parser("news", help="news 周报合集：按周打包 news，无人值守续跑")
    p.add_argument("--limit", type=int, help="最多处理几周")
    p.set_defaults(func=cmd_news)

    p = sub.add_parser("weekly", help="每周日一条命令：四源增量解读 + news 上周周报")
    p.set_defaults(func=cmd_weekly)

    p = sub.add_parser("feed", help="生成播客 RSS docs/feed.xml")
    p.set_defaults(func=cmd_feed)

    p = sub.add_parser("publish", help="发布到 GitHub Pages：站点推到 gh-pages 分支")
    p.add_argument("--branch", help=f"站点分支（默认 {config.PAGES_BRANCH}）")
    p.add_argument("--dry-run", action="store_true", help="只构建本地站点，不推送")
    p.set_defaults(func=cmd_publish)

    p = sub.add_parser("catalog", help="生成全集目录 CATALOG.md 并刷新 README 集数")
    p.set_defaults(func=cmd_catalog)

    p = sub.add_parser("voices", help="生成音色试听样品")
    p.set_defaults(func=cmd_voices)

    p = sub.add_parser("status", help="显示各篇进度")
    p.set_defaults(func=cmd_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
