from __future__ import annotations

import argparse
import csv
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from mlbotnav.visual_entry_low_anchor_suggester import _bar_width_days, _draw_candles, _load_ohlcv, _source_csv, _style_axis
from mlbotnav.visual_entry_stas2_market_phase_review import (
    OVERVIEW_COMBO_HEIGHT_RATIOS,
    OVERVIEW_HEIGHT_RATIOS,
    _render_macro_wave_strip,
    _render_rank_strip,
    _safe_float,
    _set_day_time_axis,
    _shade_sessions,
)
from mlbotnav.visual_entry_strategy_passport_overlay_v2b import _density_window_features
from mlbotnav.visual_entry_strategy_passport_overlay_v2a import (
    _add_closed_bar_features,
    _breakout_retest_state,
    _channel_state,
    _fib_state,
    _last_structure_event,
    _nearest_levels,
    _raw_pivots,
)
from mlbotnav.visual_entry_strategy_passport_overlay_v2d_patterns import _add_pattern_features


STATUS = "STAS4_FAMILY_OVERLAY_V0_REVIEW_ONLY_NO_ML_NO_OPTUNA"
SYMBOL = "SOLUSDT"
TIMEFRAME = "1m"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(root: Path, path: Path) -> str:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    try:
        return str(resolved_path.relative_to(resolved_root)).replace("\\", "/")
    except ValueError:
        return str(resolved_path).replace("\\", "/")


def _fmt_ts(value: pd.Timestamp) -> str:
    return value.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_csv_dicts(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _add_price_volatility_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for n in [1, 3, 6, 12, 24]:
        out[f"F{n:03d}_ret_{n}"] = out["close"].pct_change(n) * 100.0
    out["F006_hl_spread"] = (out["high"] - out["low"]) / out["open"].replace(0, np.nan) * 100.0
    out["ret_1m_for_std"] = out["close"].pct_change() * 100.0
    out["F007_rolling_std20"] = out["ret_1m_for_std"].rolling(20, min_periods=5).std()
    prev_close = out["close"].shift(1)
    tr = pd.concat(
        [
            out["high"] - out["low"],
            (out["high"] - prev_close).abs(),
            (out["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    out["F008_atr14"] = tr.ewm(alpha=1 / 14, adjust=False, min_periods=5).mean() / out["close"].replace(0, np.nan) * 100.0
    out["rolling_low_20"] = out["low"].rolling(20, min_periods=1).min()
    out["rolling_high_20"] = out["high"].rolling(20, min_periods=1).max()
    denom = (out["rolling_high_20"] - out["rolling_low_20"]).replace(0, np.nan)
    out["range_pos_20"] = (out["close"] - out["rolling_low_20"]) / denom
    out["reclaim_from_low_bps"] = (out["close"] - out["low"]) / out["close"].replace(0, np.nan) * 10000.0
    return out


def _add_trend_momentum_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ema20"] = out["close"].ewm(span=20, adjust=False).mean()
    out["ema50"] = out["close"].ewm(span=50, adjust=False).mean()
    out["ema200"] = out["close"].ewm(span=200, adjust=False).mean()
    out["F009_ema_gap"] = (out["ema20"] - out["ema50"]) / out["close"].replace(0, np.nan) * 100.0
    out["F010_ema20_slope_5"] = (out["ema20"] / out["ema20"].shift(5).replace(0, np.nan) - 1.0) * 100.0
    out["F011_ema200_gap"] = (out["close"] - out["ema200"]) / out["close"].replace(0, np.nan) * 100.0

    delta = out["close"].diff()
    gain = delta.clip(lower=0).rolling(14, min_periods=1).mean()
    loss = (-delta.clip(upper=0)).rolling(14, min_periods=1).mean()
    rs = gain / loss.replace(0, np.nan)
    out["F012_rsi14"] = 100.0 - (100.0 / (1.0 + rs))

    ema12 = out["close"].ewm(span=12, adjust=False).mean()
    ema26 = out["close"].ewm(span=26, adjust=False).mean()
    out["F013_macd_line"] = ema12 - ema26
    out["F014_macd_signal"] = out["F013_macd_line"].ewm(span=9, adjust=False).mean()
    out["F015_macd_hist"] = out["F013_macd_line"] - out["F014_macd_signal"]
    out["F015_macd_hist_delta"] = out["F015_macd_hist"].diff()

    up_move = out["high"].diff()
    down_move = -out["low"].diff()
    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=out.index)
    minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=out.index)
    prev_close = out["close"].shift(1)
    tr = pd.concat(
        [
            out["high"] - out["low"],
            (out["high"] - prev_close).abs(),
            (out["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr = tr.ewm(alpha=1 / 14, adjust=False, min_periods=5).mean()
    plus_di = 100.0 * plus_dm.ewm(alpha=1 / 14, adjust=False, min_periods=5).mean() / atr.replace(0, np.nan)
    minus_di = 100.0 * minus_dm.ewm(alpha=1 / 14, adjust=False, min_periods=5).mean() / atr.replace(0, np.nan)
    dx = ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)) * 100.0
    out["F016_adx14"] = dx.ewm(alpha=1 / 14, adjust=False, min_periods=5).mean()

    low14 = out["low"].rolling(14, min_periods=5).min()
    high14 = out["high"].rolling(14, min_periods=5).max()
    out["F017_stoch_k14"] = (out["close"] - low14) / (high14 - low14).replace(0, np.nan) * 100.0
    out["F018_stoch_d14"] = out["F017_stoch_k14"].rolling(3, min_periods=1).mean()
    return out


def _add_volume_flow_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    vol_ma20 = out["volume"].rolling(20, min_periods=5).mean()
    vol_std20 = out["volume"].rolling(20, min_periods=5).std()
    out["F019_vol_chg"] = out["volume"].pct_change() * 100.0
    out["F020_vol_z20"] = (out["volume"] - vol_ma20) / vol_std20.replace(0, np.nan)
    body_dir = np.sign(out["close"] - out["open"])
    out["F021_delta_volume"] = out["volume"] * body_dir
    obv_step = np.sign(out["close"].diff()).fillna(0.0) * out["volume"]
    out["obv"] = obv_step.cumsum()
    out["F022_obv_slope5"] = out["obv"] - out["obv"].shift(5)
    typical = (out["high"] + out["low"] + out["close"]) / 3.0
    raw_money = typical * out["volume"]
    positive_flow = raw_money.where(typical > typical.shift(1), 0.0).rolling(14, min_periods=5).sum()
    negative_flow = raw_money.where(typical < typical.shift(1), 0.0).rolling(14, min_periods=5).sum()
    money_ratio = positive_flow / negative_flow.replace(0, np.nan)
    out["F023_mfi14"] = 100.0 - (100.0 / (1.0 + money_ratio))
    cumulative_pv = (typical * out["volume"]).cumsum()
    cumulative_vol = out["volume"].cumsum().replace(0, np.nan)
    out["vwap"] = cumulative_pv / cumulative_vol
    out["F024_vwap_distance"] = (out["close"] - out["vwap"]) / out["close"].replace(0, np.nan) * 100.0
    out["rolling_low_20"] = out["low"].rolling(20, min_periods=1).min()
    out["rolling_high_20"] = out["high"].rolling(20, min_periods=1).max()
    denom = (out["rolling_high_20"] - out["rolling_low_20"]).replace(0, np.nan)
    out["range_pos_20"] = (out["close"] - out["rolling_low_20"]) / denom
    return out


def _add_density_profile_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    typical = ((out["high"] + out["low"] + out["close"]) / 3.0).to_numpy(dtype=float)
    volume = out["volume"].to_numpy(dtype=float)
    close = out["close"].to_numpy(dtype=float)
    rows: list[dict[str, float | None]] = []
    for idx in range(len(out)):
        row: dict[str, float | None] = {}
        row.update(_density_window_features(typical, volume, close, idx, window=60))
        row.update(_density_window_features(typical, volume, close, idx, window=240))
        rows.append(row)
    dens = pd.DataFrame(rows)
    out = pd.concat([out.reset_index(drop=True), dens.reset_index(drop=True)], axis=1)
    out["F025_vpoc_distance_60"] = out["density_vpoc_distance_60_pct"]
    out["F026_bin_share_60"] = out["density_bin_share_60"]
    out["F027_cluster_share_60"] = out["density_cluster_share_60"]
    out["F028_vpoc_share_60"] = out["density_vpoc_share_60"]
    out["F029_vpoc_distance_240"] = out["density_vpoc_distance_240_pct"]
    out["F030_bin_share_240"] = out["density_bin_share_240"]
    out["F031_cluster_share_240"] = out["density_cluster_share_240"]
    out["F032_vpoc_share_240"] = out["density_vpoc_share_240"]
    out["F033_vpoc_drift_20"] = out["F025_vpoc_distance_60"] - out["F025_vpoc_distance_60"].shift(20)
    out["F034_cluster_ratio_60_240"] = out["F027_cluster_share_60"] / out["F031_cluster_share_240"].replace(0, np.nan)
    out["rolling_low_20"] = out["low"].rolling(20, min_periods=1).min()
    out["rolling_high_20"] = out["high"].rolling(20, min_periods=1).max()
    denom = (out["rolling_high_20"] - out["rolling_low_20"]).replace(0, np.nan)
    out["range_pos_20"] = (out["close"] - out["rolling_low_20"]) / denom
    return out


def _quantile(series: pd.Series, q: float, default: float) -> float:
    value = series.replace([np.inf, -np.inf], np.nan).dropna().quantile(q)
    if pd.isna(value):
        return default
    return float(value)


def _row_at_time(df: pd.DataFrame, time_utc: str) -> pd.Series | None:
    ts = pd.Timestamp(time_utc).tz_convert("UTC")
    matched = df.index[df["open_time_utc"] == ts].tolist()
    if not matched:
        return None
    return df.iloc[int(matched[0])]


def _idx_at_time(df: pd.DataFrame, time_utc: str) -> int | None:
    ts = pd.Timestamp(time_utc).tz_convert("UTC")
    matched = df.index[df["open_time_utc"] == ts].tolist()
    if not matched:
        return None
    return int(matched[0])


def _price_volatility_old_entry_marks(df: pd.DataFrame, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    q = {
        "hl_p85": _quantile(df["F006_hl_spread"], 0.85, 0.0),
        "std_p85": _quantile(df["F007_rolling_std20"], 0.85, 0.0),
        "atr_p85": _quantile(df["F008_atr14"], 0.85, 0.0),
        "ret3_p90": _quantile(df["F003_ret_3"].abs(), 0.90, 0.0),
        "ret6_p90": _quantile(df["F006_ret_6"].abs(), 0.90, 0.0),
    }
    marks: list[dict[str, Any]] = []
    for row in rows:
        signal_time = row.get("anchor_time_utc") or row.get("entry_time_utc") or ""
        feature_row = _row_at_time(df, signal_time)
        if feature_row is None:
            continue
        votes: list[str] = []
        if _safe_float(feature_row.get("F006_hl_spread")) >= q["hl_p85"]:
            votes.append("B002/F006 high HL spread")
        if _safe_float(feature_row.get("F007_rolling_std20")) >= q["std_p85"]:
            votes.append("B003/F007 high rolling std")
        if _safe_float(feature_row.get("F008_atr14")) >= q["atr_p85"]:
            votes.append("B004/F008 high ATR")
        if abs(_safe_float(feature_row.get("F003_ret_3"))) >= q["ret3_p90"]:
            votes.append("B001/F002 strong ret_3")
        if abs(_safe_float(feature_row.get("F006_ret_6"))) >= q["ret6_p90"]:
            votes.append("B001/F003 strong ret_6")
        risk_flags = str(row.get("stas1_risk_flags") or "")
        setup_rank = int(_safe_float(row.get("entry_setup_quality_rank"), 99))
        if len(votes) >= 2 or ("wide_signal_range" in risk_flags and votes) or (setup_rank <= 1 and votes):
            marks.append(
                {
                    "kind": "old_removed_candidate",
                    "candidate_id": row.get("candidate_id") or "",
                    "record_id": row.get("record_id") or "",
                    "signal_time_utc": signal_time,
                    "entry_time_utc": row.get("entry_time_utc") or "",
                    "entry_open_price": _safe_float(row.get("entry_open_price")),
                    "source": "price_volatility:B001-B004/F001-F008",
                    "reasons": votes,
                }
            )
    return marks


def _price_volatility_new_candidates(df: pd.DataFrame, old_rows: list[dict[str, Any]], *, max_candidates: int = 24) -> list[dict[str, Any]]:
    q = {
        "hl_p75": _quantile(df["F006_hl_spread"], 0.75, 0.0),
        "atr_p70": _quantile(df["F008_atr14"], 0.70, 0.0),
        "ret3_neg_p70": _quantile((-df["F003_ret_3"]).clip(lower=0), 0.70, 0.0),
    }
    old_entry_times = {str(row.get("entry_time_utc") or "") for row in old_rows}
    raw: list[dict[str, Any]] = []
    for idx in range(30, len(df) - 1):
        row = df.iloc[idx]
        next_row = df.iloc[idx + 1]
        if _safe_float(row.get("range_pos_20"), 1.0) > 0.28:
            continue
        if _safe_float(row.get("reclaim_from_low_bps")) < 3.0:
            continue
        votes: list[str] = []
        if _safe_float(row.get("F006_hl_spread")) >= q["hl_p75"]:
            votes.append("B002/F006 expansion")
        if _safe_float(row.get("F008_atr14")) >= q["atr_p70"]:
            votes.append("B004/F008 ATR regime")
        if -_safe_float(row.get("F003_ret_3")) >= q["ret3_neg_p70"]:
            votes.append("B001/F002 pullback ret_3")
        if len(votes) < 2:
            continue
        signal_time = pd.Timestamp(row["open_time_utc"]).tz_convert("UTC")
        entry_time = pd.Timestamp(next_row["open_time_utc"]).tz_convert("UTC")
        if _fmt_ts(entry_time) in old_entry_times:
            continue
        score = len(votes) + min(_safe_float(row.get("reclaim_from_low_bps")) / 20.0, 2.0)
        raw.append(
            {
                "kind": "new_candidate",
                "candidate_id": f"STAS4_PV_{signal_time.strftime('%H%M')}",
                "signal_time_utc": _fmt_ts(signal_time),
                "entry_time_utc": _fmt_ts(entry_time),
                "entry_open_price": float(next_row["open"]),
                "source": "price_volatility:B001-B004/F001-F008",
                "score": round(float(score), 4),
                "reasons": votes,
            }
        )
    selected: list[dict[str, Any]] = []
    last_time: pd.Timestamp | None = None
    for item in sorted(raw, key=lambda x: (-float(x["score"]), x["signal_time_utc"])):
        ts = pd.Timestamp(item["signal_time_utc"]).tz_convert("UTC")
        if last_time is not None and abs((ts - last_time).total_seconds()) < 10 * 60:
            continue
        selected.append(item)
        last_time = ts
        if len(selected) >= max_candidates:
            break
    return sorted(selected, key=lambda x: x["signal_time_utc"])


def _trend_momentum_old_entry_marks(df: pd.DataFrame, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    marks: list[dict[str, Any]] = []
    for row in rows:
        signal_time = row.get("anchor_time_utc") or row.get("entry_time_utc") or ""
        feature_row = _row_at_time(df, signal_time)
        if feature_row is None:
            continue
        votes: list[str] = []
        if _safe_float(feature_row.get("F009_ema_gap")) < 0 and _safe_float(feature_row.get("F011_ema200_gap")) < 0:
            votes.append("B005/F009+F011 bearish EMA context")
        if _safe_float(feature_row.get("F010_ema20_slope_5")) < 0:
            votes.append("B005/F010 EMA20 slope down")
        if _safe_float(feature_row.get("F012_rsi14")) < 38:
            votes.append("B006/F012 RSI weak")
        if _safe_float(feature_row.get("F015_macd_hist")) < 0 and _safe_float(feature_row.get("F015_macd_hist_delta")) < 0:
            votes.append("B007/F015 MACD hist falling")
        if _safe_float(feature_row.get("F016_adx14")) < 14:
            votes.append("B008/F016 weak ADX")
        if _safe_float(feature_row.get("F017_stoch_k14")) < _safe_float(feature_row.get("F018_stoch_d14")) and _safe_float(feature_row.get("F017_stoch_k14")) < 35:
            votes.append("B009/F017_F018 stochastic weak")
        setup_rank = int(_safe_float(row.get("entry_setup_quality_rank"), 99))
        if len(votes) >= 3 or (setup_rank <= 1 and len(votes) >= 2):
            marks.append(
                {
                    "kind": "old_removed_candidate",
                    "candidate_id": row.get("candidate_id") or "",
                    "record_id": row.get("record_id") or "",
                    "signal_time_utc": signal_time,
                    "entry_time_utc": row.get("entry_time_utc") or "",
                    "entry_open_price": _safe_float(row.get("entry_open_price")),
                    "source": "trend_momentum:B005-B009/F009-F018",
                    "reasons": votes,
                }
            )
    return marks


def _trend_momentum_new_candidates(df: pd.DataFrame, old_rows: list[dict[str, Any]], *, max_candidates: int = 24) -> list[dict[str, Any]]:
    old_entry_times = {str(row.get("entry_time_utc") or "") for row in old_rows}
    raw: list[dict[str, Any]] = []
    for idx in range(210, len(df) - 1):
        row = df.iloc[idx]
        prev = df.iloc[idx - 1]
        next_row = df.iloc[idx + 1]
        votes: list[str] = []
        if _safe_float(row.get("F009_ema_gap")) > 0 and _safe_float(row.get("F010_ema20_slope_5")) > 0:
            votes.append("B005/F009+F010 EMA up")
        if _safe_float(row.get("F011_ema200_gap")) > 0:
            votes.append("B005/F011 above EMA200")
        rsi = _safe_float(row.get("F012_rsi14"))
        prev_rsi = _safe_float(prev.get("F012_rsi14"))
        if 42 <= rsi <= 62 and rsi > prev_rsi:
            votes.append("B006/F012 RSI recovery")
        hist = _safe_float(row.get("F015_macd_hist"))
        prev_hist = _safe_float(prev.get("F015_macd_hist"))
        if hist > prev_hist and (hist > 0 or prev_hist < 0 <= hist):
            votes.append("B007/F015 MACD improving")
        if _safe_float(row.get("F016_adx14")) >= 16:
            votes.append("B008/F016 ADX active")
        k = _safe_float(row.get("F017_stoch_k14"))
        d = _safe_float(row.get("F018_stoch_d14"))
        prev_k = _safe_float(prev.get("F017_stoch_k14"))
        prev_d = _safe_float(prev.get("F018_stoch_d14"))
        if prev_k <= prev_d and k > d and k < 72:
            votes.append("B009/F017_F018 stochastic cross up")
        if len(votes) < 4:
            continue
        signal_time = pd.Timestamp(row["open_time_utc"]).tz_convert("UTC")
        entry_time = pd.Timestamp(next_row["open_time_utc"]).tz_convert("UTC")
        if _fmt_ts(entry_time) in old_entry_times:
            continue
        score = len(votes)
        if "B007/F015 MACD improving" in votes:
            score += 0.5
        if "B009/F017_F018 stochastic cross up" in votes:
            score += 0.5
        raw.append(
            {
                "kind": "new_candidate",
                "candidate_id": f"STAS4_TM_{signal_time.strftime('%H%M')}",
                "signal_time_utc": _fmt_ts(signal_time),
                "entry_time_utc": _fmt_ts(entry_time),
                "entry_open_price": float(next_row["open"]),
                "source": "trend_momentum:B005-B009/F009-F018",
                "score": round(float(score), 4),
                "reasons": votes,
            }
        )
    selected: list[dict[str, Any]] = []
    last_time: pd.Timestamp | None = None
    for item in sorted(raw, key=lambda x: (-float(x["score"]), x["signal_time_utc"])):
        ts = pd.Timestamp(item["signal_time_utc"]).tz_convert("UTC")
        if last_time is not None and abs((ts - last_time).total_seconds()) < 10 * 60:
            continue
        selected.append(item)
        last_time = ts
        if len(selected) >= max_candidates:
            break
    return sorted(selected, key=lambda x: x["signal_time_utc"])


def _volume_flow_old_entry_marks(df: pd.DataFrame, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    marks: list[dict[str, Any]] = []
    for row in rows:
        signal_time = row.get("anchor_time_utc") or row.get("entry_time_utc") or ""
        feature_row = _row_at_time(df, signal_time)
        if feature_row is None:
            continue
        votes: list[str] = []
        if _safe_float(feature_row.get("F020_vol_z20")) < -0.55:
            votes.append("B010/F020 low volume z-score")
        if _safe_float(feature_row.get("F021_delta_volume")) < 0:
            votes.append("B010/F021 negative proxy delta")
        if _safe_float(feature_row.get("F022_obv_slope5")) < 0:
            votes.append("B011/F022 OBV slope down")
        if _safe_float(feature_row.get("F023_mfi14"), 50.0) < 35:
            votes.append("B012/F023 weak MFI")
        if _safe_float(feature_row.get("F024_vwap_distance")) < -0.35:
            votes.append("B026/F024 far below VWAP")
        risk_flags = str(row.get("stas1_risk_flags") or "")
        setup_rank = int(_safe_float(row.get("entry_setup_quality_rank"), 99))
        if len(votes) >= 3 or ("low_volume_confirmation" in risk_flags and votes) or (setup_rank <= 1 and len(votes) >= 2):
            marks.append(
                {
                    "kind": "old_removed_candidate",
                    "candidate_id": row.get("candidate_id") or "",
                    "record_id": row.get("record_id") or "",
                    "signal_time_utc": signal_time,
                    "entry_time_utc": row.get("entry_time_utc") or "",
                    "entry_open_price": _safe_float(row.get("entry_open_price")),
                    "source": "volume_flow:B010-B012+B026/F019-F024",
                    "reasons": votes,
                }
            )
    return marks


def _volume_flow_new_candidates(df: pd.DataFrame, old_rows: list[dict[str, Any]], *, max_candidates: int = 24) -> list[dict[str, Any]]:
    old_entry_times = {str(row.get("entry_time_utc") or "") for row in old_rows}
    raw: list[dict[str, Any]] = []
    for idx in range(30, len(df) - 1):
        row = df.iloc[idx]
        prev = df.iloc[idx - 1]
        next_row = df.iloc[idx + 1]
        votes: list[str] = []
        if _safe_float(row.get("F020_vol_z20")) >= 1.0:
            votes.append("B010/F020 volume spike")
        if _safe_float(row.get("F021_delta_volume")) > 0:
            votes.append("B010/F021 positive proxy delta")
        if _safe_float(row.get("F022_obv_slope5")) > 0:
            votes.append("B011/F022 OBV slope up")
        mfi = _safe_float(row.get("F023_mfi14"), 50.0)
        prev_mfi = _safe_float(prev.get("F023_mfi14"), 50.0)
        if 35 <= mfi <= 65 and mfi > prev_mfi:
            votes.append("B012/F023 MFI recovery")
        vwap_distance = _safe_float(row.get("F024_vwap_distance"))
        if -0.45 <= vwap_distance <= 0.45:
            votes.append("B026/F024 near VWAP")
        if _safe_float(row.get("range_pos_20"), 1.0) > 0.40:
            continue
        if len(votes) < 4:
            continue
        signal_time = pd.Timestamp(row["open_time_utc"]).tz_convert("UTC")
        entry_time = pd.Timestamp(next_row["open_time_utc"]).tz_convert("UTC")
        if _fmt_ts(entry_time) in old_entry_times:
            continue
        score = len(votes) + min(max(_safe_float(row.get("F020_vol_z20")), 0.0), 3.0) * 0.25
        raw.append(
            {
                "kind": "new_candidate",
                "candidate_id": f"STAS4_VF_{signal_time.strftime('%H%M')}",
                "signal_time_utc": _fmt_ts(signal_time),
                "entry_time_utc": _fmt_ts(entry_time),
                "entry_open_price": float(next_row["open"]),
                "source": "volume_flow:B010-B012+B026/F019-F024",
                "score": round(float(score), 4),
                "reasons": votes,
            }
        )
    selected: list[dict[str, Any]] = []
    last_time: pd.Timestamp | None = None
    for item in sorted(raw, key=lambda x: (-float(x["score"]), x["signal_time_utc"])):
        ts = pd.Timestamp(item["signal_time_utc"]).tz_convert("UTC")
        if last_time is not None and abs((ts - last_time).total_seconds()) < 10 * 60:
            continue
        selected.append(item)
        last_time = ts
        if len(selected) >= max_candidates:
            break
    return sorted(selected, key=lambda x: x["signal_time_utc"])


def _density_profile_old_entry_marks(df: pd.DataFrame, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    marks: list[dict[str, Any]] = []
    for row in rows:
        signal_time = row.get("anchor_time_utc") or row.get("entry_time_utc") or ""
        feature_row = _row_at_time(df, signal_time)
        if feature_row is None:
            continue
        votes: list[str] = []
        if abs(_safe_float(feature_row.get("F025_vpoc_distance_60"))) > 0.75:
            votes.append("B013/F025 far from VPOC60")
        if abs(_safe_float(feature_row.get("F029_vpoc_distance_240"))) > 0.95:
            votes.append("B013/F029 far from VPOC240")
        if _safe_float(feature_row.get("F027_cluster_share_60")) < 0.10:
            votes.append("B013/F027 weak current cluster60")
        if _safe_float(feature_row.get("F028_vpoc_share_60")) < 0.10:
            votes.append("B013/F028 weak VPOC60 share")
        if abs(_safe_float(feature_row.get("F033_vpoc_drift_20"))) > 0.35:
            votes.append("B013/F033 VPOC drift")
        if _safe_float(feature_row.get("F034_cluster_ratio_60_240"), 1.0) < 0.65:
            votes.append("B013/F034 weak short/long density ratio")
        setup_rank = int(_safe_float(row.get("entry_setup_quality_rank"), 99))
        if len(votes) >= 3 or (setup_rank <= 1 and len(votes) >= 2):
            marks.append(
                {
                    "kind": "old_removed_candidate",
                    "candidate_id": row.get("candidate_id") or "",
                    "record_id": row.get("record_id") or "",
                    "signal_time_utc": signal_time,
                    "entry_time_utc": row.get("entry_time_utc") or "",
                    "entry_open_price": _safe_float(row.get("entry_open_price")),
                    "source": "density_profile:B013/F025-F034",
                    "reasons": votes,
                }
            )
    return marks


def _density_profile_new_candidates(df: pd.DataFrame, old_rows: list[dict[str, Any]], *, max_candidates: int = 24) -> list[dict[str, Any]]:
    old_entry_times = {str(row.get("entry_time_utc") or "") for row in old_rows}
    raw: list[dict[str, Any]] = []
    for idx in range(240, len(df) - 1):
        row = df.iloc[idx]
        prev = df.iloc[idx - 1]
        next_row = df.iloc[idx + 1]
        if _safe_float(row.get("range_pos_20"), 1.0) > 0.42:
            continue
        votes: list[str] = []
        if abs(_safe_float(row.get("F025_vpoc_distance_60"))) <= 0.20:
            votes.append("B013/F025 near VPOC60")
        if abs(_safe_float(row.get("F029_vpoc_distance_240"))) <= 0.30:
            votes.append("B013/F029 near VPOC240")
        if _safe_float(row.get("F027_cluster_share_60")) >= 0.18:
            votes.append("B013/F027 dense cluster60")
        if _safe_float(row.get("F028_vpoc_share_60")) >= 0.14:
            votes.append("B013/F028 strong VPOC60 share")
        if _safe_float(row.get("F034_cluster_ratio_60_240"), 0.0) >= 1.15:
            votes.append("B013/F034 local density stronger than long")
        drift_now = _safe_float(row.get("F033_vpoc_drift_20"))
        drift_prev = _safe_float(prev.get("F033_vpoc_drift_20"))
        if abs(drift_now) < abs(drift_prev) or drift_now >= 0:
            votes.append("B013/F033 stable/improving VPOC drift")
        if len(votes) < 4:
            continue
        signal_time = pd.Timestamp(row["open_time_utc"]).tz_convert("UTC")
        entry_time = pd.Timestamp(next_row["open_time_utc"]).tz_convert("UTC")
        if _fmt_ts(entry_time) in old_entry_times:
            continue
        score = len(votes)
        if "B013/F025 near VPOC60" in votes:
            score += 0.5
        if "B013/F027 dense cluster60" in votes:
            score += 0.5
        raw.append(
            {
                "kind": "new_candidate",
                "candidate_id": f"STAS4_DP_{signal_time.strftime('%H%M')}",
                "signal_time_utc": _fmt_ts(signal_time),
                "entry_time_utc": _fmt_ts(entry_time),
                "entry_open_price": float(next_row["open"]),
                "source": "density_profile:B013/F025-F034",
                "score": round(float(score), 4),
                "reasons": votes,
            }
        )
    selected: list[dict[str, Any]] = []
    last_time: pd.Timestamp | None = None
    for item in sorted(raw, key=lambda x: (-float(x["score"]), x["signal_time_utc"])):
        ts = pd.Timestamp(item["signal_time_utc"]).tz_convert("UTC")
        if last_time is not None and abs((ts - last_time).total_seconds()) < 10 * 60:
            continue
        selected.append(item)
        last_time = ts
        if len(selected) >= max_candidates:
            break
    return sorted(selected, key=lambda x: x["signal_time_utc"])


def _structure_context(df: pd.DataFrame) -> tuple[pd.DataFrame, Any, Any]:
    enriched = _add_closed_bar_features(df)
    pivots_3 = _raw_pivots(enriched, left=3, right=3)
    pivots_10 = _raw_pivots(enriched, left=10, right=10)
    return enriched, pivots_3, pivots_10


def _structure_votes(df: pd.DataFrame, pivots_3: Any, pivots_10: Any, idx: int) -> dict[str, Any]:
    row = df.iloc[idx]
    levels = _nearest_levels(df, pivots_3, idx)
    fib = _fib_state(pivots_10, idx)
    channel = _channel_state(df, idx)
    breakout = _breakout_retest_state(df, pivots_3, idx)
    internal = _last_structure_event(df, pivots_3, idx, lookback=120, max_age=120, deviation_pct=0.15)
    external = _last_structure_event(df, pivots_10, idx, lookback=240, max_age=240, deviation_pct=0.30)
    close = float(row["close"])
    fib_0382 = fib.get("levels", {}).get("0.382")
    fib_0618 = fib.get("levels", {}).get("0.618")
    fib_0382_dist = None if fib_0382 is None else (close / float(fib_0382) - 1.0) * 100.0
    fib_0618_dist = None if fib_0618 is None else (close / float(fib_0618) - 1.0) * 100.0
    support_dist = levels.get("support_dist_pct")
    resistance_dist = levels.get("resistance_dist_pct")
    range_pos_240 = _safe_float(row.get("range_pos_240"), 0.5)
    support_hint = support_dist is not None and abs(float(support_dist)) <= 0.25
    range_hint = range_pos_240 <= 0.35
    fib_hint = any(value is not None and abs(float(value)) <= 0.25 for value in [fib_0382_dist, fib_0618_dist])
    retest_hint = bool(breakout.get("retest_near_signal")) and str(breakout.get("retest_side") or "").startswith("UP")
    structure_hint = bool(internal.get("bos_up_now") or internal.get("choch_like_near_signal") or external.get("bos_up_now"))
    conflict_hint = bool(range_pos_240 >= 0.80 and not support_hint)
    near_resistance = resistance_dist is not None and float(resistance_dist) <= 0.25
    down_structure = bool(internal.get("bos_down_now") or external.get("bos_down_now"))
    channel_pos = channel.get("pos_sigma") if channel.get("status") == "ok" else None
    return {
        "levels": levels,
        "fib": fib,
        "channel": channel,
        "breakout": breakout,
        "internal": internal,
        "external": external,
        "range_pos_240": range_pos_240,
        "support_hint": support_hint,
        "range_hint": range_hint,
        "fib_hint": fib_hint,
        "retest_hint": retest_hint,
        "structure_hint": structure_hint,
        "conflict_hint": conflict_hint,
        "near_resistance": near_resistance,
        "down_structure": down_structure,
        "channel_pos": channel_pos,
    }


def _structure_ta_old_entry_marks(df: pd.DataFrame, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    enriched, pivots_3, pivots_10 = _structure_context(df)
    marks: list[dict[str, Any]] = []
    for row in rows:
        signal_time = row.get("anchor_time_utc") or row.get("entry_time_utc") or ""
        idx = _idx_at_time(enriched, signal_time)
        if idx is None:
            continue
        state = _structure_votes(enriched, pivots_3, pivots_10, idx)
        votes: list[str] = []
        if state["conflict_hint"]:
            votes.append("B014/F038 high in range without support")
        if state["near_resistance"]:
            votes.append("B014/F036 near resistance")
        if state["channel_pos"] is not None and float(state["channel_pos"]) > 1.15:
            votes.append("B014/F039 high channel position")
        if state["down_structure"]:
            votes.append("B018/F051 BOS down")
        breakout = state["breakout"]
        if str(breakout.get("last_break_event") or "") == "BREAK_DOWN" and _safe_float(breakout.get("last_break_age_bars"), 999) <= 12:
            votes.append("B017/F046 recent downside break")
        if not state["support_hint"] and not state["range_hint"] and not state["fib_hint"] and not state["retest_hint"]:
            votes.append("B014-B017 no structural support")
        setup_rank = int(_safe_float(row.get("entry_setup_quality_rank"), 99))
        if len(votes) >= 2 or (setup_rank <= 1 and votes):
            marks.append(
                {
                    "kind": "old_removed_candidate",
                    "candidate_id": row.get("candidate_id") or "",
                    "record_id": row.get("record_id") or "",
                    "signal_time_utc": signal_time,
                    "entry_time_utc": row.get("entry_time_utc") or "",
                    "entry_open_price": _safe_float(row.get("entry_open_price")),
                    "source": "structure_ta:B014-B018/F035-F052",
                    "reasons": votes,
                }
            )
    return marks


def _structure_ta_new_candidates(df: pd.DataFrame, old_rows: list[dict[str, Any]], *, max_candidates: int = 24) -> list[dict[str, Any]]:
    enriched, pivots_3, pivots_10 = _structure_context(df)
    old_entry_times = {str(row.get("entry_time_utc") or "") for row in old_rows}
    raw: list[dict[str, Any]] = []
    for idx in range(240, len(enriched) - 1):
        row = enriched.iloc[idx]
        next_row = enriched.iloc[idx + 1]
        state = _structure_votes(enriched, pivots_3, pivots_10, idx)
        votes: list[str] = []
        if state["support_hint"]:
            votes.append("B014/F035 near support")
        if state["range_hint"]:
            votes.append("B014/F038 lower range")
        if state["fib_hint"]:
            votes.append("B015/F040-F041 near fib")
        if state["retest_hint"]:
            votes.append("B017/F047 up retest")
        if state["structure_hint"]:
            votes.append("B018/F050-F052 structure support")
        if state["channel_pos"] is not None and -1.20 <= float(state["channel_pos"]) <= 0.25:
            votes.append("B014/F039 lower channel half")
        if state["near_resistance"] or state["down_structure"]:
            continue
        if len(votes) < 3:
            continue
        signal_time = pd.Timestamp(row["open_time_utc"]).tz_convert("UTC")
        entry_time = pd.Timestamp(next_row["open_time_utc"]).tz_convert("UTC")
        if _fmt_ts(entry_time) in old_entry_times:
            continue
        score = len(votes)
        if "B017/F047 up retest" in votes:
            score += 1.0
        if "B018/F050-F052 structure support" in votes:
            score += 0.7
        raw.append(
            {
                "kind": "new_candidate",
                "candidate_id": f"STAS4_ST_{signal_time.strftime('%H%M')}",
                "signal_time_utc": _fmt_ts(signal_time),
                "entry_time_utc": _fmt_ts(entry_time),
                "entry_open_price": float(next_row["open"]),
                "source": "structure_ta:B014-B018/F035-F052",
                "score": round(float(score), 4),
                "reasons": votes,
            }
        )
    selected: list[dict[str, Any]] = []
    last_time: pd.Timestamp | None = None
    for item in sorted(raw, key=lambda x: (-float(x["score"]), x["signal_time_utc"])):
        ts = pd.Timestamp(item["signal_time_utc"]).tz_convert("UTC")
        if last_time is not None and abs((ts - last_time).total_seconds()) < 10 * 60:
            continue
        selected.append(item)
        last_time = ts
        if len(selected) >= max_candidates:
            break
    return sorted(selected, key=lambda x: x["signal_time_utc"])


def _recent_bool(df: pd.DataFrame, idx: int, columns: list[str], lookback: int) -> dict[str, bool]:
    start = max(0, idx - lookback + 1)
    win = df.iloc[start : idx + 1]
    return {col: bool(win[col].fillna(False).astype(bool).any()) for col in columns}


def _pattern_old_entry_marks(df: pd.DataFrame, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    enriched = _add_pattern_features(df)
    marks: list[dict[str, Any]] = []
    for row in rows:
        signal_time = row.get("anchor_time_utc") or row.get("entry_time_utc") or ""
        idx = _idx_at_time(enriched, signal_time)
        if idx is None:
            continue
        item = enriched.iloc[idx]
        candle_flags = _recent_bool(
            enriched,
            idx,
            [
                "pin_bar_bull_flag",
                "hammer_flag",
                "engulf_bull_flag",
                "doji_flag",
                "inside_bar_flag",
                "pin_bar_bear_flag",
                "shooting_star_flag",
                "engulf_bear_flag",
            ],
            3,
        )
        div_flags = _recent_bool(enriched, idx, ["rsi_bull_div_flag", "macd_bull_div_flag", "obv_bull_div_flag"], 8)
        chart_flags = _recent_bool(enriched, idx, ["double_bottom_like", "range_flag", "wedge_falling_like"], 8)
        votes: list[str] = []
        if any(candle_flags[key] for key in ["pin_bar_bear_flag", "shooting_star_flag", "engulf_bear_flag"]):
            votes.append("B019/F056-F060 bearish candle conflict")
        if not any(candle_flags[key] for key in ["pin_bar_bull_flag", "hammer_flag", "engulf_bull_flag", "doji_flag", "inside_bar_flag"]):
            votes.append("B019 no bullish candle support")
        if not any(div_flags.values()):
            votes.append("B020 no bullish divergence")
        if not any(chart_flags.values()):
            votes.append("B022 no bullish chart pattern")
        if _safe_float(item.get("pattern_strength")) <= 1:
            votes.append("B021/F067 weak pattern strength")
        if _safe_float(item.get("pattern_age_bars"), 99) > 12:
            votes.append("B021/F068 old/no fresh pattern")
        if not bool(item.get("pattern_confirm")):
            votes.append("B023/F078-F079 no volume/level confirm")
        setup_rank = int(_safe_float(row.get("entry_setup_quality_rank"), 99))
        if "B019/F056-F060 bearish candle conflict" in votes or (setup_rank <= 1 and len(votes) >= 4) or len(votes) >= 5:
            marks.append(
                {
                    "kind": "old_removed_candidate",
                    "candidate_id": row.get("candidate_id") or "",
                    "record_id": row.get("record_id") or "",
                    "signal_time_utc": signal_time,
                    "entry_time_utc": row.get("entry_time_utc") or "",
                    "entry_open_price": _safe_float(row.get("entry_open_price")),
                    "source": "pattern:B019-B025/F053-F083",
                    "reasons": votes,
                }
            )
    return marks


def _pattern_new_candidates(df: pd.DataFrame, old_rows: list[dict[str, Any]], *, max_candidates: int = 24) -> list[dict[str, Any]]:
    enriched = _add_pattern_features(df)
    old_entry_times = {str(row.get("entry_time_utc") or "") for row in old_rows}
    raw: list[dict[str, Any]] = []
    for idx in range(80, len(enriched) - 1):
        row = enriched.iloc[idx]
        next_row = enriched.iloc[idx + 1]
        candle_flags = _recent_bool(
            enriched,
            idx,
            [
                "pin_bar_bull_flag",
                "hammer_flag",
                "engulf_bull_flag",
                "doji_flag",
                "inside_bar_flag",
                "pin_bar_bear_flag",
                "shooting_star_flag",
                "engulf_bear_flag",
            ],
            3,
        )
        div_flags = _recent_bool(enriched, idx, ["rsi_bull_div_flag", "macd_bull_div_flag", "obv_bull_div_flag"], 8)
        chart_flags = _recent_bool(enriched, idx, ["double_bottom_like", "range_flag", "wedge_falling_like"], 8)
        confirm_flags = _recent_bool(enriched, idx, ["volume_confirm", "level_confirm_long"], 3)
        if any(candle_flags[key] for key in ["pin_bar_bear_flag", "shooting_star_flag", "engulf_bear_flag"]):
            continue
        votes: list[str] = []
        if any(candle_flags[key] for key in ["pin_bar_bull_flag", "hammer_flag", "engulf_bull_flag", "doji_flag", "inside_bar_flag"]):
            votes.append("B019/F053-F060 bullish candle")
        if any(div_flags.values()):
            votes.append("B020/F061-F066 bullish divergence")
        if _safe_float(row.get("pattern_strength")) >= 2:
            votes.append("B021/F067 pattern strength")
        if _safe_float(row.get("pattern_age_bars"), 99) <= 5:
            votes.append("B021/F068 fresh pattern")
        if any(chart_flags.values()):
            votes.append("B022/F069-F077 chart long pattern")
        if any(confirm_flags.values()):
            votes.append("B023/F078-F079 pattern confirmation")
        if bool(row.get("pattern_long_composite")):
            votes.append("B024/F080 composite LONG")
        if _safe_float(row.get("pattern_strength")) >= 3 and _safe_float(row.get("pattern_age_bars"), 99) <= 8:
            votes.append("B025/F082-F083 pattern context ok")
        if len(votes) < 4:
            continue
        signal_time = pd.Timestamp(row["open_time_utc"]).tz_convert("UTC")
        entry_time = pd.Timestamp(next_row["open_time_utc"]).tz_convert("UTC")
        if _fmt_ts(entry_time) in old_entry_times:
            continue
        score = len(votes)
        if "B024/F080 composite LONG" in votes:
            score += 1.0
        raw.append(
            {
                "kind": "new_candidate",
                "candidate_id": f"STAS4_PT_{signal_time.strftime('%H%M')}",
                "signal_time_utc": _fmt_ts(signal_time),
                "entry_time_utc": _fmt_ts(entry_time),
                "entry_open_price": float(next_row["open"]),
                "source": "pattern:B019-B025/F053-F083",
                "score": round(float(score), 4),
                "reasons": votes,
            }
        )
    selected: list[dict[str, Any]] = []
    last_time: pd.Timestamp | None = None
    for item in sorted(raw, key=lambda x: (-float(x["score"]), x["signal_time_utc"])):
        ts = pd.Timestamp(item["signal_time_utc"]).tz_convert("UTC")
        if last_time is not None and abs((ts - last_time).total_seconds()) < 10 * 60:
            continue
        selected.append(item)
        last_time = ts
        if len(selected) >= max_candidates:
            break
    return sorted(selected, key=lambda x: x["signal_time_utc"])


def _family_marks(df: pd.DataFrame, rows: list[dict[str, Any]], family: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if "+" in family:
        families = [part.strip() for part in family.split("+") if part.strip()]
        return _combo_family_marks(df, rows, families)
    if family == "price_volatility":
        enriched = _add_price_volatility_features(df)
        return _price_volatility_old_entry_marks(enriched, rows), _price_volatility_new_candidates(enriched, rows)
    if family == "trend_momentum":
        enriched = _add_trend_momentum_features(df)
        return _trend_momentum_old_entry_marks(enriched, rows), _trend_momentum_new_candidates(enriched, rows)
    if family == "volume_flow":
        enriched = _add_volume_flow_features(df)
        return _volume_flow_old_entry_marks(enriched, rows), _volume_flow_new_candidates(enriched, rows)
    if family == "density_profile":
        enriched = _add_density_profile_features(df)
        return _density_profile_old_entry_marks(enriched, rows), _density_profile_new_candidates(enriched, rows)
    if family == "structure_ta":
        return _structure_ta_old_entry_marks(df, rows), _structure_ta_new_candidates(df, rows)
    if family == "pattern":
        return _pattern_old_entry_marks(df, rows), _pattern_new_candidates(df, rows)
    raise ValueError("Implemented families: price_volatility, trend_momentum, volume_flow, density_profile, structure_ta, pattern.")


def _mark_key(item: dict[str, Any]) -> str:
    return str(item.get("record_id") or item.get("candidate_id") or item.get("entry_time_utc") or "")


def _merge_reasons(prefix: str, item: dict[str, Any]) -> list[str]:
    return [f"{prefix}: {reason}" for reason in item.get("reasons", [])]


def _combo_family_marks(df: pd.DataFrame, rows: list[dict[str, Any]], families: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if len(families) < 2:
        raise ValueError("Combo family must contain at least two families.")
    family_payloads: dict[str, tuple[list[dict[str, Any]], list[dict[str, Any]]]] = {}
    for item in families:
        family_payloads[item] = _family_marks(df, rows, item)

    old_maps = {
        family: {_mark_key(item): item for item in payload[0] if _mark_key(item)}
        for family, payload in family_payloads.items()
    }
    common_old_keys = set.intersection(*(set(items.keys()) for items in old_maps.values())) if old_maps else set()
    old_removed: list[dict[str, Any]] = []
    for key in sorted(common_old_keys):
        first = old_maps[families[0]][key]
        reasons: list[str] = []
        for family in families:
            reasons.extend(_merge_reasons(family, old_maps[family][key]))
        old_removed.append(
            {
                **first,
                "source": "+".join(families),
                "reasons": reasons,
            }
        )

    new_lists = {family: payload[1] for family, payload in family_payloads.items()}
    base_family = families[0]
    raw_new: list[dict[str, Any]] = []
    for base_item in new_lists[base_family]:
        base_ts = pd.Timestamp(base_item["entry_time_utc"]).tz_convert("UTC")
        matched = {base_family: base_item}
        ok = True
        for family in families[1:]:
            candidates = []
            for other in new_lists[family]:
                other_ts = pd.Timestamp(other["entry_time_utc"]).tz_convert("UTC")
                diff_min = abs((other_ts - base_ts).total_seconds()) / 60.0
                if diff_min <= 5.0:
                    candidates.append((diff_min, other))
            if not candidates:
                ok = False
                break
            matched[family] = sorted(candidates, key=lambda x: x[0])[0][1]
        if not ok:
            continue
        entry_ts = max(pd.Timestamp(item["entry_time_utc"]).tz_convert("UTC") for item in matched.values())
        signal_ts = entry_ts - pd.Timedelta(minutes=1)
        reasons = []
        score = 0.0
        for family, item in matched.items():
            reasons.extend(_merge_reasons(family, item))
            score += _safe_float(item.get("score"), 0.0)
        raw_new.append(
            {
                "kind": "new_candidate",
                "candidate_id": f"STAS4_COMBO_{'_'.join(f[:2].upper() for f in families)}_{signal_ts.strftime('%H%M')}",
                "signal_time_utc": _fmt_ts(signal_ts),
                "entry_time_utc": _fmt_ts(entry_ts),
                "entry_open_price": _safe_float(matched[base_family].get("entry_open_price")),
                "source": "+".join(families),
                "score": round(float(score), 4),
                "reasons": reasons,
            }
        )

    selected_new: list[dict[str, Any]] = []
    last_time: pd.Timestamp | None = None
    for item in sorted(raw_new, key=lambda x: (-float(x["score"]), x["entry_time_utc"])):
        ts = pd.Timestamp(item["entry_time_utc"]).tz_convert("UTC")
        if last_time is not None and abs((ts - last_time).total_seconds()) < 10 * 60:
            continue
        selected_new.append(item)
        last_time = ts
    return old_removed, sorted(selected_new, key=lambda x: x["entry_time_utc"])


def _safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_+-]+", "_", value).strip("_")


def _draw_marker_labels(ax: Any, items: list[dict[str, Any]], *, color: str, marker_text: str, y_offset: float) -> None:
    for item in items:
        entry_time = pd.Timestamp(item["entry_time_utc"]).tz_convert(None)
        price = float(item["entry_open_price"])
        ax.text(
            entry_time,
            price + y_offset,
            marker_text,
            color=color,
            fontsize=10,
            fontweight="bold",
            ha="center",
            va="center",
            zorder=12,
        )
        label = str(item.get("candidate_id") or item.get("record_id") or "")
        ax.annotate(
            label[:14],
            xy=(entry_time, price + y_offset),
            xytext=(3, 8),
            textcoords="offset points",
            color=color,
            fontsize=5.8,
            alpha=0.88,
            zorder=12,
        )


def _add_combo_spectrum_features(df: pd.DataFrame) -> pd.DataFrame:
    out = _add_trend_momentum_features(df)
    prev_close = out["close"].shift(1)
    tr = pd.concat(
        [
            out["high"] - out["low"],
            (out["high"] - prev_close).abs(),
            (out["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    out["combo_atr14_pct"] = tr.ewm(alpha=1 / 14, adjust=False, min_periods=5).mean() / out["close"].replace(0, np.nan) * 100.0
    out["combo_rsi_signal"] = out["F012_rsi14"].ewm(span=9, adjust=False, min_periods=3).mean()
    out["combo_macd_hist_norm"] = out["F015_macd_hist"] / out["close"].replace(0, np.nan) * 10000.0
    return out


def _pivot_indices(values: pd.Series, *, mode: str, left: int = 3, right: int = 3) -> list[int]:
    series = values.reset_index(drop=True)
    pivots: list[int] = []
    for idx in range(left, len(series) - right):
        center = series.iloc[idx]
        if pd.isna(center):
            continue
        left_part = series.iloc[idx - left : idx]
        right_part = series.iloc[idx + 1 : idx + right + 1]
        if left_part.isna().any() or right_part.isna().any():
            continue
        if mode == "low":
            if center < left_part.min() and center <= right_part.min():
                pivots.append(idx)
        elif mode == "high":
            if center > left_part.max() and center >= right_part.max():
                pivots.append(idx)
        else:
            raise ValueError("mode must be low or high")
    return pivots


def _divergence_segments(df: pd.DataFrame, *, left: int = 3, right: int = 3) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    lows = _pivot_indices(df["low"], mode="low", left=left, right=right)
    highs = _pivot_indices(df["high"], mode="high", left=left, right=right)
    osc = df["F012_rsi14"].reset_index(drop=True)
    for pivots, price_col, regular_kind, hidden_kind in [
        (lows, "low", "bullish_divergence", "hidden_bullish_divergence"),
        (highs, "high", "bearish_divergence", "hidden_bearish_divergence"),
    ]:
        for prev, cur in zip(pivots, pivots[1:]):
            if cur - prev > 180:
                continue
            prev_osc = osc.iloc[prev]
            cur_osc = osc.iloc[cur]
            if pd.isna(prev_osc) or pd.isna(cur_osc):
                continue
            prev_price = float(df[price_col].iloc[prev])
            cur_price = float(df[price_col].iloc[cur])
            if price_col == "low":
                if cur_price < prev_price and float(cur_osc) > float(prev_osc):
                    kind = regular_kind
                elif cur_price > prev_price and float(cur_osc) < float(prev_osc):
                    kind = hidden_kind
                else:
                    continue
            else:
                if cur_price > prev_price and float(cur_osc) < float(prev_osc):
                    kind = regular_kind
                elif cur_price < prev_price and float(cur_osc) > float(prev_osc):
                    kind = hidden_kind
                else:
                    continue
            confirm_idx = min(cur + right, len(df) - 1)
            out.append(
                {
                    "kind": kind,
                    "prev_idx": prev,
                    "cur_idx": cur,
                    "confirm_idx": confirm_idx,
                    "prev_time_utc": _fmt_ts(df["open_time_utc"].iloc[prev]),
                    "pivot_time_utc": _fmt_ts(df["open_time_utc"].iloc[cur]),
                    "confirmed_time_utc": _fmt_ts(df["open_time_utc"].iloc[confirm_idx]),
                    "prev_osc": float(prev_osc),
                    "pivot_osc": float(cur_osc),
                }
            )
    return sorted(out, key=lambda item: item["confirm_idx"])


def _render_combo_spectrum(ax: Any, df: pd.DataFrame, day: str) -> list[dict[str, Any]]:
    enriched = _add_combo_spectrum_features(df)
    divergences = _divergence_segments(enriched, left=3, right=3)
    x = enriched["open_time_utc"].dt.tz_convert(None)
    rsi = enriched["F012_rsi14"]
    signal = enriched["combo_rsi_signal"]
    macd_hist = enriched["combo_macd_hist_norm"].clip(-8, 8)

    _style_axis(ax)
    _shade_sessions(ax, day)
    ax.set_facecolor("#10152a")
    ax.axhspan(80, 100, color="#5b1f34", alpha=0.34, zorder=0)
    ax.axhspan(0, 20, color="#143b2e", alpha=0.34, zorder=0)
    for level, color, alpha in [(80, "#ff3355", 0.75), (60, "#7d8594", 0.32), (50, "#cfd8dc", 0.35), (40, "#7d8594", 0.32), (20, "#00e676", 0.75)]:
        ax.axhline(level, color=color, linestyle="--" if level in {80, 20} else "-", linewidth=0.80, alpha=alpha, zorder=1)

    bar_colors = np.where(macd_hist >= 0, "#00c781", "#ff4b5c")
    ax.bar(x, macd_hist * 2.2, bottom=50, width=_bar_width_days(TIMEFRAME), color=bar_colors, alpha=0.30, zorder=2)
    ax.plot(x, rsi, color="white", linewidth=1.20, alpha=0.96, zorder=5)
    ax.plot(x, signal, color="#f3d42b", linewidth=1.05, alpha=0.92, zorder=6)

    for item in divergences:
        prev_idx = int(item["prev_idx"])
        cur_idx = int(item["cur_idx"])
        confirm_idx = int(item["confirm_idx"])
        kind = str(item["kind"])
        color = "#00ffc3" if "bullish" in kind else "#ff3333"
        linestyle = "--" if kind.startswith("hidden_") else "-"
        ax.plot(
            [x.iloc[prev_idx], x.iloc[cur_idx]],
            [rsi.iloc[prev_idx], rsi.iloc[cur_idx]],
            color=color,
            linewidth=1.75,
            linestyle=linestyle,
            alpha=0.96,
            zorder=8,
        )
        marker_y = 15 if "bullish" in kind else 86
        marker = "^" if "bullish" in kind else "v"
        ax.scatter([x.iloc[confirm_idx]], [marker_y], marker=marker, s=42, color=color, edgecolors="#101418", linewidths=0.45, zorder=9)

    atr = enriched["combo_atr14_pct"].replace([np.inf, -np.inf], np.nan)
    q1 = atr.quantile(0.35)
    q2 = atr.quantile(0.70)
    q3 = atr.quantile(0.90)
    for ts, value in zip(x, atr):
        if pd.isna(value):
            color = "#263238"
        elif value <= q1:
            color = "#1e88e5"
        elif value <= q2:
            color = "#00c781"
        elif value <= q3:
            color = "#ffd02f"
        else:
            color = "#ff4b36"
        ax.axvspan(ts, ts + pd.Timedelta(minutes=1), ymin=0.030, ymax=0.085, color=color, alpha=0.86, linewidth=0, zorder=7)

    ax.text(0.005, 0.88, "COMBO SPECTRUM: RSI + MACD + STOCH + ATR + divergence", transform=ax.transAxes, color="white", fontsize=8.8, fontweight="bold", va="top")
    ax.text(0.005, 0.68, "white=RSI/composite  yellow=smooth  bars=MACD  bottom ribbon=ATR volatility", transform=ax.transAxes, color="#b0bec5", fontsize=7.0, va="top")
    ax.text(0.995, 0.12, "ATR: blue calm / green normal / yellow high / red extreme", transform=ax.transAxes, color="#b0bec5", fontsize=6.6, ha="right", va="bottom")
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 50, 60, 80])
    ax.tick_params(axis="y", labelsize=7)
    ax.set_ylabel("Combo", color="white")
    return divergences


def _render_overlay(
    *,
    df: pd.DataFrame,
    stas2_rows: list[dict[str, Any]],
    hour_rows: list[dict[str, Any]],
    macro_wave_rows: list[dict[str, Any]],
    old_removed: list[dict[str, Any]],
    new_candidates: list[dict[str, Any]],
    day: str,
    family: str,
    out_path: Path,
    combo_spectrum: bool = False,
) -> None:
    if combo_spectrum:
        fig, axes = plt.subplots(
            7,
            1,
            figsize=(32, 19.2),
            sharex=True,
            gridspec_kw={"height_ratios": OVERVIEW_COMBO_HEIGHT_RATIOS},
        )
        ax_price, ax_bg_phase, ax_long_wave, ax_short_wave, ax_macro_wave, ax_combo, ax_vol = axes
    else:
        fig, axes = plt.subplots(
            6,
            1,
            figsize=(32, 17.4),
            sharex=True,
            gridspec_kw={"height_ratios": OVERVIEW_HEIGHT_RATIOS},
        )
        ax_price, ax_bg_phase, ax_long_wave, ax_short_wave, ax_macro_wave, ax_vol = axes
        ax_combo = None
    fig.patch.set_facecolor("#101418")
    _style_axis(ax_price)
    _style_axis(ax_vol)
    _draw_candles(ax_price, df, TIMEFRAME, linewidth=0.30)
    _shade_sessions(ax_price, day, label_top=True)
    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(df["open"], df["close"])]
    ax_vol.bar(df["open_time_utc"].dt.tz_convert(None), df["volume"], width=_bar_width_days(TIMEFRAME), color=colors, alpha=0.70)
    _shade_sessions(ax_vol, day)
    _render_rank_strip(ax_bg_phase, hour_rows, day, rank_field="hour_background_phase_rank", label="Fon", color_kind="phase", pct_field="hour_background_phase_metric_pct")
    _render_rank_strip(ax_long_wave, hour_rows, day, rank_field="hour_long_wave_rank", label="LONG", color_kind="long", pct_field="hour_long_wave_up_from_low_pct")
    _render_rank_strip(ax_short_wave, hour_rows, day, rank_field="hour_short_wave_rank", label="SHORT", color_kind="short", pct_field="hour_short_wave_down_from_high_pct")
    _render_macro_wave_strip(ax_macro_wave, macro_wave_rows, day)
    if combo_spectrum and ax_combo is not None:
        _render_combo_spectrum(ax_combo, df, day)

    for row in stas2_rows:
        entry_time = pd.Timestamp(row["entry_time_utc"]).tz_convert(None)
        anchor_raw = row.get("anchor_time_utc") or row["entry_time_utc"]
        anchor_time = pd.Timestamp(anchor_raw).tz_convert(None)
        anchor_low = _safe_float(row.get("anchor_low_price"))
        entry_open = _safe_float(row.get("entry_open_price"))
        is_good = bool(row.get("is_good_stas1_review"))
        color = "#00e676" if is_good else "#ff5252"
        ax_price.axvline(entry_time, color=color, alpha=0.13 if is_good else 0.08, linewidth=0.85, zorder=3)
        ax_price.scatter([anchor_time], [anchor_low], s=13 if is_good else 9, color="#ff5252", edgecolors="#0b0f12", linewidths=0.30, alpha=0.78, zorder=6)
        ax_price.scatter(
            [entry_time],
            [entry_open],
            marker="^" if is_good else "x",
            s=40 if is_good else 46,
            color=color,
            edgecolors="white" if is_good else color,
            linewidths=0.38 if is_good else 0.95,
            alpha=0.84,
            zorder=7,
        )

    y_span = max(float(df["high"].max() - df["low"].min()), 1e-9)
    _draw_marker_labels(ax_price, old_removed, color="#eaff00", marker_text="X", y_offset=y_span * 0.010)
    _draw_marker_labels(ax_price, new_candidates, color="#37a2ff", marker_text="UP", y_offset=y_span * 0.016)

    start = pd.Timestamp(day)
    end = start + pd.Timedelta(days=1)
    ax_price.set_xlim(start.to_pydatetime(), end.to_pydatetime())
    ax_price.set_title(
        f"STAS4 overlay {family} on STAS2 {SYMBOL} {TIMEFRAME} {day} | yellow X=old entry cut candidate | blue UP=new candidate | review only",
        color="white",
        fontsize=14,
    )
    ax_price.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    _set_day_time_axis(ax_vol, day)
    fig.tight_layout()
    fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor())
    plt.close(fig)


def run(*, root: Path, stas2_run_dir: Path, day: str, family: str, out_dir: Path, combo_spectrum: bool = False) -> dict[str, Any]:
    stas2_run_dir = stas2_run_dir.resolve()
    out_dir = out_dir.resolve()
    source = _source_csv(root, day, TIMEFRAME, SYMBOL)
    df = _load_ohlcv(source)
    stas2_rows = [row for row in _read_csv_dicts(stas2_run_dir / "STAS2_RECORDS.csv") if row.get("day_utc") == day]
    hour_rows = [row for row in _read_csv_dicts(stas2_run_dir / "STAS2_HOURLY_PHASES.csv") if row.get("day_utc") == day]
    macro_wave_rows = [row for row in _read_csv_dicts(stas2_run_dir / "STAS2_MACRO_WAVES.csv") if row.get("day_utc") == day]
    old_removed, new_candidates = _family_marks(df, stas2_rows, family)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_day = day.replace("-", "")
    family_slug = _safe_slug(family)
    spectrum_suffix = "_COMBO_SPECTRUM" if combo_spectrum else ""
    png_path = out_dir / f"STAS4_{family_slug}_OVERLAY{spectrum_suffix}_{safe_day}_{stamp}.png"
    json_path = out_dir / f"STAS4_{family_slug}_OVERLAY{spectrum_suffix}_{safe_day}_{stamp}.json"
    csv_path = out_dir / f"STAS4_{family_slug}_MARKS_{safe_day}_{stamp}.csv"
    report_path = out_dir / f"STAS4_{family_slug}_REPORT_{safe_day}_{stamp}_RU.md"
    _render_overlay(
        df=df,
        stas2_rows=stas2_rows,
        hour_rows=hour_rows,
        macro_wave_rows=macro_wave_rows,
        old_removed=old_removed,
        new_candidates=new_candidates,
        day=day,
        family=family,
        out_path=png_path,
        combo_spectrum=combo_spectrum,
    )
    marks = old_removed + new_candidates
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        fieldnames = ["kind", "candidate_id", "record_id", "signal_time_utc", "entry_time_utc", "entry_open_price", "source", "score", "reasons"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in marks:
            writer.writerow({key: json.dumps(item.get(key), ensure_ascii=False) if key == "reasons" else item.get(key, "") for key in fieldnames})
    payload = {
        "status": STATUS,
        "created_utc": _utc_now(),
        "family": family,
        "day": day,
        "combo_spectrum": combo_spectrum,
        "source_stas2_run_dir": _rel(root, stas2_run_dir),
        "old_removed_candidate_count": len(old_removed),
        "new_candidate_count": len(new_candidates),
        "artifacts": {"png": _rel(root, png_path), "csv": _rel(root, csv_path), "json": _rel(root, json_path), "report_ru": _rel(root, report_path)},
        "guardrails": [
            "review_only_no_ml_no_optuna",
            "features_use_closed_signal_candle_or_past_only",
            "entry_time_is_next_candle_open_for_new_candidates",
            "old_stas1_stas2_logic_is_not_modified",
            "combo_spectrum_is_visual_feature_layer_not_ml_training",
        ],
        "marks": marks,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    report_path.write_text(
        "\n".join(
            [
                f"# STAS4 {family} overlay {day}",
                "",
                f"Статус: `{STATUS}`.",
                "",
                "Назначение: первый обзорный слой Stas4 поверх Stas2 без ML/Optuna и без изменения старых входов.",
                "",
                f"- Старых входов на день: `{len(stas2_rows)}`.",
                f"- Зеленых галочек-кандидатов на удаление шума: `{len(old_removed)}`.",
                f"- Синих новых кандидатов: `{len(new_candidates)}`.",
                "",
                "Правило входа: сигнал на закрытой свече, вход следующей свечой.",
                "",
                "Артефакты:",
                f"- PNG: `{_rel(root, png_path)}`",
                f"- CSV: `{_rel(root, csv_path)}`",
                f"- JSON: `{_rel(root, json_path)}`",
            ]
        ),
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Render STAS4 family overlay on an existing STAS2 run.")
    parser.add_argument("--stas2-run-dir", required=True)
    parser.add_argument("--day", required=True)
    parser.add_argument("--family", default="price_volatility")
    parser.add_argument("--out-dir", default="STAS4_FEATURE_HYPOTHESIS_REVIEW")
    parser.add_argument("--combo-spectrum", action="store_true", help="Add RSI/MACD/Stoch/ATR/divergence spectrum panel above volume.")
    args = parser.parse_args()
    root = Path.cwd()
    payload = run(
        root=root,
        stas2_run_dir=Path(args.stas2_run_dir),
        day=str(args.day),
        family=str(args.family),
        out_dir=Path(args.out_dir),
        combo_spectrum=bool(args.combo_spectrum),
    )
    print(json.dumps(payload["artifacts"], ensure_ascii=False, indent=2))
    print(f"old_removed_candidate_count={payload['old_removed_candidate_count']} new_candidate_count={payload['new_candidate_count']}")


if __name__ == "__main__":
    main()
