from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from xau_lfx.connectors.base import SourceRequest
from xau_lfx.connectors.ohlcv_adapter import build_ohlcv_connector_payload, normalize_candle

TIMEFRAME_ATTRS = {"M1": "TIMEFRAME_M1", "M5": "TIMEFRAME_M5", "M15": "TIMEFRAME_M15", "H1": "TIMEFRAME_H1"}
DEFAULT_SYMBOL_MAP = {"XAUUSD": "XAUUSD", "XAU_USD": "XAUUSD"}


class MT5BridgeConnector:
    source_id = "MT5_BRIDGE"
    source_type = "MT5_TERMINAL"

    def __init__(
        self,
        mt5_module: Any | None = None,
        symbol_map: dict[str, str] | None = None,
        skip_current_bar: bool = True,
    ) -> None:
        if mt5_module is None:
            try:
                import MetaTrader5 as mt5_module  # type: ignore[no-redef]
            except ImportError:
                mt5_module = None
        self.mt5 = mt5_module
        self.symbol_map = symbol_map or DEFAULT_SYMBOL_MAP
        self.skip_current_bar = skip_current_bar

    def _symbol(self, symbol: str) -> str:
        return self.symbol_map.get(symbol.upper(), symbol)

    def _timeframe(self, timeframe: str) -> Any:
        attr = TIMEFRAME_ATTRS.get(timeframe.upper())
        if attr is None:
            raise ValueError(f"unsupported timeframe: {timeframe}")
        if self.mt5 is None or not hasattr(self.mt5, attr):
            raise ValueError(f"MT5 timeframe missing: {attr}")
        return getattr(self.mt5, attr)

    def _last_error(self) -> str:
        if self.mt5 is None or not hasattr(self.mt5, "last_error"):
            return "UNKNOWN"
        return str(self.mt5.last_error())

    def _field(self, row: Any, name: str, default: Any = None) -> Any:
        try:
            return row[name]
        except (KeyError, TypeError, ValueError, IndexError):
            return getattr(row, name, default)

    def _rows(self, rates: Any, request: SourceRequest) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for rate in list(rates or []):
            ts = datetime.fromtimestamp(float(self._field(rate, "time")), tz=timezone.utc)
            rows.append(
                normalize_candle(
                    source_id=self.source_id,
                    source_type=self.source_type,
                    symbol=request.symbol,
                    timeframe=request.timeframe,
                    ts_utc=ts,
                    open_price=self._field(rate, "open"),
                    high_price=self._field(rate, "high"),
                    low_price=self._field(rate, "low"),
                    close_price=self._field(rate, "close"),
                    tick_volume=self._field(rate, "tick_volume", 0),
                    spread=self._field(rate, "spread", None),
                    is_complete=True,
                    source_latency_ms=None,
                )
            )
        return rows

    def fetch(self, request: SourceRequest) -> dict[str, Any]:
        if self.mt5 is None:
            return build_ohlcv_connector_payload(
                source_id=self.source_id,
                source_type=self.source_type,
                symbol=request.symbol,
                timeframe=request.timeframe,
                rows=[],
                errors=["MT5_MODULE_NOT_AVAILABLE"],
                quality_flags=["MT5_MODULE_NOT_AVAILABLE"],
            )
        try:
            if hasattr(self.mt5, "initialize") and not self.mt5.initialize():
                raise RuntimeError(f"MT5_INITIALIZE_FAILED: {self._last_error()}")
            symbol = self._symbol(request.symbol)
            if hasattr(self.mt5, "symbol_select") and not self.mt5.symbol_select(symbol, True):
                raise RuntimeError(f"MT5_SYMBOL_SELECT_FAILED: {symbol}")
            timeframe = self._timeframe(request.timeframe)
            start_pos = 1 if self.skip_current_bar else 0
            rates = self.mt5.copy_rates_from_pos(symbol, timeframe, start_pos, max(1, int(request.limit)))
            if rates is None:
                raise RuntimeError(f"MT5_COPY_RATES_FAILED: {self._last_error()}")
            rows = self._rows(rates, request)
            return build_ohlcv_connector_payload(
                source_id=self.source_id,
                source_type=self.source_type,
                symbol=request.symbol,
                timeframe=request.timeframe,
                rows=rows,
                quality_flags=["MT5_CURRENT_BAR_SKIPPED"] if self.skip_current_bar else [],
            )
        except Exception as exc:  # noqa: BLE001 - connector must return payload errors, not raise into pipeline
            return build_ohlcv_connector_payload(
                source_id=self.source_id,
                source_type=self.source_type,
                symbol=request.symbol,
                timeframe=request.timeframe,
                rows=[],
                errors=[f"MT5_BRIDGE_FETCH_FAILED: {exc}"],
                quality_flags=["MT5_BRIDGE_FETCH_FAILED"],
            )
