import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OANDA_FIXTURE = ROOT / "data" / "events" / "oanda_candles_fixture.json"


def test_candle_cli_writes_oanda_normalized_output_from_fixture(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "xau_lfx.connectors.candle_cli",
            "--source",
            "oanda",
            "--symbol",
            "XAUUSD",
            "--timeframe",
            "M1",
            "--limit",
            "1",
            "--fixture-json",
            str(OANDA_FIXTURE),
            "--oanda-token",
            "token-for-test",
            "--out-dir",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "OK"
    assert payload["source_id"] == "OANDA_REST"
    assert payload["monitor_only"] is True
    output_path = Path(payload["report_paths"]["json"])
    assert output_path.name == "normalized_ohlcv.json"
    assert output_path.exists()
    written = json.loads(output_path.read_text(encoding="utf-8"))
    rows = written["payload"]["ohlcv"]["M1"]
    assert rows[0]["source_type"] == "BROKER_REST"
    assert rows[0]["close"] == 3300.5
    assert rows[0]["is_complete"] is True


def test_candle_cli_returns_nonzero_when_oanda_token_missing(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "xau_lfx.connectors.candle_cli",
            "--source",
            "oanda",
            "--symbol",
            "XAUUSD",
            "--timeframe",
            "M1",
            "--fixture-json",
            str(OANDA_FIXTURE),
            "--out-dir",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
        env={},
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "ERROR"
    assert "OANDA_TOKEN_MISSING" in payload["errors"]
    assert Path(payload["report_paths"]["json"]).exists()


def test_candle_cli_mt5_missing_module_returns_nonzero(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "xau_lfx.connectors.candle_cli",
            "--source",
            "mt5",
            "--symbol",
            "XAUUSD",
            "--timeframe",
            "M5",
            "--out-dir",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "ERROR"
    assert payload["monitor_only"] is True
    assert Path(payload["report_paths"]["json"]).exists()
