"""digest.py：按周分组、迟到文章重做、周报 prompt 渲染。不联网、不调模型。"""

import unittest
from datetime import date, timedelta
from unittest import mock

from chatgpt_fm import config, digest
from tests.test_packaging import TempRoot


def _write_news(published: str, title: str, url: str) -> str:
    slug = f"{published}-{title}"
    config.ensure_source_dirs(config.DIGEST_SOURCE)
    config.article_path(config.DIGEST_SOURCE, slug).write_text(
        f"---\ntitle: {title}\nurl: {url}\npublished: {published}\n---\n\n"
        f"Body of {title}.\n",
        encoding="utf-8",
    )
    return slug


def _state_with(entries):
    st = {"next_episode": 1, "articles": {}, "digests": {}}
    for published, title in entries:
        url = f"https://openai.com/index/{title}"
        st["articles"][url] = {
            "stages": {"fetched": True},
            "source": config.DIGEST_SOURCE,
            "slug": _write_news(published, title, url),
            "title": title,
            "published": published,
        }
    return st


class TestGroupNewsWeeks(unittest.TestCase):
    def test_groups_by_sunday_week_and_skips_current_week(self):
        with TempRoot():
            today = date.today()
            this_sunday = today - timedelta(days=(today.weekday() + 1) % 7)
            last_sunday = this_sunday - timedelta(days=7)
            st = _state_with([
                (last_sunday.isoformat(), "a"),
                ((last_sunday + timedelta(days=3)).isoformat(), "b"),
                (this_sunday.isoformat(), "current-week"),   # 进行中的周，不该出现
            ])
            weeks = digest.group_news_weeks(st)
            self.assertTrue(all(w["sunday"] < this_sunday for w in weeks))
            target = [w for w in weeks if w["sunday"] == last_sunday]
            self.assertEqual(len(target), 1)
            self.assertEqual(len(target[0]["items"]), 2)
            self.assertTrue(target[0]["slug"].endswith("OpenAI一周快讯"))

    def test_other_sources_are_not_grouped(self):
        with TempRoot():
            st = _state_with([("2026-02-09", "a")])
            st["articles"]["https://openai.com/index/a"]["source"] = "engineering"
            self.assertEqual(digest.group_news_weeks(st), [])


class TestResetStaleWeeks(unittest.TestCase):
    def test_week_with_new_article_is_reset(self):
        with TempRoot():
            st = _state_with([("2026-02-09", "a"), ("2026-02-10", "b")])
            sunday = date(2026, 2, 8)
            week = digest.group_news_weeks(st)[0]
            self.assertEqual(week["sunday"], sunday)

            # 假装这一周此前只用 1 条做过，且已打包
            config.script_path(config.DIGEST_SOURCE, week["slug"]).write_text(
                "---\nepisode_title: x\nitem_count: 1\n---\n\n## Script\n\n正文。\n",
                encoding="utf-8",
            )
            st["digests"][sunday.isoformat()] = {
                "slug": week["slug"],
                "stages": {"interpreted": True, "synthesized": True, "packaged": True},
            }
            with mock.patch.object(digest.state, "save"):
                stale = digest.reset_stale_weeks(st, [week])
            self.assertEqual(len(stale), 1)
            stages = st["digests"][sunday.isoformat()]["stages"]
            self.assertFalse(stages["interpreted"])
            self.assertFalse(stages["packaged"])

    def test_unchanged_week_is_left_alone(self):
        with TempRoot():
            st = _state_with([("2026-02-09", "a")])
            sunday = date(2026, 2, 8)
            week = digest.group_news_weeks(st)[0]
            config.script_path(config.DIGEST_SOURCE, week["slug"]).write_text(
                "---\nepisode_title: x\nitem_count: 1\n---\n\n## Script\n\n正文。\n",
                encoding="utf-8",
            )
            st["digests"][sunday.isoformat()] = {
                "slug": week["slug"],
                "stages": {"interpreted": True, "synthesized": True, "packaged": True},
            }
            with mock.patch.object(digest.state, "save"):
                self.assertEqual(digest.reset_stale_weeks(st, [week]), [])
            self.assertTrue(st["digests"][sunday.isoformat()]["stages"]["packaged"])


class TestDigestPrompt(unittest.TestCase):
    def test_placeholders_are_all_substituted(self):
        items = [
            ({"title": "Item one", "published": "2026-02-09"}, "First body."),
            ({"title": "Item two", "published": "2026-02-11"}, "Second body."),
        ]
        p = digest.build_prompt("2026年2月8日–2026年2月14日", items)
        for ph in ("{week_label}", "{count}", "{today}", "{items}"):
            self.assertNotIn(ph, p)
        self.assertIn("Item one", p)
        self.assertIn("Item two", p)
        self.assertIn("本期共 2 条快讯", p)

    def test_long_body_is_capped(self):
        items = [({"title": "Long", "published": "2026-02-09"}, "x" * (digest.BODY_CAP * 3))]
        p = digest.build_prompt("某周", items)
        self.assertIn("……", p)
        self.assertLess(p.count("x"), digest.BODY_CAP * 2)


if __name__ == "__main__":
    unittest.main()
