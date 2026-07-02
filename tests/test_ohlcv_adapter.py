import pytest

from xau_lfx.connectors.ohlcv_adapter import OhlcvAdapterError, build_ohlcv_connector_payload, normalize_candle


def test_normalize_candle_outputs_monitor_only_contract():
    candle = normalize_candle(
        source_id="TEST",
        source_type="BROKER_REST",
        symbol="XAUUSD",
        timeframe="M1",
        ts_utc="2026-07-02T01:00:00Z",
        open_price="3300.0",
        high_price="3301.0",
        low_price="3299.0",
        close_price="3300.5",
        tick_volume="42",
        spread="0.1",
        is_complete=True,
        source_latency_ms="12.5",
    )

    assert candle["source_id"] == "TEST"
    assert candle["source_type"] == "BROKER_REST"
    assert candle["timeframe"] == "M1"
    assert candle["ts_utc"] == "2026-07-02T01:00:00+00:00"
    assert candle["tick_volume"] == 42.0
    assert candle["is_complete"] is True
    assert candle["monitor_only"] is True


def test_normalize_candle_rejects_bad_price_shape():
    with pytest.raises(OhlcvAdapterError, match="high is below open/close"):
        normalize_candle(
            source_id="TEST",
            source_type="BROKER_REST",
            symbol="XAUUSD",
            timeframe="M1",
            ts_utc="2026-07-02T01:00:00Z",
            open_price=3300.0,
            high_price=3299.0,
            low_price=3298.0,
            close_price=3300.5,
        )


def test_build_ohlcv_connector_payload_statuses():
    warn_payload = build_ohlcv_connector_payload(
        source_id="TEST",
        source_type="BROKER_REST",
        symbol="XAUUSD",
        timeframe="M1",
        rows=[],
    )
    assert warn_payload["status"] == "WARN"
    assert "NO_COMPLETED_CANDLES" in warn_payload["quality_flags"]

    error_payload = build_ohlcv_connector_payload(
        source_id="TEST",
        source_type="BROKER_REST",
        symbol="XAUUSD",
        timeframe="M1",
        rows=[],
        errors=["SOURCE_MISSING"],
    )
    assert error_payload["status"] == "ERROR"
    assert error_payload["monitor_only"] is True
