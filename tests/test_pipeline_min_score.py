from src.pipelines.rss_pipeline import _build_source_min_score_map


def test_build_source_min_score_map_applies_default_to_all_sources():
    rss_configs = [
        {"name": "OpenAI Blog"},
        {"name": "Qiita", "min_score": 3},
    ]

    result = _build_source_min_score_map(rss_configs, default_min_score=2)

    assert result == {"OpenAI Blog": 2, "Qiita": 3}
