import logging
from datetime import datetime, timedelta
from pathlib import Path

LOGGER = logging.getLogger(__name__)


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
    directory = Path(dir_path)
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
