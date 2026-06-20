from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from xau_lfx.utils import utc_now_iso

OANDA_PRACTICE_REST_URL = "https://api-fxpractice.oanda.com"
OANDA_INSTRUMENT = "XAU_USD"
OANDA_PRICE_COMPONENTS = "MBA"
OANDA_TIMEFRAMES = ("M5", "M15", "H1")
OANDA_CANDLE_COUNT = 300


class OandaError(RuntimeError):
    pass


class OandaTransportError(OandaError):
    pass


class OandaResponseError(OandaError):
    pass


@dataclass(frozen=True)
class OandaPracticeConfig:
    token: str = field(repr=False)
    timeout_seconds: float

    def __post_init__(self) -> None:
        if not self.token.strip():
            raise ValueError("OANDA_API_TOKEN is empty")
        if not math.isfinite(self.timeout_seconds) or self.timeout_seconds <= 0:
            raise ValueError("request timeout must be a positive finite number")


class JsonTransport(Protocol):
    def get_json(self, url: str, headers: dict[str, str], timeout_seconds: float) -> dict[str, Any]:
        ...


class UrllibJsonTransport:
    def get_json(self, url: str, headers: dict[str, str], timeout_seconds: float) -> dict[str, Any]:
        request = Request(url=url, headers=headers, method="GET")
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                raw = response.read()
        except HTTPError as exc:
            raw = exc.read()
            code, message = _parse_error_payload(raw)
            detail = f"{code}: {message}" if code and message else f"HTTP {exc.code}"
            raise OandaTransportError(f"OANDA Practice rejected the request ({detail})") from exc
        except URLError as exc:
            raise OandaTransportError(f"OANDA Practice request failed ({exc.reason})") from exc

        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise OandaResponseError("OANDA Practice returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise OandaResponseError("OANDA Practice response root must be an object")
        return payload


def _parse_error_payload(raw: bytes) -> tuple[str | None, str | None]:
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, None
    if not isinstance(payload, dict):
        return None, None
    code = payload.get("errorCode")
    message = payload.get("errorMessage")
    return str(code) if code is not None else None, str(message) if message is not None else None


def _redact_secret(message: str, secret: str) -> str:
    return message.replace(secret, "[REDACTED]") if secret else message


def _parse_timestamp(value: Any) -> str:
    if not isinstance(value, str):
        raise OandaResponseError("candle time must be a string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise OandaResponseError(f"candle time is not RFC3339: {value}") from exc
    if parsed.tzinfo is None:
        raise OandaResponseError(f"candle time has no timezone: {value}")
    return parsed.astimezone(timezone.utc).isoformat()


def _parse_number(value: Any, field_name: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise OandaResponseError(f"{field_name} is not numeric") from exc
    if not math.isfinite(parsed):
        raise OandaResponseError(f"{field_name} is not finite")
    return parsed


def _parse_price_component(value: Any, component: str) -> dict[str, float]:
    if not isinstance(value, dict):
        raise OandaResponseError(f"candle {component} component is missing")
    try:
        parsed = {
            "open": _parse_number(value["o"], f"{component}.open"),
            "high": _parse_number(value["h"], f"{component}.high"),
            "low": _parse_number(value["l"], f"{component}.low"),
            "close": _parse_number(value["c"], f"{component}.close"),
        }
    except KeyError as exc:
        raise OandaResponseError(f"candle {component} is missing field {exc.args[0]}") from exc
    if parsed["high"] < max(parsed["open"], parsed["close"]):
        raise OandaResponseError(f"candle {component} high is below open/close")
    if parsed["low"] > min(parsed["open"], parsed["close"]):
        raise OandaResponseError(f"candle {component} low is above open/close")
    return parsed


def _parse_candle(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OandaResponseError("candle must be an object")
    try:
        volume = value["volume"]
        complete = value["complete"]
        candle = {
            "ts_utc": _parse_timestamp(value["time"]),
            "complete": complete,
            "price_count": volume,
            "mid": _parse_price_component(value["mid"], "mid"),
            "bid": _parse_price_component(value["bid"], "bid"),
            "ask": _parse_price_component(value["ask"], "ask"),
        }
    except KeyError as exc:
        raise OandaResponseError(f"candle is missing field {exc.args[0]}") from exc
    if not isinstance(complete, bool):
        raise OandaResponseError("candle complete must be boolean")
    if isinstance(volume, bool) or not isinstance(volume, int) or volume < 0:
        raise OandaResponseError("candle volume must be a non-negative integer")
    if candle["ask"]["close"] < candle["bid"]["close"]:
        raise OandaResponseError("candle ask close is below bid close")
    return candle


def parse_candles_response(payload: dict[str, Any], timeframe: str) -> list[dict[str, Any]]:
    try:
        instrument = payload["instrument"]
        granularity = payload["granularity"]
        raw_candles = payload["candles"]
    except KeyError as exc:
        raise OandaResponseError(f"candles response is missing field {exc.args[0]}") from exc
    if instrument != OANDA_INSTRUMENT:
        raise OandaResponseError(f"unexpected instrument: {instrument}")
    if granularity != timeframe:
        raise OandaResponseError(f"unexpected granularity: {granularity}")
    if not isinstance(raw_candles, list) or not raw_candles:
        raise OandaResponseError(f"OANDA returned no {timeframe} candles")

    candles = [_parse_candle(value) for value in raw_candles]
    timestamps = [candle["ts_utc"] for candle in candles]
    if timestamps != sorted(timestamps) or len(timestamps) != len(set(timestamps)):
        raise OandaResponseError(f"OANDA {timeframe} candles are not strictly increasing")
    return candles


class OandaPracticeConnector:
    source_id = "OANDA_V20_PRACTICE"

    def __init__(self, config: OandaPracticeConfig, transport: JsonTransport) -> None:
        self._config = config
        self._transport = transport

    def fetch_snapshot(self) -> dict[str, Any]:
        try:
            timeframes: dict[str, dict[str, Any]] = {}
            headers = {
                "Authorization": f"Bearer {self._config.token}",
                "Accept": "application/json",
                "Accept-Datetime-Format": "RFC3339",
                "User-Agent": "xauusd-market-context/2.4.0",
            }
            for timeframe in OANDA_TIMEFRAMES:
                query = urlencode(
                    {
                        "price": OANDA_PRICE_COMPONENTS,
                        "granularity": timeframe,
                        "count": OANDA_CANDLE_COUNT,
                        "smooth": "false",
                    }
                )
                url = f"{OANDA_PRACTICE_REST_URL}/v3/instruments/{OANDA_INSTRUMENT}/candles?{query}"
                payload = self._transport.get_json(url, headers, self._config.timeout_seconds)
                candles = parse_candles_response(payload, timeframe)
                timeframes[timeframe] = {
                    "granularity": timeframe,
                    "candles": candles,
                }
        except OandaError as exc:
            raise OandaError(_redact_secret(str(exc), self._config.token)) from exc

        return {
            "schema_version": "oanda-live.v1",
            "ts_utc": utc_now_iso(),
            "source": {
                "source_id": self.source_id,
                "provider": "OANDA",
                "environment": "practice",
                "instrument": OANDA_INSTRUMENT,
                "price_components": ["mid", "bid", "ask"],
                "candle_count_requested": OANDA_CANDLE_COUNT,
                "volume_policy": "price_count is the number of OANDA prices in the candle, not centralized traded volume",
            },
            "timeframes": timeframes,
        }
