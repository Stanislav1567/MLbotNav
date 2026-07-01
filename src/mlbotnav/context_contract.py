from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pandas as pd

from mlbotnav.timeframes import canonical_timeframe, timeframe_delta


CONTEXT_CONTRACT_VERSION = "market_context_v1"

FUNDING_REQUIRED_COLUMNS = [
    "exchange",
    "market_type",
    "symbol",
    "timeframe",
    "event_time_utc",
    "funding_rate",
    "ingest_run_id",
    "source_ts_utc",
]

OPEN_INTEREST_REQUIRED_COLUMNS = [
    "exchange",
    "market_type",
    "symbol",
    "timeframe",
    "open_time_utc",
    "open_interest",
    "ingest_run_id",
    "source_ts_utc",
]

VALID_TIMEFRAMES = {"1m", "5m", "15m", "30m", "1h", "4h", "1d", "8h", "60m", "240m"}


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


def _tf_delta(timeframe: str) -> timedelta:
    tf = canonical_timeframe(timeframe)
    if tf == "8h":
        return timedelta(hours=8)
    return timeframe_delta(tf)


def validate_funding_contract(
    df: pd.DataFrame,
    *,
    expected_symbol: str,
    expected_market_type: str,
    expected_trade_date_utc: str,
) -> ContractValidationResult:
    violations: list[str] = []
    missing = [c for c in FUNDING_REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        violations.append(f"missing_columns:{','.join(missing)}")
        return ContractValidationResult(clean_df=df.copy(), violations=violations, dropped_rows=0)

    work = df.copy()
    work["funding_rate"] = pd.to_numeric(work["funding_rate"], errors="coerce")
    work["event_time_utc"] = pd.to_datetime(work["event_time_utc"], utc=True, errors="coerce")
    work["source_ts_utc"] = pd.to_datetime(work["source_ts_utc"], utc=True, errors="coerce")
    work["trade_date_utc"] = expected_trade_date_utc
    work["contract_version"] = CONTEXT_CONTRACT_VERSION

    before = len(work)
    work = work.dropna(subset=["event_time_utc", "funding_rate"]).copy()
    dropped = before - len(work)
    if dropped > 0:
        violations.append(f"rows_with_parse_errors:{dropped}")

    day_start = datetime.strptime(expected_trade_date_utc, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)
    in_day = (work["event_time_utc"] >= day_start) & (work["event_time_utc"] < day_end)
    out_rows = int((~in_day).sum())
    if out_rows > 0:
        violations.append(f"rows_outside_day_window:{out_rows}")
        work = work.loc[in_day].copy()

    if not (work["symbol"] == expected_symbol).all():
        violations.append("symbol_mismatch")
    if not (work["market_type"] == expected_market_type).all():
        violations.append("market_type_mismatch")
    if not (work["timeframe"] == "8h").all():
        violations.append("timeframe_mismatch")

    # Funding rates can be negative; only NaN/inf are invalid.
    invalid_num = (~pd.Series(pd.to_numeric(work["funding_rate"], errors="coerce")).apply(lambda x: pd.notna(x))).sum()
    if int(invalid_num) > 0:
        violations.append(f"invalid_funding_rate_rows:{int(invalid_num)}")

    work = work[FUNDING_REQUIRED_COLUMNS + ["trade_date_utc", "contract_version"]]
    work = work.drop_duplicates(subset=["exchange", "market_type", "symbol", "timeframe", "event_time_utc"])
    work = work.sort_values("event_time_utc").reset_index(drop=True)
    return ContractValidationResult(clean_df=work, violations=violations, dropped_rows=dropped)


def validate_open_interest_contract(
    df: pd.DataFrame,
    *,
    expected_symbol: str,
    expected_timeframe: str,
    expected_market_type: str,
    expected_trade_date_utc: str,
) -> ContractValidationResult:
    violations: list[str] = []
    missing = [c for c in OPEN_INTEREST_REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        violations.append(f"missing_columns:{','.join(missing)}")
        return ContractValidationResult(clean_df=df.copy(), violations=violations, dropped_rows=0)

    work = df.copy()
    work["open_interest"] = pd.to_numeric(work["open_interest"], errors="coerce")
    work["open_time_utc"] = pd.to_datetime(work["open_time_utc"], utc=True, errors="coerce")
    work["source_ts_utc"] = pd.to_datetime(work["source_ts_utc"], utc=True, errors="coerce")
    work["trade_date_utc"] = expected_trade_date_utc
    work["contract_version"] = CONTEXT_CONTRACT_VERSION

    before = len(work)
    work = work.dropna(subset=["open_time_utc", "open_interest"]).copy()
    dropped = before - len(work)
    if dropped > 0:
        violations.append(f"rows_with_parse_errors:{dropped}")

    expected_tf = canonical_timeframe(expected_timeframe)
    if expected_tf not in VALID_TIMEFRAMES and expected_timeframe not in VALID_TIMEFRAMES:
        violations.append(f"unsupported_timeframe:{expected_timeframe}")

    day_start = datetime.strptime(expected_trade_date_utc, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)
    in_day = (work["open_time_utc"] >= day_start) & (work["open_time_utc"] < day_end)
    out_rows = int((~in_day).sum())
    if out_rows > 0:
        violations.append(f"rows_outside_day_window:{out_rows}")
        work = work.loc[in_day].copy()

    if not (work["symbol"] == expected_symbol).all():
        violations.append("symbol_mismatch")
    if not (work["market_type"] == expected_market_type).all():
        violations.append("market_type_mismatch")
    work["timeframe"] = work["timeframe"].astype(str).map(_safe_canonical_tf)
    if not (work["timeframe"] == expected_tf).all():
        violations.append("timeframe_mismatch")
    if (work["open_interest"] < 0).any():
        violations.append(f"invalid_open_interest_rows:{int((work['open_interest'] < 0).sum())}")

    if expected_tf in VALID_TIMEFRAMES:
        step = int(_tf_delta(expected_tf).total_seconds())
        sorted_ts = work["open_time_utc"].sort_values()
        diffs = sorted_ts.diff().dropna().dt.total_seconds()
        bad_step = int((diffs != step).sum())
        if bad_step > 0:
            violations.append(f"non_uniform_step_rows:{bad_step}")

    work = work[OPEN_INTEREST_REQUIRED_COLUMNS + ["trade_date_utc", "contract_version"]]
    work = work.drop_duplicates(subset=["exchange", "market_type", "symbol", "timeframe", "open_time_utc"])
    work = work.sort_values("open_time_utc").reset_index(drop=True)
    return ContractValidationResult(clean_df=work, violations=violations, dropped_rows=dropped)
