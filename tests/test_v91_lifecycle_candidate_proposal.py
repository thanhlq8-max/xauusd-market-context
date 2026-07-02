from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "docs" / "V91_ROLLING_DATASET_LIFECYCLE_CANDIDATE_PROPOSAL.md"
GOVERNANCE = ROOT / "docs" / "V91_LIFECYCLE_CANDIDATE_GOVERNANCE.md"


def test_lifecycle_candidate_proposal_is_proposal_only():
    text = PROPOSAL.read_text(encoding="utf-8")

    assert "STATUS: PROPOSAL_ONLY" in text
    assert "IMPLEMENTATION: NO" in text
    assert "TRADING_MODE: MONITOR_ONLY" in text
    assert "CANDIDATE_RECLAIM" in text
    assert "CANDIDATE_ACCEPT" in text
    assert "NEEDS_MANUAL_REVIEW" in text
    assert "v9.1-I — Lifecycle Candidate Artifact Implementation" in text


def test_lifecycle_candidate_proposal_forbids_runtime_and_execution_promotion():
    text = PROPOSAL.read_text(encoding="utf-8")

    for forbidden in [
        "overwrite rolling_event_dataset.csv lifecycle fields automatically",
        "emit direct entry labels",
        "emit BUY or SELL commands",
        "create route or delivery conclusions",
        "create notification bridge messages",
        "call broker or terminal execution APIs",
        "claim statistical edge",
    ]:
        assert forbidden in text


def test_lifecycle_candidate_governance_keeps_candidates_separate():
    text = GOVERNANCE.read_text(encoding="utf-8")

    assert "STATUS: GOVERNANCE_PROPOSAL" in text
    assert "IMPLEMENTATION: NO" in text
    assert "lifecycle_candidates.json" in text
    assert "must not mutate" in text
    assert "rolling_event_dataset.csv" in text
    assert "explicit review/patch workflow" in text
