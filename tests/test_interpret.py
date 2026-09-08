"""interpret.py：限额识别、短稿加长重写、落盘格式。用假的 run_llm，不调真模型。"""

import unittest
from unittest import mock

from chatgpt_fm import config, interpret
from tests.test_packaging import TempRoot


def _raw(script: str, title: str = "标题") -> str:
    return (f"===EPISODE_TITLE===\n{title}\n"
            f"===SHOWNOTES===\n简介\n\n- 要点\n"
            f"===SCRIPT===\n{script}\n")


class TestSessionLimitParsing(unittest.TestCase):
    def test_five_hour_limit_with_reset_time(self):
        got = interpret._parse_session_limit("Claude usage limit reached, resets 4:50pm")
        self.assertIsNotNone(got)
        reset, weekly = got
        self.assertEqual(reset, "4:50pm")
        self.assertFalse(weekly)

    def test_weekly_limit_is_flagged(self):
        got = interpret._parse_session_limit("You've hit your weekly limit; resets Jun 22 at 10am")
        self.assertIsNotNone(got)
        _, weekly = got
        self.assertTrue(weekly)

    def test_ordinary_error_is_not_a_limit(self):
        self.assertIsNone(interpret._parse_session_limit("connection reset by peer"))

    def test_limit_without_reset_time(self):
        got = interpret._parse_session_limit("session limit reached")
        self.assertEqual(got, ("", False))


class TestCodexLimitDetection(unittest.TestCase):
    def test_429_is_a_limit(self):
        self.assertTrue(interpret._is_codex_limit_error(429, "whatever"))

    def test_quota_wording_is_a_limit(self):
        self.assertTrue(interpret._is_codex_limit_error(None, "ChatGPT quota exceeded"))

    def test_plain_500_is_not(self):
        self.assertFalse(interpret._is_codex_limit_error(500, "internal error"))


class TestCnDate(unittest.TestCase):
    def test_renders_chinese_date(self):
        self.assertIn("二〇二六年二月十一日", interpret._cn_date("2026-02-11"))

    def test_teens_and_tens(self):
        self.assertIn("十月十日", interpret._cn_date("2026-10-10"))
        self.assertIn("十一月三十日", interpret._cn_date("2026-11-30"))

    def test_missing_date_tells_the_host_to_say_so(self):
        self.assertIn("未知", interpret._cn_date(""))


class TestInterpretWriting(unittest.TestCase):
    META = {"title": "T", "url": "https://openai.com/index/t",
            "source": "engineering", "published": "2026-02-11"}

    def test_script_is_written_with_frontmatter(self):
        with TempRoot():
            config.ensure_source_dirs("engineering")
            long_script = "正" * (interpret.MIN_HAN_CHARS + 100)
            with mock.patch.object(interpret, "run_llm", return_value=_raw(long_script)) as m:
                interpret.interpret(self.META, "English body", "2026-02-11-T")
            self.assertEqual(m.call_count, 1)  # 够长，不该触发重写
            text = config.script_path("engineering", "2026-02-11-T").read_text(encoding="utf-8")
            self.assertIn("episode_title: 标题", text)
            self.assertIn("## Shownotes", text)
            self.assertIn("## Script", text)

    def test_short_script_triggers_one_longer_rewrite(self):
        with TempRoot():
            config.ensure_source_dirs("engineering")
            short = "短" * 100
            longer = "长" * (interpret.MIN_HAN_CHARS + 500)
            with mock.patch.object(interpret, "run_llm",
                                   side_effect=[_raw(short), _raw(longer)]) as m:
                got = interpret.interpret(self.META, "body", "2026-02-11-T")
            self.assertEqual(m.call_count, 2)
            self.assertGreater(interpret.han_count(got["script"]), interpret.MIN_HAN_CHARS)

    def test_unparseable_output_is_retried(self):
        with TempRoot():
            config.ensure_source_dirs("engineering")
            good = _raw("正" * (interpret.MIN_HAN_CHARS + 10))
            with mock.patch.object(interpret, "run_llm",
                                   side_effect=["no markers at all", good]) as m:
                interpret.interpret(self.META, "body", "2026-02-11-T")
            self.assertEqual(m.call_count, 2)

    def test_session_limit_is_not_swallowed(self):
        # 撞限额必须原样上抛给 autorun，不能被解析重试吞掉
        with TempRoot():
            config.ensure_source_dirs("engineering")
            with mock.patch.object(interpret, "run_llm",
                                   side_effect=interpret.SessionLimitError("limit", "4pm")):
                with self.assertRaises(interpret.SessionLimitError):
                    interpret.interpret(self.META, "body", "2026-02-11-T")


if __name__ == "__main__":
    unittest.main()
