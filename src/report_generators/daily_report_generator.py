from datetime import datetime


MAX_TOP_TOPICS = 3
MAX_HIGHLIGHT_ARTICLES = 3


def _select_top_topics(topic_summaries: list[dict]) -> list[dict]:
    sorted_topics = sorted(
        topic_summaries,
        key=lambda topic: (
            -topic.get("article_count", 0),
            topic.get("topic_id", ""),
        ),
    )

    return [
        {
            "topic_id": topic.get("topic_id", ""),
            "article_count": topic.get("article_count", 0),
            "top_keywords": topic.get("top_keywords", []),
        }
        for topic in sorted_topics[:MAX_TOP_TOPICS]
    ]


def _select_highlight_articles(entries: list[dict]) -> list[dict]:
    candidate_entries = [entry for entry in entries if entry.get("matched") is True]

    if not candidate_entries:
        candidate_entries = list(entries)

    sorted_entries = sorted(
        candidate_entries,
        key=lambda entry: (
            -entry.get("score", 0),
            entry.get("title", ""),
        ),
    )

    return [
        {
            "title": entry.get("title", ""),
            "score": entry.get("score", 0),
            "topic_id": entry.get("topic_id", ""),
        }
        for entry in sorted_entries[:MAX_HIGHLIGHT_ARTICLES]
    ]


def _build_report_summary(topic_count: int, top_topics: list[dict]) -> str:
    top_keywords = []

    for topic in top_topics:
        for keyword in topic.get("top_keywords", []):
            if keyword and keyword not in top_keywords:
                top_keywords.append(keyword)
            if len(top_keywords) >= 3:
                break
        if len(top_keywords) >= 3:
            break

    if top_keywords:
        return f"本日は {', '.join(top_keywords)} を中心とした話題が多く見られた。"

    if topic_count:
        return f"本日は {topic_count} 件のトピックが確認された。"

    return "本日は注目トピックは確認されなかった。"


def build_daily_report(entries: list[dict], topic_summaries: list[dict]) -> dict:
    if not isinstance(entries, list):
        raise ValueError("entries must be a list.")

    if not isinstance(topic_summaries, list):
        raise ValueError("topic_summaries must be a list.")

    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Each entry must be a dict.")

    for topic_summary in topic_summaries:
        if not isinstance(topic_summary, dict):
            raise ValueError("Each topic summary must be a dict.")

    top_topics = _select_top_topics(topic_summaries)
    highlight_articles = _select_highlight_articles(entries)
    topic_count = len(topic_summaries)

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "topic_count": topic_count,
        "top_topics": top_topics,
        "highlight_articles": highlight_articles,
        "summary": _build_report_summary(topic_count, top_topics),
    }
