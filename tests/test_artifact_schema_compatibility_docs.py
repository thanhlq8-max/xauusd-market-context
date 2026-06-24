from pathlib import Path

from xau_lfx.forbidden_language import assert_clean_language


ROOT = Path(__file__).resolve().parents[1]


def test_artifact_schema_compatibility_policy_documents_change_types():
    text = (ROOT / "docs" / "ARTIFACT_SCHEMA_COMPATIBILITY.md").read_text(encoding="utf-8")

    for required_phrase in [
        "compatible",
        "breaking",
        "v2.1.0 schema implementation milestone is treated as skipped and not delivered",
        "does not change artifact fields",
        "new artifact contract version plus a changelog note",
    ]:
        assert required_phrase in text

    assert_clean_language(text)


def test_artifact_contract_links_compatibility_policy():
    text = (ROOT / "docs" / "ARTIFACT_CONTRACT.md").read_text(encoding="utf-8")

    assert "ARTIFACT_SCHEMA_COMPATIBILITY.md" in text
    assert "compatible additions" in text
    assert "breaking changes" in text
    assert_clean_language(text)
