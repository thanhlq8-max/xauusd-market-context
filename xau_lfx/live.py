from __future__ import annotations

import asyncio
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from xau_lfx.connectors.oanda_v20 import OandaError, OandaPracticeConnector
from xau_lfx.live_context import build_live_context
from xau_lfx.utils import utc_now_iso

LIVE_REFRESH_SECONDS = 5


class LiveSnapshotUnavailable(RuntimeError):
    pass


class OandaLiveService:
    def __init__(self, connector: OandaPracticeConnector) -> None:
        self._connector = connector
        self._snapshot: dict[str, Any] | None = None
        self._last_attempt_utc: str | None = None
        self._last_success_utc: str | None = None
        self._last_error: str | None = None
        self._stop_event = asyncio.Event()

    async def refresh_once(self) -> None:
        self._last_attempt_utc = utc_now_iso()
        try:
            snapshot = await asyncio.to_thread(self._connector.fetch_snapshot)
        except OandaError as exc:
            self._last_error = str(exc)
            return
        except Exception:
            self._last_error = "Unexpected live refresh failure"
            return
        self._snapshot = snapshot
        self._last_success_utc = utc_now_iso()
        self._last_error = None

    async def run(self) -> None:
        while not self._stop_event.is_set():
            await self.refresh_once()
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=LIVE_REFRESH_SECONDS)
            except asyncio.TimeoutError:
                continue

    def stop(self) -> None:
        self._stop_event.set()

    def health(self) -> dict[str, Any]:
        if self._snapshot is None:
            status = "STARTING" if self._last_error is None else "UNAVAILABLE"
        else:
            status = "OK" if self._last_error is None else "STALE"
        return {
            "status": status,
            "refresh_seconds": LIVE_REFRESH_SECONDS,
            "last_attempt_utc": self._last_attempt_utc,
            "last_success_utc": self._last_success_utc,
            "last_error": self._last_error,
        }

    def snapshot_view(self, now: datetime) -> dict[str, Any]:
        if self._snapshot is None:
            raise LiveSnapshotUnavailable("No successful OANDA Practice snapshot is available")
        if now.tzinfo is None:
            raise ValueError("now must include a timezone")

        view = deepcopy(self._snapshot)
        view["status"] = "OK" if self._last_error is None else "STALE"
        view["transport_health"] = self.health()
        view["context"] = build_live_context(view, now.astimezone(timezone.utc))
        return view
