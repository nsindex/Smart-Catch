import json
import re
import urllib.error
import urllib.request


EXACT_LINE_MAP = {
    "# Daily Report": "# 日次レポート",
    "# Action Suggestions": "# 行動提案",
    "## Top Topics": "## 注目トピック",
    "## Highlight Articles": "## 注目記事",
    "## Recommended Actions": "## 推奨アクション",
    "## Priority Topics": "## 優先トピック",
    "## Topic Summaries": "## トピック要約",
    "# Collected Articles": "# 収集記事一覧",
    "# Monitored Articles": "# 監視記事一覧",
    "### Summary": "### 要約",
}

LABEL_MAP = {
    "- topic_id:": "- topic_id:",
    "- Summary:": "- 要約:",
    "- Top Keywords:": "- 主要キーワード:",
    "- Article Count:": "- 記事数:",
    "- Generated At:": "- 生成日時:",
    "- Topic Count:": "- トピック数:",
    "- Source:": "- ソース:",
    "- Published:": "- 公開日:",
    "- Matched:": "- 一致:",
    "- Score:": "- スコア:",
    "- Matched Keywords:": "- 一致キーワード:",
    "- URL:": "- URL:",
}

PHRASE_MAP = [
    ("prompt injection", "プロンプトインジェクション"),
    ("open source", "オープンソース"),
    ("domain-specific", "特化型"),
    ("under a day", "短期間で"),
    ("twice as fast", "2倍の速さで"),
    ("support speed", "支援速度"),
    ("catalog accuracy", "カタログ精度"),
    ("internal coding agents", "内部コーディングエージェント"),
    ("computer environment", "コンピュータ環境"),
    ("safety blueprint", "安全指針"),
    ("coding agent", "コーディングエージェント"),
]

TERM_MAP = {
    "ai": "AI",
    "agent": "エージェント",
    "agents": "エージェント",
    "chatgpt": "ChatGPT",
    "codex": "Codex",
    "openai": "OpenAI",
    "model": "モデル",
    "models": "モデル",
    "research": "研究",
    "performance": "性能",
    "data": "データ",
    "training": "学習",
    "source": "ソース",
    "security": "セキュリティ",
    "report": "レポート",
    "designing": "設計",
    "resist": "耐える",
    "monitor": "監視",
    "monitoring": "監視",
    "internal": "内部",
    "coding": "コーディング",
    "misalignment": "不整合",
    "acquire": "買収",
    "introducing": "紹介",
    "boosts": "向上",
    "accuracy": "精度",
    "support": "支援",
    "speed": "速度",
    "fixes": "改善",
    "issues": "問題",
    "workers": "労働者",
    "insights": "洞察",
    "compensation": "報酬",
    "responses": "レスポンス",
    "environment": "環境",
    "japan": "日本",
    "face": "Face",
    "hugging": "Hugging",
    "build": "構築",
    "embedding": "埋め込み",
}

DEFAULT_TRANSLATION_MODEL = "gemma3n:e4b"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_TIMEOUT_SECONDS = 12
ASCII_WORD_PATTERN = re.compile(r"\b[A-Za-z][A-Za-z0-9'\-\.]*\b")
HIGHLIGHT_ARTICLE_PATTERN = re.compile(r"^- \[(?P<topic>[^\]]+)\] (?P<title>.*) \(Score: (?P<score>[^\)]+)\)$")
TOPIC_ID_PATTERN = re.compile(r"^#{1,6}\s+topic_\d+$")
URL_ONLY_PATTERN = re.compile(r"^https?://", re.IGNORECASE)
JAPANESE_CHAR_PATTERN = re.compile(r"[ぁ-んァ-ン一-龠々ー]")
_TRANSLATION_CACHE = {}


def _translate_text_to_japanese(text: str) -> str:
    if not isinstance(text, str) or not text:
        return text

    translated_text = text

    for source_text, target_text in PHRASE_MAP:
        translated_text = re.sub(
            re.escape(source_text),
            target_text,
            translated_text,
            flags=re.IGNORECASE,
        )

    translated_text = ASCII_WORD_PATTERN.sub(
        lambda match: TERM_MAP.get(match.group(0).lower(), match.group(0)),
        translated_text,
    )

    translated_text = re.sub(r"\s+/\s+", " / ", translated_text)
    translated_text = re.sub(r"\s{2,}", " ", translated_text).strip()
    translated_text = re.sub(r"\s+([。、])", r"\1", translated_text)

    return translated_text


def _looks_like_markdown_safe_translation(source_text: str, translated_text: str) -> bool:
    if not translated_text or not isinstance(translated_text, str):
        return False

    stripped = translated_text.strip()
    if not stripped:
        return False

    if "以下が翻訳" in stripped or "翻訳結果" in stripped:
        return False

    source_urls = re.findall(r"https?://\S+", source_text)
    translated_urls = re.findall(r"https?://\S+", translated_text)
    if source_urls != translated_urls:
        return False

    source_topic_ids = re.findall(r"topic_\d+", source_text)
    translated_topic_ids = re.findall(r"topic_\d+", translated_text)
    if source_topic_ids != translated_topic_ids:
        return False

    return True


def _build_translation_prompt(text: str) -> str:
    return (
        "次の英語テキストを、自然で読みやすい日本語に翻訳してください。\n"
        "Markdown 記法、URL、topic_001 のような ID、数値は維持してください。\n"
        "余計な説明や前置きは書かず、翻訳後の本文だけを返してください。\n"
        "固有名詞は無理に訳さず原文維持で構いません。\n\n"
        f"{text}"
    )


def _build_title_translation_prompt(text: str) -> str:
    return (
        "次の英語テキストは記事タイトルです。\n"
        "日本語の見出しとして自然な表現に翻訳してください。\n"
        "単語ごとの直訳ではなく、意味が自然に伝わる日本語を優先してください。\n"
        "製品名、API名、サービス名、固有名詞の綴りは絶対に変更しないでください。1文字たりとも改変してはいけません。\n"
        "入力にない URL、topic_001 のような ID、角括弧付き補足、説明文は追加しないでください。\n"
        "数値や固有名詞は必要に応じて維持してください。\n"
        "余計な説明、前置き、引用符は不要です。翻訳結果だけを返してください。\n\n"
        f"{text}"
    )


def _should_use_ollama_translation(text: str) -> bool:
    if not isinstance(text, str) or not text.strip():
        return False

    if not ASCII_WORD_PATTERN.search(text):
        return False

    if JAPANESE_CHAR_PATTERN.search(text):
        return False

    return True


def _translate_text_with_ollama(text: str, content_type: str = "general") -> str | None:
    if not _should_use_ollama_translation(text):
        return None

    cache_key = f"{content_type}:{text}"
    if cache_key in _TRANSLATION_CACHE:
        return _TRANSLATION_CACHE[cache_key]

    prompt = _build_title_translation_prompt(text) if content_type == "title" else _build_translation_prompt(text)
    payload = {
        "model": DEFAULT_TRANSLATION_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    request = urllib.request.Request(
        OLLAMA_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=OLLAMA_TIMEOUT_SECONDS) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        _TRANSLATION_CACHE[cache_key] = None
        return None

    translated_text = response_data.get("response")
    if not isinstance(translated_text, str):
        _TRANSLATION_CACHE[cache_key] = None
        return None

    translated_text = translated_text.strip()
    if not _looks_like_markdown_safe_translation(text, translated_text):
        _TRANSLATION_CACHE[cache_key] = None
        return None

    _TRANSLATION_CACHE[cache_key] = translated_text
    return translated_text


def _translate_content_with_fallback(text: str, content_type: str = "general") -> str:
    llm_translated_text = _translate_text_with_ollama(text, content_type=content_type)
    if llm_translated_text:
        return llm_translated_text

    dictionary_translated_text = _translate_text_to_japanese(text)
    if dictionary_translated_text:
        return dictionary_translated_text

    return text


def _translate_keyword_list(text: str) -> str:
    parts = [part.strip() for part in text.split(",")]
    translated_parts = [_translate_text_to_japanese(part) for part in parts if part]
    return ", ".join(translated_parts)


def _translate_label_line(line: str) -> str:
    for source_label, target_label in LABEL_MAP.items():
        if line.startswith(source_label):
            value = line[len(source_label):].strip()

            if source_label in {"- Top Keywords:", "- Matched Keywords:"}:
                translated_value = _translate_keyword_list(value)
            elif source_label == "- Matched:":
                translated_value = {"Yes": "はい", "No": "いいえ"}.get(value, value)
            elif source_label == "- Source:":
                translated_value = _translate_text_to_japanese(value)
            elif source_label == "- Summary:":
                translated_value = _translate_content_with_fallback(value)
            else:
                translated_value = value

            if translated_value:
                return f"{target_label} {translated_value}"
            return target_label

    return line


def _translate_title_line(line: str) -> str:
    if not line.startswith("## "):
        return line

    if line in EXACT_LINE_MAP:
        return EXACT_LINE_MAP[line]

    title = line[3:].strip()
    return f"## {_translate_content_with_fallback(title, content_type='title')}"


def _translate_highlight_article_line(line: str) -> str:
    match = HIGHLIGHT_ARTICLE_PATTERN.match(line)
    if not match:
        return line

    topic_id = match.group("topic")
    title = _translate_content_with_fallback(match.group("title"), content_type="title")
    score = match.group("score")
    return f"- [{topic_id}] {title} (スコア: {score})"


def translate_markdown_to_japanese(
    markdown_text: str,
    document_type: str = "exploration",
) -> str:
    if not isinstance(markdown_text, str):
        raise ValueError("markdown_text must be a string.")

    if not isinstance(document_type, str):
        raise ValueError("document_type must be a string.")

    translated_lines = []
    in_article_summary = False

    for line in markdown_text.splitlines():
        if line == "### Summary":
            translated_lines.append("### 要約")
            in_article_summary = True
            continue

        if in_article_summary:
            if line.startswith("## ") or line.startswith("# ") or line.startswith("- "):
                in_article_summary = False
            elif line.strip():
                translated_lines.append(_translate_content_with_fallback(line))
                continue
            else:
                translated_lines.append(line)
                continue

        if not line:
            translated_lines.append(line)
            continue

        if document_type == "monitoring" and line == "# Collected Articles":
            translated_lines.append("# 監視記事一覧")
            continue

        if line in EXACT_LINE_MAP:
            translated_lines.append(EXACT_LINE_MAP[line])
            continue

        if TOPIC_ID_PATTERN.match(line.strip()):
            translated_lines.append(line)
            continue

        if line.startswith("## "):
            translated_lines.append(_translate_title_line(line))
            continue

        if line.startswith("- ["):
            translated_lines.append(_translate_highlight_article_line(line))
            continue

        if line.startswith("- "):
            translated_lines.append(_translate_label_line(line))
            continue

        translated_lines.append(_translate_text_to_japanese(line))

    return "\n".join(translated_lines)


