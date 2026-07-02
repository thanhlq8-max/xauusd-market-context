from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE = ROOT / "docs" / "V9_FINAL_GOVERNANCE_LOCK.md"
CHECKLIST = ROOT / "docs" / "V9_FINAL_WORKFLOW_CHECKLIST.md"
PRECONDITIONS = ROOT / "docs" / "V9_ALERT_BRIDGE_PRECONDITIONS.md"


def test_final_governance_lock_contains_completed_gates_and_boundaries():
    text = GOVERNANCE.read_text(encoding="utf-8")

    for gate in ["Gate A", "Gate B", "Gate C", "Gate D", "Gate E", "Gate F", "Gate G", "Gate H", "Gate I", "Gate J", "Gate K"]:
        assert gate in text
    assert "TRADING_MODE: MONITOR_ONLY" in text
    assert "AUTO_ENTRY: NO" in text
    assert "BUY_SELL_SIGNAL: NO" in text
    assert "BROKER_EXECUTION: NO" in text
    assert "No v9.0 component may turn review labels" in text


def test_final_workflow_checklist_contains_required_artifacts_and_commands():
    text = CHECKLIST.read_text(encoding="utf-8")

    for artifact in [
        "event_replay_report.json",
        "case_library_seed.json",
        "case_index.json",
        "evidence_pack.json",
        "updated_case_index.json",
    ]:
        assert artifact in text
    for command in [
        "validate-event-log",
        "replay-event-log",
        "case_library_cli",
        "case_index_cli",
        "evidence_pack_cli",
        "review_patch_cli",
    ]:
        assert command in text


def test_notification_bridge_preconditions_are_proposal_only():
    text = PRECONDITIONS.read_text(encoding="utf-8")

    assert "MODE: PROPOSAL_ONLY" in text
    assert "The bridge is not implemented in v9.0-L." in text
    assert "validated event log" in text
    assert "separate scoped task" in text
    assert "execution instructions" in text
