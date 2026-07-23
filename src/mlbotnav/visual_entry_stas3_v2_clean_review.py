from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle


STATUS = "STAS3_V2_CLEAN_LONG_ONLY_READY_NO_OLD_STAS3_NO_ML_NO_OPTUNA_POST_ENTRY_AUDIT"
DEFAULT_STAS2_RUN = (
    "STAS2_MARKET_PHASE_REVIEW/runs/"
    "stas2_20260510_20260512_continuous_wave_v2_20260709_081330"
)
WORK_DAYS = ["2026-05-10", "2026-05-11", "2026-05-12"]
BOUNDARY = "clean_stas3_v2_from_stas2_only_long_post_entry_audit_no_ml_no_optuna_no_api"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _parse_ts(value: Any) -> pd.Timestamp | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    ts = pd.to_datetime(text, utc=True, errors="coerce", format="mixed")
    if pd.isna(ts):
        return None
    return pd.Timestamp(ts).tz_convert("UTC")


def _fmt_ts(value: pd.Timestamp | None) -> str:
    if value is None or pd.isna(value):
        return ""
    return pd.Timestamp(value).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def _fmt_min(value: pd.Timestamp | None) -> str:
    if value is None or pd.isna(value):
        return ""
    return pd.Timestamp(value).tz_convert("UTC").strftime("%H:%M")


def _safe_float(value: Any, default: float | None = None) -> float | None:
    if value is None:
        return default
    text = str(value).strip()
    if text == "":
        return default
    try:
        out = float(text)
    except Exception:
        return default
    if np.isnan(out) or np.isinf(out):
        return default
    return out


def _round6(value: float | None) -> float | str:
    if value is None or np.isnan(value):
        return ""
    return round(float(value), 6)


def _pct_key(value: float) -> str:
    return f"{value:.1f}".replace(".", "p")


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def build_percent_ladder() -> list[float]:
    vals: list[float] = []
    vals.extend(round(i / 10, 1) for i in range(3, 10))
    vals.extend(round(i / 10, 1) for i in range(10, 21))
    vals.extend(round(i / 10, 1) for i in range(22, 201, 2))
    out: list[float] = []
    seen: set[float] = set()
    for val in vals:
        if val not in seen:
            out.append(val)
            seen.add(val)
    return out


PERCENT_LADDER = build_percent_ladder()


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        cols: list[str] = []
        seen: set[str] = set()
        for row in rows:
            for key in row.keys():
                if key not in seen:
                    cols.append(key)
                    seen.add(key)
        fieldnames = cols
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _source_csv(root: Path, day: str, timeframe: str, symbol: str) -> Path:
    return root / "data" / "core" / "bybit_ohlcv" / f"dt={day}" / f"tf={timeframe}" / f"symbol={symbol}" / "part-final.csv"


def _load_ohlcv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], utc=True, errors="raise", format="mixed")
    df["close_time_utc"] = pd.to_datetime(df["close_time_utc"], utc=True, errors="raise", format="mixed")
    df = df.sort_values("open_time_utc").reset_index(drop=True)
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    return df


def _day_range(start_day: str, end_day: str, extra_days: int = 0) -> list[str]:
    start = datetime.strptime(start_day, "%Y-%m-%d").date()
    end = datetime.strptime(end_day, "%Y-%m-%d").date() + timedelta(days=extra_days)
    days: list[str] = []
    cur = start
    while cur <= end:
        days.append(cur.isoformat())
        cur += timedelta(days=1)
    return days


def _load_ohlcv_range(root: Path, days: list[str], timeframe: str, symbol: str) -> tuple[pd.DataFrame, list[str]]:
    frames: list[pd.DataFrame] = []
    missing: list[str] = []
    for day in days:
        path = _source_csv(root, day, timeframe, symbol)
        if not path.exists():
            missing.append(path.as_posix())
            continue
        frames.append(_load_ohlcv(path))
    if not frames:
        return pd.DataFrame(), missing
    df = pd.concat(frames, ignore_index=True).sort_values("open_time_utc").reset_index(drop=True)
    return df, missing


def _bar_width_days(timeframe: str) -> float:
    if timeframe.endswith("m"):
        return (int(timeframe[:-1]) / (24 * 60)) * 0.72
    return (1 / (24 * 60)) * 0.72


def _style_axis(ax: Any) -> None:
    ax.set_facecolor("#0a1116")
    ax.grid(True, color="#23313a", alpha=0.45, linewidth=0.55)
    ax.tick_params(colors="#c8d2d8", labelsize=7)
    for spine in ax.spines.values():
        spine.set_color("#31414b")


def _draw_candles(ax: Any, df: pd.DataFrame, timeframe: str) -> None:
    if df.empty:
        return
    width = _bar_width_days(timeframe)
    times = mdates.date2num(df["open_time_utc"].dt.tz_convert(None))
    for x, row in zip(times, df.itertuples(index=False)):
        open_p = float(row.open)
        high_p = float(row.high)
        low_p = float(row.low)
        close_p = float(row.close)
        color = "#20c7b5" if close_p >= open_p else "#f05b57"
        ax.vlines(x, low_p, high_p, color=color, linewidth=0.42, alpha=0.9)
        body_low = min(open_p, close_p)
        body_h = max(abs(close_p - open_p), 0.00001)
        ax.add_patch(Rectangle((x - width / 2, body_low), width, body_h, facecolor=color, edgecolor=color, linewidth=0.25, alpha=0.9))


def _interval_match(rows: list[dict[str, str]], ts: pd.Timestamp, start_key: str, end_key: str) -> dict[str, str] | None:
    for row in rows:
        start = _parse_ts(row.get(start_key))
        end = _parse_ts(row.get(end_key))
        if start is None or end is None:
            continue
        if start <= ts <= end:
            return row
    return None


def _hour_match(rows: list[dict[str, str]], ts: pd.Timestamp) -> dict[str, str] | None:
    for row in rows:
        start = _parse_ts(row.get("hour_start_utc"))
        if start is None:
            continue
        end = start + pd.Timedelta(hours=1)
        if start <= ts < end:
            return row
    return None


def _field(row: dict[str, Any] | None, key: str) -> str:
    if not row:
        return ""
    return str(row.get(key, "") or "")


def _context_for_entry(
    record: dict[str, str],
    entry_ts: pd.Timestamp,
    hourly_rows: list[dict[str, str]],
    macro_rows: list[dict[str, str]],
    continuous_rows: list[dict[str, str]],
) -> dict[str, Any]:
    hour = _hour_match(hourly_rows, entry_ts)
    macro = _interval_match(macro_rows, entry_ts, "macro_wave_start_time_utc", "macro_wave_end_time_utc")
    continuous = _interval_match(
        continuous_rows,
        entry_ts,
        "continuous_wave_start_time_utc",
        "continuous_wave_end_time_utc",
    )
    out: dict[str, Any] = {
        "source_context": "STAS2_TABLES_ONLY",
        "direction_scope": "LONG_ONLY",
        "long_only_flag": True,
        "short_context_only_flag": True,
        "wave_context_scope": "HINDSIGHT_WAVE_REVIEW",
        "session_time_bucket_code": record.get("session_time_bucket_code", ""),
        "session_time_bucket_label": record.get("session_time_bucket_label", ""),
        "effective_session_code": record.get("effective_session_code", ""),
        "effective_session_label": record.get("effective_session_label", ""),
        "real_tradfi_session_open": record.get("real_tradfi_session_open", ""),
        "entry_setup_quality_code": record.get("entry_setup_quality_code", ""),
        "entry_setup_quality_label": record.get("entry_setup_quality_label", ""),
        "entry_setup_quality_reason": record.get("entry_setup_quality_reason", ""),
        "suggested_type": record.get("suggested_type", ""),
        "score": record.get("score", ""),
        "review_label": record.get("review_label", ""),
        "outcome_status": record.get("outcome_status", ""),
        "stas1_volume_ratio20": record.get("stas1_feature_volume_ratio20", ""),
        "pre_5m_background_phase": record.get("pre_5m_background_phase", ""),
        "pre_15m_background_phase": record.get("pre_15m_background_phase", ""),
        "pre_30m_background_phase": record.get("pre_30m_background_phase", ""),
        "pre_60m_background_phase": record.get("pre_60m_background_phase", ""),
        "pre_5m_long_wave_phase": record.get("pre_5m_long_wave_phase", ""),
        "pre_15m_long_wave_phase": record.get("pre_15m_long_wave_phase", ""),
        "pre_30m_long_wave_phase": record.get("pre_30m_long_wave_phase", ""),
        "pre_60m_long_wave_phase": record.get("pre_60m_long_wave_phase", ""),
    }
    if hour:
        for key in [
            "hour_start_utc",
            "hour_range_pct",
            "hour_close_move_pct",
            "hour_path_pct",
            "hour_background_phase",
            "hour_background_phase_rank",
            "hour_long_wave_up_from_low_pct",
            "hour_long_wave_close_from_low_pct",
            "hour_long_wave_pullback_from_post_low_high_pct",
            "hour_long_wave_phase",
            "hour_long_wave_rank",
            "hour_short_wave_down_from_high_pct",
            "hour_short_wave_close_from_high_pct",
            "hour_short_wave_bounce_from_post_high_low_pct",
            "hour_short_wave_phase",
            "hour_short_wave_rank",
            "hour_direction_bias",
        ]:
            out[key] = hour.get(key, "")
    else:
        out["hour_start_utc"] = ""
    if macro:
        for key in [
            "macro_wave_id",
            "macro_wave_no",
            "macro_wave_segment_kind",
            "macro_wave_direction",
            "macro_wave_status",
            "macro_wave_start_time_utc",
            "macro_wave_start_price",
            "macro_wave_end_time_utc",
            "macro_wave_end_price",
            "macro_wave_move_pct",
            "macro_wave_visible_move_pct",
            "macro_wave_full_move_pct",
            "macro_wave_duration_min",
            "macro_wave_carry_from_prev_day",
            "macro_wave_carry_to_next_day",
        ]:
            out[key] = macro.get(key, "")
    else:
        out["macro_wave_segment_kind"] = ""
        out["macro_wave_direction"] = ""
    if continuous:
        for key in [
            "continuous_wave_id",
            "continuous_wave_no",
            "continuous_wave_segment_kind",
            "continuous_wave_direction",
            "continuous_wave_status",
            "continuous_wave_start_time_utc",
            "continuous_wave_start_price",
            "continuous_wave_end_time_utc",
            "continuous_wave_end_price",
            "continuous_wave_move_pct",
            "continuous_wave_duration_min",
            "continuous_wave_crossed_day_count",
            "continuous_wave_crossed_hour_count",
        ]:
            out[key] = continuous.get(key, "")
    else:
        out["continuous_wave_segment_kind"] = ""
        out["continuous_wave_direction"] = ""
    return out


def _clean_hit(drawdown_pct: float | None, tp_pct: float, minutes: float | None) -> bool:
    if drawdown_pct is None or minutes is None:
        return False
    max_drawdown = max(0.35, min(2.0, tp_pct * 0.80))
    max_minutes = 240.0 if tp_pct < 1.0 else 720.0 if tp_pct <= 3.0 else 1440.0
    return drawdown_pct <= max_drawdown and minutes <= max_minutes


def _analyze_path(
    candles: pd.DataFrame,
    entry_ts: pd.Timestamp,
    entry_price: float,
    hold_hours: float,
    ladder: list[float],
) -> tuple[dict[str, Any], dict[float, dict[str, Any]]]:
    end_ts = entry_ts + pd.Timedelta(hours=hold_hours)
    future = candles[(candles["open_time_utc"] >= entry_ts) & (candles["open_time_utc"] <= end_ts)].copy()
    if future.empty or entry_price <= 0:
        return {
            "path_status": "NO_FUTURE_BARS_OR_BAD_ENTRY_PRICE",
            "future_bar_count": 0,
        }, {}

    max_idx = int(future["high"].idxmax())
    min_idx = int(future["low"].idxmin())
    max_row = future.loc[max_idx]
    min_row = future.loc[min_idx]
    max_mfe_pct = (float(max_row["high"]) / entry_price - 1.0) * 100.0
    max_mae_pct = max(0.0, (entry_price / float(min_row["low"]) - 1.0) * 100.0)

    base: dict[str, Any] = {
        "path_status": "OK",
        "future_bar_count": int(len(future)),
        "hold_hours": hold_hours,
        "max_high_time_utc": _fmt_ts(pd.Timestamp(max_row["open_time_utc"])),
        "max_high_price": _round6(float(max_row["high"])),
        "max_mfe_pct": _round6(max_mfe_pct),
        "min_low_time_utc": _fmt_ts(pd.Timestamp(min_row["open_time_utc"])),
        "min_low_price": _round6(float(min_row["low"])),
        "max_mae_pct": _round6(max_mae_pct),
    }

    hit_map: dict[float, dict[str, Any]] = {}
    for tp_pct in ladder:
        target = entry_price * (1.0 + tp_pct / 100.0)
        hit = future[future["high"] >= target]
        key_data: dict[str, Any] = {
            "hit": False,
            "target_price": target,
            "time_to_min": None,
            "hit_time_utc": None,
            "drawdown_before_hit_pct": None,
            "clean_hit": False,
        }
        if not hit.empty:
            first = hit.iloc[0]
            hit_ts = pd.Timestamp(first["open_time_utc"]).tz_convert("UTC")
            until_hit = future[future["open_time_utc"] <= hit_ts]
            min_low_before = float(until_hit["low"].min())
            dd_before = max(0.0, (entry_price / min_low_before - 1.0) * 100.0)
            minutes = (hit_ts - entry_ts).total_seconds() / 60.0
            key_data.update(
                {
                    "hit": True,
                    "time_to_min": minutes,
                    "hit_time_utc": hit_ts,
                    "drawdown_before_hit_pct": dd_before,
                    "clean_hit": _clean_hit(dd_before, tp_pct, minutes),
                }
            )
        hit_map[tp_pct] = key_data
    return base, hit_map


def _highest_hit(hit_map: dict[float, dict[str, Any]], *, clean_only: bool = False, max_minutes: float | None = None) -> float | None:
    out: float | None = None
    for tp_pct, data in hit_map.items():
        if not data.get("hit"):
            continue
        if clean_only and not data.get("clean_hit"):
            continue
        minutes = data.get("time_to_min")
        if max_minutes is not None and (minutes is None or float(minutes) > max_minutes):
            continue
        out = tp_pct if out is None else max(out, tp_pct)
    return out


def _decision_fields(hit_map: dict[float, dict[str, Any]], path: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    max_mfe = _safe_float(path.get("max_mfe_pct"), 0.0) or 0.0
    best_observed = _highest_hit(hit_map)
    fast_observed = _highest_hit(hit_map, max_minutes=120.0)
    clean_review = _highest_hit(hit_map, clean_only=True)
    clean_fast = _highest_hit(hit_map, clean_only=True, max_minutes=120.0)
    hit_0p3 = bool(hit_map.get(0.3, {}).get("hit"))
    hit_1 = bool(hit_map.get(1.0, {}).get("hit"))
    one = hit_map.get(1.0, {})
    one_time = one.get("time_to_min")
    one_dd = one.get("drawdown_before_hit_pct")
    wrong_1 = (not hit_1) or (one_time is not None and float(one_time) > 720.0) or (one_dd is not None and float(one_dd) > 1.0)
    hit03_dd = hit_map.get(0.3, {}).get("drawdown_before_hit_pct")
    setup_text = f"{context.get('entry_setup_quality_code', '')} {context.get('entry_setup_quality_label', '')}".upper()
    noise = max_mfe < 0.3 or (hit03_dd is not None and float(hit03_dd) > 0.8) or ("NOISE" in setup_text)

    short_risk = _safe_float(context.get("hour_short_wave_down_from_high_pct"), 0.0) or 0.0
    long_power = _safe_float(context.get("hour_long_wave_up_from_low_pct"), 0.0) or 0.0
    warning_parts: list[str] = []
    if short_risk >= max(long_power, 0.01) and short_risk >= 0.8:
        warning_parts.append("SHORT-risk сильнее или равен LONG-контексту")
    if one_dd is not None and float(one_dd) > 1.0:
        warning_parts.append("1% требовал просадку больше 1%")
    if one_time is not None and float(one_time) > 720.0:
        warning_parts.append("1% пришел поздно")
    if not hit_1:
        warning_parts.append("1% не достигнут")

    if noise:
        label = "NOISE_OR_NO_TP_ROOM"
        reason = "Вход шумовой или после входа не было честного места даже под быстрый TP."
        review_tp = clean_review or fast_observed or best_observed
    elif clean_review is not None and clean_review >= 1.0:
        label = "MEDIUM_TP_CLEAN_REVIEW"
        reason = "Средний TP был достигнут без чрезмерной просадки и без слишком позднего ожидания."
        review_tp = clean_review
    elif clean_fast is not None:
        label = "FAST_TP_ONLY"
        reason = "Чистый быстрый TP был, но средний 1% либо грязный, либо поздний, либо не достигнут."
        review_tp = clean_fast
    elif best_observed is not None:
        label = "DIRTY_OR_LATE_MOVE_REVIEW_ONLY"
        reason = "Движение после входа было, но как TP оно грязное или позднее; нельзя выдавать как чистую цель."
        review_tp = fast_observed or best_observed
    else:
        label = "NO_REVIEW_TP"
        reason = "После входа не достигнута даже минимальная рабочая ступень 0.3%."
        review_tp = None

    return {
        "best_observed_tp_pct": _round6(best_observed),
        "fast_observed_tp_pct": _round6(fast_observed),
        "clean_review_tp_pct": _round6(review_tp),
        "clean_review_tp_basis_pct": _round6(clean_review),
        "clean_fast_tp_pct": _round6(clean_fast),
        "decision_label": label,
        "decision_reason": reason,
        "warning": "; ".join(warning_parts),
        "wrong_1pct_flag": bool(wrong_1),
        "noise_flag": bool(noise),
        "good_entry_wrong_tp_flag": bool(hit_0p3 and not noise and wrong_1),
        "short_risk_pct": _round6(short_risk),
        "long_power_pct": _round6(long_power),
    }


BASE_COLUMNS = [
    "record_id",
    "candidate_id",
    "day_utc",
    "anchor_time_utc",
    "anchor_low_price",
    "entry_time_utc",
    "entry_open_price",
    "entry_price_5bps",
    "entry_price_for_calc",
    "direction_scope",
    "long_only_flag",
    "short_context_only_flag",
    "wave_context_scope",
    "session_time_bucket_label",
    "effective_session_label",
    "entry_setup_quality_label",
    "entry_setup_quality_reason",
    "hour_background_phase",
    "hour_range_pct",
    "hour_path_pct",
    "hour_long_wave_up_from_low_pct",
    "hour_long_wave_phase",
    "hour_short_wave_down_from_high_pct",
    "hour_short_wave_phase",
    "hour_direction_bias",
    "macro_wave_segment_kind",
    "macro_wave_direction",
    "macro_wave_no",
    "macro_wave_move_pct",
    "macro_wave_visible_move_pct",
    "macro_wave_duration_min",
    "continuous_wave_direction",
    "continuous_wave_no",
    "continuous_wave_move_pct",
    "continuous_wave_duration_min",
    "stas1_volume_ratio20",
    "source_context",
]


PATH_COLUMNS = [
    "path_status",
    "future_bar_count",
    "hold_hours",
    "max_high_time_utc",
    "max_high_price",
    "max_mfe_pct",
    "min_low_time_utc",
    "min_low_price",
    "max_mae_pct",
]


DECISION_COLUMNS = [
    "best_observed_tp_pct",
    "fast_observed_tp_pct",
    "clean_review_tp_pct",
    "clean_review_tp_basis_pct",
    "clean_fast_tp_pct",
    "decision_label",
    "decision_reason",
    "warning",
    "wrong_1pct_flag",
    "noise_flag",
    "good_entry_wrong_tp_flag",
    "short_risk_pct",
    "long_power_pct",
]


def _hit_columns(ladder: list[float]) -> list[str]:
    cols: list[str] = []
    for pct in ladder:
        key = _pct_key(pct)
        cols.extend(
            [
                f"hit_{key}",
                f"time_to_{key}_min",
                f"target_{key}_price",
                f"hit_{key}_time_utc",
                f"drawdown_before_{key}_pct",
                f"clean_hit_{key}",
            ]
        )
    return cols


def _flatten_hit_map(hit_map: dict[float, dict[str, Any]], ladder: list[float]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for pct in ladder:
        key = _pct_key(pct)
        data = hit_map.get(pct, {})
        hit_ts = data.get("hit_time_utc")
        out[f"hit_{key}"] = bool(data.get("hit"))
        out[f"time_to_{key}_min"] = _round6(data.get("time_to_min"))
        out[f"target_{key}_price"] = _round6(data.get("target_price"))
        out[f"hit_{key}_time_utc"] = _fmt_ts(hit_ts) if hit_ts is not None else ""
        out[f"drawdown_before_{key}_pct"] = _round6(data.get("drawdown_before_hit_pct"))
        out[f"clean_hit_{key}"] = bool(data.get("clean_hit"))
    return out


def build_clean_rows(
    root: Path,
    *,
    stas2_run_dir: Path,
    start_day: str,
    end_day: str,
    symbol: str,
    timeframe: str,
    hold_hours: float,
    ladder: list[float],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    records = _read_csv_rows(stas2_run_dir / "STAS2_RECORDS.csv")
    hourly_rows = _read_csv_rows(stas2_run_dir / "STAS2_HOURLY_PHASES.csv")
    macro_rows = _read_csv_rows(stas2_run_dir / "STAS2_MACRO_WAVES.csv")
    continuous_rows = _read_csv_rows(stas2_run_dir / "STAS2_CONTINUOUS_WAVES.csv")
    extra_days = int(np.ceil(hold_hours / 24.0)) + 1
    candle_days = _day_range(start_day, end_day, extra_days=extra_days)
    candles, missing_candles = _load_ohlcv_range(root, candle_days, timeframe, symbol)
    days = set(_day_range(start_day, end_day))

    context_rows: list[dict[str, Any]] = []
    tp_path_rows: list[dict[str, Any]] = []
    decision_rows: list[dict[str, Any]] = []
    skipped_rows: list[dict[str, Any]] = []

    for record in records:
        day = str(record.get("day_utc", "")).strip()
        if day not in days:
            continue
        entry_ts = _parse_ts(record.get("entry_time_utc"))
        anchor_ts = _parse_ts(record.get("anchor_time_utc"))
        entry_price = _safe_float(record.get("entry_price_5bps"))
        if entry_ts is None or entry_price is None:
            skipped_rows.append(
                {
                    "record_id": record.get("record_id", ""),
                    "candidate_id": record.get("candidate_id", ""),
                    "day_utc": day,
                    "skip_reason": "missing_entry_time_or_entry_price_5bps",
                    "entry_time_utc": record.get("entry_time_utc", ""),
                    "entry_price_5bps": record.get("entry_price_5bps", ""),
                    "boundary": BOUNDARY,
                }
            )
            continue
        base = {
            "record_id": record.get("record_id", ""),
            "candidate_id": record.get("candidate_id", ""),
            "day_utc": day,
            "anchor_time_utc": _fmt_ts(anchor_ts),
            "anchor_low_price": record.get("anchor_low_price", ""),
            "entry_time_utc": _fmt_ts(entry_ts),
            "entry_open_price": record.get("entry_open_price", ""),
            "entry_price_5bps": record.get("entry_price_5bps", ""),
            "entry_price_for_calc": _round6(entry_price),
        }
        context = _context_for_entry(record, entry_ts, hourly_rows, macro_rows, continuous_rows)
        context_row = {**base, **context, "boundary": BOUNDARY}
        path, hit_map = _analyze_path(candles, entry_ts, entry_price, hold_hours, ladder)
        if path.get("path_status") != "OK":
            skipped_rows.append(
                {
                    **base,
                    "skip_reason": path.get("path_status", "path_error"),
                    "future_bar_count": path.get("future_bar_count", 0),
                    "boundary": BOUNDARY,
                }
            )
            continue
        hit_fields = _flatten_hit_map(hit_map, ladder)
        decision = _decision_fields(hit_map, path, context)
        context_rows.append(context_row)
        tp_path_rows.append({**context_row, **path, **hit_fields})
        decision_rows.append({**context_row, **path, **decision})
    return context_rows, tp_path_rows, decision_rows, skipped_rows, missing_candles


def _group_ladder_rows(decision_rows: list[dict[str, Any]], tp_path_rows: list[dict[str, Any]], ladder: list[float]) -> list[dict[str, Any]]:
    path_by_record = {str(r.get("record_id")): r for r in tp_path_rows}
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in decision_rows:
        specs = [
            ("hour_background_phase", row.get("hour_background_phase", "")),
            ("hour_long_wave_phase", row.get("hour_long_wave_phase", "")),
            ("hour_short_wave_phase", row.get("hour_short_wave_phase", "")),
            ("effective_session", row.get("effective_session_label", "")),
            ("setup_quality", row.get("entry_setup_quality_label", "")),
            ("macro_wave_direction", row.get("macro_wave_direction", "")),
            ("continuous_wave_direction", row.get("continuous_wave_direction", "")),
        ]
        for group_type, value in specs:
            value_text = str(value or "").strip()
            if value_text:
                groups[(group_type, value_text)].append(row)

    out: list[dict[str, Any]] = []
    for (group_type, value), rows in sorted(groups.items()):
        if len(rows) < 3:
            continue
        best_60: float | None = None
        clean_50: float | None = None
        fast_50: float | None = None
        for pct in ladder:
            key = _pct_key(pct)
            hit_count = 0
            clean_count = 0
            fast_count = 0
            for row in rows:
                path = path_by_record.get(str(row.get("record_id")), {})
                if str(path.get(f"hit_{key}", "")).lower() == "true":
                    hit_count += 1
                if str(path.get(f"clean_hit_{key}", "")).lower() == "true":
                    clean_count += 1
                minutes = _safe_float(path.get(f"time_to_{key}_min"))
                if str(path.get(f"hit_{key}", "")).lower() == "true" and minutes is not None and minutes <= 120:
                    fast_count += 1
            hit_rate = hit_count / len(rows)
            clean_rate = clean_count / len(rows)
            fast_rate = fast_count / len(rows)
            if hit_rate >= 0.60:
                best_60 = pct
            if clean_rate >= 0.50:
                clean_50 = pct
            if fast_rate >= 0.50:
                fast_50 = pct
        mfes = [_safe_float(r.get("max_mfe_pct"), 0.0) or 0.0 for r in rows]
        maes = [_safe_float(r.get("max_mae_pct"), 0.0) or 0.0 for r in rows]
        out.append(
            {
                "group_type": group_type,
                "group_value": value,
                "sample_count": len(rows),
                "tp_hit_rate_60pct": _round6(best_60),
                "tp_clean_rate_50pct": _round6(clean_50),
                "tp_fast_rate_50pct": _round6(fast_50),
                "median_mfe_pct": _round6(float(np.median(mfes)) if mfes else None),
                "median_mae_pct": _round6(float(np.median(maes)) if maes else None),
                "noise_count": sum(1 for r in rows if str(r.get("noise_flag")).lower() == "true"),
                "wrong_1pct_count": sum(1 for r in rows if str(r.get("wrong_1pct_flag")).lower() == "true"),
                "boundary": BOUNDARY,
            }
        )
    return out


def _color_for_pct(value: Any, *, invert: bool = False) -> str:
    pct = _safe_float(value, 0.0) or 0.0
    if pct >= 2.0:
        color = "#d4f04a"
    elif pct >= 1.0:
        color = "#22c06a"
    elif pct >= 0.6:
        color = "#2a9d8f"
    elif pct >= 0.3:
        color = "#2c7da0"
    else:
        color = "#264653"
    if invert and pct >= 1.0:
        color = "#d95f5f"
    return color


def _draw_context_rows(ax: Any, day: str, hourly_rows: list[dict[str, str]]) -> None:
    rows = [r for r in hourly_rows if r.get("day_utc") == day]
    ax.set_ylim(0, 3)
    ax.set_yticks([0.5, 1.5, 2.5])
    ax.set_yticklabels(["SHORT-risk", "LONG", "Фон"], color="#c8d2d8", fontsize=7)
    ax.tick_params(axis="x", labelbottom=False)
    _style_axis(ax)
    for row in rows:
        start = _parse_ts(row.get("hour_start_utc"))
        if start is None:
            continue
        end = start + pd.Timedelta(hours=1)
        x0 = mdates.date2num(start.tz_convert(None))
        x1 = mdates.date2num(end.tz_convert(None))
        width = x1 - x0
        bg = row.get("hour_background_phase", "")
        long_pct = row.get("hour_long_wave_up_from_low_pct", "")
        short_pct = row.get("hour_short_wave_down_from_high_pct", "")
        items = [
            (2, _color_for_pct(row.get("hour_range_pct")), f"{bg}\n{row.get('hour_range_pct','')}%"),
            (1, _color_for_pct(long_pct), f"L {long_pct}%"),
            (0, _color_for_pct(short_pct, invert=True), f"S {short_pct}%"),
        ]
        for y, color, label in items:
            ax.add_patch(Rectangle((x0, y), width, 0.95, facecolor=color, edgecolor="#121b20", linewidth=0.45, alpha=0.92))
            if width > 0.025:
                ax.text(x0 + width / 2, y + 0.47, label, ha="center", va="center", color="#061014", fontsize=5.4, fontweight="bold")


def _draw_wave_row(ax: Any, day: str, macro_rows: list[dict[str, str]]) -> None:
    rows = [r for r in macro_rows if r.get("day_utc") == day]
    ax.set_ylim(0, 1)
    ax.set_yticks([0.5])
    ax.set_yticklabels(["WAVE"], color="#c8d2d8", fontsize=7)
    ax.tick_params(axis="x", labelbottom=False)
    _style_axis(ax)
    for row in rows:
        start = _parse_ts(row.get("macro_wave_start_time_utc"))
        end = _parse_ts(row.get("macro_wave_end_time_utc"))
        if start is None or end is None:
            continue
        x0 = mdates.date2num(start.tz_convert(None))
        x1 = mdates.date2num(end.tz_convert(None))
        width = max(x1 - x0, 0.0005)
        direction = row.get("macro_wave_direction", "")
        if direction == "LONG":
            color = "#22c06a"
        elif direction == "SHORT":
            color = "#df6b4f"
        else:
            color = "#646b75"
        label = f"{row.get('macro_wave_no','')} {direction}\n{row.get('macro_wave_visible_move_pct') or row.get('macro_wave_move_pct','')}%"
        ax.add_patch(Rectangle((x0, 0), width, 0.95, facecolor=color, edgecolor="#121b20", linewidth=0.45, alpha=0.9))
        if width > 0.03:
            ax.text(x0 + width / 2, 0.48, label, ha="center", va="center", color="#071014", fontsize=5.3, fontweight="bold")


def _draw_day_overview(
    out_path: Path,
    day: str,
    day_candles: pd.DataFrame,
    day_rows: list[dict[str, Any]],
    hourly_rows: list[dict[str, str]],
    macro_rows: list[dict[str, str]],
    timeframe: str,
) -> None:
    fig, axes = plt.subplots(
        4,
        1,
        figsize=(19, 10),
        gridspec_kw={"height_ratios": [7, 1.4, 0.9, 1.6], "hspace": 0.04},
        sharex=True,
    )
    ax_price, ax_ctx, ax_wave, ax_vol = axes
    fig.patch.set_facecolor("#071014")
    _style_axis(ax_price)
    _draw_candles(ax_price, day_candles, timeframe)
    ax_price.set_title(
        f"STAS3 V2 CLEAN {day} | LONG entries from STAS2 | entry_price_5bps -> TP ladder | NO OLD STAS3",
        color="#e6eef2",
        fontsize=11,
    )
    ax_price.set_ylabel("Price", color="#c8d2d8", fontsize=8)
    for row in day_rows:
        entry_ts = _parse_ts(row.get("entry_time_utc"))
        entry_price = _safe_float(row.get("entry_price_for_calc"))
        if entry_ts is None or entry_price is None:
            continue
        x = mdates.date2num(entry_ts.tz_convert(None))
        noise = str(row.get("noise_flag")).lower() == "true"
        color = "#ff6b6b" if noise else "#44e5a4"
        ax_price.scatter([entry_ts.tz_convert(None)], [entry_price], marker="^", s=18, color=color, edgecolor="#071014", linewidth=0.3, zorder=5)
        tp = _safe_float(row.get("clean_review_tp_pct"))
        if tp is not None and tp > 0:
            target = entry_price * (1.0 + tp / 100.0)
            hit_ts = None
            key = _pct_key(round(tp, 1))
            # clean decision pct always belongs to the ladder, so this field exists in the path row after merge.
            hit_ts = _parse_ts(row.get(f"hit_{key}_time_utc"))
            x_end = mdates.date2num((hit_ts or (entry_ts + pd.Timedelta(minutes=60))).tz_convert(None))
            ax_price.hlines(target, x, x_end, colors="#f6c945", linewidth=0.65, alpha=0.65)
    if not day_candles.empty:
        ax_price.set_xlim(day_candles["open_time_utc"].min().tz_convert(None), day_candles["open_time_utc"].max().tz_convert(None))
    _draw_context_rows(ax_ctx, day, hourly_rows)
    _draw_wave_row(ax_wave, day, macro_rows)
    _style_axis(ax_vol)
    if not day_candles.empty:
        colors = np.where(day_candles["close"] >= day_candles["open"], "#1aa99a", "#d95f5f")
        ax_vol.bar(day_candles["open_time_utc"].dt.tz_convert(None), day_candles["volume"], width=_bar_width_days(timeframe), color=colors, alpha=0.65)
    ax_vol.set_ylabel("Volume", color="#c8d2d8", fontsize=8)
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.subplots_adjust(left=0.045, right=0.995, top=0.94, bottom=0.06)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def _draw_entry_pages(
    out_dir: Path,
    rows: list[dict[str, Any]],
    candles: pd.DataFrame,
    *,
    timeframe: str,
    prefix: str,
    title_suffix: str,
    max_pages: int | None = None,
) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    per_page = 6
    pages = [rows[i : i + per_page] for i in range(0, len(rows), per_page)]
    if max_pages is not None:
        pages = pages[:max_pages]
    for page_no, chunk in enumerate(pages, start=1):
        fig, axes = plt.subplots(3, 2, figsize=(18, 12), sharex=False)
        fig.patch.set_facecolor("#071014")
        flat = axes.ravel()
        for ax, row in zip(flat, chunk):
            _style_axis(ax)
            entry_ts = _parse_ts(row.get("entry_time_utc"))
            entry_price = _safe_float(row.get("entry_price_for_calc"))
            if entry_ts is None or entry_price is None:
                ax.axis("off")
                continue
            best_time = _parse_ts(row.get("max_high_time_utc"))
            minutes_to_best = 0.0
            if best_time is not None:
                minutes_to_best = max(0.0, (best_time - entry_ts).total_seconds() / 60.0)
            window_min = min(1440.0, max(360.0, minutes_to_best + 90.0))
            end_ts = entry_ts + pd.Timedelta(minutes=window_min)
            sub = candles[(candles["open_time_utc"] >= entry_ts - pd.Timedelta(minutes=15)) & (candles["open_time_utc"] <= end_ts)]
            if not sub.empty:
                x = sub["open_time_utc"].dt.tz_convert(None)
                ax.fill_between(x, sub["low"].to_numpy(), sub["high"].to_numpy(), color="#24404a", alpha=0.35, linewidth=0)
                ax.plot(x, sub["close"].to_numpy(), color="#d8e4e8", linewidth=0.75, alpha=0.95)
            ax.axhline(entry_price, color="#8fd3ff", linewidth=0.75, alpha=0.9)
            ax.axvline(entry_ts.tz_convert(None), color="#8fd3ff", linewidth=0.75, alpha=0.9)
            levels = [0.3, 0.5, 1.0]
            tp = _safe_float(row.get("clean_review_tp_pct"))
            best = _safe_float(row.get("best_observed_tp_pct"))
            for val in [tp, best, 2.0, 3.0]:
                if val is not None and val > 0 and val not in levels:
                    levels.append(round(val, 1))
            for val in sorted(set(levels)):
                target = entry_price * (1.0 + val / 100.0)
                color = "#f6c945" if tp is not None and round(val, 1) == round(tp, 1) else "#75848d"
                ax.axhline(target, color=color, linewidth=0.65, linestyle="--", alpha=0.75)
                ax.text(0.995, target, f"{val:.1f}%", transform=ax.get_yaxis_transform(), ha="right", va="bottom", color=color, fontsize=6.4)
            max_high = _safe_float(row.get("max_high_price"))
            min_low = _safe_float(row.get("min_low_price"))
            max_ts = _parse_ts(row.get("max_high_time_utc"))
            min_ts = _parse_ts(row.get("min_low_time_utc"))
            if max_ts is not None and max_high is not None:
                ax.scatter([max_ts.tz_convert(None)], [max_high], marker="*", s=44, color="#b7ff4a", edgecolor="#071014", linewidth=0.3, zorder=6)
            if min_ts is not None and min_low is not None:
                ax.scatter([min_ts.tz_convert(None)], [min_low], marker="v", s=28, color="#ff6b6b", edgecolor="#071014", linewidth=0.3, zorder=6)
            title = (
                f"{row.get('candidate_id','')} {row.get('entry_time_utc','')} | entry {entry_price:.4f}\n"
                f"TPclean {row.get('clean_review_tp_pct','')} | max {row.get('best_observed_tp_pct','')} | "
                f"L {row.get('hour_long_wave_up_from_low_pct','')}% / S-risk {row.get('hour_short_wave_down_from_high_pct','')}%"
            )
            ax.set_title(title, color="#e6eef2", fontsize=7)
            box = (
                f"{row.get('decision_label','')}\n"
                f"{row.get('hour_background_phase','')} | {row.get('macro_wave_direction','')}/{row.get('macro_wave_segment_kind','')}\n"
                f"{row.get('warning','')}"
            )
            ax.text(0.01, 0.98, box, transform=ax.transAxes, ha="left", va="top", color="#d8e4e8", fontsize=6.2, bbox={"facecolor": "#071014", "alpha": 0.72, "edgecolor": "#31414b", "linewidth": 0.4})
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
        for ax in flat[len(chunk) :]:
            ax.axis("off")
        fig.suptitle(f"STAS3 V2 CLEAN | {title_suffix} | page {page_no:02d}", color="#e6eef2", fontsize=12)
        fig.subplots_adjust(left=0.04, right=0.995, top=0.93, bottom=0.055, hspace=0.36, wspace=0.13)
        out_path = out_dir / f"{prefix}_{page_no:02d}.png"
        fig.savefig(out_path, dpi=145)
        plt.close(fig)
        paths.append(out_path.as_posix())
    return paths


def _write_report(
    path: Path,
    *,
    run_dir: Path,
    stas2_run_dir: Path,
    summary: dict[str, Any],
    artifacts: dict[str, str],
) -> None:
    text = f"""# STAS3 V2 CLEAN REPORT

Статус: `{STATUS}`.

Это чистый перезапуск Stas3 V2. Старый Stas3-файл и старые Stas3-таблицы не использовались как основа.

## Источник

- Stas2 run: `{stas2_run_dir.as_posix()}`
- Дни: `{', '.join(WORK_DAYS)}`
- Направление: только `LONG`
- Цена расчета входа: только `entry_price_5bps`
- `SHORT`: только risk-context, не сделка
- `WAVE/GAP/continuous`: hindsight-review контекст, не live-признак

## Сводка

- Входов из Stas2: `{summary['stas2_rows_input']}`
- Обработано: `{summary['processed_rows']}`
- Skipped: `{summary['skipped_rows']}`
- Noise: `{summary['noise_rows']}`
- Good entry but wrong 1% TP: `{summary['good_entry_wrong_1pct_rows']}`
- Wrong 1% TP всего: `{summary['wrong_1pct_rows']}`
- Hit 1%: `{summary['hit_1pct_rows']}`
- Clean medium TP `>=1%`: `{summary['clean_medium_rows']}`
- PNG: `{summary['png_count']}`
- Пустые PNG: `{summary['empty_png_count']}`

## Артефакты

- Entry context: `{artifacts['entry_context_csv']}`
- TP path: `{artifacts['tp_path_csv']}`
- TP decision: `{artifacts['tp_decision_csv']}`
- Phase ladder: `{artifacts['phase_ladder_csv']}`
- Wrong TP: `{artifacts['wrong_tp_csv']}`
- Noise: `{artifacts['noise_csv']}`
- Workbook: `{artifacts['xlsx']}`
- Browse by day: `{artifacts['browse_by_day']}`

## Граница

`clean_review_tp_pct` - это review-кандидат, а не команда на live-выход. Он показывает, какой TP был достижим по факту с учетом времени и просадки. Нельзя использовать его как scorer, target-lock, ML-label или торговую стратегию без отдельной причинной разметки.

`MFE/MAX` не является take profit. Это только факт максимального хода после входа.

ML/export/training, Optuna, scorer, target-lock и API не запускались.
"""
    path.write_text(text, encoding="utf-8")


def run_clean_review(
    *,
    root: Path,
    stas2_run_dir: Path,
    start_day: str,
    end_day: str,
    run_label: str,
    symbol: str,
    timeframe: str,
    hold_hours: float,
) -> Path:
    ladder = PERCENT_LADDER
    run_dir = root / "STAS3_PERCENT_LADDER_REVIEW" / "runs" / f"{run_label}_{_run_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=True)
    browse_dir = run_dir / "BROWSE_BY_DAY"
    plot_dir = run_dir / "ENTRY_PAGES"
    medium_dir = run_dir / "MEDIUM_1PCT_PLUS_PAGES"

    context_rows, tp_path_rows, decision_rows, skipped_rows, missing_candles = build_clean_rows(
        root,
        stas2_run_dir=stas2_run_dir,
        start_day=start_day,
        end_day=end_day,
        symbol=symbol,
        timeframe=timeframe,
        hold_hours=hold_hours,
        ladder=ladder,
    )
    path_by_record = {str(r.get("record_id")): r for r in tp_path_rows}
    decision_plus_path = [{**path_by_record.get(str(r.get("record_id")), {}), **r} for r in decision_rows]
    wrong_tp_rows = [r for r in decision_plus_path if str(r.get("wrong_1pct_flag")).lower() == "true"]
    noise_rows = [r for r in decision_plus_path if str(r.get("noise_flag")).lower() == "true"]
    phase_ladder_rows = _group_ladder_rows(decision_rows, tp_path_rows, ladder)

    entry_context_csv = run_dir / "STAS3_V2_CLEAN_ENTRY_CONTEXT.csv"
    tp_path_csv = run_dir / "STAS3_V2_CLEAN_TP_PATH.csv"
    tp_decision_csv = run_dir / "STAS3_V2_CLEAN_TP_DECISION.csv"
    phase_ladder_csv = run_dir / "STAS3_V2_CLEAN_PHASE_LADDER.csv"
    wrong_tp_csv = run_dir / "STAS3_V2_CLEAN_WRONG_TP.csv"
    noise_csv = run_dir / "STAS3_V2_CLEAN_NOISE.csv"
    skipped_csv = run_dir / "STAS3_V2_CLEAN_SKIPPED_ROWS.csv"
    xlsx_path = run_dir / "STAS3_V2_CLEAN_TABLES.xlsx"
    report_path = run_dir / "STAS3_V2_CLEAN_REPORT_RU.md"
    payload_path = run_dir / "STAS3_V2_CLEAN_PAYLOAD.json"

    _write_csv(entry_context_csv, context_rows, BASE_COLUMNS + ["boundary"])
    _write_csv(tp_path_csv, tp_path_rows, BASE_COLUMNS + PATH_COLUMNS + _hit_columns(ladder) + ["boundary"])
    _write_csv(tp_decision_csv, decision_rows, BASE_COLUMNS + PATH_COLUMNS + DECISION_COLUMNS + ["boundary"])
    _write_csv(phase_ladder_csv, phase_ladder_rows)
    _write_csv(wrong_tp_csv, wrong_tp_rows)
    _write_csv(noise_csv, noise_rows)
    _write_csv(skipped_csv, skipped_rows)

    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        pd.DataFrame(context_rows).to_excel(writer, index=False, sheet_name="Clean Entry Context")
        pd.DataFrame(tp_path_rows).to_excel(writer, index=False, sheet_name="Clean TP Path")
        pd.DataFrame(decision_rows).to_excel(writer, index=False, sheet_name="Clean TP Decision")
        pd.DataFrame(phase_ladder_rows).to_excel(writer, index=False, sheet_name="Clean Phase Ladder")
        pd.DataFrame(wrong_tp_rows).to_excel(writer, index=False, sheet_name="Clean Wrong TP")
        pd.DataFrame(noise_rows).to_excel(writer, index=False, sheet_name="Clean Noise")
        pd.DataFrame(skipped_rows).to_excel(writer, index=False, sheet_name="Clean Skipped")

    extra_days = int(np.ceil(hold_hours / 24.0)) + 1
    candles, _ = _load_ohlcv_range(root, _day_range(start_day, end_day, extra_days=extra_days), timeframe, symbol)
    hourly_rows = _read_csv_rows(stas2_run_dir / "STAS2_HOURLY_PHASES.csv")
    macro_rows = _read_csv_rows(stas2_run_dir / "STAS2_MACRO_WAVES.csv")
    png_paths: list[str] = []
    for day in _day_range(start_day, end_day):
        day_dir = browse_dir / day
        day_dir.mkdir(parents=True, exist_ok=True)
        start = pd.Timestamp(f"{day}T00:00:00Z")
        end = start + pd.Timedelta(days=1)
        day_candles = candles[(candles["open_time_utc"] >= start) & (candles["open_time_utc"] < end)]
        day_rows = [r for r in decision_plus_path if r.get("day_utc") == day]
        _write_csv(day_dir / f"{day.replace('-', '')}_STAS3_V2_CLEAN_DECISION.csv", day_rows)
        day_png = day_dir / f"STAS3_V2_CLEAN_DAY_OVERVIEW_{day.replace('-', '')}.png"
        _draw_day_overview(day_png, day, day_candles, day_rows, hourly_rows, macro_rows, timeframe)
        png_paths.append(day_png.as_posix())

    png_paths.extend(_draw_entry_pages(plot_dir, decision_plus_path, candles, timeframe=timeframe, prefix="STAS3_V2_CLEAN_ENTRY_PAGE", title_suffix="all LONG entries"))
    medium_rows = [r for r in decision_plus_path if (_safe_float(r.get("best_observed_tp_pct"), 0.0) or 0.0) >= 1.0]
    png_paths.extend(_draw_entry_pages(medium_dir, medium_rows, candles, timeframe=timeframe, prefix="STAS3_V2_CLEAN_MEDIUM_1PCT_PLUS_PAGE", title_suffix="1pct+ observed moves"))
    empty_png = [p for p in png_paths if Path(p).exists() and Path(p).stat().st_size <= 1024]

    hit_1_rows = [r for r in decision_plus_path if str(r.get("hit_1p0", "")).lower() == "true"]
    clean_medium_rows = [r for r in decision_plus_path if (_safe_float(r.get("clean_review_tp_pct"), 0.0) or 0.0) >= 1.0 and str(r.get("noise_flag")).lower() != "true"]
    stas2_rows_input = len([r for r in _read_csv_rows(stas2_run_dir / "STAS2_RECORDS.csv") if r.get("day_utc") in set(_day_range(start_day, end_day))])
    summary = {
        "stas2_rows_input": stas2_rows_input,
        "processed_rows": len(decision_rows),
        "skipped_rows": len(skipped_rows),
        "row_count_parity_ok": stas2_rows_input == len(decision_rows) + len(skipped_rows),
        "noise_rows": len(noise_rows),
        "wrong_1pct_rows": len(wrong_tp_rows),
        "good_entry_wrong_1pct_rows": sum(1 for r in decision_rows if str(r.get("good_entry_wrong_tp_flag")).lower() == "true"),
        "hit_1pct_rows": len(hit_1_rows),
        "clean_medium_rows": len(clean_medium_rows),
        "phase_ladder_rows": len(phase_ladder_rows),
        "png_count": len(png_paths),
        "empty_png_count": len(empty_png),
        "missing_candle_sources": len(missing_candles),
    }
    artifacts = {
        "entry_context_csv": _rel(root, entry_context_csv),
        "tp_path_csv": _rel(root, tp_path_csv),
        "tp_decision_csv": _rel(root, tp_decision_csv),
        "phase_ladder_csv": _rel(root, phase_ladder_csv),
        "wrong_tp_csv": _rel(root, wrong_tp_csv),
        "noise_csv": _rel(root, noise_csv),
        "skipped_csv": _rel(root, skipped_csv),
        "xlsx": _rel(root, xlsx_path),
        "report": _rel(root, report_path),
        "payload": _rel(root, payload_path),
        "browse_by_day": _rel(root, browse_dir),
        "entry_pages": _rel(root, plot_dir),
        "medium_pages": _rel(root, medium_dir),
    }
    _write_report(report_path, run_dir=run_dir, stas2_run_dir=stas2_run_dir, summary=summary, artifacts=artifacts)
    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "run_dir": _rel(root, run_dir),
        "source_stas2_run": _rel(root, stas2_run_dir),
        "work_days": _day_range(start_day, end_day),
        "symbol": symbol,
        "timeframe": timeframe,
        "hold_hours": hold_hours,
        "percent_ladder": ladder,
        "summary": summary,
        "artifacts": artifacts,
        "missing_candles": missing_candles,
        "guardrails": [
            "NO_OLD_STAS3_BASE",
            "LONG_ONLY",
            "ENTRY_PRICE_FOR_CALC_EQUALS_ENTRY_PRICE_5BPS",
            "SHORT_RISK_CONTEXT_ONLY",
            "WAVE_GAP_CONTINUOUS_ARE_HINDSIGHT_REVIEW",
            "NO_ML",
            "NO_OPTUNA",
            "NO_API",
            "NO_SCORER",
            "NO_TARGET_LOCK",
        ],
        "boundary": BOUNDARY,
    }
    payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return run_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Clean Stas3 V2 review from Stas2 tables only.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--stas2-run-dir", default=DEFAULT_STAS2_RUN)
    parser.add_argument("--start-day", default="2026-05-10")
    parser.add_argument("--end-day", default="2026-05-12")
    parser.add_argument("--run-label", default="stas3_v2_clean_20260510_20260512_long_only")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--hold-hours", type=float, default=48.0)
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    stas2_run_dir = Path(args.stas2_run_dir)
    if not stas2_run_dir.is_absolute():
        stas2_run_dir = root / stas2_run_dir
    run_dir = run_clean_review(
        root=root,
        stas2_run_dir=stas2_run_dir,
        start_day=args.start_day,
        end_day=args.end_day,
        run_label=args.run_label,
        symbol=args.symbol,
        timeframe=args.timeframe,
        hold_hours=args.hold_hours,
    )
    print(json.dumps({"status": STATUS, "run_dir": _rel(root, run_dir)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
