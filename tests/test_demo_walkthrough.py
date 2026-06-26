from pathlib import Path

from xau_lfx.forbidden_language import assert_clean_language


def test_demo_walkthrough_documents_required_artifacts():
    text = Path("docs/DEMO_WALKTHROUGH.md").read_text(encoding="utf-8")
    assert "xau_context_summary.json" in text
    assert "xau_market_context_report.md" in text
    assert "site/index.html" in text
    assert "monitor-only" in text.lower()
    assert_clean_language(text)


def test_sample_artifacts_readme_explains_demo_outputs():
    text = Path("examples/sample-artifacts/README.md").read_text(encoding="utf-8")
    assert "synthetic fixture data" in text
    assert "xau_artifact_quality.json" in text
    assert "xau_context_summary.json" in text
    assert "xau_market_context_report.md" in text
    assert "Practical Zone Deck" in text
    assert "practical_zone_deck" in text
    assert "ranks supplied session high/low references by distance from `latest_close`" in text
    assert_clean_language(text)


def test_github_pages_demo_documents_practical_zone_deck():
    text = Path("docs/GITHUB_PAGES_DEMO.md").read_text(encoding="utf-8")
    assert "site/index.html" in text
    assert "Practical Zone Deck" in text
    assert "ranked by distance from the latest composite close" in text
    assert "actual dealer inventory claims" in text
    assert "actual retail-side positioning claims" in text
    assert_clean_language(text)
