from pathlib import Path

from xau_lfx.artifact_contract import ARTIFACT_SCHEMA_FILES
from xau_lfx.forbidden_language import assert_clean_language


ROOT = Path(__file__).resolve().parents[1]


def test_artifact_json_schema_docs_reference_all_schema_files():
    text = (ROOT / "docs" / "ARTIFACT_JSON_SCHEMAS.md").read_text(encoding="utf-8")

    for schema_file in ARTIFACT_SCHEMA_FILES.values():
        assert schema_file in text
    assert "xau-lfx validate-artifacts --artifact-dir artifacts" in text
    assert "docs/ARTIFACT_SCHEMA_COMPATIBILITY.md" in text
    assert_clean_language(text)


def test_manifest_includes_artifact_json_schemas():
    manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")

    assert "recursive-include schemas *.json" in manifest
