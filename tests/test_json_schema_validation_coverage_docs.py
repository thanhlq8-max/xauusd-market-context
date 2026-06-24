from pathlib import Path

from xau_lfx.artifact_contract import ARTIFACT_REQUIRED_KEYS
from xau_lfx.config import artifact_paths
from xau_lfx.forbidden_language import assert_clean_language


ROOT = Path(__file__).resolve().parents[1]


def test_json_schema_validation_coverage_lists_current_json_artifacts():
    text = (ROOT / "docs" / "JSON_SCHEMA_VALIDATION_COVERAGE.md").read_text(encoding="utf-8")
    paths = artifact_paths(ROOT / "artifacts")

    for artifact_key in ARTIFACT_REQUIRED_KEYS:
        assert paths[artifact_key].name in text

    assert "ARTIFACT_CONTRACT.md" in text
    assert "ARTIFACT_SCHEMA_COMPATIBILITY.md" in text
    assert_clean_language(text)


def test_json_schema_validation_coverage_is_proposal_only():
    text = (ROOT / "docs" / "JSON_SCHEMA_VALIDATION_COVERAGE.md").read_text(encoding="utf-8")

    for required_phrase in [
        "documentation only",
        "does not add schema files",
        "Current artifact inventory",
        "Recommended implementation sequence",
    ]:
        assert required_phrase in text

    assert_clean_language(text)
