from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "docs" / "V91_NOTIFICATION_BRIDGE_PROPOSAL.md"
DATA_SOURCE = ROOT / "docs" / "V91_OHLCV_DATA_SOURCE_DECISION.md"
ADAPTER_CONTRACT = ROOT / "docs" / "V91_DATA_INPUT_ADAPTER_CONTRACT.md"


def test_notification_bridge_proposal_is_proposal_only_and_monitor_only():
    text = PROPOSAL.read_text(encoding="utf-8")

    assert "STATUS: PROPOSAL_ONLY" in text
    assert "IMPLEMENTATION: NO" in text
    assert "TRADING_MODE: MONITOR_ONLY" in text
    assert "TRACK_RECLAIM" in text
    assert "D_FAILED" in text
    assert "TARGET_HIT" in text
    assert "No code implementation." in text
    assert "No broker API action." in text


def test_ohlcv_data_source_decision_preserves_source_boundaries():
    text = DATA_SOURCE.read_text(encoding="utf-8")

    assert "Primary: broker REST API source" in text
    assert "OANDA REST" in text
    assert "MT5 Python bridge" in text
    assert "vendor API" in text
    assert "tick count / quote activity" in text
    assert "must not be described as centralized traded volume" in text
    assert "v9.1-B — OHLCV Adapter Implementation" in text


def test_data_input_adapter_contract_rejects_execution_fields():
    text = ADAPTER_CONTRACT.read_text(encoding="utf-8")

    for field in ["source_id", "source_type", "symbol", "timeframe", "is_complete", "monitor_only"]:
        assert field in text
    for forbidden in ["BUY", "SELL", "stop_loss", "take_profit", "lot_size", "order_id"]:
        assert forbidden in text
    assert "Only completed candles" in text
