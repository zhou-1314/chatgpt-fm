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


class TestCodexLimitReset(unittest.TestCase):
    """codex 的 429 响应体带精确重置时间，必须解析出来。

    实测响应体（ChatGPT Pro 撞周限额时）：
      {"error":{"type":"usage_limit_reached","message":"The usage limit has been reached",
                "plan_type":"pro","resets_at":1789435516,"resets_in_seconds":513840}}
    """

    PRO_WEEKLY = ('{"error":{"type":"usage_limit_reached","message":"The usage limit has '
                  'been reached","plan_type":"pro","resets_at":1789435516,'
                  '"resets_in_seconds":513840}}')

    def test_weekly_limit_is_flagged_and_not_slept_through(self):
        err = interpret._codex_limit_error(self.PRO_WEEKLY, "quota exceeded")
        self.assertEqual(err.reset_seconds, 513840)
        self.assertTrue(err.weekly)          # 6 天后重置，autorun 必须停下而不是睡等
        self.assertIn("天后", err.reset_raw)

    def test_short_limit_is_sleepable(self):
        err = interpret._codex_limit_error(
            '{"error":{"resets_in_seconds":1800}}', "rate limited")
        self.assertEqual(err.reset_seconds, 1800)
        self.assertFalse(err.weekly)         # 半小时，睡等即可
        self.assertIn("小时后", err.reset_raw)

    def test_resets_at_timestamp_is_converted(self):
        import time as _t
        raw = '{"error":{"resets_at":%d}}' % int(_t.time() + 7200)
        err = interpret._codex_limit_error(raw, "x")
        self.assertIsNotNone(err.reset_seconds)
        self.assertAlmostEqual(err.reset_seconds, 7200, delta=10)

    def test_unparseable_body_degrades_gracefully(self):
        for raw in ("not json", "", "{}", '{"error":null}'):
            err = interpret._codex_limit_error(raw, "quota exceeded")
            self.assertIsInstance(err, interpret.SessionLimitError)
            self.assertIsNone(err.reset_seconds)
            self.assertFalse(err.weekly)


class TestSecondsUntilReset(unittest.TestCase):
    def test_precise_seconds_win_over_text(self):
        from chatgpt_fm import cli
        self.assertEqual(cli._seconds_until_reset("4:50pm", 1800), 1980)  # 1800 + 180 缓冲

    def test_falls_back_to_text_parsing(self):
        from chatgpt_fm import cli
        got = cli._seconds_until_reset("4:50pm", None)
        self.assertGreater(got, 0)
        self.assertLessEqual(got, 24 * 3600 + 180)

    def test_no_information_falls_back_to_an_hour(self):
        from chatgpt_fm import cli
        self.assertEqual(cli._seconds_until_reset("", None), 3600)
