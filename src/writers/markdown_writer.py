def build_markdown(entries: list[dict]) -> str:
    if not isinstance(entries, list):
        raise TypeError("entries must be a list.")

    markdown_parts = ["# Collected Articles"]

    for entry in entries:
        if not isinstance(entry, dict):
            raise TypeError("Each entry must be a dict.")

        title = entry.get("title", "")
        url = entry.get("url", "")
        source = entry.get("source", "")
        published_at = entry.get("published_at", "")
        summary = entry.get("summary", "")
        matched = "Yes" if entry.get("matched", False) else "No"
        matched_keywords = entry.get("matched_keywords", [])
        matched_keywords_text = ", ".join(matched_keywords) if matched_keywords else "None"

        markdown_parts.append(
            "\n".join(
                [
                    f"## {title}",
                    f"- URL: {url}",
                    f"- Source: {source}",
                    f"- Published: {published_at}",
                    f"- Matched: {matched}",
                    f"- Matched Keywords: {matched_keywords_text}",
                    "### Summary",
                    summary,
                ]
            )
        )

    return "\n\n".join(markdown_parts)
