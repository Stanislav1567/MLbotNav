from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pandas as pd

from mlbotnav.timeframes import canonical_timeframe


@dataclass(frozen=True)
class DQResult:
    expected_rows: int
    actual_rows: int
    completeness_pct: float
    duplicate_rows: int
    invalid_rows: int
    gap_count: int
    status: str


EXPECTED_ROWS = {
    "1m": 1440,
    "5m": 288,
    "15m": 96,
    "30m": 48,
    "1h": 24,
    "4h": 6,
    "1d": 1,
}

TF_STEP_SECONDS = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
}


def detect_gap_events_for_step(df: pd.DataFrame, *, time_col: str, step_seconds: int) -> list[str]:
    if step_seconds <= 0 or time_col not in df.columns or len(df) < 2:
        return []
    times = pd.to_datetime(df[time_col], utc=True, errors="coerce").dropna().drop_duplicates().sort_values()
    if len(times) < 2:
        return []

    out: list[str] = []
    step = pd.Timedelta(seconds=step_seconds)
    vals = list(times)
    for prev, curr in zip(vals[:-1], vals[1:]):
        probe = prev + step
        while probe < curr:
            out.append(probe.isoformat())
            probe = probe + step
    return out


def detect_gap_events(df: pd.DataFrame, *, timeframe: str, time_col: str = "open_time_utc") -> list[str]:
    tf = canonical_timeframe(timeframe)
    return detect_gap_events_for_step(df, time_col=time_col, step_seconds=TF_STEP_SECONDS[tf])


def run_ohlcv_dq(df: pd.DataFrame, *, timeframe: str, is_current_day: bool) -> DQResult:
    tf = canonical_timeframe(timeframe)
    expected_rows = EXPECTED_ROWS[tf]
    threshold = 99.0 if is_current_day else 99.9

    actual_rows = len(df)
    duplicate_rows = int(df.duplicated(subset=["open_time_utc"]).sum())

    invalid_price = (
        (df["high"] < df["low"])
        | (df["low"] > df[["open", "close"]].min(axis=1))
        | (df["high"] < df[["open", "close"]].max(axis=1))
    )
    invalid_time = pd.to_datetime(df["close_time_utc"], utc=True) <= pd.to_datetime(df["open_time_utc"], utc=True)
    invalid_rows = int((invalid_price | invalid_time).sum())

    gap_events = detect_gap_events(df, timeframe=tf, time_col="open_time_utc")
    gap_count = len(gap_events)

    completeness_pct = (actual_rows / expected_rows) * 100 if expected_rows else 0.0
    status = "PASS"
    if completeness_pct < threshold or invalid_rows > 0:
        status = "FAIL"
    elif duplicate_rows > 0 or gap_count > 0:
        status = "WARN"

    return DQResult(
        expected_rows=expected_rows,
        actual_rows=actual_rows,
        completeness_pct=round(completeness_pct, 3),
        duplicate_rows=duplicate_rows,
        invalid_rows=invalid_rows,
        gap_count=gap_count,
        status=status,
    )


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
