import pytest
from pathlib import Path
from src.utils.file_manager import resolve_safe_output_dir


def test_valid_relative_subpath(tmp_path):
    result = resolve_safe_output_dir("exploration", output_root=tmp_path)
    assert result == (tmp_path / "exploration").resolve()


def test_valid_absolute_within_root(tmp_path):
    target = tmp_path / "monitoring"
    result = resolve_safe_output_dir(str(target), output_root=tmp_path)
    assert result == target.resolve()


def test_rejects_path_traversal(tmp_path):
    with pytest.raises(ValueError, match="(?i)output"):
        resolve_safe_output_dir("../../etc", output_root=tmp_path)


def test_rejects_absolute_path_outside_root(tmp_path):
    with pytest.raises(ValueError, match="(?i)output"):
        resolve_safe_output_dir("/tmp/evil", output_root=tmp_path)


def test_rejects_double_dot_in_middle(tmp_path):
    with pytest.raises(ValueError, match="(?i)output"):
        resolve_safe_output_dir("exploration/../../../etc", output_root=tmp_path)
