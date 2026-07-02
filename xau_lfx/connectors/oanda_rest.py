from __future__ import annotations

import time
from typing import Any, Callable
from urllib.parse import urlencode

from xau_lfx.connectors.base import SourceRequest
from xau_lfx.connectors.ohlcv_adapter import OhlcvAdapterError, build_ohlcv_connector_payload, normalize_candle

Transport = Callable[[str, dict[str, str], float], dict[str, Any]]

TIMEFRAME_TO_OANDA = {"M1": "M1", "M5": "M5", "M15": "M15", "H1": "H1"}
DEFAULT_INSTRUMENT_MAP = {"XAUUSD": "XAU_USD", "XAU_USD": "XAU_USD"}


class OandaRestConnector:
    source_id = "OANDA_REST"
    source_type = "BROKER_REST"

    def __init__(
        self,
        token: str | None = None,
        api_url: str = "https://api-fxpractice.oanda.com/v3",
        price_component: str = "M",
        transport: Transport | None = None,
        instrument_map: dict[str, str] | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.token = token
        self.api_url = api_url.rstrip("/")
        self.price_component = price_component
        self.transport = transport
        self.instrument_map = instrument_map or DEFAULT_INSTRUMENT_MAP
        self.timeout = timeout

    def _instrument(self, symbol: str) -> str:
        return self.instrument_map.get(symbol.upper(), symbol.upper())

    def _headers(self) -> dict[str, str]:
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}

    def _url(self, request: SourceRequest) -> str:
        timeframe = request.timeframe.upper()
        if timeframe not in TIMEFRAME_TO_OANDA:
            raise OhlcvAdapterError(f"unsupported timeframe: {request.timeframe}")
        query = urlencode(
            {
                "price": self.price_component,
                "granularity": TIMEFRAME_TO_OANDA[timeframe],
                "count": max(1, int(request.limit)),
            }
        )
        return f"{self.api_url}/instruments/{self._instrument(request.symbol)}/candles?{query}"

    def _price_block(self, candle: dict[str, Any]) -> dict[str, Any]:
        if "mid" in candle:
            return candle["mid"]
        if "bid" in candle:
            return candle["bid"]
        if "ask" in candle:
            return candle["ask"]
        raise OhlcvAdapterError("OANDA candle has no mid/bid/ask price block")

    def _spread(self, candle: dict[str, Any]) -> float | None:
        bid = candle.get("bid")
        ask = candle.get("ask")
        if not isinstance(bid, dict) or not isinstance(ask, dict):
            return None
        try:
            return abs(float(ask["c"]) - float(bid["c"]))
        except (KeyError, TypeError, ValueError):
            return None

    def _rows(self, payload: dict[str, Any], request: SourceRequest, latency_ms: float) -> tuple[list[dict[str, Any]], list[str]]:
        rows: list[dict[str, Any]] = []
        quality_flags: list[str] = []
        for candle in payload.get("candles", []):
            if not candle.get("complete", False):
                quality_flags.append("OANDA_INCOMPLETE_CANDLES_SKIPPED")
                continue
            prices = self._price_block(candle)
            rows.append(
                normalize_candle(
                    source_id=self.source_id,
                    source_type=self.source_type,
                    symbol=request.symbol,
                    timeframe=request.timeframe,
                    ts_utc=candle["time"],
                    open_price=prices["o"],
                    high_price=prices["h"],
                    low_price=prices["l"],
                    close_price=prices["c"],
                    tick_volume=candle.get("volume", 0),
                    spread=self._spread(candle),
                    is_complete=True,
                    source_latency_ms=latency_ms,
                )
            )
        return rows, quality_flags

    def fetch(self, request: SourceRequest) -> dict[str, Any]:
        if not self.token:
            return build_ohlcv_connector_payload(
                source_id=self.source_id,
                source_type=self.source_type,
                symbol=request.symbol,
                timeframe=request.timeframe,
                rows=[],
                errors=["OANDA_TOKEN_MISSING"],
                quality_flags=["OANDA_NOT_CONFIGURED"],
            )
        if self.transport is None:
            return build_ohlcv_connector_payload(
                source_id=self.source_id,
                source_type=self.source_type,
                symbol=request.symbol,
                timeframe=request.timeframe,
                rows=[],
                errors=["OANDA_TRANSPORT_NOT_CONFIGURED"],
                quality_flags=["OANDA_TRANSPORT_MISSING"],
            )
        try:
            started = time.perf_counter()
            payload = self.transport(self._url(request), self._headers(), self.timeout)
            latency_ms = round((time.perf_counter() - started) * 1000, 3)
            rows, flags = self._rows(payload, request, latency_ms)
            return build_ohlcv_connector_payload(
                source_id=self.source_id,
                source_type=self.source_type,
                symbol=request.symbol,
                timeframe=request.timeframe,
                rows=rows,
                quality_flags=flags,
            )
        except Exception as exc:  # noqa: BLE001 - connector must return payload errors, not raise into pipeline
            return build_ohlcv_connector_payload(
                source_id=self.source_id,
                source_type=self.source_type,
                symbol=request.symbol,
                timeframe=request.timeframe,
                rows=[],
                errors=[f"OANDA_FETCH_FAILED: {exc}"],
                quality_flags=["OANDA_FETCH_FAILED"],
            )
