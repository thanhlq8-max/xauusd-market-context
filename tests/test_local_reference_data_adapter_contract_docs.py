from pathlib import Path

from xau_lfx.forbidden_language import assert_clean_language


ROOT = Path(__file__).resolve().parents[1]


def test_local_reference_data_adapter_contract_documents_required_boundaries():
    text = (ROOT / "docs" / "LOCAL_REFERENCE_DATA_ADAPTER_CONTRACT.md").read_text(encoding="utf-8")

    for required_phrase in [
        "documentation only",
        "user-owned, synthetic, or rights-cleared",
        "explicit local path",
        "normalized to UTC",
        "freshness age or a freshness limitation",
        "Missing values must not be silently filled",
        "must not upgrade weak core evidence",
        "no change to base-run behavior when optional data is absent",
    ]:
        assert required_phrase in text

    assert_clean_language(text)


def test_local_reference_data_adapter_contract_cites_baseline_and_policy():
    text = (ROOT / "docs" / "LOCAL_REFERENCE_DATA_ADAPTER_CONTRACT.md").read_text(encoding="utf-8")

    assert "LFX_EXTERNAL_BASELINE.md" in text
    assert "artifact compatibility policy" in text
    assert_clean_language(text)
