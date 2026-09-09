"""publish.py：附件命名、待上传集合、Pages 首页渲染。不碰网络、不调 gh。"""

import unittest
from unittest import mock

from chatgpt_fm import config, publish
from tests.test_packaging import TempRoot, _make_episode


class TestAssetNaming(unittest.TestCase):
    def test_asset_name_is_ascii_and_stable(self):
        name = config.audio_asset_name(123)
        self.assertEqual(name, "EP123.mp3")
        self.assertTrue(name.isascii())

    def test_url_points_at_the_release(self):
        url = config.audio_url(7)
        self.assertTrue(url.startswith("https://github.com/"))
        self.assertIn("/releases/download/", url)
        self.assertTrue(url.endswith("/EP7.mp3"))

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


class TestUploadAudio(unittest.TestCase):
    def test_unchanged_assets_are_skipped(self):
        with TempRoot():
            _make_episode("engineering", "2026-02-11-A", 1, "甲", audio_bytes=b"x" * 4096)
            st = {"next_episode": 2, "articles": {
                "u1": {"stages": {"packaged": True}, "source": "engineering",
                       "slug": "2026-02-11-A", "episode": 1}}, "digests": {}}
            with mock.patch.object(publish.state, "load", return_value=st), \
                 mock.patch.object(publish, "ensure_release"), \
                 mock.patch.object(publish, "release_assets", return_value={"EP1.mp3": 4096}), \
                 mock.patch.object(publish, "_gh") as gh:
                uploaded, skipped = publish.upload_audio("audio")
            self.assertEqual((uploaded, skipped), (0, 1))
            gh.assert_not_called()

    def test_changed_size_triggers_reupload(self):
        with TempRoot():
            _make_episode("engineering", "2026-02-11-A", 1, "甲", audio_bytes=b"x" * 4096)
            st = {"next_episode": 2, "articles": {
                "u1": {"stages": {"packaged": True}, "source": "engineering",
                       "slug": "2026-02-11-A", "episode": 1}}, "digests": {}}
            with mock.patch.object(publish.state, "load", return_value=st), \
                 mock.patch.object(publish, "ensure_release"), \
                 mock.patch.object(publish, "release_assets", return_value={"EP1.mp3": 99}), \
                 mock.patch.object(publish, "_gh") as gh:
                uploaded, skipped = publish.upload_audio("audio")
            self.assertEqual((uploaded, skipped), (1, 0))
            args = gh.call_args[0]
            self.assertEqual(args[:3], ("release", "upload", "audio"))
            self.assertIn("--clobber", args)
            self.assertTrue(args[3].endswith("EP1.mp3"))   # 传的是改好名的副本

    def test_dry_run_uploads_nothing(self):
        with TempRoot():
            _make_episode("engineering", "2026-02-11-A", 1, "甲")
            st = {"next_episode": 2, "articles": {
                "u1": {"stages": {"packaged": True}, "source": "engineering",
                       "slug": "2026-02-11-A", "episode": 1}}, "digests": {}}
            with mock.patch.object(publish.state, "load", return_value=st), \
                 mock.patch.object(publish, "release_assets", return_value={}), \
                 mock.patch.object(publish, "_gh") as gh:
                uploaded, _ = publish.upload_audio("audio", dry_run=True)
            self.assertEqual(uploaded, 1)
            gh.assert_not_called()


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
            self.assertEqual(site, root / "docs")
            self.assertTrue((site / "feed.xml").exists())
            self.assertTrue((site / "index.html").exists())
            # 没有 .nojekyll 的话 Pages 会拿 Jekyll 处理 docs/，下划线开头的资源被吞
            self.assertTrue((site / ".nojekyll").exists())
            self.assertEqual(n, 0)


if __name__ == "__main__":
    unittest.main()
