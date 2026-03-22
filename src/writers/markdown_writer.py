def build_daily_report_markdown(daily_report: dict) -> str:
    if not isinstance(daily_report, dict):
        raise ValueError("daily_report must be a dict.")

    markdown_parts = [
        "# Daily Report",
        f"- Generated At: {daily_report.get('generated_at', '')}",
        f"- Topic Count: {daily_report.get('topic_count', 0)}",
        "## Top Topics",
    ]

    top_topics = daily_report.get("top_topics", [])
    if top_topics:
        for topic in top_topics:
            if not isinstance(topic, dict):
                raise ValueError("Each top topic must be a dict.")

            top_keywords = topic.get("top_keywords", [])
            top_keywords_text = ", ".join(top_keywords) if top_keywords else "None"
            markdown_parts.append(
                "\n".join(
                    [
                        f"### {topic.get('topic_id', '')}",
                        f"- Article Count: {topic.get('article_count', 0)}",
                        f"- Top Keywords: {top_keywords_text}",
                    ]
                )
            )
    else:
        markdown_parts.append("- None")

    markdown_parts.append("## Highlight Articles")
    highlight_articles = daily_report.get("highlight_articles", [])
    if highlight_articles:
        for article in highlight_articles:
            if not isinstance(article, dict):
                raise ValueError("Each highlight article must be a dict.")

            markdown_parts.append(
                f"- [{article.get('topic_id', '')}] {article.get('title', '')} (Score: {article.get('score', 0)})"
            )
    else:
        markdown_parts.append("- None")

    markdown_parts.extend(
        [
            "## Summary",
            daily_report.get("summary", "本日は注目トピックは確認されなかった。"),
        ]
    )

    return "\n\n".join(markdown_parts)


def build_action_suggestions_markdown(action_suggestions: dict) -> str:
    if not isinstance(action_suggestions, dict):
        raise ValueError("action_suggestions must be a dict.")

    markdown_parts = ["# Action Suggestions", "## Priority Topics"]

    priority_topics = action_suggestions.get("priority_topics", [])
    if priority_topics:
        for topic in priority_topics:
            if not isinstance(topic, dict):
                raise ValueError("Each priority topic must be a dict.")

            top_keywords = topic.get("top_keywords", [])
            top_keywords_text = ", ".join(top_keywords) if top_keywords else "None"
            markdown_parts.append(
                "\n".join(
                    [
                        f"### {topic.get('topic_id', '')}",
                        f"- Article Count: {topic.get('article_count', 0)}",
                        f"- Top Keywords: {top_keywords_text}",
                    ]
                )
            )
    else:
        markdown_parts.append("- None")

    markdown_parts.append("## Highlight Articles")
    highlight_articles = action_suggestions.get("highlight_articles", [])
    if highlight_articles:
        for article in highlight_articles:
            if not isinstance(article, dict):
                raise ValueError("Each action highlight article must be a dict.")

            markdown_parts.append(
                f"- [{article.get('topic_id', '')}] {article.get('title', '')} (Score: {article.get('score', 0)})"
            )
    else:
        markdown_parts.append("- None")

    markdown_parts.append("## Recommended Actions")
    recommended_actions = action_suggestions.get("recommended_actions", [])
    if recommended_actions:
        for action in recommended_actions:
            markdown_parts.append(f"- {action}")
    else:
        markdown_parts.append("- 主要トピックを確認する")

    return "\n\n".join(markdown_parts)


def build_topic_summaries_markdown(topic_summaries: list[dict]) -> str:
    if not isinstance(topic_summaries, list):
        raise ValueError("topic_summaries must be a list.")

    if not topic_summaries:
        return ""

    markdown_parts = ["## Topic Summaries"]

    for topic_summary in topic_summaries:
        if not isinstance(topic_summary, dict):
            raise ValueError("Each topic summary must be a dict.")

        top_keywords = topic_summary.get("top_keywords", [])
        top_keywords_text = ", ".join(top_keywords) if top_keywords else "None"
        summary = topic_summary.get("summary", "関連する記事が 0 件あるトピック。")

        markdown_parts.append(
            "\n".join(
                [
                    f"### {topic_summary.get('topic_id', '')}",
                    f"- Article Count: {topic_summary.get('article_count', 0)}",
                    f"- Top Keywords: {top_keywords_text}",
                    f"- Summary: {summary}",
                ]
            )
        )

    return "\n\n".join(markdown_parts)


def build_markdown(
    entries: list[dict],
    topic_summaries: list[dict] | None = None,
    daily_report: dict | None = None,
    action_suggestions: dict | None = None,
) -> str:
    if not isinstance(entries, list):
        raise ValueError("entries must be a list.")

    markdown_parts = []

    if daily_report is not None:
        markdown_parts.append(build_daily_report_markdown(daily_report))

    if action_suggestions is not None:
        markdown_parts.append(build_action_suggestions_markdown(action_suggestions))

    if topic_summaries is not None:
        topic_summaries_markdown = build_topic_summaries_markdown(topic_summaries)
        if topic_summaries_markdown:
            markdown_parts.append(topic_summaries_markdown)

    markdown_parts.append("# Collected Articles")

    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Each entry must be a dict.")

        title = entry.get("title", "")
        url = entry.get("url", "")
        source = entry.get("source", "")
        published_at = entry.get("published_at", "")
        summary = entry.get("summary", "")
        matched = "Yes" if entry.get("matched", False) else "No"
        matched_keywords = entry.get("matched_keywords", [])
        matched_keywords_text = ", ".join(matched_keywords) if matched_keywords else "None"
        score = entry.get("score", 0)

        markdown_parts.append(
            "\n".join(
                [
                    f"## {title}",
                    f"- URL: {url}",
                    f"- Source: {source}",
                    f"- Published: {published_at}",
                    f"- Matched: {matched}",
                    f"- Score: {score}",
                    f"- Matched Keywords: {matched_keywords_text}",
                    "### Summary",
                    summary,
                ]
            )
        )

    return "\n\n".join(markdown_parts)
