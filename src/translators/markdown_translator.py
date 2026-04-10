import json
import logging
import os
import re
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

from src.utils.llm_sanitizer import sanitize_llm_input

LOGGER = logging.getLogger(__name__)

_CACHE_FILE = Path("output/translation_cache.json")
_CACHE_MAX_ENTRIES = 2000


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

_DEFAULT_OLLAMA_HOST = "http://localhost:11434"
_DEFAULT_OLLAMA_MODEL = "gemma3n:e4b"
OLLAMA_TIMEOUT_SECONDS = 60
ASCII_WORD_PATTERN = re.compile(r"\b[A-Za-z][A-Za-z0-9'\-\.]*\b")
HIGHLIGHT_ARTICLE_PATTERN = re.compile(r"^- \[(?P<topic>[^\]]+)\] (?P<title>.*) \(Score: (?P<score>[^\)]+)\)$")
TOPIC_ID_PATTERN = re.compile(r"^#{1,6}\s+topic_\d+$")
URL_ONLY_PATTERN = re.compile(r"^https?://", re.IGNORECASE)
JAPANESE_CHAR_PATTERN = re.compile(r"[ぁ-んァ-ン一-龠々ー]")
CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
COMMON_ENGLISH_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}
DICTIONARY_TRANSLATION_MAX_WORDS = 3


def _load_translation_cache() -> dict:
    if not _CACHE_FILE.exists():
        return {}
    try:
        return json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
    except Exception as exc:
        LOGGER.warning("Failed to load translation cache: %s", exc)
        return {}


def _save_translation_cache(cache: dict) -> None:
    try:
        _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(cache, ensure_ascii=False, indent=None, separators=(",", ":"))
        fd, tmp_name = tempfile.mkstemp(
            dir=_CACHE_FILE.parent, prefix=_CACHE_FILE.name, suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            Path(tmp_name).replace(_CACHE_FILE)
        except Exception:
            tmp = Path(tmp_name)
            if tmp.exists():
                tmp.unlink(missing_ok=True)
            raise
    except Exception as exc:
        LOGGER.warning("Failed to save translation cache: %s", exc)


_TRANSLATION_CACHE: dict = _load_translation_cache()


def _translate_text_to_japanese(text: str) -> str:
    if not isinstance(text, str) or not text:
        return text

    # 辞書翻訳はキーワードや短いフレーズ向けに限定し、
    # 英文タイトルや英文要約のような自然文は Ollama 側に委ねる。
    if _is_english_rich_text(text) and not _is_dictionary_safe_text(text):
        return text

    translated_text = text

    for source_text, target_text in sorted(PHRASE_MAP, key=lambda x: len(x[0]), reverse=True):
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


def _count_ascii_words(text: str) -> int:
    return len(ASCII_WORD_PATTERN.findall(text))


def _has_common_english_words(text: str) -> bool:
    lowered_words = [word.lower() for word in ASCII_WORD_PATTERN.findall(text)]
    return any(word in COMMON_ENGLISH_WORDS for word in lowered_words)


def _is_dictionary_safe_text(text: str) -> bool:
    ascii_word_count = _count_ascii_words(text)
    if ascii_word_count == 0:
        return True

    if ascii_word_count <= DICTIONARY_TRANSLATION_MAX_WORDS and "\n" not in text:
        return True

    return False


def _is_english_rich_text(text: str) -> bool:
    if not isinstance(text, str):
        return False

    stripped = text.strip()
    if not stripped:
        return False

    if URL_ONLY_PATTERN.match(stripped) or TOPIC_ID_PATTERN.match(stripped):
        return False

    ascii_word_count = _count_ascii_words(text)
    if ascii_word_count < 2:
        return False

    if JAPANESE_CHAR_PATTERN.search(text):
        return True

    return _has_common_english_words(text) or ascii_word_count >= 4


def _normalize_ollama_host(ollama_host: str) -> str:
    normalized = (ollama_host or _DEFAULT_OLLAMA_HOST).strip()
    if not normalized:
        return _DEFAULT_OLLAMA_HOST
    return normalized.rstrip("/")


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
    safe_text = CONTROL_CHAR_PATTERN.sub("", text)
    safe_text = safe_text.replace("```", "` ` `").replace("---", "—").strip()[:4000]
    return (
        "次のテキストを、自然で読みやすい日本語に翻訳してください。\n"
        "Markdown の見出し・箇条書き・改行・空行は維持してください。\n"
        "URL、topic_001 のような ID、数値、製品名・API名・サービス名は維持してください。\n"
        "入力にない説明、前置き、補足、コードブロックは追加しないでください。\n"
        "翻訳後の本文だけを返してください。\n\n"
        "<text>\n"
        f"{safe_text}\n"
        "</text>"
    )


def _build_title_translation_prompt(text: str) -> str:
    safe_text = sanitize_llm_input(text, limit=300)
    return (
        "次の英語テキストは記事タイトルです。\n"
        "日本語の見出しとして自然な表現に翻訳してください。\n"
        "単語ごとの直訳ではなく、意味が自然に伝わる日本語を優先してください。\n"
        "製品名、API名、サービス名、固有名詞の綴りは絶対に変更しないでください。1文字たりとも改変してはいけません。\n"
        "入力にない URL、topic_001 のような ID、角括弧付き補足、説明文は追加しないでください。\n"
        "数値や固有名詞は必要に応じて維持してください。\n"
        "余計な説明、前置き、引用符は不要です。翻訳結果だけを返してください。\n\n"
        f"{safe_text}"
    )


def _should_use_ollama_translation(text: str) -> bool:
    if not isinstance(text, str) or not text.strip():
        return False

    if not ASCII_WORD_PATTERN.search(text):
        return False

    stripped = text.strip()
    if URL_ONLY_PATTERN.match(stripped) or TOPIC_ID_PATTERN.match(stripped):
        return False

    return _is_english_rich_text(text) or not _is_dictionary_safe_text(text)


def _translate_text_with_ollama(
    text: str,
    content_type: str = "general",
    ollama_host: str = _DEFAULT_OLLAMA_HOST,
    ollama_model: str = _DEFAULT_OLLAMA_MODEL,
) -> str | None:
    if not _should_use_ollama_translation(text):
        return None

    ollama_host = _normalize_ollama_host(ollama_host)

    cache_key = f"{content_type}:{text}"
    if cache_key in _TRANSLATION_CACHE:
        cached = _TRANSLATION_CACHE[cache_key]
        if cached is None:
            LOGGER.debug("Ollama translation: cache miss (previously failed): %r", text[:80])
        return cached

    LOGGER.debug("Ollama translation: requesting %s %r", content_type, text[:80])
    prompt = _build_title_translation_prompt(text) if content_type == "title" else _build_translation_prompt(text)
    payload = {
        "model": ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "stop": ["</text>", "```"],
        },
    }
    request = urllib.request.Request(
        f"{ollama_host}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=OLLAMA_TIMEOUT_SECONDS) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        LOGGER.warning("Ollama request failed (URLError): %s | host=%s", exc, ollama_host)
        # タイムアウト・接続エラーはキャッシュしない（ホスト変更後にリトライできるよう）
        return None
    except TimeoutError as exc:
        LOGGER.warning("Ollama request timed out (%ss): %s", OLLAMA_TIMEOUT_SECONDS, exc)
        return None
    except (ValueError, OSError) as exc:
        LOGGER.warning("Ollama request error: %s", exc)
        return None

    translated_text = response_data.get("response")
    if not isinstance(translated_text, str):
        LOGGER.warning("Ollama response missing 'response' field: %r", response_data)
        _TRANSLATION_CACHE[cache_key] = None
        return None

    translated_text = translated_text.strip()
    if not _looks_like_markdown_safe_translation(text, translated_text):
        LOGGER.warning(
            "Ollama output rejected by validator: source=%r translated=%r",
            text[:60],
            translated_text[:60],
        )
        _TRANSLATION_CACHE[cache_key] = None
        return None

    _TRANSLATION_CACHE[cache_key] = translated_text
    if len(_TRANSLATION_CACHE) > _CACHE_MAX_ENTRIES:
        # 古いエントリを先頭から削除して上限に収める
        excess = len(_TRANSLATION_CACHE) - _CACHE_MAX_ENTRIES
        for old_key in list(_TRANSLATION_CACHE.keys())[:excess]:
            del _TRANSLATION_CACHE[old_key]
    _save_translation_cache(_TRANSLATION_CACHE)
    return translated_text


def _translate_content_with_fallback(
    text: str,
    content_type: str = "general",
    ollama_host: str = _DEFAULT_OLLAMA_HOST,
    ollama_model: str = _DEFAULT_OLLAMA_MODEL,
) -> str:
    llm_translated_text = _translate_text_with_ollama(text, content_type=content_type, ollama_host=ollama_host, ollama_model=ollama_model)
    if llm_translated_text:
        return llm_translated_text

    if _is_english_rich_text(text) and not _is_dictionary_safe_text(text):
        return text

    dictionary_translated_text = _translate_text_to_japanese(text)
    if dictionary_translated_text:
        return dictionary_translated_text

    return text


def _translate_keyword_list(
    text: str,
    use_ollama: bool = False,
    ollama_host: str = _DEFAULT_OLLAMA_HOST,
    ollama_model: str = _DEFAULT_OLLAMA_MODEL,
) -> str:
    parts = [part.strip() for part in text.split(",") if part.strip()]
    translated_parts = []
    seen: set[str] = set()

    for part in parts:
        translated = (
            _translate_content_with_fallback(part, ollama_host=ollama_host, ollama_model=ollama_model)
            if use_ollama
            else _translate_text_to_japanese(part)
        )
        # 翻訳後の日本語重複を除去（空白・記号を除いた形で比較）
        dedupe_key = re.sub(r"\s+", "", translated.strip())
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        translated_parts.append(translated)

    return ", ".join(translated_parts)


def _translate_label_line(
    line: str,
    use_ollama: bool = False,
    ollama_host: str = _DEFAULT_OLLAMA_HOST,
    ollama_model: str = _DEFAULT_OLLAMA_MODEL,
) -> str:
    for source_label, target_label in LABEL_MAP.items():
        if line.startswith(source_label):
            value = line[len(source_label):].strip()

            if source_label in {"- Top Keywords:", "- Matched Keywords:"}:
                translated_value = _translate_keyword_list(value, use_ollama=use_ollama, ollama_host=ollama_host, ollama_model=ollama_model)
            elif source_label == "- Matched:":
                translated_value = {"Yes": "はい", "No": "いいえ"}.get(value, value)
            elif source_label == "- Source:":
                translated_value = _translate_text_to_japanese(value)
            elif source_label == "- Summary:":
                translated_value = (
                    _translate_content_with_fallback(value, ollama_host=ollama_host, ollama_model=ollama_model)
                    if use_ollama or _should_use_ollama_translation(value)
                    else _translate_text_to_japanese(value)
                )
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
    use_ollama: bool = False,
    ollama_host: str = _DEFAULT_OLLAMA_HOST,
    ollama_model: str = _DEFAULT_OLLAMA_MODEL,
) -> str:
    """Markdown を日本語に翻訳する。

    Args:
        markdown_text: 翻訳対象の Markdown 文字列。
        document_type: "exploration" または "monitoring"。
        use_ollama: True のとき Ollama LLM 翻訳を試みる（遅いが高品質）。
                    False のとき辞書翻訳のみ（高速）。
    """
    if not isinstance(markdown_text, str):
        raise ValueError("markdown_text must be a string.")

    if not isinstance(document_type, str):
        raise ValueError("document_type must be a string.")

    def _translate_content(text: str, content_type: str = "general") -> str:
        if use_ollama or _should_use_ollama_translation(text):
            return _translate_content_with_fallback(text, content_type=content_type, ollama_host=ollama_host, ollama_model=ollama_model)
        return _translate_text_to_japanese(text)

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
                translated_lines.append(_translate_content(line))
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
            if line in EXACT_LINE_MAP:
                translated_lines.append(EXACT_LINE_MAP[line])
            else:
                title = line[3:].strip()
                translated_lines.append(f"## {_translate_content(title, 'title')}")
            continue

        if line.startswith("- ["):
            match = HIGHLIGHT_ARTICLE_PATTERN.match(line)
            if match:
                topic_id = match.group("topic")
                title = _translate_content(match.group("title"), "title")
                score = match.group("score")
                translated_lines.append(f"- [{topic_id}] {title} (スコア: {score})")
            else:
                translated_lines.append(line)
            continue

        if line.startswith("- "):
            translated_lines.append(_translate_label_line(line, use_ollama=use_ollama, ollama_host=ollama_host, ollama_model=ollama_model))
            continue

        translated_lines.append(_translate_content(line))

    return "\n".join(translated_lines)


