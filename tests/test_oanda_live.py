from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from xau_lfx.connectors.oanda_v20 import OandaTransportError, parse_candles_response
from xau_lfx.live import LIVE_REFRESH_SECONDS, OandaLiveService
from tests.test_oanda_v20_connector import candle_payload


def _snapshot() -> dict:
    return {
        "schema_version": "oanda-live.v1",
        "ts_utc": "2026-06-19T12:40:01+00:00",
        "source": {
            "source_id": "OANDA_V20_PRACTICE",
            "provider": "OANDA",
            "environment": "practice",
            "instrument": "XAU_USD",
            "price_components": ["mid", "bid", "ask"],
        },
        "timeframes": {
            timeframe: {
                "granularity": timeframe,
                "candles": parse_candles_response(candle_payload(timeframe), timeframe),
            }
            for timeframe in ("M5", "M15", "H1")
        },
    }


class SequenceConnector:
    def __init__(self, results: list[object]) -> None:
        self.results = results

    def fetch_snapshot(self) -> dict:
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


def test_live_service_exposes_context_after_successful_refresh():
    service = OandaLiveService(SequenceConnector([_snapshot()]))  # type: ignore[arg-type]

    asyncio.run(service.refresh_once())
    view = service.snapshot_view(datetime(2026, 6, 19, 12, 41, tzinfo=timezone.utc))

    assert LIVE_REFRESH_SECONDS == 5
    assert view["status"] == "OK"
    assert view["context"]["past"]["state"] == "OBSERVED"
    assert view["context"]["now"]["state"] == "FORMING"
    assert view["context"]["mission"]["state"] == "NOT_INFERRED"
    assert view["context"]["inventory_release"]["state"] == "NOT_INFERRED"
    assert view["context"]["key_zones"]["sessions"]
    assert view["context"]["source_risk"]["source_family_count"] == 1


def test_live_service_keeps_last_success_and_marks_refresh_failure_stale():
    service = OandaLiveService(
        SequenceConnector([_snapshot(), OandaTransportError("practice endpoint unavailable")])  # type: ignore[arg-type]
    )

    asyncio.run(service.refresh_once())
    asyncio.run(service.refresh_once())
    view = service.snapshot_view(datetime(2026, 6, 19, 12, 42, tzinfo=timezone.utc))

    assert view["status"] == "STALE"
    assert view["transport_health"]["status"] == "STALE"
    assert view["transport_health"]["last_error"] == "practice endpoint unavailable"
    assert view["timeframes"]["M5"]["candles"]


def test_unexpected_refresh_error_does_not_expose_exception_detail():
    secret = "do-not-return-this-token"
    service = OandaLiveService(SequenceConnector([RuntimeError(secret)]))  # type: ignore[arg-type]

    asyncio.run(service.refresh_once())

    assert service.health()["status"] == "UNAVAILABLE"
    assert secret not in str(service.health())
