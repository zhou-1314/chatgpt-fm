"""sources.py 的纯函数单测：RSS / sitemap 解析、URL 归一、分源路由。不联网。"""

import unittest

from chatgpt_fm import config, sources

RSS_SAMPLE = """<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>
<title><![CDATA[OpenAI News]]></title>
<item>
  <title><![CDATA[Harness engineering: leveraging Codex]]></title>
  <description><![CDATA[By Ryan Lopopolo, Member of the Technical Staff]]></description>
  <link>https://openai.com/index/harness-engineering</link>
  <guid isPermaLink="true">https://openai.com/index/harness-engineering</guid>
  <category><![CDATA[Engineering]]></category>
  <pubDate>Wed, 11 Feb 2026 09:00:00 GMT</pubDate>
</item>
<item>
  <title><![CDATA[GPT-6 Astra: A new generation of intelligence]]></title>
  <description><![CDATA[Introducing GPT-6 Astra]]></description>
  <link>https://openai.com/index/gpt-6-astra</link>
  <category><![CDATA[Research]]></category>
  <pubDate>Mon, 03 Aug 2026 10:00:00 GMT</pubDate>
</item>
<item>
  <title><![CDATA[Some customer story]]></title>
  <description><![CDATA[No category at all]]></description>
  <link>https://openai.com/index/some-customer-story</link>
  <pubDate>Fri, 31 Jul 2026 00:00:00 GMT</pubDate>
</item>
<item>
  <title><![CDATA[A landing page, not an article]]></title>
  <link>https://openai.com/chatgpt/pricing</link>
  <pubDate>Fri, 31 Jul 2026 00:00:00 GMT</pubDate>
</item>
</channel></rss>"""

SITEMAP_SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://openai.com/news/engineering/</loc><lastmod>2026-09-08T12:48:48.348Z</lastmod></url>
  <url><loc>https://openai.com/index/scaling-postgresql/</loc><lastmod>2026-08-25T00:00:00.000Z</lastmod></url>
  <url><loc>https://openai.com/index/dall-e-2/</loc></url>
  <url><loc>https://openai.com/index/deep/nested/page/</loc></url>
</urlset>"""


class TestUrlNormalisation(unittest.TestCase):
    def test_trailing_slash_is_stripped(self):
        self.assertEqual(
            sources.normalize_url("https://openai.com/index/sora/"),
            "https://openai.com/index/sora",
        )

    def test_rss_and_sitemap_forms_collapse_to_one(self):
        # RSS 不带尾斜杠、sitemap 带，归一后必须相等，否则同一篇会被抓两次
        self.assertEqual(
            sources.normalize_url("https://openai.com/index/sora"),
            sources.normalize_url("https://openai.com/index/sora/"),
        )


class TestRfc822Date(unittest.TestCase):
    def test_parses_rss_pubdate(self):
        self.assertEqual(
            sources._rfc822_date("Wed, 11 Feb 2026 09:00:00 GMT"), "2026-02-11"
        )

    def test_empty_and_garbage(self):
        self.assertEqual(sources._rfc822_date(""), "")
        self.assertEqual(sources._rfc822_date("not a date"), "")

    def test_falls_back_to_iso_substring(self):
        self.assertEqual(sources._rfc822_date("published 2024-05-13 sometime"), "2024-05-13")


class TestParseRss(unittest.TestCase):
    def setUp(self):
        self.refs = sources.parse_rss(RSS_SAMPLE)

    def test_only_article_urls_are_kept(self):
        # /chatgpt/pricing 是栏目页，不是 /index/ 文章
        self.assertEqual(len(self.refs), 3)
        for r in self.refs:
            self.assertTrue(r.url.startswith(config.ARTICLE_PREFIX))

    def test_metadata_is_extracted(self):
        first = self.refs[0]
        self.assertEqual(first.title, "Harness engineering: leveraging Codex")
        self.assertEqual(first.published, "2026-02-11")
        self.assertEqual(first.category, "Engineering")
        self.assertEqual(first.source, "engineering")
        self.assertIn("Ryan Lopopolo", first.summary)

    def test_category_routing(self):
        by_url = {r.url: r for r in self.refs}
        self.assertEqual(by_url["https://openai.com/index/gpt-6-astra"].source, "research")

    def test_uncategorised_falls_back_to_digest_source(self):
        by_url = {r.url: r for r in self.refs}
        story = by_url["https://openai.com/index/some-customer-story"]
        self.assertEqual(story.category, "")
        self.assertEqual(story.source, config.DEFAULT_SOURCE)


class TestParseSitemap(unittest.TestCase):
    def test_only_single_level_index_urls(self):
        urls = sources.parse_sitemap_urls(SITEMAP_SAMPLE)
        self.assertEqual(
            urls,
            [
                "https://openai.com/index/scaling-postgresql",
                "https://openai.com/index/dall-e-2",
            ],
        )


class TestCategoryRouting(unittest.TestCase):
    def test_every_configured_category_routes_to_its_source(self):
        for name, src in config.SOURCES.items():
            for cat in src["categories"]:
                self.assertEqual(config.source_of_category(cat), name, cat)

    def test_unknown_category_goes_to_default(self):
        self.assertEqual(config.source_of_category("Brand New Category"),
                         config.DEFAULT_SOURCE)

    def test_no_category_is_claimed_by_two_sources(self):
        seen = set()
        for src in config.SOURCES.values():
            for cat in src["categories"]:
                self.assertNotIn(cat, seen, f"分类 {cat} 被两个源同时认领")
                seen.add(cat)

    def test_sitemap_tags_map_to_known_categories(self):
        for tag, cat in config.SITEMAP_CATEGORIES.items():
            self.assertIn(cat, config.CATEGORY_SOURCE, f"sitemap {tag} 映射到未知分类 {cat}")


if __name__ == "__main__":
    unittest.main()
