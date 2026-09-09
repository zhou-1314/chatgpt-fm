"""端到端（不联网、不调模型）：上传包 → CATALOG.md → feed.xml。

用临时目录顶掉 config 里的 ROOT/CONTENT_DIR，避免污染仓库真实内容目录。
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from chatgpt_fm import catalog, config, episode, feed, state


class TempRoot:
    """把 config 的路径全部指到临时目录，退出时还原。"""

    def __enter__(self):
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self._patches = [
            mock.patch.object(config, "ROOT", root),
            mock.patch.object(config, "CONTENT_DIR", root / "content"),
            mock.patch.object(config, "STATE_FILE", root / "content" / "state.json"),
            # SITE_DIR 是 import 时按 ROOT 算好的常量，不跟着 ROOT 走，得单独顶掉，
            # 否则 write_feed 会把测试产物写进真实仓库的 docs/
            mock.patch.object(config, "SITE_DIR", root / "docs"),
        ]
        for p in self._patches:
            p.start()
        return root

    def __exit__(self, *exc):
        for p in reversed(self._patches):
            p.stop()
        self._tmp.cleanup()
        return False


def _make_episode(source, slug, ep_no, title, duration=1500.0, audio_bytes=b"x" * 4096):
    """造一集完整产物：script + article + audio + episode 上传包。"""
    config.ensure_source_dirs(source)
    config.script_path(source, slug).write_text(
        "---\nepisode_title: x\n---\n\n## Shownotes\n\n本期简介。\n\n- 要点一\n\n## Script\n\n正文。\n",
        encoding="utf-8",
    )
    config.article_path(source, slug).write_text(
        "---\ntitle: x\n---\n\nEnglish body.\n", encoding="utf-8"
    )
    config.audio_path(source, slug).write_bytes(audio_bytes)
    episode.write_episode(
        slug=slug,
        episode_no=ep_no,
        episode_title=title,
        shownotes="本期简介。\n\n- 要点一",
        article_meta={"title": title, "url": f"https://openai.com/index/{slug}",
                      "published": slug[:10], "source": source},
        duration_sec=duration,
    )


class TestPackagingChain(unittest.TestCase):
    def test_episode_catalog_and_feed(self):
        with TempRoot() as root:
            st = {
                "next_episode": 3,
                "articles": {
                    "https://openai.com/index/harness-engineering": {
                        "stages": {"fetched": True, "interpreted": True,
                                   "synthesized": True, "packaged": True},
                        "source": "engineering",
                        "slug": "2026-02-11-Harness engineering",
                        "title": "Harness engineering",
                        "published": "2026-02-11",
                        "duration_sec": 1500.0,
                        "episode": 1,
                    },
                },
                "digests": {
                    "2026-02-08": {
                        "slug": "2026-02-08-OpenAI一周快讯",
                        "stages": {"interpreted": True, "synthesized": True,
                                   "packaged": True},
                        "duration_sec": 300.0,
                        "episode": 2,
                        "item_count": 4,
                    },
                },
            }
            _make_episode("engineering", "2026-02-11-Harness engineering", 1,
                          "Harness 工程实践")
            _make_episode(config.DIGEST_SOURCE, "2026-02-08-OpenAI一周快讯", 2,
                          "OpenAI 一周快讯", duration=300.0)
            state.save(st)

            # 上传包写出来了，标题里带集号
            ep_file = config.episode_path("engineering", "2026-02-11-Harness engineering")
            self.assertTrue(ep_file.exists())
            self.assertIn("# EP1 | Harness 工程实践", ep_file.read_text(encoding="utf-8"))

            # README 存在时 catalog 会去刷集数，这里造一个最小版
            (root / "README.md").write_text(
                "![episodes](https://img.shields.io/badge/已更新-0%20集-1DB954)\n"
                "完整 0 集目录\n\n"
                "| 来源 | 集数 |\n|---|---|\n| 🛠️ Engineering | 0 |\n"
                "| 📰 News 周报 | 0 |\n| | **0 集** |\n",
                encoding="utf-8",
            )
            total, counts = catalog.build_catalog()
            self.assertEqual(total, 2)
            self.assertEqual(counts["engineering"], 1)
            self.assertEqual(counts[config.DIGEST_SOURCE], 1)

            cat_text = (root / "CATALOG.md").read_text(encoding="utf-8")
            self.assertIn("Harness 工程实践", cat_text)
            self.assertIn("英文原文", cat_text)          # 单篇有原文链接
            self.assertIn("OpenAI 一周快讯", cat_text)

            readme = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("已更新-2%20集", readme)
            self.assertIn("完整 2 集目录", readme)
            self.assertIn("| 🛠️ Engineering | 1 |", readme)

            xml = feed.build_feed()
            self.assertEqual(xml.count("<item>"), 2)
            self.assertIn("<itunes:duration>25:00</itunes:duration>", xml)
            self.assertIn("EP1 · 2026-02-11 | Harness 工程实践", xml)
            # 周报标题本身带日期范围，不再重复拼日期
            self.assertIn("EP2 | OpenAI 一周快讯", xml)
            self.assertIn('type="audio/mpeg"', xml)
            self.assertIn("length=\"4096\"", xml)
            # 音频 enclosure 必须指向 Release 附件，且用集号命名
            self.assertIn(f"{config.AUDIO_BASE_URL}/EP1.mp3", xml)
            self.assertIn(f"{config.AUDIO_BASE_URL}/EP2.mp3", xml)
            self.assertNotIn("github.io/chatgpt-fm/audio", xml)

            out, n = feed.write_feed()
            self.assertEqual(n, 2)
            self.assertTrue(out.exists())
            self.assertEqual(out, root / "docs" / "feed.xml")   # 写进 Pages 目录

    def test_feed_skips_episodes_without_audio(self):
        with TempRoot():
            st = {
                "next_episode": 2,
                "articles": {
                    "https://openai.com/index/no-audio": {
                        "stages": {"packaged": True},
                        "source": "engineering",
                        "slug": "2026-03-01-No audio yet",
                        "published": "2026-03-01",
                        "episode": 1,
                    },
                },
            }
            config.ensure_source_dirs("engineering")
            state.save(st)
            # 没有 episodes/*.md 也没有 mp3 → 不该出现在 RSS 里
            self.assertEqual(feed.build_feed().count("<item>"), 0)


if __name__ == "__main__":
    unittest.main()
