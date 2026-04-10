from src.classifiers.keyword_classifier import classify_entries


def test_classify_entries_ignores_openai_academy_urls():
    entries = [
        {
            "source": "OpenAI Blog",
            "source_url": "https://openai.com/blog/rss.xml",
            "title": "Using projects in ChatGPT",
            "url": "https://openai.com/academy/projects",
            "published_at": "Fri, 10 Apr 2026 00:00:00 GMT",
            "summary": "Learn how to use ChatGPT projects effectively.",
        }
    ]

    result = classify_entries(entries, ["ChatGPT"])

    assert result[0]["matched"] is False
    assert result[0]["score"] == 0
    assert result[0]["matched_keywords"] == []
