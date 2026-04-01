import logging
from datetime import datetime, timedelta
from pathlib import Path

LOGGER = logging.getLogger(__name__)

_OUTPUT_ROOT = Path("output").resolve()


def resolve_safe_output_dir(user_value: str, output_root: Path | None = None) -> Path:
    """出力ディレクトリパスを output/ 配下に限定して解決する。
    パストラバーサル（../ や絶対パスによる脱出）を防ぐ。

    Args:
        user_value: config.json から受け取ったディレクトリ指定文字列。
        output_root: テスト用オーバーライド。None のとき _OUTPUT_ROOT を使用。
    """
    root = output_root.resolve() if output_root is not None else _OUTPUT_ROOT
    candidate_path = Path(user_value)

    if candidate_path.is_absolute():
        resolved = candidate_path.resolve()
    else:
        resolved = (root / user_value).resolve()

    if root != resolved and root not in resolved.parents:
        raise ValueError(
            f"Output path must stay under {root}, got: {resolved}"
        )
    return resolved


def get_unique_path(path: Path) -> Path:
    """ファイルが存在しなければそのまま返す。存在する場合は _2, _3, ... を付けて一意なパスを返す。"""
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 2
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def purge_old_files(dir_path: str, days_old: int) -> list[str]:
    """dir_path 直下の .md ファイルのうち days_old 日以上前のものを削除する。
    削除したファイルのパス文字列リストを返す。
    """
    directory = resolve_safe_output_dir(dir_path)
    if not directory.exists():
        return []

    cutoff = datetime.now() - timedelta(days=days_old)
    deleted: list[str] = []

    for file in sorted(directory.glob("*.md")):
        if not file.is_file():
            continue
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        if mtime < cutoff:
            try:
                file.unlink()
                deleted.append(str(file))
                LOGGER.info("Purged old file: %s", file)
            except OSError as exc:
                LOGGER.warning("Failed to purge file %s: %s", file, exc)

    return deleted
