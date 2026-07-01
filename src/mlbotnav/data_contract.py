from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pandas as pd

from mlbotnav.timeframes import canonical_timeframe, timeframe_delta


CONTRACT_VERSION = "ohlcv_v1"

REQUIRED_COLUMNS = [
    "exchange",
    "market_type",
    "symbol",
    "timeframe",
    "open_time_utc",
    "close_time_utc",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "turnover",
    "ingest_run_id",
    "source_ts_utc",
]

VALID_TIMEFRAMES = {"1m", "5m", "15m", "30m", "1h", "4h", "1d", "60m", "240m"}
VALID_MARKET_TYPES = {"spot", "linear"}


@dataclass(frozen=True)
class ContractValidationResult:
    clean_df: pd.DataFrame
    violations: list[str]
    dropped_rows: int

    @property
    def is_valid(self) -> bool:
        return len(self.violations) == 0


def _safe_canonical_tf(value: str) -> str:
    try:
        return canonical_timeframe(str(value))
    except Exception:
        return str(value)


def timeframe_to_delta(timeframe: str) -> timedelta:
    return timeframe_delta(timeframe)


def validate_ohlcv_contract(
    df: pd.DataFrame,
    *,
    expected_symbol: str,
    expected_timeframe: str,
    expected_market_type: str,
    expected_exchange: str,
    expected_trade_date_utc: str,
) -> ContractValidationResult:
    violations: list[str] = []

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        violations.append(f"missing_columns:{','.join(missing_cols)}")
        return ContractValidationResult(clean_df=df.copy(), violations=violations, dropped_rows=0)

    work = df.copy()
    work["trade_date_utc"] = expected_trade_date_utc
    work["contract_version"] = CONTRACT_VERSION

    try:
        expected_tf_canonical = canonical_timeframe(expected_timeframe)
    except Exception:
        expected_tf_canonical = expected_timeframe
    if expected_timeframe not in VALID_TIMEFRAMES and expected_tf_canonical not in VALID_TIMEFRAMES:
        violations.append(f"unsupported_timeframe:{expected_timeframe}")
    if expected_market_type not in VALID_MARKET_TYPES:
        violations.append(f"unsupported_market_type:{expected_market_type}")

    for col in ("open", "high", "low", "close", "volume", "turnover"):
        work[col] = pd.to_numeric(work[col], errors="coerce")

    work["open_time_utc"] = pd.to_datetime(work["open_time_utc"], utc=True, errors="coerce")
    work["close_time_utc"] = pd.to_datetime(work["close_time_utc"], utc=True, errors="coerce")
    work["source_ts_utc"] = pd.to_datetime(work["source_ts_utc"], utc=True, errors="coerce")

    before = len(work)
    work = work.dropna(
        subset=[
            "open_time_utc",
            "close_time_utc",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
    ).copy()
    dropped_rows = before - len(work)

    if dropped_rows > 0:
        violations.append(f"rows_with_parse_errors:{dropped_rows}")

    day_start = datetime.strptime(expected_trade_date_utc, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)
    in_day = (work["open_time_utc"] >= day_start) & (work["open_time_utc"] < day_end)
    out_of_day_rows = int((~in_day).sum())
    if out_of_day_rows > 0:
        violations.append(f"rows_outside_day_window:{out_of_day_rows}")
        work = work.loc[in_day].copy()

    if not (work["symbol"] == expected_symbol).all():
        violations.append("symbol_mismatch")
    work["timeframe"] = work["timeframe"].astype(str).map(_safe_canonical_tf)
    if not (work["timeframe"] == expected_tf_canonical).all():
        violations.append("timeframe_mismatch")
    if not (work["market_type"] == expected_market_type).all():
        violations.append("market_type_mismatch")
    if not (work["exchange"] == expected_exchange).all():
        violations.append("exchange_mismatch")

    invalid_prices = (
        (work["high"] < work["low"])
        | (work["low"] > work[["open", "close"]].min(axis=1))
        | (work["high"] < work[["open", "close"]].max(axis=1))
        | (work["open"] <= 0)
        | (work["high"] <= 0)
        | (work["low"] <= 0)
        | (work["close"] <= 0)
        | (work["volume"] < 0)
    )
    invalid_price_rows = int(invalid_prices.sum())
    if invalid_price_rows > 0:
        violations.append(f"invalid_price_rows:{invalid_price_rows}")

    invalid_time = work["close_time_utc"] <= work["open_time_utc"]
    invalid_time_rows = int(invalid_time.sum())
    if invalid_time_rows > 0:
        violations.append(f"invalid_time_rows:{invalid_time_rows}")

    if expected_tf_canonical in VALID_TIMEFRAMES:
        step = int(timeframe_to_delta(expected_tf_canonical).total_seconds())
        sorted_ts = work["open_time_utc"].sort_values()
        diffs = sorted_ts.diff().dropna().dt.total_seconds()
        bad_step_rows = int((diffs != step).sum())
        if bad_step_rows > 0:
            violations.append(f"non_uniform_step_rows:{bad_step_rows}")

    # Keep only contract columns + extra governed fields, sorted for deterministic output.
    keep_cols = REQUIRED_COLUMNS + ["trade_date_utc", "contract_version"]
    work = work[keep_cols].drop_duplicates(
        subset=["exchange", "market_type", "symbol", "timeframe", "open_time_utc"]
    )
    work = work.sort_values("open_time_utc").reset_index(drop=True)

    # Critical violations that invalidate the batch.
    critical_prefixes = (
        "missing_columns:",
        "unsupported_",
        "symbol_mismatch",
        "timeframe_mismatch",
        "market_type_mismatch",
        "exchange_mismatch",
        "invalid_price_rows:",
        "invalid_time_rows:",
    )
    has_critical = any(v.startswith(critical_prefixes) for v in violations)
    if has_critical:
        return ContractValidationResult(clean_df=work, violations=violations, dropped_rows=dropped_rows)
    return ContractValidationResult(clean_df=work, violations=violations, dropped_rows=dropped_rows)
