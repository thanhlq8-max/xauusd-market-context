from pathlib import Path

from xau_lfx.forbidden_language import assert_clean_language


ROOT = Path(__file__).resolve().parents[1]


def test_lfx_monitor_vocabulary_cites_external_baseline():
    text = (ROOT / "docs" / "LFX_MONITOR_VOCABULARY.md").read_text(encoding="utf-8")

    for required_phrase in [
        "LFX_EXTERNAL_BASELINE.md",
        "Past context",
        "Current context",
        "Conditional-next context",
        "Reset",
        "Barrier",
        "Release-reference",
        "Structural-reference",
        "Density-reference",
    ]:
        assert required_phrase in text

    assert_clean_language(text)


def test_lfx_monitor_vocabulary_preserves_reference_boundaries():
    text = (ROOT / "docs" / "LFX_MONITOR_VOCABULARY.md").read_text(encoding="utf-8")

    for required_phrase in [
        "documentation only",
        "does not copy Pine thresholds",
        "footprint hypothesis",
        "footprint proxy",
        "confluence/reference only",
        "must stay subordinate to source quality",
    ]:
        assert required_phrase in text

    assert_clean_language(text)
