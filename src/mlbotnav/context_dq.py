from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from mlbotnav.dq import detect_gap_events_for_step
from mlbotnav.timeframes import canonical_timeframe


@dataclass(frozen=True)
class ContextDQResult:
    expected_rows: int
    actual_rows: int
    completeness_pct: float
    duplicate_rows: int
    invalid_rows: int
    gap_count: int
    status: str


EXPECTED_ROWS_BY_TF = {
    "1m": 1440,
    "5m": 288,
    "15m": 96,
    "30m": 48,
    "1h": 24,
    "4h": 6,
    "1d": 1,
    "8h": 3,
}

STEP_SECONDS_BY_TF = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
    "8h": 28800,
}


def run_context_dq(
    df: pd.DataFrame,
    *,
    timeframe: str,
    time_col: str,
    value_col: str,
    is_current_day: bool,
) -> ContextDQResult:
    tf = canonical_timeframe(timeframe)
    expected_rows = int(EXPECTED_ROWS_BY_TF.get(tf, 0))
    threshold = 99.0 if is_current_day else 99.9
    actual_rows = int(len(df))
    duplicate_rows = int(df.duplicated(subset=[time_col]).sum()) if len(df) else 0

    vals = pd.to_numeric(df[value_col], errors="coerce")
    invalid_rows = int(vals.isna().sum())
    if value_col == "open_interest":
        invalid_rows += int((vals < 0).sum())

    step = int(STEP_SECONDS_BY_TF.get(tf, 0))
    gap_count = len(detect_gap_events_for_step(df, time_col=time_col, step_seconds=step))

    completeness_pct = (actual_rows / expected_rows) * 100.0 if expected_rows > 0 else 0.0
    status = "PASS"
    if completeness_pct < threshold or invalid_rows > 0:
        status = "FAIL"
    elif duplicate_rows > 0 or gap_count > 0:
        status = "WARN"

    return ContextDQResult(
        expected_rows=expected_rows,
        actual_rows=actual_rows,
        completeness_pct=round(float(completeness_pct), 3),
        duplicate_rows=duplicate_rows,
        invalid_rows=invalid_rows,
        gap_count=gap_count,
        status=status,
    )
