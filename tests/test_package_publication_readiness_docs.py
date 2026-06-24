from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_package_publication_readiness_doc_exists_and_keeps_decision_gate():
    doc = ROOT / "docs" / "PACKAGE_PUBLICATION_READINESS.md"
    text = doc.read_text(encoding="utf-8")

    assert "PACKAGE_NAME_DECISION" in text
    assert "xau-lfx-external-data-foundation" in text
    assert "TestPyPI" in text
    assert "PyPI" in text
    assert "python -m build" in text
    assert "python scripts/check_release_readiness.py --strict" in text
    assert "xau-lfx validate-artifacts --artifact-dir examples/sample-artifacts" in text


def test_package_publication_doc_preserves_monitor_only_boundary():
    text = (ROOT / "docs" / "PACKAGE_PUBLICATION_READINESS.md").read_text(encoding="utf-8")

    for phrase in [
        "MONITOR_ONLY",
        "NO_EXECUTION",
        "NO_BUY_SELL_SIGNAL",
        "NO_FINANCIAL_ADVICE",
        "NO_STATISTICAL_EDGE_CLAIM",
    ]:
        assert phrase in text

    assert "Upload credentials must remain outside the repository" in text
    assert "Do not add automatic publishing without a separate scope decision" in text
