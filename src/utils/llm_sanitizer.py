import re

_CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_llm_input(text: object, limit: int = 500) -> str:
    """LLMプロンプトに埋め込む外部入力をサニタイズする。

    - str以外は空文字列を返す
    - 制御文字を除去
    - ``` と --- をエスケープ（プロンプトインジェクション対策）
    - 連続空白を正規化
    - limit 文字で切り捨て
    """
    if not isinstance(text, str):
        return ""
    result = _CONTROL_CHAR_PATTERN.sub("", text)
    result = result.replace("```", "` ` `").replace("---", "\u2014")
    result = " ".join(result.split())
    return result[:limit]
