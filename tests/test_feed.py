"""feed.py 的纯函数单测：时长、日期、CDATA 转义。"""

import unittest

from chatgpt_fm import feed


class TestDuration(unittest.TestCase):
    def test_under_an_hour(self):
        self.assertEqual(feed._hms(1502), "25:02")

    def test_over_an_hour(self):
        self.assertEqual(feed._hms(3725), "1:02:05")

    def test_zero(self):
        self.assertEqual(feed._hms(0), "0:00")


class TestRfc822(unittest.TestCase):
    def test_same_day_episodes_keep_stable_order(self):
        earlier = feed._rfc822("2026-02-11", 10)
        later = feed._rfc822("2026-02-11", 11)
        self.assertNotEqual(earlier, later)

    def test_bad_date_does_not_raise(self):
        self.assertIn("2021", feed._rfc822("not-a-date", 1))


class TestCdata(unittest.TestCase):
    def test_plain_text_is_wrapped(self):
        self.assertEqual(feed._cdata("hi"), "<![CDATA[hi]]>")

    def test_nested_terminator_is_escaped(self):
        # shownotes 里出现 ]]> 会提前闭合 CDATA，必须拆开
        out = feed._cdata("a]]>b")
        self.assertTrue(out.startswith("<![CDATA["))
        self.assertTrue(out.endswith("]]>"))
        self.assertNotIn("a]]>b", out)


if __name__ == "__main__":
    unittest.main()
