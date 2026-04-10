from src.translators import markdown_translator


def test_should_use_ollama_translation_for_mixed_language_text():
    assert markdown_translator._should_use_ollama_translation(
        "ChatGPT の projects feature overview"
    )


def test_should_use_ollama_translation_for_english_title():
    assert markdown_translator._should_use_ollama_translation(
        "Introducing the Child Safety Blueprint"
    )


def test_dictionary_translation_does_not_partially_translate_english_title():
    assert (
        markdown_translator._translate_text_to_japanese(
            "Introducing the Child Safety Blueprint"
        )
        == "Introducing the Child Safety Blueprint"
    )


def test_translate_markdown_uses_ollama_for_plain_lines(monkeypatch):
    monkeypatch.setattr(
        markdown_translator,
        "_translate_text_with_ollama",
        lambda text, content_type="general", ollama_host="http://localhost:11434", ollama_model="gemma3n:e4b": "日本語訳",
    )

    result = markdown_translator.translate_markdown_to_japanese(
        "ChatGPT can analyze files.",
        use_ollama=True,
    )

    assert result == "日本語訳"


def test_build_translation_prompt_preserves_line_breaks():
    prompt = markdown_translator._build_translation_prompt("Line 1\n\n- Bullet")

    assert "Line 1\n\n- Bullet" in prompt


def test_translate_markdown_uses_ollama_for_english_title_even_when_disabled(monkeypatch):
    monkeypatch.setattr(
        markdown_translator,
        "_translate_text_with_ollama",
        lambda text, content_type="general", ollama_host="http://localhost:11434", ollama_model="gemma3n:e4b": "子どもの安全指針の紹介",
    )

    result = markdown_translator.translate_markdown_to_japanese(
        "## Introducing the Child Safety Blueprint",
        use_ollama=False,
    )

    assert result == "## 子どもの安全指針の紹介"
