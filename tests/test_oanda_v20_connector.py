from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import pytest

from xau_lfx.connectors.oanda_v20 import (
    OANDA_PRACTICE_REST_URL,
    OandaError,
    OandaPracticeConfig,
    OandaPracticeConnector,
    OandaResponseError,
    OandaTransportError,
    parse_candles_response,
)


def _component(base: float) -> dict[str, str]:
    return {
        "o": f"{base:.3f}",
        "h": f"{base + 2:.3f}",
        "l": f"{base - 1:.3f}",
        "c": f"{base + 1:.3f}",
    }


def candle_payload(granularity: str) -> dict:
    times = {
        "M5": ["2026-06-19T12:30:00Z", "2026-06-19T12:35:00Z", "2026-06-19T12:40:00Z"],
        "M15": ["2026-06-19T06:45:00Z", "2026-06-19T07:00:00Z", "2026-06-19T07:15:00Z"],
        "H1": ["2026-06-19T05:00:00Z", "2026-06-19T06:00:00Z", "2026-06-19T07:00:00Z"],
    }[granularity]
    candles = []
    for index, ts_utc in enumerate(times):
        base = 3000.0 + index
        candles.append(
            {
                "time": ts_utc,
                "volume": 10 + index,
                "complete": index < 2,
                "mid": _component(base),
                "bid": _component(base - 0.1),
                "ask": _component(base + 0.1),
            }
        )
    return {"instrument": "XAU_USD", "granularity": granularity, "candles": candles}


class FakeTransport:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, str], float]] = []

    def get_json(self, url: str, headers: dict[str, str], timeout_seconds: float) -> dict:
        self.calls.append((url, headers, timeout_seconds))
        granularity = parse_qs(urlparse(url).query)["granularity"][0]
        return candle_payload(granularity)


def test_oanda_practice_connector_fetches_locked_candle_contract():
    secret = "local-secret-value"
    transport = FakeTransport()
    config = OandaPracticeConfig(token=secret, timeout_seconds=9.0)
    connector = OandaPracticeConnector(config=config, transport=transport)

    snapshot = connector.fetch_snapshot()

    assert list(snapshot["timeframes"]) == ["M5", "M15", "H1"]
    assert snapshot["source"]["environment"] == "practice"
    assert snapshot["source"]["instrument"] == "XAU_USD"
    assert snapshot["source"]["price_components"] == ["mid", "bid", "ask"]
    assert len(transport.calls) == 3
    for url, headers, timeout in transport.calls:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        assert url.startswith(OANDA_PRACTICE_REST_URL)
        assert query["price"] == ["MBA"]
        assert query["count"] == ["300"]
        assert query["smooth"] == ["false"]
        assert headers["Authorization"] == f"Bearer {secret}"
        assert timeout == 9.0
    assert secret not in repr(config)
    assert secret not in str(snapshot)


def test_parse_candles_response_rejects_missing_price_component():
    payload = candle_payload("M5")
    del payload["candles"][0]["ask"]

    with pytest.raises(OandaResponseError, match="ask"):
        parse_candles_response(payload, "M5")


def test_parse_candles_response_rejects_non_increasing_timestamps():
    payload = candle_payload("M15")
    payload["candles"][1]["time"] = payload["candles"][0]["time"]

    with pytest.raises(OandaResponseError, match="strictly increasing"):
        parse_candles_response(payload, "M15")


def test_connector_redacts_token_if_transport_error_reflects_it():
    secret = "local-secret-value"

    class ReflectingTransport:
        def get_json(self, _url: str, _headers: dict[str, str], _timeout_seconds: float) -> dict:
            raise OandaTransportError(f"upstream reflected {secret}")

    connector = OandaPracticeConnector(
        config=OandaPracticeConfig(token=secret, timeout_seconds=9.0),
        transport=ReflectingTransport(),
    )

    with pytest.raises(OandaError) as exc_info:
        connector.fetch_snapshot()
    assert secret not in str(exc_info.value)
    assert "[REDACTED]" in str(exc_info.value)


@pytest.mark.parametrize("timeout", [0.0, -1.0, float("nan")])
def test_oanda_config_rejects_invalid_timeout(timeout: float):
    with pytest.raises(ValueError, match="timeout"):
        OandaPracticeConfig(token="local", timeout_seconds=timeout)
