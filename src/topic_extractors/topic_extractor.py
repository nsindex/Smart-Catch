import re


WORD_PATTERN = re.compile(r"\w+")
NOISE_TOPIC_WORDS = {"news", "update", "latest", "new", "report"}
WEAK_TOPIC_WORDS = {"ai", "agent", "openai"}


def _normalize_topic_word(word: str) -> str:
    return word.strip().lower()


def _is_noise_topic_word(word: str) -> bool:
    if not word:
        return True

    if len(word) == 1:
        return True

    if word.isdigit():
        return True

    if word in NOISE_TOPIC_WORDS:
        return True

    return False


def _filter_topic_words(words: list[str]) -> set[str]:
    filtered_words = set()

    for word in words:
        if not isinstance(word, str):
            continue

        normalized_word = _normalize_topic_word(word)
        if _is_noise_topic_word(normalized_word):
            continue

        filtered_words.add(normalized_word)

    return filtered_words


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
    combined_text = f"{title} {summary}"
    return _filter_topic_words(WORD_PATTERN.findall(combined_text))


def assign_topics(articles: list[dict]) -> list[dict]:
    if not isinstance(articles, list):
        raise ValueError("articles must be a list.")

    topics = {}
    articles_with_topics = []

    for article in articles:
        if not isinstance(article, dict):
            raise ValueError("Each article must be a dict.")

        article_keywords = _extract_keywords(article)
        source = article.get("source", "")

        if article_keywords:
            topic_key = sorted(article_keywords)[0]
        else:
            topic_key = source if source else "other"

        if topic_key not in topics:
            topics[topic_key] = f"topic_{len(topics) + 1:03d}"

        article_with_topic = dict(article)
        article_with_topic["topic_id"] = topics[topic_key]
        articles_with_topics.append(article_with_topic)

    return articles_with_topics
