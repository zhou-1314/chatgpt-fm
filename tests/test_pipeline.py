"""fetch / tts / digest / feed 的纯函数单测。不联网、不写仓库内容目录。"""

import unittest
from datetime import date

from chatgpt_fm import config, digest, fetch, interpret, tts


class TestMakeBase(unittest.TestCase):
    def test_date_and_title(self):
        self.assertEqual(
            fetch.make_base("2026-02-11", "Harness engineering"),
            "2026-02-11-Harness engineering",
        )

    def test_illegal_filename_chars_are_replaced(self):
        base = fetch.make_base("2026-02-11", "Harness engineering: Codex/agents?")
        self.assertNotIn(":", base)
        self.assertNotIn("/", base)
        self.assertNotIn("?", base)

    def test_missing_date_uses_placeholder(self):
        self.assertTrue(fetch.make_base("", "Untitled").startswith("0000-00-00-"))

    def test_trailing_dot_stripped(self):
        # Windows 上以点结尾的文件名非法
        self.assertFalse(fetch.make_base("2026-01-01", "Ends with a dot.").endswith("."))


class TestExtractPublished(unittest.TestCase):
    def test_json_ld(self):
        html = '<script>{"datePublished":"2026-02-11T09:00:00.000Z"}</script>'
        self.assertEqual(fetch._extract_published(html), "2026-02-11")

    def test_time_tag(self):
        self.assertEqual(
            fetch._extract_published('<time datetime="2024-05-13T10:00:00Z">May 13</time>'),
            "2024-05-13",
        )

    def test_no_anchor_returns_empty(self):
        # 页面上有推荐位日期也不能瞎猜，宁可返回空
        self.assertEqual(fetch._extract_published("<p>Aug 25, 2026</p>"), "")


class TestCleanMarkdown(unittest.TestCase):
    def test_boilerplate_heading_and_next_paragraph_dropped(self):
        md = "# Real title\n\nBody text.\n\n## Related articles\n\nSome teaser link.\n\nMore body."
        out = fetch._clean_markdown(md)
        self.assertIn("Body text.", out)
        self.assertIn("More body.", out)
        self.assertNotIn("Related articles", out)
        self.assertNotIn("Some teaser link.", out)


class TestChunking(unittest.TestCase):
    def test_chunks_respect_limit(self):
        text = "\n\n".join("句子。" * 300 for _ in range(6))
        chunks = tts.split_chunks(text, limit=2000)
        self.assertTrue(chunks)
        for c in chunks:
            self.assertLessEqual(len(c), 2000)

    def test_no_content_lost(self):
        text = "第一段。\n\n第二段。\n\n第三段。"
        joined = "".join(tts.split_chunks(text, limit=50))
        for part in ("第一段。", "第二段。", "第三段。"):
            self.assertIn(part, joined)

    def test_oversized_paragraph_is_split_by_sentence(self):
        chunks = tts.split_chunks("阿" * 100 + "。" + "阿" * 100 + "。", limit=120)
        self.assertGreater(len(chunks), 1)


class TestScriptSections(unittest.TestCase):
    BODY = "## Shownotes\n\n本期简介。\n\n- 要点一\n\n## Script\n\n正文第一段。\n\n正文第二段。\n"

    def test_extract_script(self):
        self.assertEqual(tts.extract_script(self.BODY), "正文第一段。\n\n正文第二段。")

    def test_extract_shownotes(self):
        self.assertIn("本期简介。", tts.extract_shownotes(self.BODY))
        self.assertNotIn("正文第一段", tts.extract_shownotes(self.BODY))


class TestParseOutput(unittest.TestCase):
    RAW = (
        "===EPISODE_TITLE===\n标题在这里\n"
        "===SHOWNOTES===\n简介\n\n- 要点\n"
        "===SCRIPT===\n正文内容。\n"
    )

    def test_three_sections(self):
        got = interpret.parse_output(self.RAW)
        self.assertEqual(got["episode_title"], "标题在这里")
        self.assertIn("要点", got["shownotes"])
        self.assertEqual(got["script"], "正文内容。")

    def test_missing_script_raises(self):
        with self.assertRaises(RuntimeError):
            interpret.parse_output("===EPISODE_TITLE===\n只有标题\n")

    def test_han_count(self):
        self.assertEqual(interpret.han_count("abc 中文字 123"), 3)


class TestWeekGrouping(unittest.TestCase):
    def test_week_sunday_is_sunday(self):
        # 2026-02-11 是周三，所在周的周日是 2026-02-08
        self.assertEqual(digest.week_sunday("2026-02-11"), date(2026, 2, 8))

    def test_sunday_maps_to_itself(self):
        self.assertEqual(digest.week_sunday("2026-02-08"), date(2026, 2, 8))

    def test_saturday_stays_in_same_week(self):
        self.assertEqual(digest.week_sunday("2026-02-14"), date(2026, 2, 8))

    def test_week_label_covers_seven_days(self):
        self.assertEqual(digest.week_label(date(2026, 2, 8)), "2026年2月8日–2026年2月14日")

    def test_date_window(self):
        self.assertTrue(digest.in_date_window("2026-02-10", "2026-02-08", "2026-02-14"))
        self.assertFalse(digest.in_date_window("2026-02-15", "2026-02-08", "2026-02-14"))
        # 缺任一端就不过滤
        self.assertTrue(digest.in_date_window("2026-02-15", None, None))


class TestConfigPaths(unittest.TestCase):
    def test_each_source_has_its_own_directory(self):
        dirs = [config.source_dir(s) for s in config.SOURCES]
        self.assertEqual(len(dirs), len(set(dirs)))

    def test_paths_live_under_content(self):
        p = config.script_path("engineering", "2026-02-11-x")
        self.assertTrue(str(p).startswith(str(config.CONTENT_DIR)))

    def test_digest_source_is_a_real_source(self):
        self.assertIn(config.DIGEST_SOURCE, config.SOURCES)
        self.assertIn(config.DEFAULT_SOURCE, config.SOURCES)


if __name__ == "__main__":
    unittest.main()


class TestThrottle(unittest.TestCase):
    """连续密集抓 openai.com 会被出口 IP 限流，请求之间必须有最小间隔。"""

    def test_consecutive_calls_are_spaced_out(self):
        import time
        from chatgpt_fm import net
        original = net.MIN_REQUEST_INTERVAL
        net.MIN_REQUEST_INTERVAL = 0.15
        net._last_request_at = 0.0
        try:
            start = time.monotonic()
            for _ in range(3):
                net._throttle()
            elapsed = time.monotonic() - start
        finally:
            net.MIN_REQUEST_INTERVAL = original
            net._last_request_at = 0.0
        # 第一次不等，后两次各等一个间隔
        self.assertGreaterEqual(elapsed, 0.15 * 2 * 0.9)

    def test_interval_is_configured(self):
        from chatgpt_fm import net
        self.assertGreater(net.MIN_REQUEST_INTERVAL, 0)


class TestTtsRetryBackoff(unittest.TestCase):
    """edge-tts 偶发断流；一块失败会让整篇作废，退避必须够长。"""

    def test_backoff_is_long_enough_to_ride_out_a_blip(self):
        from chatgpt_fm import tts
        self.assertGreaterEqual(sum(tts._RETRY_BACKOFF), 100)

    def test_backoff_increases(self):
        from chatgpt_fm import tts
        b = tts._RETRY_BACKOFF
        self.assertEqual(list(b), sorted(b))
        self.assertGreater(len(b), 2)
