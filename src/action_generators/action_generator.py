MAX_PRIORITY_TOPICS = 3
MAX_HIGHLIGHT_ARTICLES = 3
MAX_RECOMMENDED_ACTIONS = 3


def _select_priority_topics(topic_summaries: list[dict]) -> list[dict]:
    sorted_topics = sorted(
        topic_summaries,
        key=lambda topic: (
            -topic.get("article_count", 0),
            -len(topic.get("top_keywords", [])),
            topic.get("topic_id", ""),
        ),
    )

    return [
        {
            "topic_id": topic.get("topic_id", ""),
            "article_count": topic.get("article_count", 0),
            "top_keywords": topic.get("top_keywords", []),
        }
        for topic in sorted_topics[:MAX_PRIORITY_TOPICS]
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


def _build_recommended_actions(
    priority_topics: list[dict],
    highlight_articles: list[dict],
) -> list[str]:
    actions = []

    for topic in priority_topics:
        top_keywords = topic.get("top_keywords", [])
        if not top_keywords:
            continue

        first_keyword = top_keywords[0]
        actions.append(f"{first_keyword} 関連を深掘りする")

        if len(top_keywords) >= 2:
            actions.append(
                f"{top_keywords[0]} / {top_keywords[1]} の動向を継続監視する"
            )
        break

    if highlight_articles:
        actions.append("高スコア記事を重点確認する")

    if not actions:
        actions.append("主要トピックを確認する")

    unique_actions = []
    for action in actions:
        if action not in unique_actions:
            unique_actions.append(action)
        if len(unique_actions) >= MAX_RECOMMENDED_ACTIONS:
            break

    return unique_actions


def build_action_suggestions(
    entries: list[dict],
    topic_summaries: list[dict],
) -> dict:
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

    priority_topics = _select_priority_topics(topic_summaries)
    highlight_articles = _select_highlight_articles(entries)
    recommended_actions = _build_recommended_actions(
        priority_topics,
        highlight_articles,
    )

    return {
        "priority_topics": priority_topics,
        "highlight_articles": highlight_articles,
        "recommended_actions": recommended_actions,
    }
