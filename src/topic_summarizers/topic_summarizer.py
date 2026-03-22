import re


WORD_PATTERN = re.compile(r"\w+")
ASCII_WORD_PATTERN = re.compile(r"\b[a-zA-Z][a-zA-Z0-9_-]*\b")
MAX_TOP_KEYWORDS = 3
MAX_FOCUS_WORDS = 2
MAX_REPRESENTATIVE_TITLES = 2
NOISE_TOPIC_WORDS = {
    "news",
    "update",
    "latest",
    "new",
    "report",
    "and",
    "to",
    "of",
    "in",
    "on",
    "for",
    "with",
    "blog",
    "feed",
    "gmt",
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
}
WEAK_TOPIC_WORDS = {"ai", "agent", "openai"}
JAPANESE_NOISE_WORDS = {
    "について",
    "扱っている",
    "説明している",
    "紹介している",
    "まとめている",
    "関する",
    "について扱っている",
    "について説明している",
    "について紹介している",
    "についてまとめている",
    "元のフィード要約が無いため",
    "情報源は",
    "公開日は",
    "題名と付随情報をもとに要点を確認しやすい形で補っている",
}
JAPANESE_TERM_MAP = {
    "ai": "AI",
    "model": "モデル",
    "models": "モデル",
    "research": "研究",
    "performance": "性能",
    "data": "データ",
    "training": "学習",
    "agent": "エージェント",
    "agents": "エージェント",
    "chatgpt": "ChatGPT",
    "codex": "Codex",
    "openai": "OpenAI",
    "source": "ソース",
    "open": "オープン",
}


def _normalize_topic_word(word: str) -> str:
    return word.strip().lower()


def _is_noise_topic_word(word: str) -> bool:
    if not word:
        return True

    if len(word) <= 2:
        return True

    if word.isdigit():
        return True

    if word in NOISE_TOPIC_WORDS:
        return True

    if word in JAPANESE_NOISE_WORDS:
        return True

    return False


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
    combined_text = f"{title} {summary}"
    return [
        normalized_word
        for normalized_word in (
            _normalize_topic_word(word) for word in WORD_PATTERN.findall(combined_text)
        )
        if not _is_noise_topic_word(normalized_word)
    ]


def _select_top_keywords(keyword_counts: dict[str, int], word_counts: dict[str, int]) -> list[str]:
    counts = keyword_counts if keyword_counts else word_counts
    sorted_keywords = sorted(
        counts.items(),
        key=lambda item: (item[0] in WEAK_TOPIC_WORDS, -item[1], item[0]),
    )
    return [keyword for keyword, _ in sorted_keywords[:MAX_TOP_KEYWORDS]]


def _select_focus_words(top_keywords: list[str], word_counts: dict[str, int]) -> list[str]:
    sorted_words = sorted(word_counts.items(), key=lambda item: (-item[1], item[0]))
    focus_words = []

    for word, _ in sorted_words:
        if word in top_keywords:
            continue
        if word in focus_words:
            continue
        focus_words.append(word)
        if len(focus_words) >= MAX_FOCUS_WORDS:
            break

    return focus_words


def _normalize_title(title: str) -> str:
    normalized_title = " ".join(title.split())
    if len(normalized_title) > 48:
        return f"{normalized_title[:45]}..."
    return normalized_title


def _translate_to_japanese(summary: str) -> str:
    if not isinstance(summary, str):
        return summary

    translated_summary = ASCII_WORD_PATTERN.sub(
        lambda match: JAPANESE_TERM_MAP.get(match.group(0).lower(), match.group(0)),
        summary,
    )

    translated_summary = re.sub(r"\s+([。、])", r"\1", translated_summary)
    translated_summary = re.sub(r"\s{2,}", " ", translated_summary).strip()

    if translated_summary and not translated_summary.endswith("。"):
        translated_summary += "。"

    return translated_summary


def _build_topic_summary(
    article_count: int,
    top_keywords: list[str],
    focus_words: list[str],
    representative_titles: list[str],
) -> str:
    topic_label = " / ".join(top_keywords[:2]) if top_keywords else "関連記事"
    summary_parts = [f"{topic_label} に関する記事が {article_count} 件まとまっている。"]

    if focus_words:
        summary_parts.append(
            f"記事では {', '.join(focus_words)} に関する記述が目立ち、同じ論点が繰り返し扱われている。"
        )
    elif len(top_keywords) >= 2:
        summary_parts.append(
            f"共通する話題は {top_keywords[0]} と {top_keywords[1]} に集まり、テーマの軸が比較的はっきりしている。"
        )
    else:
        summary_parts.append(
            "同じ話題圏の記事が複数集まっており、直近の動きをまとめて追いやすい。"
        )

    if representative_titles and article_count >= 3:
        summary_parts.append(
            f"代表例として「{representative_titles[0]}」などがあり、注目点を素早く把握しやすい。"
        )
    elif article_count >= 5:
        summary_parts.append("件数も一定数あり、継続して確認する価値がある。")

    return "".join(summary_parts)


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
                "representative_titles": [],
            }
            topic_order.append(topic_id)

        topic = topic_map[topic_id]
        topic["article_count"] += 1

        title = article.get("title", "")
        if isinstance(title, str):
            normalized_title = _normalize_title(title)
            if normalized_title and normalized_title not in topic["representative_titles"]:
                topic["representative_titles"].append(normalized_title)
                topic["representative_titles"] = topic["representative_titles"][:MAX_REPRESENTATIVE_TITLES]

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
        focus_words = _select_focus_words(top_keywords, topic["word_counts"])
        summary = _build_topic_summary(
            topic["article_count"],
            top_keywords,
            focus_words,
            topic["representative_titles"],
        )
        summary = _translate_to_japanese(summary)
        topic_summaries.append(
            {
                "topic_id": topic_id,
                "article_count": topic["article_count"],
                "top_keywords": top_keywords,
                "summary": summary,
            }
        )

    return topic_summaries
