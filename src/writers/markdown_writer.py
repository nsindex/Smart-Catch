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
) -> str:
    if not isinstance(entries, list):
        raise ValueError("entries must be a list.")

    markdown_parts = []

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
