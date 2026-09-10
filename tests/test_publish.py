"""publish.py：附件命名、待上传集合、Pages 首页渲染。不碰网络、不调 gh。"""

import unittest
from pathlib import Path
from unittest import mock

from chatgpt_fm import config, publish, state
from tests.test_packaging import TempRoot, _make_episode


class TestAssetNaming(unittest.TestCase):
    def test_asset_name_is_ascii_and_stable(self):
        name = config.audio_asset_name(123)
        self.assertEqual(name, "EP123.mp3")
        self.assertTrue(name.isascii())

    def test_url_points_at_pages_not_release(self):
        url = config.audio_url(7)
        # Release 的地址带 content-disposition: attachment，播放器会拒播，
        # 所以音频必须走 Pages
        self.assertTrue(url.startswith(config.FEED_BASE_URL))
        self.assertNotIn("/releases/download/", url)
        self.assertTrue(url.endswith("/audio/EP7.mp3"))

    def test_slug_characters_never_reach_the_url(self):
        # slug 里有空格/中文/’，GitHub 会改名；集号命名就是为了绕开这个
        self.assertNotIn(" ", config.audio_url(7))
        self.assertTrue(config.audio_url(7).isascii())


class TestCollectAudio(unittest.TestCase):
    def _state(self):
        return {
            "next_episode": 3,
            "articles": {
                "u1": {"stages": {"packaged": True}, "source": "engineering",
                       "slug": "2026-02-11-A", "episode": 1},
                "u2": {"stages": {"packaged": False}, "source": "engineering",
                       "slug": "2026-02-12-B", "episode": 2},
            },
            "digests": {
                "2026-02-08": {"stages": {"packaged": True},
                               "slug": "2026-02-08-OpenAI一周快讯", "episode": 3},
            },
        }

    def test_only_packaged_episodes_with_local_audio(self):
        with TempRoot():
            _make_episode("engineering", "2026-02-11-A", 1, "甲")
            _make_episode(config.DIGEST_SOURCE, "2026-02-08-OpenAI一周快讯", 3, "快讯")
            # 未打包的那篇不造音频
            got = publish.collect_audio(self._state())
            self.assertEqual([e["ep"] for e in got], [1, 3])

    def test_missing_audio_file_is_skipped(self):
        with TempRoot():
            config.ensure_source_dirs("engineering")   # 目录在，但没有 mp3
            self.assertEqual(publish.collect_audio(self._state()), [])


class TestSyncAudio(unittest.TestCase):
    ST = {"next_episode": 2, "articles": {
        "u1": {"stages": {"packaged": True}, "source": "engineering",
               "slug": "2026-02-11-A", "episode": 1}}, "digests": {}}

    def test_audio_is_copied_under_episode_number(self):
        with TempRoot() as root:
            _make_episode("engineering", "2026-02-11-A", 1, "甲", audio_bytes=b"x" * 4096)
            site = root / "site"
            with mock.patch.object(publish.state, "load", return_value=self.ST):
                r = publish.sync_audio(site)
            self.assertEqual((r["copied"], r["skipped"]), (1, 0))
            dest = site / "audio" / "EP1.mp3"
            self.assertTrue(dest.exists())
            self.assertEqual(dest.stat().st_size, 4096)

    def test_unchanged_audio_is_skipped(self):
        with TempRoot() as root:
            _make_episode("engineering", "2026-02-11-A", 1, "甲", audio_bytes=b"x" * 4096)
            site = root / "site"
            with mock.patch.object(publish.state, "load", return_value=self.ST):
                publish.sync_audio(site)
                r = publish.sync_audio(site)   # 第二次
            # 同名同大小不该重复复制，否则几百集每次 publish 都会让 git 认为全变了
            self.assertEqual((r["copied"], r["skipped"]), (0, 1))

    def test_resynthesised_audio_is_replaced(self):
        with TempRoot() as root:
            _make_episode("engineering", "2026-02-11-A", 1, "甲", audio_bytes=b"x" * 4096)
            site = root / "site"
            with mock.patch.object(publish.state, "load", return_value=self.ST):
                publish.sync_audio(site)
                # 重新合成，大小变了
                config.audio_path("engineering", "2026-02-11-A").write_bytes(b"y" * 8192)
                r = publish.sync_audio(site)
            self.assertEqual((r["copied"], r["skipped"]), (1, 0))
            self.assertEqual((site / "audio" / "EP1.mp3").stat().st_size, 8192)

    def test_dry_run_writes_nothing(self):
        with TempRoot() as root:
            _make_episode("engineering", "2026-02-11-A", 1, "甲")
            site = root / "site"
            with mock.patch.object(publish.state, "load", return_value=self.ST):
                r = publish.sync_audio(site, dry_run=True)
            self.assertEqual(r["copied"], 1)
            self.assertFalse((site / "audio").exists())


class TestMirror(unittest.TestCase):
    def test_stale_files_are_removed_but_git_is_kept(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            src, dest = Path(tmp) / "src", Path(tmp) / "dest"
            (src / "audio").mkdir(parents=True)
            (src / "feed.xml").write_text("new", encoding="utf-8")
            (src / "audio" / "EP1.mp3").write_bytes(b"a")
            (dest / ".git").mkdir(parents=True)
            (dest / ".git" / "HEAD").write_text("ref", encoding="utf-8")
            (dest / "stale.html").write_text("old", encoding="utf-8")
            publish._mirror(src, dest)
            self.assertFalse((dest / "stale.html").exists())
            self.assertEqual((dest / "feed.xml").read_text(encoding="utf-8"), "new")
            self.assertTrue((dest / "audio" / "EP1.mp3").exists())
            self.assertTrue((dest / ".git" / "HEAD").exists())   # .git 绝不能动


class TestIndexPage(unittest.TestCase):
    ITEMS = {
        "engineering": [{"ep": 1, "date": "2026-02-11", "title": "Harness 工程实践",
                         "link": "content/openai/engineering/scripts/a.md",
                         "article": "content/openai/engineering/articles/a.md"}],
        "news": [{"ep": 2, "date": "2026-02-08", "title": "OpenAI 一周快讯",
                  "link": "content/openai/news/scripts/b.md", "article": None}],
    }

    def test_renders_episodes_and_subscribe_url(self):
        html = publish.build_index(self.ITEMS)
        self.assertIn("Harness 工程实践", html)
        self.assertIn("OpenAI 一周快讯", html)
        self.assertIn(f"{config.FEED_BASE_URL}/feed.xml", html)
        self.assertIn(config.audio_url(1), html)
        self.assertIn("英文原文", html)

    def test_html_is_escaped(self):
        items = {"engineering": [{"ep": 1, "date": "2026-01-01",
                                  "title": "a <script>alert(1)</script> b",
                                  "link": "x.md", "article": None}]}
        html = publish.build_index(items)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_empty_catalogue_still_renders(self):
        html = publish.build_index({})
        self.assertIn("还没有已发布的单集", html)
        self.assertIn("<!doctype html>", html)


class TestWriteSite(unittest.TestCase):
    def test_writes_feed_index_and_nojekyll(self):
        with TempRoot() as root:
            (root / "README.md").write_text("| 🛠️ Engineering | 0 |\n", encoding="utf-8")
            site, n = publish.write_site()
            self.assertEqual(site, root / ".site")
            self.assertTrue((site / "feed.xml").exists())
            self.assertTrue((site / "index.html").exists())
            # 没有 .nojekyll 的话 Pages 会拿 Jekyll 处理 docs/，下划线开头的资源被吞
            self.assertTrue((site / ".nojekyll").exists())
            self.assertEqual(n, 0)


if __name__ == "__main__":
    unittest.main()


class TestBatchCircuitBreaker(unittest.TestCase):
    """连续失败多半是限流这类全局问题，继续一篇篇试只会加重，应提前停。"""

    def _refs(self, n):
        from chatgpt_fm import sources
        return [sources.ArticleRef(url=f"https://openai.com/index/a{i}",
                                   source="engineering") for i in range(n)]

    def test_stops_after_consecutive_failures(self):
        from chatgpt_fm import cli
        with mock.patch.object(cli, "_pipeline_one", side_effect=RuntimeError("连不上")):
            ok, failed, limit = cli._run_batch(self._refs(20), {"articles": {}})
        self.assertEqual(ok, 0)
        self.assertIsNone(limit)
        # 熔断后不该把 20 篇全试一遍
        self.assertEqual(len(failed), cli.MAX_CONSECUTIVE_FAILURES)

    def test_success_resets_the_counter(self):
        from chatgpt_fm import cli
        # 失败两次 → 成功一次（计数清零）→ 再失败两次，都不该触发熔断
        outcomes = [RuntimeError("x"), RuntimeError("x"), True,
                    RuntimeError("x"), RuntimeError("x"), True]
        with mock.patch.object(cli, "_pipeline_one", side_effect=outcomes):
            ok, failed, _ = cli._run_batch(self._refs(6), {"articles": {}})
        self.assertEqual(ok, 2)
        self.assertEqual(len(failed), 4)   # 6 篇全试过了，没被提前掐断


class TestStateNotPollutedByFetchFailure(unittest.TestCase):
    """抓取失败不该在 state 里留空壳，否则 discover 的新文章数会永久失真。"""

    def test_failed_fetch_leaves_no_entry(self):
        from chatgpt_fm import cli, sources
        st = {"articles": {}}
        ref = sources.ArticleRef(url="https://openai.com/index/boom", source="engineering")
        with mock.patch.object(cli.fetch, "fetch_article", side_effect=RuntimeError("抓取失败")):
            with self.assertRaises(RuntimeError):
                cli._pipeline_one(ref, st)
        self.assertNotIn(ref.url, st["articles"])

    def test_already_fetched_entry_is_preserved(self):
        from chatgpt_fm import cli, sources
        ref = sources.ArticleRef(url="https://openai.com/index/keep", source="engineering")
        st = {"articles": {ref.url: {"stages": {"fetched": True}, "slug": "s", "title": "t"}}}
        with mock.patch.object(cli.fetch, "read_with_frontmatter",
                               side_effect=RuntimeError("后面某步炸了")):
            with self.assertRaises(RuntimeError):
                cli._pipeline_one(ref, st)
        self.assertIn(ref.url, st["articles"])   # 已抓到的成果不能因后续失败被丢掉


class TestNoBodySkip(unittest.TestCase):
    """没有正文的页面重抓多少次都一样，必须永久跳过而不是每轮重试。"""

    def test_nobody_marks_skipped_and_does_not_raise(self):
        from chatgpt_fm import cli, fetch, sources
        st = {"articles": {}}
        ref = sources.ArticleRef(url="https://openai.com/index/shell", source="engineering")
        with mock.patch.object(cli.fetch, "fetch_article",
                               side_effect=fetch.NoBodyError("只提取到导航栏")), \
             mock.patch.object(cli.state, "save"):
            done = cli._pipeline_one(ref, st)
        self.assertFalse(done)                                   # 不算完成
        self.assertIn("skipped", st["articles"][ref.url])        # 但留了标记

    def test_collect_refs_filters_skipped(self):
        from chatgpt_fm import cli, sources
        refs = {"engineering": [
            sources.ArticleRef(url="https://openai.com/index/shell", source="engineering"),
            sources.ArticleRef(url="https://openai.com/index/good", source="engineering"),
        ]}
        st = {"articles": {"https://openai.com/index/shell": {
            "stages": {}, "skipped": "只提取到导航栏"}}}
        with mock.patch.object(cli.sources, "discover_all", return_value=refs):
            got = cli._collect_refs(st, source="engineering")
        self.assertEqual([r.url for r in got], ["https://openai.com/index/good"])


class TestStateAtomicWrite(unittest.TestCase):
    """进度文件写到一半被打断（限额中断、Ctrl-C、OOM）会毁掉几百集的记录。"""

    def test_no_temp_file_left_behind(self):
        from chatgpt_fm import state
        with TempRoot():
            state.save({"next_episode": 1, "articles": {}})
            self.assertTrue(config.STATE_FILE.exists())
            self.assertFalse(config.STATE_FILE.with_suffix(".json.tmp").exists())

    def test_existing_state_survives_a_failed_write(self):
        from chatgpt_fm import state
        with TempRoot():
            state.save({"next_episode": 7, "articles": {"u": {"stages": {}}}})
            # 模拟写临时文件时炸掉：原文件必须保持完好，而不是被截断
            with mock.patch.object(Path, "write_text", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    state.save({"next_episode": 99, "articles": {}})
            self.assertEqual(state.load()["next_episode"], 7)


class TestAlreadyFetchedShellPage(unittest.TestCase):
    """正文校验上线前落盘的壳页，抓取那步会被跳过，得在解读前再拦一次。"""

    def test_fetched_shell_page_is_skipped_before_the_model_call(self):
        from chatgpt_fm import cli, sources
        ref = sources.ArticleRef(url="https://openai.com/index/shell", source="engineering")
        st = {"articles": {ref.url: {"stages": {"fetched": True}, "slug": "s", "title": "t"}}}
        nav = "Skip to main content\nResearch\nProducts\nLog in\nShare"
        with mock.patch.object(cli.fetch, "read_with_frontmatter", return_value=({}, nav)), \
             mock.patch.object(cli.state, "save"), \
             mock.patch.object(cli.interpret, "interpret") as interp:
            done = cli._pipeline_one(ref, st)
        self.assertFalse(done)
        interp.assert_not_called()            # 关键：没有白花一次模型调用
        self.assertIn("skipped", st["articles"][ref.url])


class TestBudgetSelection(unittest.TestCase):
    """站点容量有限（Pages 1GB），只能挂各源最新的几集。各源必须都有代表，
    否则集数多的源（research 两百多集）会把整个站点淹掉。"""

    @staticmethod
    def _eps(spec, size=10):
        """spec: {源名: [集号...]}；每集 size MB。"""
        out = []
        for src, eps in spec.items():
            for ep in eps:
                m = mock.MagicMock()
                m.stat.return_value.st_size = size * 1024 * 1024
                out.append({"ep": ep, "source": src, "slug": f"s{ep}", "path": m})
        return out

    def test_everything_fits_when_budget_is_ample(self):
        from chatgpt_fm import publish
        eps = self._eps({"engineering": [1, 2], "research": [3, 4]})
        sel, used = publish.select_within_budget(eps, 1000 * 1024 * 1024)
        self.assertEqual({e["ep"] for e in sel}, {1, 2, 3, 4})
        self.assertAlmostEqual(used / 1024 / 1024, 40)

    def test_newest_are_kept_within_each_source(self):
        from chatgpt_fm import publish
        eps = self._eps({"engineering": [1, 2, 3], "research": [10, 11, 12]})
        # 40MB 预算 / 每集 10MB = 4 集，轮流取 → 各源最新 2 集
        sel, _ = publish.select_within_budget(eps, 40 * 1024 * 1024)
        self.assertEqual({e["ep"] for e in sel}, {2, 3, 11, 12})

    def test_large_source_does_not_crowd_out_small_one(self):
        from chatgpt_fm import publish
        # research 200 集、engineering 只有 2 集；预算只够 4 集
        eps = self._eps({"engineering": [1, 2], "research": list(range(100, 300))})
        sel, _ = publish.select_within_budget(eps, 40 * 1024 * 1024)
        by_src = {}
        for e in sel:
            by_src.setdefault(e["source"], []).append(e["ep"])
        self.assertIn("engineering", by_src)      # 小源必须有代表
        self.assertEqual(sorted(by_src["engineering"]), [1, 2])
        self.assertEqual(len(sel), 4)

    def test_exhausted_source_leaves_budget_to_others(self):
        from chatgpt_fm import publish
        # engineering 只有 1 集，剩下的预算应该全给 research，而不是浪费
        eps = self._eps({"engineering": [1], "research": [10, 11, 12, 13]})
        sel, _ = publish.select_within_budget(eps, 40 * 1024 * 1024)
        self.assertEqual(len(sel), 4)
        self.assertEqual(sorted(e["ep"] for e in sel), [1, 11, 12, 13])

    def test_zero_budget_selects_nothing(self):
        from chatgpt_fm import publish
        sel, used = publish.select_within_budget(self._eps({"a": [1, 2]}), 0)
        self.assertEqual(sel, [])
        self.assertEqual(used, 0)

    def test_result_is_deterministic(self):
        from chatgpt_fm import publish
        eps = self._eps({"b": [5, 6], "a": [1, 2], "c": [8, 9]})
        a, _ = publish.select_within_budget(eps, 30 * 1024 * 1024)
        b, _ = publish.select_within_budget(eps, 30 * 1024 * 1024)
        self.assertEqual([e["ep"] for e in a], [e["ep"] for e in b])


class TestRollingWindowCleanup(unittest.TestCase):
    def test_episodes_falling_out_of_window_are_removed_from_site(self):
        from chatgpt_fm import publish
        with TempRoot() as root:
            for ep, slug in ((1, "2026-01-01-A"), (2, "2026-02-01-B")):
                _make_episode("engineering", slug, ep, f"第{ep}集", audio_bytes=b"x" * 4096)
            st = {"next_episode": 3, "articles": {
                "u1": {"stages": {"packaged": True}, "source": "engineering",
                       "slug": "2026-01-01-A", "episode": 1},
                "u2": {"stages": {"packaged": True}, "source": "engineering",
                       "slug": "2026-02-01-B", "episode": 2}}, "digests": {}}
            site = root / "site"
            with mock.patch.object(publish.state, "load", return_value=st):
                # 预算足够，两集都上
                r = publish.sync_audio(site)
                self.assertEqual(r["eps"], {1, 2})
                # 预算收紧到只装得下一集 → 老的那集必须从站点撤掉
                with mock.patch.object(config, "SITE_AUDIO_BUDGET_MB", 4096 / 1024 / 1024):
                    r = publish.sync_audio(site)
            self.assertEqual(r["eps"], {2})
            self.assertEqual(r["removed"], 1)
            self.assertFalse((site / "audio" / "EP1.mp3").exists())
            self.assertTrue((site / "audio" / "EP2.mp3").exists())
            # 本地音频不能被动
            self.assertTrue(config.audio_path("engineering", "2026-01-01-A").exists())


class TestFeedOnlyIncludesPlayable(unittest.TestCase):
    """滚动窗口之外的集不能进 feed，否则 enclosure 404、客户端直接报错。"""

    def test_feed_skips_episodes_without_site_audio(self):
        from chatgpt_fm import feed
        with TempRoot():
            for ep, slug in ((1, "2026-01-01-A"), (2, "2026-02-01-B")):
                _make_episode("engineering", slug, ep, f"第{ep}集")
            state.save({"next_episode": 3, "articles": {
                "u1": {"stages": {"packaged": True}, "source": "engineering",
                       "slug": "2026-01-01-A", "published": "2026-01-01", "episode": 1},
                "u2": {"stages": {"packaged": True}, "source": "engineering",
                       "slug": "2026-02-01-B", "published": "2026-02-01", "episode": 2}}})
            self.assertEqual(feed.build_feed().count("<item>"), 2)          # 不限时全收
            xml = feed.build_feed(only_eps={2})
            self.assertEqual(xml.count("<item>"), 1)
            self.assertIn("EP2", xml)
            self.assertNotIn("audio/EP1.mp3", xml)
