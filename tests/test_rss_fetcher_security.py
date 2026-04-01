import pytest
from src.fetchers.rss_fetcher import validate_rss_url


def test_valid_https_url():
    validate_rss_url("https://huggingface.co/blog/feed.xml")  # 例外が出なければOK


def test_valid_http_url():
    validate_rss_url("http://example.com/feed.xml")


def test_rejects_file_scheme():
    with pytest.raises(ValueError, match="http/https"):
        validate_rss_url("file:///etc/passwd")


def test_rejects_ftp_scheme():
    with pytest.raises(ValueError, match="http/https"):
        validate_rss_url("ftp://example.com/feed.xml")


def test_rejects_localhost():
    with pytest.raises(ValueError, match="localhost"):
        validate_rss_url("http://localhost/feed")


def test_rejects_127_0_0_1():
    with pytest.raises(ValueError, match="private"):
        validate_rss_url("http://127.0.0.1/feed")


def test_rejects_private_ip_192_168():
    with pytest.raises(ValueError, match="private"):
        validate_rss_url("http://192.168.1.1/feed")


def test_rejects_private_ip_10():
    with pytest.raises(ValueError, match="private"):
        validate_rss_url("http://10.0.0.1/feed")


def test_rejects_empty_url():
    with pytest.raises(ValueError):
        validate_rss_url("")


def test_rejects_no_host():
    with pytest.raises(ValueError, match="host"):
        validate_rss_url("http:///feed")
