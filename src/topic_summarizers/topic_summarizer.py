import re


WORD_PATTERN = re.compile(r"\w+")
MAX_TOP_KEYWORDS = 3
STOPWORDS = {
    "the",
    "and",
    "of",
    "to",
    "a",
    "an",
    "in",
    "on",
    "for",
    "with",
    "is",
    "are",
}


def _extract_keywords(article: dict) -> list[str]:
    matched_keywords = article.get("matched_keywords", [])
    if not isinstance(matched_keywords, list):
        return []

    keywords = []
    for keyword in matched_keywords:
        if isinstance(keyword, str):
            normalized_keyword = keyword.strip().lower()
            if normalized_keyword:
                keywords.append(normalized_keyword)

    return keywords


def _extract_words(article: dict) -> list[str]:
    title = article.get("title", "")
    summary = article.get("summary", "")
    combined_text = f"{title} {summary}".lower()
    return [
        word
        for word in WORD_PATTERN.findall(combined_text)
        if word and word not in STOPWORDS
    ]


def _select_top_keywords(keyword_counts: dict[str, int], word_counts: dict[str, int]) -> list[str]:
    counts = keyword_counts if keyword_counts else word_counts
    sorted_keywords = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [keyword for keyword, _ in sorted_keywords[:MAX_TOP_KEYWORDS]]


def _build_topic_summary(article_count: int, top_keywords: list[str]) -> str:
    if top_keywords:
        return (
            f"{', '.join(top_keywords)} を中心とした記事が "
            f"{article_count} 件あるトピック。"
        )

    return f"関連する記事が {article_count} 件あるトピック。"


def summarize_topics(articles: list[dict]) -> list[dict]:
    if not isinstance(articles, list):
        raise ValueError("articles must be a list.")

    topic_map = {}
    topic_order = []

    for article in articles:
        if not isinstance(article, dict):
            raise ValueError("Each article must be a dict.")

        topic_id = article.get("topic_id", "")
        if not isinstance(topic_id, str) or not topic_id:
            continue

        if topic_id not in topic_map:
            topic_map[topic_id] = {
                "article_count": 0,
                "keyword_counts": {},
                "word_counts": {},
            }
            topic_order.append(topic_id)

        topic = topic_map[topic_id]
        topic["article_count"] += 1

        for keyword in _extract_keywords(article):
            topic["keyword_counts"][keyword] = topic["keyword_counts"].get(keyword, 0) + 1

        for word in _extract_words(article):
            topic["word_counts"][word] = topic["word_counts"].get(word, 0) + 1

    topic_summaries = []

    for topic_id in topic_order:
        topic = topic_map[topic_id]
        top_keywords = _select_top_keywords(
            topic["keyword_counts"],
            topic["word_counts"],
        )
        topic_summaries.append(
            {
                "topic_id": topic_id,
                "article_count": topic["article_count"],
                "top_keywords": top_keywords,
                "summary": _build_topic_summary(
                    topic["article_count"],
                    top_keywords,
                ),
            }
        )

    return topic_summaries
