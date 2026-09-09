"""publish.py：附件命名、待上传集合、Pages 首页渲染。不碰网络、不调 gh。"""

import unittest
from pathlib import Path
from unittest import mock

from chatgpt_fm import config, publish
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
                copied, skipped = publish.sync_audio(site)
            self.assertEqual((copied, skipped), (1, 0))
            dest = site / "audio" / "EP1.mp3"
            self.assertTrue(dest.exists())
            self.assertEqual(dest.stat().st_size, 4096)

    def test_unchanged_audio_is_skipped(self):
        with TempRoot() as root:
            _make_episode("engineering", "2026-02-11-A", 1, "甲", audio_bytes=b"x" * 4096)
            site = root / "site"
            with mock.patch.object(publish.state, "load", return_value=self.ST):
                publish.sync_audio(site)
                copied, skipped = publish.sync_audio(site)   # 第二次
            # 同名同大小不该重复复制，否则几百集每次 publish 都会让 git 认为全变了
            self.assertEqual((copied, skipped), (0, 1))

    def test_resynthesised_audio_is_replaced(self):
        with TempRoot() as root:
            _make_episode("engineering", "2026-02-11-A", 1, "甲", audio_bytes=b"x" * 4096)
            site = root / "site"
            with mock.patch.object(publish.state, "load", return_value=self.ST):
                publish.sync_audio(site)
                # 重新合成，大小变了
                config.audio_path("engineering", "2026-02-11-A").write_bytes(b"y" * 8192)
                copied, skipped = publish.sync_audio(site)
            self.assertEqual((copied, skipped), (1, 0))
            self.assertEqual((site / "audio" / "EP1.mp3").stat().st_size, 8192)

    def test_dry_run_writes_nothing(self):
        with TempRoot() as root:
            _make_episode("engineering", "2026-02-11-A", 1, "甲")
            site = root / "site"
            with mock.patch.object(publish.state, "load", return_value=self.ST):
                copied, _ = publish.sync_audio(site, dry_run=True)
            self.assertEqual(copied, 1)
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
