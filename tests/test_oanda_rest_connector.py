from xau_lfx.connectors.base import SourceRequest
from xau_lfx.connectors.oanda_rest import OandaRestConnector


def test_oanda_rest_connector_parses_completed_candles_and_skips_incomplete():
    calls = {}

    def transport(url, headers, timeout):
        calls["url"] = url
        calls["headers"] = headers
        calls["timeout"] = timeout
        return {
            "candles": [
                {
                    "time": "2026-07-02T01:00:00Z",
                    "complete": True,
                    "volume": 12,
                    "mid": {"o": "3300.0", "h": "3301.0", "l": "3299.5", "c": "3300.5"},
                },
                {
                    "time": "2026-07-02T01:01:00Z",
                    "complete": False,
                    "volume": 1,
                    "mid": {"o": "3300.5", "h": "3301.5", "l": "3300.0", "c": "3301.0"},
                },
            ]
        }

    connector = OandaRestConnector(token="token-for-test", transport=transport, timeout=3.0)
    result = connector.fetch(SourceRequest(source_id="TEST", symbol="XAUUSD", timeframe="M1", limit=2))

    assert result["status"] == "OK"
    assert result["source_id"] == "OANDA_REST"
    assert result["source_type"] == "BROKER_REST"
    assert "XAU_USD" in calls["url"]
    assert "granularity=M1" in calls["url"]
    assert calls["headers"]["Accept"] == "application/json"
    rows = result["payload"]["ohlcv"]["M1"]
    assert len(rows) == 1
    assert rows[0]["close"] == 3300.5
    assert rows[0]["is_complete"] is True
    assert rows[0]["monitor_only"] is True
    assert "OANDA_INCOMPLETE_CANDLES_SKIPPED" in result["quality_flags"]


def test_oanda_rest_connector_reports_missing_token():
    connector = OandaRestConnector(token="", transport=lambda *_: {"candles": []})
    result = connector.fetch(SourceRequest(source_id="TEST", symbol="XAUUSD", timeframe="M1", limit=1))

    assert result["status"] == "ERROR"
    assert "OANDA_TOKEN_MISSING" in result["errors"]
    assert result["monitor_only"] is True


def test_oanda_rest_connector_reports_missing_transport():
    connector = OandaRestConnector(token="token-for-test", transport=None)
    result = connector.fetch(SourceRequest(source_id="TEST", symbol="XAUUSD", timeframe="M5", limit=1))

    assert result["status"] == "ERROR"
    assert "OANDA_TRANSPORT_NOT_CONFIGURED" in result["errors"]
