from types import SimpleNamespace

from src.fetchers import rss_fetcher


def test_fetch_rss_entries_filters_openai_academy_links(monkeypatch):
    feed = SimpleNamespace(
        status=200,
        bozo=0,
        entries=[
            {
                "title": "Using projects in ChatGPT",
                "link": "https://openai.com/academy/projects",
                "summary": "Learn ChatGPT projects.",
                "published": "Fri, 10 Apr 2026 00:00:00 GMT",
            },
            {
                "title": "Codex flexible pricing for teams",
                "link": "https://openai.com/index/codex-flexible-pricing-for-teams",
                "summary": "Pricing update for Codex.",
                "published": "Fri, 10 Apr 2026 00:00:00 GMT",
            },
        ],
    )
    monkeypatch.setattr(rss_fetcher.feedparser, "parse", lambda _: feed)

    result = rss_fetcher.fetch_rss_entries(
        {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml"}
    )

    assert [entry["link"] for entry in result] == [
        "https://openai.com/index/codex-flexible-pricing-for-teams"
    ]
