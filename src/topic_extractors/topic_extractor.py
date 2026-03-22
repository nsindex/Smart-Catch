import re


WORD_PATTERN = re.compile(r"\w+")


def _extract_keywords(article: dict) -> set[str]:
    matched_keywords = article.get("matched_keywords", [])
    if not isinstance(matched_keywords, list):
        return set()

    keywords = set()
    for keyword in matched_keywords:
        if isinstance(keyword, str):
            normalized_keyword = keyword.strip().lower()
            if normalized_keyword:
                keywords.add(normalized_keyword)

    return keywords


def _extract_words(article: dict) -> set[str]:
    title = article.get("title", "")
    summary = article.get("summary", "")
    combined_text = f"{title} {summary}".lower()
    return {word for word in WORD_PATTERN.findall(combined_text) if word}


def _is_same_topic(article_keywords: set[str], article_words: set[str], topic: dict) -> bool:
    if article_keywords & topic["keywords"]:
        return True

    common_words = article_words & topic["words"]
    return len(common_words) >= 2


def assign_topics(articles: list[dict]) -> list[dict]:
    if not isinstance(articles, list):
        raise ValueError("articles must be a list.")

    topics = []
    articles_with_topics = []

    for article in articles:
        if not isinstance(article, dict):
            raise ValueError("Each article must be a dict.")

        article_keywords = _extract_keywords(article)
        article_words = _extract_words(article)
        assigned_topic_id = None

        for topic in topics:
            if _is_same_topic(article_keywords, article_words, topic):
                assigned_topic_id = topic["topic_id"]
                topic["keywords"].update(article_keywords)
                topic["words"].update(article_words)
                break

        if assigned_topic_id is None:
            assigned_topic_id = f"topic_{len(topics) + 1:03d}"
            topics.append(
                {
                    "topic_id": assigned_topic_id,
                    "keywords": set(article_keywords),
                    "words": set(article_words),
                }
            )

        article_with_topic = dict(article)
        article_with_topic["topic_id"] = assigned_topic_id
        articles_with_topics.append(article_with_topic)

    return articles_with_topics

