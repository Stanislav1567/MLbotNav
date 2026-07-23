from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from mlbotnav.stas5_common import PROJECT_ROOT, compact_day, iter_days, normalize_day, rel


SYMBOL = "SOLUSDT"
TIMEFRAME = "1m"
BOLLINGER_WINDOW = 20
BOLLINGER_STD = 2.0
BOLLINGER_LAYER_ID = "BOLLINGER_LAYER_V1"
BOLLINGER_FEATURE_CONTRACT = "X439_PLUS_BB24_V1"

BOLLINGER_FEATURE_COLUMNS = [
    "bb20_mid_rel_pct",
    "bb20_upper_rel_pct",
    "bb20_lower_rel_pct",
    "bb20_width_pct",
    "bb20_position_0_1",
    "bb20_zscore",
    "bb20_upper_gap_pct",
    "bb20_lower_gap_pct",
    "bb20_mid_slope_15m_pct",
    "bb20_mid_slope_60m_pct",
    "bb20_close_ret_5m_pct",
    "bb20_close_ret_15m_pct",
    "bb20_close_ret_30m_pct",
    "bb20_close_ret_60m_pct",
    "bb20_range_20m_pct",
    "bb20_range_60m_pct",
    "bb20_atr20_pct",
    "bb20_upper_touch_count_60m",
    "bb20_lower_touch_count_60m",
    "bb20_down_channel_score",
    "bb20_falling_knife_score",
    "bb20_rebound_from_low_score",
    "bb20_post_knife_stabilization_score",
    "bb20_dead_move_score",
]

BOLLINGER_AUDIT_COLUMNS = [
    "bb_source_time_utc",
    "bb_feature_ready",
    "bb_preview_block",
    "bb_preview_reason",
    "bb_preview_block_score",
    "bb_preview_blocked_manual_good",
    "bb_preview_blocked_manual_bad",
]


def bollinger_feature_count() -> int:
    return len(BOLLINGER_FEATURE_COLUMNS)


def extended_feature_columns(base_features: list[str]) -> list[str]:
    out = [str(column) for column in base_features]
    for column in BOLLINGER_FEATURE_COLUMNS:
        if column not in out:
            out.append(column)
    return out


def _ohlcv_day_path(day: str, *, project_root: Path = PROJECT_ROOT) -> Path:
    return (
        project_root
        / "data"
        / "core"
        / "bybit_ohlcv"
        / f"dt={normalize_day(day)}"
        / f"tf={TIMEFRAME}"
        / f"symbol={SYMBOL}"
        / "part-final.csv"
    )


def _previous_day(day: str) -> str:
    return (pd.Timestamp(normalize_day(day)) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")


def load_ohlcv_context_for_range(
    *,
    start_day: str,
    end_day: str,
    warmup_days: int = 1,
    project_root: Path = PROJECT_ROOT,
    strict: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    start_day = normalize_day(start_day)
    end_day = normalize_day(end_day)
    source_start = start_day
    for _ in range(max(int(warmup_days), 0)):
        source_start = _previous_day(source_start)

    frames: list[pd.DataFrame] = []
    inputs: list[dict[str, Any]] = []
    missing: list[str] = []
    for day in iter_days(source_start, end_day):
        path = _ohlcv_day_path(day, project_root=project_root)
        if not path.exists():
            missing.append(day)
            continue
        frame = pd.read_csv(path, encoding="utf-8-sig")
        if "open_time_utc" not in frame.columns:
            raise ValueError(f"OHLCV missing open_time_utc: {path}")
        frame = frame.copy()
        frame["open_time_utc"] = pd.to_datetime(frame["open_time_utc"], utc=True, errors="raise", format="mixed")
        frames.append(frame)
        inputs.append({"day": day, "path": rel(path), "rows": int(len(frame))})

    context = pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()
    duplicate_open_time_count = 0
    if not context.empty:
        duplicate_open_time_count = int(context.duplicated(["open_time_utc"]).sum())
        context = (
            context.sort_values("open_time_utc")
            .drop_duplicates(["open_time_utc"], keep="last")
            .reset_index(drop=True)
        )

    status = "PASS_V5C_BOLLINGER_OHLCV_CONTEXT_READY" if inputs and not missing else "FAIL_V5C_BOLLINGER_OHLCV_CONTEXT"
    manifest = {
        "status": status,
        "layer_id": BOLLINGER_LAYER_ID,
        "start_day": start_day,
        "end_day": end_day,
        "source_start_day": source_start,
        "warmup_days": int(warmup_days),
        "rows": int(len(context)),
        "first_open_time_utc": _ts_to_string(context["open_time_utc"].iloc[0]) if not context.empty else "",
        "last_open_time_utc": _ts_to_string(context["open_time_utc"].iloc[-1]) if not context.empty else "",
        "missing_days": missing,
        "duplicate_open_time_count": duplicate_open_time_count,
        "source_inputs": inputs,
    }
    if strict and status.startswith("FAIL"):
        raise ValueError(f"Bollinger OHLCV context is not ready: {manifest}")
    return context, manifest


def prepare_bollinger_source(
    ohlcv_df: pd.DataFrame,
    *,
    window: int = BOLLINGER_WINDOW,
    num_std: float = BOLLINGER_STD,
) -> pd.DataFrame:
    if ohlcv_df.empty:
        return pd.DataFrame()
    source = ohlcv_df.copy().sort_values("open_time_utc").reset_index(drop=True)
    source["open_time_utc"] = pd.to_datetime(source["open_time_utc"], utc=True, errors="raise", format="mixed")
    for column in ["open", "high", "low", "close", "volume"]:
        if column in source.columns:
            source[column] = pd.to_numeric(source[column], errors="coerce")
    close = pd.to_numeric(source["close"], errors="coerce")
    high = pd.to_numeric(source["high"], errors="coerce")
    low = pd.to_numeric(source["low"], errors="coerce")

    mid = close.rolling(window=window, min_periods=window).mean()
    std = close.rolling(window=window, min_periods=window).std(ddof=0)
    upper = mid + float(num_std) * std
    lower = mid - float(num_std) * std
    band = (upper - lower).replace(0, np.nan)
    prev_close = close.shift(1)
    true_range = pd.concat([(high - low).abs(), (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    recent_low_60 = low.rolling(window=60, min_periods=1).min()
    recent_high_60 = high.rolling(window=60, min_periods=1).max()

    source["bb20_mid"] = mid
    source["bb20_upper"] = upper
    source["bb20_lower"] = lower
    source["bb20_std"] = std
    source["bb20_mid_rel_pct"] = _pct(mid, close)
    source["bb20_upper_rel_pct"] = _pct(upper, close)
    source["bb20_lower_rel_pct"] = _pct(lower, close)
    source["bb20_width_pct"] = _pct(upper - lower, mid)
    source["bb20_position_0_1"] = ((close - lower) / band).clip(-2.0, 3.0)
    source["bb20_zscore"] = ((close - mid) / std.replace(0, np.nan)).clip(-8.0, 8.0)
    source["bb20_upper_gap_pct"] = _pct(upper - close, close)
    source["bb20_lower_gap_pct"] = _pct(close - lower, close)
    source["bb20_mid_slope_15m_pct"] = _pct(mid - mid.shift(15), mid.shift(15))
    source["bb20_mid_slope_60m_pct"] = _pct(mid - mid.shift(60), mid.shift(60))
    for minutes in [5, 15, 30, 60]:
        source[f"bb20_close_ret_{minutes}m_pct"] = _pct(close - close.shift(minutes), close.shift(minutes))
    source["bb20_range_20m_pct"] = _pct(high.rolling(20, min_periods=1).max() - low.rolling(20, min_periods=1).min(), close)
    source["bb20_range_60m_pct"] = _pct(recent_high_60 - recent_low_60, close)
    source["bb20_atr20_pct"] = _pct(true_range.rolling(window=20, min_periods=1).mean(), close)
    source["bb20_upper_touch_count_60m"] = high.ge(upper).rolling(60, min_periods=1).sum()
    source["bb20_lower_touch_count_60m"] = low.le(lower).rolling(60, min_periods=1).sum()

    down_slope = _clip01(-source["bb20_mid_slope_60m_pct"] / 1.2)
    down_ret = _clip01(-source["bb20_close_ret_60m_pct"] / 2.0)
    lower_highs = high.rolling(20, min_periods=1).max().lt(high.shift(20).rolling(20, min_periods=1).max()).astype(float)
    weak_reclaim = source["bb20_position_0_1"].lt(0.52).astype(float)
    source["bb20_down_channel_score"] = (0.35 * down_slope + 0.35 * down_ret + 0.15 * lower_highs + 0.15 * weak_reclaim).clip(0, 1)

    knife_15 = _clip01(-source["bb20_close_ret_15m_pct"] / 1.2)
    knife_30 = _clip01(-source["bb20_close_ret_30m_pct"] / 2.0)
    lower_break = source["bb20_position_0_1"].lt(0.08).astype(float)
    source["bb20_falling_knife_score"] = (0.45 * knife_15 + 0.35 * knife_30 + 0.20 * lower_break).clip(0, 1)

    rebound_from_low = _pct(close - recent_low_60, close).clip(lower=0)
    ret5_pos = source["bb20_close_ret_5m_pct"].clip(lower=0)
    reclaim_mid = source["bb20_position_0_1"].gt(0.45).astype(float)
    source["bb20_rebound_from_low_score"] = (_clip01(rebound_from_low / 1.1) * 0.45 + _clip01(ret5_pos / 0.45) * 0.30 + reclaim_mid * 0.25).clip(0, 1)

    prior_knife = source["bb20_falling_knife_score"].shift(1).rolling(45, min_periods=1).max().fillna(0)
    source["bb20_post_knife_stabilization_score"] = (
        0.45 * prior_knife
        + 0.30 * source["bb20_rebound_from_low_score"]
        + 0.25 * source["bb20_position_0_1"].between(0.18, 0.72).astype(float)
    ).clip(0, 1)

    low_width = _clip01((0.85 - source["bb20_width_pct"]) / 0.85)
    low_range = _clip01((1.20 - source["bb20_range_60m_pct"]) / 1.20)
    source["bb20_dead_move_score"] = (0.55 * low_width + 0.45 * low_range).clip(0, 1)
    return source


def attach_bollinger_features(
    candidates_df: pd.DataFrame,
    ohlcv_df: pd.DataFrame,
    *,
    entry_time_column: str = "entry_time_utc",
    entry_price_columns: tuple[str, ...] = ("entry_price_5bps", "entry_open_price", "entry_price"),
    window: int = BOLLINGER_WINDOW,
    num_std: float = BOLLINGER_STD,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    out = candidates_df.copy()
    for column in BOLLINGER_FEATURE_COLUMNS:
        out[column] = 0.0
    out["bb_source_time_utc"] = ""
    out["bb_feature_ready"] = 0
    out["bb_preview_block"] = 0
    out["bb_preview_reason"] = ""
    out["bb_preview_block_score"] = 0.0
    out["bb_preview_blocked_manual_good"] = 0
    out["bb_preview_blocked_manual_bad"] = 0
    if out.empty:
        return out, _attach_summary(out, source_rows=0)
    if entry_time_column not in out.columns:
        out["bb_feature_ready"] = 0
        out["bb_preview_reason"] = "MISSING_ENTRY_TIME"
        return out, _attach_summary(out, source_rows=0)

    source = prepare_bollinger_source(ohlcv_df, window=window, num_std=num_std)
    if source.empty:
        out["bb_feature_ready"] = 0
        out["bb_preview_reason"] = "MISSING_OHLCV_CONTEXT"
        return out, _attach_summary(out, source_rows=0)

    source_times = (
        source["open_time_utc"]
        .dt.tz_convert("UTC")
        .dt.tz_localize(None)
        .to_numpy(dtype="datetime64[ns]")
        .astype("int64")
    )
    entry_times = pd.to_datetime(out[entry_time_column], utc=True, errors="coerce", format="mixed")
    price_column = next((column for column in entry_price_columns if column in out.columns), "")
    price_values = pd.to_numeric(out[price_column], errors="coerce") if price_column else pd.Series(np.nan, index=out.index)

    ready_count = 0
    source_after_entry = 0
    for row_index, entry_ts in entry_times.items():
        if pd.isna(entry_ts):
            out.at[row_index, "bb_feature_ready"] = 0
            out.at[row_index, "bb_preview_reason"] = "BAD_ENTRY_TIME"
            continue
        entry_ns = int(pd.Timestamp(entry_ts).value)
        source_idx = int(np.searchsorted(source_times, entry_ns, side="left") - 1)
        if source_idx < 0:
            out.at[row_index, "bb_feature_ready"] = 0
            out.at[row_index, "bb_preview_reason"] = "NO_CLOSED_BAR_BEFORE_ENTRY"
            continue
        source_row = source.iloc[source_idx]
        source_time = pd.Timestamp(source_row["open_time_utc"])
        if source_time > pd.Timestamp(entry_ts):
            source_after_entry += 1
        entry_price = _safe_float(price_values.loc[row_index], _safe_float(source_row.get("close"), 0.0))
        values = _feature_values_for_row(source_row, entry_price=entry_price)
        for column, value in values.items():
            out.at[row_index, column] = value
        block = _preview_block_for_values(values)
        out.at[row_index, "bb_source_time_utc"] = _ts_to_string(source_time)
        out.at[row_index, "bb_feature_ready"] = 1 if pd.notna(source_row.get("bb20_mid")) else 0
        out.at[row_index, "bb_preview_block"] = int(block["blocked"])
        out.at[row_index, "bb_preview_reason"] = block["reason"]
        out.at[row_index, "bb_preview_block_score"] = block["score"]
        ready_count += int(out.at[row_index, "bb_feature_ready"] == 1)

    if "entry_y" in out.columns:
        entry_y = pd.to_numeric(out["entry_y"], errors="coerce").fillna(0).astype(int)
        blocked = pd.to_numeric(out["bb_preview_block"], errors="coerce").fillna(0).astype(int).eq(1)
        out["bb_preview_blocked_manual_good"] = (blocked & entry_y.eq(1)).astype(int)
        out["bb_preview_blocked_manual_bad"] = (blocked & entry_y.eq(0)).astype(int)

    out[BOLLINGER_FEATURE_COLUMNS] = out[BOLLINGER_FEATURE_COLUMNS].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    return out, _attach_summary(out, source_rows=len(source), source_after_entry=source_after_entry, ready_count=ready_count)


def bollinger_source_time_check(df: pd.DataFrame) -> dict[str, Any]:
    if "bb_source_time_utc" not in df.columns or "entry_time_utc" not in df.columns:
        return {"missing_column": True}
    source = pd.to_datetime(df["bb_source_time_utc"], utc=True, errors="coerce", format="mixed")
    entry = pd.to_datetime(df["entry_time_utc"], utc=True, errors="coerce", format="mixed")
    ready = pd.to_numeric(df.get("bb_feature_ready", pd.Series(0, index=df.index)), errors="coerce").fillna(0).astype(int).eq(1)
    active = ready & source.notna() & entry.notna()
    return {
        "missing_column": False,
        "ready_rows": int(ready.sum()),
        "source_after_entry_rows": int((source[active] > entry[active]).sum()),
        "source_na_ready_rows": int((ready & source.isna()).sum()),
        "entry_na_ready_rows": int((ready & entry.isna()).sum()),
    }


def _feature_values_for_row(source_row: pd.Series, *, entry_price: float) -> dict[str, float]:
    values: dict[str, float] = {}
    close = _safe_float(source_row.get("close"), entry_price)
    price = entry_price if entry_price > 0 else close
    for column in BOLLINGER_FEATURE_COLUMNS:
        values[column] = _safe_float(source_row.get(column), 0.0)
    mid = _safe_float(source_row.get("bb20_mid"), 0.0)
    upper = _safe_float(source_row.get("bb20_upper"), 0.0)
    lower = _safe_float(source_row.get("bb20_lower"), 0.0)
    std = _safe_float(source_row.get("bb20_std"), 0.0)
    if price > 0 and mid > 0 and upper > lower and std > 0:
        width = upper - lower
        values["bb20_mid_rel_pct"] = _safe_float(_pct_scalar(mid - price, price))
        values["bb20_upper_rel_pct"] = _safe_float(_pct_scalar(upper - price, price))
        values["bb20_lower_rel_pct"] = _safe_float(_pct_scalar(lower - price, price))
        values["bb20_width_pct"] = _safe_float(_pct_scalar(width, mid))
        values["bb20_position_0_1"] = float(np.clip((price - lower) / width, -2.0, 3.0))
        values["bb20_zscore"] = float(np.clip((price - mid) / std, -8.0, 8.0))
        values["bb20_upper_gap_pct"] = _safe_float(_pct_scalar(upper - price, price))
        values["bb20_lower_gap_pct"] = _safe_float(_pct_scalar(price - lower, price))
    return values


def _preview_block_for_values(values: dict[str, float]) -> dict[str, Any]:
    position = float(values.get("bb20_position_0_1", 0.5))
    slope60 = float(values.get("bb20_mid_slope_60m_pct", 0.0))
    ret15 = float(values.get("bb20_close_ret_15m_pct", 0.0))
    down = float(values.get("bb20_down_channel_score", 0.0))
    knife = float(values.get("bb20_falling_knife_score", 0.0))
    rebound = float(values.get("bb20_rebound_from_low_score", 0.0))
    dead = float(values.get("bb20_dead_move_score", 0.0))
    range60 = float(values.get("bb20_range_60m_pct", 0.0))
    upper_touch = float(values.get("bb20_upper_touch_count_60m", 0.0))

    if knife >= 0.68 and rebound < 0.55:
        return {"blocked": True, "reason": "FALLING_KNIFE_NO_LONG", "score": round(knife, 6)}
    if down >= 0.64 and rebound < 0.48:
        return {"blocked": True, "reason": "DOWN_CHANNEL_NO_LONG", "score": round(down, 6)}
    if position >= 0.88 and slope60 <= 0.10 and upper_touch >= 1 and ret15 <= 0.35:
        return {"blocked": True, "reason": "HIGH_ZONE_WEAK_LONG_EDGE", "score": round(min(1.0, position), 6)}
    if dead >= 0.78 and range60 < 1.20 and rebound < 0.55:
        return {"blocked": True, "reason": "LOW_MOVE_CAPACITY_NO_TP_EDGE", "score": round(dead, 6)}
    return {"blocked": False, "reason": "PASS_BOLLINGER_CONTEXT", "score": 0.0}


def _attach_summary(df: pd.DataFrame, *, source_rows: int, source_after_entry: int = 0, ready_count: int | None = None) -> dict[str, Any]:
    ready = pd.to_numeric(df.get("bb_feature_ready", pd.Series(dtype=float)), errors="coerce").fillna(0).astype(int) if not df.empty else pd.Series(dtype=int)
    blocked = pd.to_numeric(df.get("bb_preview_block", pd.Series(dtype=float)), errors="coerce").fillna(0).astype(int) if not df.empty else pd.Series(dtype=int)
    if ready_count is None:
        ready_count = int(ready.eq(1).sum())
    return {
        "layer_id": BOLLINGER_LAYER_ID,
        "feature_contract": BOLLINGER_FEATURE_CONTRACT,
        "feature_count": len(BOLLINGER_FEATURE_COLUMNS),
        "source_rows": int(source_rows),
        "rows": int(len(df)),
        "ready_rows": int(ready_count),
        "preview_block_rows": int(blocked.eq(1).sum()),
        "source_after_entry_rows": int(source_after_entry),
        "feature_columns": BOLLINGER_FEATURE_COLUMNS,
        "audit_columns": BOLLINGER_AUDIT_COLUMNS,
    }


def _pct(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return (100.0 * numerator / denominator.replace(0, np.nan)).replace([np.inf, -np.inf], np.nan)


def _pct_scalar(numerator: float, denominator: float) -> float:
    if denominator == 0 or not math.isfinite(float(denominator)):
        return 0.0
    return float(100.0 * numerator / denominator)


def _clip01(values: pd.Series) -> pd.Series:
    return pd.to_numeric(values, errors="coerce").clip(lower=0.0, upper=1.0).fillna(0.0)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
        if not math.isfinite(out):
            return default
        return out
    except Exception:
        return default


def _ts_to_string(value: Any) -> str:
    if value is None or value == "":
        return ""
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
