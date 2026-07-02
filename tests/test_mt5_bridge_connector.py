from xau_lfx.connectors.base import SourceRequest
from xau_lfx.connectors.mt5_bridge import MT5BridgeConnector


class FakeMT5:
    TIMEFRAME_M1 = 1
    TIMEFRAME_M5 = 5
    TIMEFRAME_M15 = 15
    TIMEFRAME_H1 = 60

    def __init__(self):
        self.last_copy_args = None

    def initialize(self):
        return True

    def symbol_select(self, symbol, enabled):
        self.selected = (symbol, enabled)
        return True

    def copy_rates_from_pos(self, symbol, timeframe, start_pos, count):
        self.last_copy_args = (symbol, timeframe, start_pos, count)
        return [
            {
                "time": 1782954000,
                "open": 3300.0,
                "high": 3301.0,
                "low": 3299.0,
                "close": 3300.5,
                "tick_volume": 44,
                "spread": 12,
            }
        ]

    def last_error(self):
        return (0, "OK")


def test_mt5_bridge_connector_fetches_completed_rows_from_terminal_module():
    fake = FakeMT5()
    connector = MT5BridgeConnector(mt5_module=fake, skip_current_bar=True)

    result = connector.fetch(SourceRequest(source_id="TEST", symbol="XAUUSD", timeframe="M5", limit=10))

    assert result["status"] == "OK"
    assert result["source_id"] == "MT5_BRIDGE"
    assert result["source_type"] == "MT5_TERMINAL"
    assert fake.last_copy_args == ("XAUUSD", 5, 1, 10)
    rows = result["payload"]["ohlcv"]["M5"]
    assert len(rows) == 1
    assert rows[0]["close"] == 3300.5
    assert rows[0]["spread"] == 12.0
    assert rows[0]["is_complete"] is True
    assert rows[0]["monitor_only"] is True
    assert "MT5_CURRENT_BAR_SKIPPED" in result["quality_flags"]


def test_mt5_bridge_connector_reports_missing_module():
    connector = MT5BridgeConnector(mt5_module=False)
    result = connector.fetch(SourceRequest(source_id="TEST", symbol="XAUUSD", timeframe="M5", limit=1))

    assert result["status"] == "ERROR"
    assert "MT5_MODULE_NOT_AVAILABLE" in result["errors"]
    assert result["monitor_only"] is True


def test_mt5_bridge_connector_reports_failed_symbol_select():
    class BadSymbolMT5(FakeMT5):
        def symbol_select(self, symbol, enabled):
            return False

    connector = MT5BridgeConnector(mt5_module=BadSymbolMT5())
    result = connector.fetch(SourceRequest(source_id="TEST", symbol="XAUUSD", timeframe="M5", limit=1))

    assert result["status"] == "ERROR"
    assert any("MT5_SYMBOL_SELECT_FAILED" in error for error in result["errors"])
