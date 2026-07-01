from __future__ import annotations

import json
import math
import re
import numpy as np
import pandas as pd

from mlbotnav.pct_units import normalize_min_expected_move_pct
from mlbotnav.runtime_diagnostics import MIN_MOVE_UNREACHABLE


def _infer_bar_seconds(df: pd.DataFrame) -> float:
    if "open_time_utc" not in df.columns or len(df) < 2:
        return 0.0
    ts = pd.to_datetime(df["open_time_utc"], utc=True, errors="coerce").dropna().sort_values()
    if len(ts) < 2:
        return 0.0
    step = ts.diff().dropna().dt.total_seconds()
    if len(step) == 0:
        return 0.0
    return float(step.median())


def _normalize_signal_mode(signal_mode: str) -> str:
    mode = str(signal_mode or "both").strip().lower()
    if mode not in {"both", "long_only", "short_only"}:
        mode = "both"
    return mode


def _normalize_trend_filter(trend_filter: str) -> str:
    tf = str(trend_filter or "none").strip().lower()
    allowed = {
        "none",
        "ema_gap_sign",
        "ema_cross_20_50",
        "ema_cross_20_200",
        "ema_stack_bull",
        "channel_breakout_50",
        "adx_trend_18",
        "fib_retrace_0382_0618_trend_resume",
        "fib_extension_targets",
        "swing_hl_hh_long",
        "swing_lh_ll_short",
        "bos_continuation_confirm",
        "min_max_range_revert",
        "max_low_pullback_long",
        "hvn_lvn_density_reaction",
        "volume_profile_poc_vah_val_retest",
        "value_area_rotation_vs_breakout",
        "wedge_breakout_plus_profile_acceptance",
        "orderbook_imbalance_l1_l50",
        "spread_pressure_and_delta_absorption",
    }
    if tf not in allowed:
        return "none"
    return tf


def _calib_value(calibration_params: dict[str, float] | None, key: str, default: float) -> float:
    try:
        return float(dict(calibration_params or {}).get(str(key), default))
    except Exception:
        return float(default)


def _finite_distribution(values: list[float], *, prefix: str) -> dict[str, object]:
    finite = np.asarray([float(v) for v in values if np.isfinite(float(v))], dtype=float)
    out: dict[str, object] = {
        f"{prefix}_count": int(len(finite)),
        f"{prefix}_max": 0.0,
        f"{prefix}_p50": 0.0,
        f"{prefix}_p90": 0.0,
        f"{prefix}_p99": 0.0,
    }
    if len(finite) == 0:
        return out
    out[f"{prefix}_max"] = float(np.max(finite))
    out[f"{prefix}_p50"] = float(np.quantile(finite, 0.50))
    out[f"{prefix}_p90"] = float(np.quantile(finite, 0.90))
    out[f"{prefix}_p99"] = float(np.quantile(finite, 0.99))
    return out


def _min_move_reachability_diag(
    *,
    min_expected_move_pct: float,
    signal_count_after_entry_action_gates: int,
    signal_count_after_filter: int,
    signal_count_after_min_move: int,
    move_values_after_action_gate: list[float],
    move_values_after_filter: list[float],
) -> dict[str, object]:
    threshold = abs(float(min_expected_move_pct))
    action_stats = _finite_distribution(move_values_after_action_gate, prefix="min_move_proxy_after_action_gate")
    filter_stats = _finite_distribution(move_values_after_filter, prefix="min_move_proxy_after_filter")
    action_max = float(action_stats["min_move_proxy_after_action_gate_max"])
    filter_max = float(filter_stats["min_move_proxy_after_filter_max"])
    unreachable = (
        threshold > 0.0
        and int(signal_count_after_entry_action_gates) > 0
        and int(signal_count_after_filter) > 0
        and int(signal_count_after_min_move) == 0
    )
    return {
        "min_expected_move_pct": float(threshold),
        "min_move_unreachable_after_action_gate": bool(unreachable),
        "min_move_reachable_after_action_gate": bool(threshold <= action_max) if threshold > 0.0 else True,
        "min_move_reachable_after_filter": bool(threshold <= filter_max) if threshold > 0.0 else True,
        "min_move_reachability_status": MIN_MOVE_UNREACHABLE if unreachable else "OK",
        **action_stats,
        **filter_stats,
    }


ENTRY_ACTION_ALLOW_COLUMNS = (
    "F001_RET1_ALLOW",
    "F002_RET3_ALLOW",
    "F003_RET6_ALLOW",
    "F004_RET12_ALLOW",
    "F005_RET24_ALLOW",
    "F006_HLSPREAD_ALLOW",
    "F007_RSTD20_ALLOW",
    "F008_ATR14_ALLOW",
    "F009_EMAGAP_ALLOW",
    "F010_EMASLOPE5_ALLOW",
    "F011_EMA200GAP_ALLOW",
    "F012_RSI14_ALLOW",
    "F013_MACDLINE_ALLOW",
    "F014_MACDSIGNAL_ALLOW",
    "F015_MACDHIST_ALLOW",
    "F016_ADX14_ALLOW",
    "F017_F018_STOCH14_ALLOW",
    "F019_VOLCHG_ALLOW",
    "F020_VOLZ20_ALLOW",
    "F021_DELTAVOL_ALLOW",
    "F022_OBVSLOPE5_ALLOW",
    "F023_MFI14_ALLOW",
    "F024_VWAPDIST_ALLOW",
    "F025_VPOCDIST60_ALLOW",
    "F026_BINSHARE60_ALLOW",
    "F027_CLUSTERSHARE60_ALLOW",
    "F028_VPOCSHARE60_ALLOW",
    "F029_VPOCDIST240_ALLOW",
    "F030_BINSHARE240_ALLOW",
    "F031_CLUSTERSHARE240_ALLOW",
    "F032_VPOCSHARE240_ALLOW",
    "F033_VPOCDRIFT20_ALLOW",
    "F034_CLUSTERRATIO_ALLOW",
    "F035_SUPPORTDIST_ALLOW",
    "F036_RESDIST_ALLOW",
    "F037_LEVELSTRENGTH_ALLOW",
    "F038_RANGEPOSE_ALLOW",
    "F039_CHANNELPOS_ALLOW",
    "F040_FIB0382DIST_ALLOW",
    "F041_FIB0618DIST_ALLOW",
    "F042_TPCONTEXT_ALLOW",
    "F043_SLCONTEXT_ALLOW",
    "F044_RRCONTEXT_ALLOW",
    "F045_BREAKOUT_ALLOW",
    "F046_FALSEBREAK_ALLOW",
    "F047_RETEST_ALLOW",
    "F048_SWINGHIGHBREAK_ALLOW",
    "F049_SWINGLOWBREAK_ALLOW",
    "F050_BOSUP_ALLOW",
    "F051_BOSDOWN_ALLOW",
    "F052_CHOCH_ALLOW",
    "F053_DOJI_ALLOW",
    "F054_INSIDEBAR_ALLOW",
    "F055_PINBULL_ALLOW",
    "F056_PINBEAR_ALLOW",
    "F057_HAMMER_ALLOW",
    "F058_SHOOTINGSTAR_ALLOW",
    "F059_ENGULFBULL_ALLOW",
    "F060_ENGULFBEAR_ALLOW",
    "F061_RSIBULLDIV_ALLOW",
    "F062_RSIBEARDIV_ALLOW",
    "F063_MACDBULLDIV_ALLOW",
    "F064_MACDBEARDIV_ALLOW",
    "F065_OBVBULLDIV_ALLOW",
    "F066_OBVBEARDIV_ALLOW",
    "F067_PATTERNSTRENGTH_ALLOW",
    "F068_PATTERNAGE_ALLOW",
    "F069_DOUBLEBOTTOM_ALLOW",
    "F070_DOUBLETOP_ALLOW",
    "F071_HEADSHOULDERS_ALLOW",
    "F072_INVHEADSHOULDERS_ALLOW",
    "F073_TRIANGLE_ALLOW",
    "F074_PENNANT_ALLOW",
    "F075_WEDGERISING_ALLOW",
    "F076_WEDGEFALLING_ALLOW",
    "F077_RANGEFLAG_ALLOW",
    "F078_PATTERNVOLCONF_ALLOW",
    "F079_PATTERNLEVELCONF_ALLOW",
    "F080_PATTERNLONG_ALLOW",
    "F081_PATTERNSHORT_ALLOW",
    "F082_PATTERNSLBUF_ALLOW",
    "F083_PATTERNTPLADDER_ALLOW",
)
F001_RET1_ALLOW_COLUMN = "F001_RET1_ALLOW"
SIDE_AWARE_ENTRY_ACTION_COLUMNS = {
    "F042_TPCONTEXT_ALLOW": ("F042_TPCONTEXT_ALLOW_LONG", "F042_TPCONTEXT_ALLOW_SHORT"),
    "F043_SLCONTEXT_ALLOW": ("F043_SLCONTEXT_ALLOW_LONG", "F043_SLCONTEXT_ALLOW_SHORT"),
    "F044_RRCONTEXT_ALLOW": ("F044_RRCONTEXT_ALLOW_LONG", "F044_RRCONTEXT_ALLOW_SHORT"),
    "F082_PATTERNSLBUF_ALLOW": ("F082_PATTERNSLBUF_ALLOW_LONG", "F082_PATTERNSLBUF_ALLOW_SHORT"),
    "F083_PATTERNTPLADDER_ALLOW": ("F083_PATTERNTPLADDER_ALLOW_LONG", "F083_PATTERNTPLADDER_ALLOW_SHORT"),
}
LONG_ONLY_ENTRY_ACTION_COLUMNS = {"F080_PATTERNLONG_ALLOW"}
SHORT_ONLY_ENTRY_ACTION_COLUMNS = {"F081_PATTERNSHORT_ALLOW"}
_ACTION_PARAM_PREFIX_RE = re.compile(r"^(F\d{3}(?:_F\d{3})?)_")


def _action_param_prefix(name: str) -> str | None:
    match = _ACTION_PARAM_PREFIX_RE.match(str(name or ""))
    return match.group(1) if match else None


ENTRY_ACTION_COLUMNS_BY_PREFIX = {
    prefix: tuple(col for col in ENTRY_ACTION_ALLOW_COLUMNS if _action_param_prefix(col) == prefix)
    for prefix in sorted({p for p in (_action_param_prefix(c) for c in ENTRY_ACTION_ALLOW_COLUMNS) if p})
}


def _normalize_entry_action_allow_columns(columns: list[str] | tuple[str, ...] | None) -> list[str] | None:
    if columns is None:
        return None
    known = set(ENTRY_ACTION_ALLOW_COLUMNS)
    out: list[str] = []
    for col in columns:
        name = str(col or "").strip()
        if name in known and name not in out:
            out.append(name)
    return out


def _entry_action_allow_columns(
    df: pd.DataFrame,
    *,
    active_entry_action_columns: list[str] | tuple[str, ...] | None = None,
    calibration_params: dict[str, float] | None = None,
) -> list[str]:
    present = [c for c in ENTRY_ACTION_ALLOW_COLUMNS if c in df.columns]
    requested = _normalize_entry_action_allow_columns(active_entry_action_columns)
    if requested is not None:
        return [c for c in requested if c in df.columns]

    prefixes = sorted(
        {
            p
            for p in (_action_param_prefix(k) for k in dict(calibration_params or {}).keys())
            if p in ENTRY_ACTION_COLUMNS_BY_PREFIX
        }
    )
    if prefixes:
        allowed = []
        for prefix in prefixes:
            allowed.extend(ENTRY_ACTION_COLUMNS_BY_PREFIX.get(prefix, ()))
        return [c for c in ENTRY_ACTION_ALLOW_COLUMNS if c in set(allowed) and c in df.columns]
    return present


def _entry_action_gate_diag(
    df: pd.DataFrame,
    *,
    columns: list[str],
    active_entry_action_columns: list[str] | tuple[str, ...] | None = None,
    calibration_params: dict[str, float] | None = None,
) -> dict[str, object]:
    present = [c for c in ENTRY_ACTION_ALLOW_COLUMNS if c in df.columns]
    requested = _normalize_entry_action_allow_columns(active_entry_action_columns)
    prefixes = sorted(
        {
            p
            for p in (_action_param_prefix(k) for k in dict(calibration_params or {}).keys())
            if p in ENTRY_ACTION_COLUMNS_BY_PREFIX
        }
    )
    min_confirmations = _entry_action_min_confirmations(columns, calibration_params=calibration_params)
    return {
        "entry_action_gate_active": bool(len(columns) > 0),
        "entry_action_gate_columns": list(columns),
        "entry_action_gate_policy": "n_of_m" if columns and min_confirmations < len(columns) else "and_all",
        "entry_action_min_confirmations": int(min_confirmations),
        "entry_action_total_columns": int(len(columns)),
        "entry_action_gate_present_columns": list(present),
        "entry_action_gate_requested_columns": list(requested or []),
        "entry_action_gate_inferred_prefixes": list(prefixes),
        "entry_action_gate_ignored_columns": [c for c in present if c not in set(columns)],
    }


def _entry_action_allow_series(df: pd.DataFrame, columns: list[str] | None = None) -> pd.Series | None:
    cols = list(columns if columns is not None else _entry_action_allow_columns(df))
    if not cols:
        return None
    allow, _counts, _applicable, _required = _entry_action_allow_series_with_counts(df, cols, calibration_params=None)
    return allow


def _entry_action_min_confirmations(
    columns: list[str],
    calibration_params: dict[str, float] | None = None,
) -> int:
    if not columns:
        return 0
    raw = dict(calibration_params or {}).get("entry_action_min_confirmations")
    if raw is None:
        return len(columns)
    try:
        value = int(round(float(raw)))
    except Exception:
        value = len(columns)
    return max(1, min(len(columns), value))


def _entry_action_column_allow_and_applicable(
    df: pd.DataFrame,
    col: str,
) -> tuple[pd.Series, pd.Series]:
    applicable = pd.Series(True, index=df.index)
    if col not in df.columns:
        return pd.Series(True, index=df.index), pd.Series(False, index=df.index)

    if "side" in df.columns and col in LONG_ONLY_ENTRY_ACTION_COLUMNS:
        col_values = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        side = pd.to_numeric(df["side"], errors="coerce").fillna(0.0)
        applicable = side > 0
        allow = pd.Series(True, index=df.index)
        allow.loc[applicable] = col_values.loc[applicable] >= 1.0
        return allow, applicable

    if "side" in df.columns and col in SHORT_ONLY_ENTRY_ACTION_COLUMNS:
        col_values = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        side = pd.to_numeric(df["side"], errors="coerce").fillna(0.0)
        applicable = side < 0
        allow = pd.Series(True, index=df.index)
        allow.loc[applicable] = col_values.loc[applicable] >= 1.0
        return allow, applicable

    if col in SIDE_AWARE_ENTRY_ACTION_COLUMNS and "side" in df.columns:
        long_col, short_col = SIDE_AWARE_ENTRY_ACTION_COLUMNS[col]
        base = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        side = pd.to_numeric(df["side"], errors="coerce").fillna(0.0)
        allow = pd.Series(True, index=df.index)
        applicable = side != 0
        if long_col in df.columns and short_col in df.columns:
            long_allow = pd.to_numeric(df[long_col], errors="coerce").fillna(0.0)
            short_allow = pd.to_numeric(df[short_col], errors="coerce").fillna(0.0)
            allow.loc[side > 0] = long_allow.loc[side > 0] >= 1.0
            allow.loc[side < 0] = short_allow.loc[side < 0] >= 1.0
            allow.loc[side == 0] = base.loc[side == 0] >= 1.0
            return allow, applicable

    return pd.to_numeric(df[col], errors="coerce").fillna(0.0) >= 1.0, applicable


def _entry_action_allow_series_with_counts(
    df: pd.DataFrame,
    columns: list[str],
    *,
    calibration_params: dict[str, float] | None = None,
) -> tuple[pd.Series, pd.Series, pd.Series, int]:
    allow = pd.Series(True, index=df.index)
    confirmation_count = pd.Series(0, index=df.index, dtype="int64")
    applicable_count = pd.Series(0, index=df.index, dtype="int64")
    for col in columns:
        col_allow, col_applicable = _entry_action_column_allow_and_applicable(df, col)
        confirmation_count += (col_allow & col_applicable).astype("int64")
        applicable_count += col_applicable.astype("int64")
    requested = _entry_action_min_confirmations(columns, calibration_params=calibration_params)
    required = applicable_count.clip(upper=int(requested))
    allow = (applicable_count <= 0) | (confirmation_count >= required)
    return allow, confirmation_count, applicable_count, int(requested)


def _apply_entry_action_allow_gates(
    df: pd.DataFrame,
    *,
    active_entry_action_columns: list[str] | tuple[str, ...] | None = None,
    calibration_params: dict[str, float] | None = None,
) -> list[str]:
    columns = _entry_action_allow_columns(
        df,
        active_entry_action_columns=active_entry_action_columns,
        calibration_params=calibration_params,
    )
    if not columns:
        return []
    allow, confirmation_count, applicable_count, requested = _entry_action_allow_series_with_counts(
        df,
        columns,
        calibration_params=calibration_params,
    )
    df["entry_action_confirmation_count"] = confirmation_count
    df["entry_action_applicable_count"] = applicable_count
    df["entry_action_min_confirmations"] = int(requested)
    df.loc[(df["side"] != 0) & ~allow, "side"] = 0
    return columns


def _entry_action_row_allows(
    row: pd.Series,
    columns: list[str] | None = None,
    *,
    side: int | None = None,
    calibration_params: dict[str, float] | None = None,
) -> bool:
    cols = list(columns if columns is not None else [c for c in ENTRY_ACTION_ALLOW_COLUMNS if c in row.index])
    if not cols:
        return True
    try:
        confirmations = 0
        applicable = 0
        for col in cols:
            if col in LONG_ONLY_ENTRY_ACTION_COLUMNS and side is not None and int(side) <= 0:
                continue
            if col in SHORT_ONLY_ENTRY_ACTION_COLUMNS and side is not None and int(side) >= 0:
                continue
            check_col = col
            if col in SIDE_AWARE_ENTRY_ACTION_COLUMNS:
                long_col, short_col = SIDE_AWARE_ENTRY_ACTION_COLUMNS[col]
                if side is not None and int(side) > 0 and long_col in row.index:
                    check_col = long_col
                elif side is not None and int(side) < 0 and short_col in row.index:
                    check_col = short_col
            applicable += 1
            if float(row.get(check_col, 0.0)) >= 1.0:
                confirmations += 1
        if applicable <= 0:
            return True
        requested = _entry_action_min_confirmations(cols, calibration_params=calibration_params)
        return confirmations >= min(applicable, requested)
    except Exception:
        return False


def _trend_thresholds(calibration_params: dict[str, float] | None) -> dict[str, float]:
    return {
        "adx_threshold": max(0.0, _calib_value(calibration_params, "adx_threshold", 18.0)),
        "threshold_fine": max(0.0, _calib_value(calibration_params, "threshold_fine", 0.0015)),
        "imbalance_threshold": max(0.0, _calib_value(calibration_params, "imbalance_threshold", 0.35)),
        "spread_z_threshold": max(0.01, _calib_value(calibration_params, "spread_z_threshold", 1.2)),
    }


_TREND_FILTER_REQUIRED_COLUMNS: dict[str, tuple[str, ...]] = {
    "none": (),
    "ema_gap_sign": ("ema_gap",),
    "ema_cross_20_50": ("ema20", "ema50"),
    "ema_cross_20_200": ("ema20", "ema200"),
    "ema_stack_bull": ("ema20", "ema50", "ema200"),
    "channel_breakout_50": ("trend_channel_pos",),
    "adx_trend_18": ("adx14", "ema_gap"),
    "fib_retrace_0382_0618_trend_resume": ("fib_0382_distance", "fib_0618_distance", "ema_gap"),
    "fib_extension_targets": ("fib_0618_distance", "rr_context_estimate", "ema_gap", "breakout_flag"),
    "swing_hl_hh_long": ("swing_high_break_flag", "ema_slope_5"),
    "swing_lh_ll_short": ("swing_low_break_flag", "ema_slope_5"),
    "bos_continuation_confirm": ("bos_up_flag", "bos_down_flag", "retest_flag"),
    "min_max_range_revert": ("position_in_range", "breakout_flag"),
    "max_low_pullback_long": ("support_distance", "trend_channel_pos", "ema_gap"),
    "hvn_lvn_density_reaction": ("density_vpoc_distance_60", "density_cluster_share_60", "density_cluster_ratio_60_240", "ema_gap"),
    "volume_profile_poc_vah_val_retest": ("density_vpoc_distance_60", "density_vpoc_share_60", "retest_flag", "ema_gap"),
    "value_area_rotation_vs_breakout": ("position_in_range", "breakout_flag", "density_bin_share_60", "ema_gap"),
    "wedge_breakout_plus_profile_acceptance": ("trend_channel_pos", "breakout_flag", "density_vpoc_share_60", "ema_gap"),
    "orderbook_imbalance_l1_l50": ("density_vpoc_drift_20", "ema_gap"),
    "spread_pressure_and_delta_absorption": ("hl_spread", "rolling_std_20", "vol_chg", "ema_gap"),
}


def _trend_filter_required_columns(trend_filter: str) -> tuple[str, ...]:
    tf = _normalize_trend_filter(trend_filter)
    return _TREND_FILTER_REQUIRED_COLUMNS.get(tf, ())


def _trend_filter_missing_columns(df: pd.DataFrame, trend_filter: str) -> list[str]:
    req = _trend_filter_required_columns(trend_filter)
    return [c for c in req if c not in df.columns]


def _apply_trend_filter_vectorized(
    df: pd.DataFrame,
    *,
    trend_filter: str,
    min_abs_ema_gap: float,
    calibration_params: dict[str, float] | None = None,
) -> None:
    tf = _normalize_trend_filter(trend_filter)
    th = _trend_thresholds(calibration_params)
    adx_threshold = float(th["adx_threshold"])
    threshold_fine = float(th["threshold_fine"])
    imbalance_threshold = float(th["imbalance_threshold"])
    spread_z_threshold = float(th["spread_z_threshold"])
    if tf == "none":
        return
    if tf == "ema_gap_sign":
        if "ema_gap" in df.columns:
            eg = pd.to_numeric(df["ema_gap"], errors="coerce").fillna(0.0)
            df.loc[(df["side"] > 0) & (eg <= 0.0), "side"] = 0
            df.loc[(df["side"] < 0) & (eg >= 0.0), "side"] = 0
    elif tf == "ema_cross_20_50":
        if "ema20" in df.columns and "ema50" in df.columns:
            e20 = pd.to_numeric(df["ema20"], errors="coerce")
            e50 = pd.to_numeric(df["ema50"], errors="coerce")
            df.loc[(df["side"] > 0) & ~(e20 > e50), "side"] = 0
            df.loc[(df["side"] < 0) & ~(e20 < e50), "side"] = 0
    elif tf == "ema_cross_20_200":
        if "ema20" in df.columns and "ema200" in df.columns:
            e20 = pd.to_numeric(df["ema20"], errors="coerce")
            e200 = pd.to_numeric(df["ema200"], errors="coerce")
            df.loc[(df["side"] > 0) & ~(e20 > e200), "side"] = 0
            df.loc[(df["side"] < 0) & ~(e20 < e200), "side"] = 0
    elif tf == "ema_stack_bull":
        has_cols = {"ema20", "ema50", "ema200"}.issubset(df.columns)
        if has_cols:
            e20 = pd.to_numeric(df["ema20"], errors="coerce")
            e50 = pd.to_numeric(df["ema50"], errors="coerce")
            e200 = pd.to_numeric(df["ema200"], errors="coerce")
            df.loc[(df["side"] > 0) & ~((e20 > e50) & (e50 > e200)), "side"] = 0
            df.loc[(df["side"] < 0) & ~((e20 < e50) & (e50 < e200)), "side"] = 0
    elif tf == "channel_breakout_50":
        if "trend_channel_pos" in df.columns:
            pos = pd.to_numeric(df["trend_channel_pos"], errors="coerce")
            df.loc[(df["side"] > 0) & ~(pos >= 0.55), "side"] = 0
            df.loc[(df["side"] < 0) & ~(pos <= 0.45), "side"] = 0
    elif tf == "adx_trend_18":
        if "adx14" in df.columns:
            adx = pd.to_numeric(df["adx14"], errors="coerce")
            df.loc[(df["side"] != 0) & ~(adx >= adx_threshold), "side"] = 0
        if "ema_gap" in df.columns:
            eg = pd.to_numeric(df["ema_gap"], errors="coerce").fillna(0.0)
            df.loc[(df["side"] > 0) & (eg <= 0.0), "side"] = 0
            df.loc[(df["side"] < 0) & (eg >= 0.0), "side"] = 0
    elif tf == "fib_retrace_0382_0618_trend_resume":
        has_cols = {"fib_0382_distance", "fib_0618_distance", "ema_gap"}.issubset(df.columns)
        if has_cols:
            d382 = pd.to_numeric(df["fib_0382_distance"], errors="coerce")
            d618 = pd.to_numeric(df["fib_0618_distance"], errors="coerce")
            eg = pd.to_numeric(df["ema_gap"], errors="coerce").fillna(0.0)
            near = (d382.abs() <= threshold_fine * 2.0) | (d618.abs() <= threshold_fine * 2.0)
            df.loc[(df["side"] > 0) & ~(near & (eg > 0.0)), "side"] = 0
            df.loc[(df["side"] < 0) & ~(near & (eg < 0.0)), "side"] = 0
    elif tf == "fib_extension_targets":
        has_cols = {"fib_0618_distance", "rr_context_estimate", "ema_gap", "breakout_flag"}.issubset(df.columns)
        if has_cols:
            d618 = pd.to_numeric(df["fib_0618_distance"], errors="coerce")
            rr = pd.to_numeric(df["rr_context_estimate"], errors="coerce")
            eg = pd.to_numeric(df["ema_gap"], errors="coerce").fillna(0.0)
            brk = pd.to_numeric(df["breakout_flag"], errors="coerce").fillna(0.0)
            long_ok = (rr >= 1.0) & (eg > 0.0) & (d618 > 0.0) & (brk > 0.0)
            short_ok = (rr >= 1.0) & (eg < 0.0) & (d618 < 0.0) & (brk > 0.0)
            df.loc[(df["side"] > 0) & ~long_ok, "side"] = 0
            df.loc[(df["side"] < 0) & ~short_ok, "side"] = 0
    elif tf == "swing_hl_hh_long":
        has_cols = {"swing_high_break_flag", "ema_slope_5"}.issubset(df.columns)
        if has_cols:
            shb = pd.to_numeric(df["swing_high_break_flag"], errors="coerce").fillna(0.0)
            es = pd.to_numeric(df["ema_slope_5"], errors="coerce").fillna(0.0)
            long_ok = (shb > 0.0) & (es > 0.0)
            df.loc[df["side"] < 0, "side"] = 0
            df.loc[(df["side"] > 0) & ~long_ok, "side"] = 0
    elif tf == "swing_lh_ll_short":
        has_cols = {"swing_low_break_flag", "ema_slope_5"}.issubset(df.columns)
        if has_cols:
            slb = pd.to_numeric(df["swing_low_break_flag"], errors="coerce").fillna(0.0)
            es = pd.to_numeric(df["ema_slope_5"], errors="coerce").fillna(0.0)
            short_ok = (slb > 0.0) & (es < 0.0)
            df.loc[df["side"] > 0, "side"] = 0
            df.loc[(df["side"] < 0) & ~short_ok, "side"] = 0
    elif tf == "bos_continuation_confirm":
        has_cols = {"bos_up_flag", "bos_down_flag", "retest_flag"}.issubset(df.columns)
        if has_cols:
            up = pd.to_numeric(df["bos_up_flag"], errors="coerce").fillna(0.0)
            dn = pd.to_numeric(df["bos_down_flag"], errors="coerce").fillna(0.0)
            rt = pd.to_numeric(df["retest_flag"], errors="coerce").fillna(0.0)
            long_ok = (up > 0.0) & (rt > 0.0)
            short_ok = (dn > 0.0) & (rt > 0.0)
            df.loc[(df["side"] > 0) & ~long_ok, "side"] = 0
            df.loc[(df["side"] < 0) & ~short_ok, "side"] = 0
    elif tf == "min_max_range_revert":
        has_cols = {"position_in_range", "breakout_flag"}.issubset(df.columns)
        if has_cols:
            pos = pd.to_numeric(df["position_in_range"], errors="coerce")
            brk = pd.to_numeric(df["breakout_flag"], errors="coerce").fillna(0.0)
            long_ok = (pos <= 0.15) & (brk <= 0.0)
            short_ok = (pos >= 0.85) & (brk <= 0.0)
            df.loc[(df["side"] > 0) & ~long_ok, "side"] = 0
            df.loc[(df["side"] < 0) & ~short_ok, "side"] = 0
    elif tf == "max_low_pullback_long":
        has_cols = {"support_distance", "trend_channel_pos", "ema_gap"}.issubset(df.columns)
        if has_cols:
            sd = pd.to_numeric(df["support_distance"], errors="coerce")
            tcp = pd.to_numeric(df["trend_channel_pos"], errors="coerce")
            eg = pd.to_numeric(df["ema_gap"], errors="coerce").fillna(0.0)
            long_ok = (sd <= max(0.01, threshold_fine * 6.0)) & (tcp <= imbalance_threshold) & (eg > 0.0)
            df.loc[df["side"] < 0, "side"] = 0
            df.loc[(df["side"] > 0) & ~long_ok, "side"] = 0
    elif tf == "hvn_lvn_density_reaction":
        has_cols = {"density_vpoc_distance_60", "density_cluster_share_60", "density_cluster_ratio_60_240", "ema_gap"}.issubset(df.columns)
        if has_cols:
            d60 = pd.to_numeric(df["density_vpoc_distance_60"], errors="coerce")
            c60 = pd.to_numeric(df["density_cluster_share_60"], errors="coerce")
            r60 = pd.to_numeric(df["density_cluster_ratio_60_240"], errors="coerce")
            eg = pd.to_numeric(df["ema_gap"], errors="coerce").fillna(0.0)
            near_hvn = d60.abs() <= max(0.002, threshold_fine * 2.0)
            long_ok = near_hvn & (c60 >= imbalance_threshold) & (r60 >= 1.0) & (eg > 0.0)
            short_ok = near_hvn & (c60 >= imbalance_threshold) & (r60 >= 1.0) & (eg < 0.0)
            df.loc[(df["side"] > 0) & ~long_ok, "side"] = 0
            df.loc[(df["side"] < 0) & ~short_ok, "side"] = 0
    elif tf == "volume_profile_poc_vah_val_retest":
        has_cols = {"density_vpoc_distance_60", "density_vpoc_share_60", "retest_flag", "ema_gap"}.issubset(df.columns)
        if has_cols:
            d60 = pd.to_numeric(df["density_vpoc_distance_60"], errors="coerce")
            vp = pd.to_numeric(df["density_vpoc_share_60"], errors="coerce")
            rt = pd.to_numeric(df["retest_flag"], errors="coerce").fillna(0.0)
            eg = pd.to_numeric(df["ema_gap"], errors="coerce").fillna(0.0)
            near_poc = d60.abs() <= max(0.002, threshold_fine * 2.0)
            long_ok = near_poc & (vp >= max(0.10, imbalance_threshold * 0.3)) & (rt > 0.0) & (eg > 0.0)
            short_ok = near_poc & (vp >= max(0.10, imbalance_threshold * 0.3)) & (rt > 0.0) & (eg < 0.0)
            df.loc[(df["side"] > 0) & ~long_ok, "side"] = 0
            df.loc[(df["side"] < 0) & ~short_ok, "side"] = 0
    elif tf == "value_area_rotation_vs_breakout":
        has_cols = {"position_in_range", "breakout_flag", "density_bin_share_60", "ema_gap"}.issubset(df.columns)
        if has_cols:
            pos = pd.to_numeric(df["position_in_range"], errors="coerce")
            brk = pd.to_numeric(df["breakout_flag"], errors="coerce").fillna(0.0)
            bs = pd.to_numeric(df["density_bin_share_60"], errors="coerce")
            eg = pd.to_numeric(df["ema_gap"], errors="coerce").fillna(0.0)
            long_rot = (brk <= 0.0) & (pos <= 0.20) & (bs >= 0.12)
            long_brk = (brk > 0.0) & (pos >= 0.55) & (bs <= 0.20) & (eg > 0.0)
            short_rot = (brk <= 0.0) & (pos >= 0.80) & (bs >= 0.12)
            short_brk = (brk > 0.0) & (pos <= 0.45) & (bs <= 0.20) & (eg < 0.0)
            df.loc[(df["side"] > 0) & ~(long_rot | long_brk), "side"] = 0
            df.loc[(df["side"] < 0) & ~(short_rot | short_brk), "side"] = 0
    elif tf == "wedge_breakout_plus_profile_acceptance":
        has_cols = {"trend_channel_pos", "breakout_flag", "density_vpoc_share_60", "ema_gap"}.issubset(df.columns)
        if has_cols:
            tcp = pd.to_numeric(df["trend_channel_pos"], errors="coerce")
            brk = pd.to_numeric(df["breakout_flag"], errors="coerce").fillna(0.0)
            vp = pd.to_numeric(df["density_vpoc_share_60"], errors="coerce")
            eg = pd.to_numeric(df["ema_gap"], errors="coerce").fillna(0.0)
            long_ok = (brk > 0.0) & (tcp >= 0.55) & (vp >= 0.10) & (eg > 0.0)
            short_ok = (brk > 0.0) & (tcp <= 0.45) & (vp >= 0.10) & (eg < 0.0)
            df.loc[(df["side"] > 0) & ~long_ok, "side"] = 0
            df.loc[(df["side"] < 0) & ~short_ok, "side"] = 0
    elif tf == "orderbook_imbalance_l1_l50":
        # Proxy from available microstructure-derived features in feature frame.
        has_cols = {"density_vpoc_drift_20", "ema_gap"}.issubset(df.columns)
        if has_cols:
            drift = pd.to_numeric(df["density_vpoc_drift_20"], errors="coerce")
            eg = pd.to_numeric(df["ema_gap"], errors="coerce").fillna(0.0)
            long_ok = (drift > 0.0) & (eg > 0.0)
            short_ok = (drift < 0.0) & (eg < 0.0)
            df.loc[(df["side"] > 0) & ~long_ok, "side"] = 0
            df.loc[(df["side"] < 0) & ~short_ok, "side"] = 0
    elif tf == "spread_pressure_and_delta_absorption":
        # Proxy from spread/volatility/volume pressure context available in dataset.
        has_cols = {"hl_spread", "rolling_std_20", "vol_chg", "ema_gap"}.issubset(df.columns)
        if has_cols:
            spread = pd.to_numeric(df["hl_spread"], errors="coerce")
            volstd = pd.to_numeric(df["rolling_std_20"], errors="coerce")
            vchg = pd.to_numeric(df["vol_chg"], errors="coerce")
            eg = pd.to_numeric(df["ema_gap"], errors="coerce").fillna(0.0)
            calm_spread = spread <= (volstd * spread_z_threshold)
            long_ok = calm_spread & (vchg > 0.0) & (eg > 0.0)
            short_ok = calm_spread & (vchg < 0.0) & (eg < 0.0)
            df.loc[(df["side"] > 0) & ~long_ok, "side"] = 0
            df.loc[(df["side"] < 0) & ~short_ok, "side"] = 0

    if float(min_abs_ema_gap) > 0 and "ema_gap" in df.columns:
        eg = pd.to_numeric(df["ema_gap"], errors="coerce").fillna(0.0)
        df.loc[eg.abs() < float(min_abs_ema_gap), "side"] = 0


def _trend_row_allows(
    row: pd.Series,
    *,
    side: int,
    trend_filter: str,
    min_abs_ema_gap: float,
    calibration_params: dict[str, float] | None = None,
) -> bool:
    tf = _normalize_trend_filter(trend_filter)
    if side == 0 or tf == "none":
        return True
    th = _trend_thresholds(calibration_params)
    adx_threshold = float(th["adx_threshold"])
    threshold_fine = float(th["threshold_fine"])
    imbalance_threshold = float(th["imbalance_threshold"])
    spread_z_threshold = float(th["spread_z_threshold"])
    eg = float(row.get("ema_gap", 0.0) or 0.0)
    if float(min_abs_ema_gap) > 0 and abs(eg) < float(min_abs_ema_gap):
        return False
    if tf == "ema_gap_sign":
        return (eg > 0.0) if side > 0 else (eg < 0.0)
    if tf == "ema_cross_20_50":
        e20 = row.get("ema20", None)
        e50 = row.get("ema50", None)
        if e20 is None or e50 is None or pd.isna(e20) or pd.isna(e50):
            return True
        return (float(e20) > float(e50)) if side > 0 else (float(e20) < float(e50))
    if tf == "ema_cross_20_200":
        e20 = row.get("ema20", None)
        e200 = row.get("ema200", None)
        if e20 is None or e200 is None or pd.isna(e20) or pd.isna(e200):
            return True
        return (float(e20) > float(e200)) if side > 0 else (float(e20) < float(e200))
    if tf == "ema_stack_bull":
        e20 = row.get("ema20", None)
        e50 = row.get("ema50", None)
        e200 = row.get("ema200", None)
        if any(x is None or pd.isna(x) for x in (e20, e50, e200)):
            return True
        if side > 0:
            return (float(e20) > float(e50)) and (float(e50) > float(e200))
        return (float(e20) < float(e50)) and (float(e50) < float(e200))
    if tf == "channel_breakout_50":
        pos = row.get("trend_channel_pos", None)
        if pos is None or pd.isna(pos):
            return True
        return (float(pos) >= 0.55) if side > 0 else (float(pos) <= 0.45)
    if tf == "adx_trend_18":
        adx = row.get("adx14", None)
        if adx is not None and not pd.isna(adx) and float(adx) < adx_threshold:
            return False
        return (eg > 0.0) if side > 0 else (eg < 0.0)
    if tf == "fib_retrace_0382_0618_trend_resume":
        d382 = row.get("fib_0382_distance", None)
        d618 = row.get("fib_0618_distance", None)
        if d382 is None or d618 is None or pd.isna(d382) or pd.isna(d618):
            return True
        near = (abs(float(d382)) <= threshold_fine * 2.0) or (abs(float(d618)) <= threshold_fine * 2.0)
        return (near and eg > 0.0) if side > 0 else (near and eg < 0.0)
    if tf == "fib_extension_targets":
        d618 = row.get("fib_0618_distance", None)
        rr = row.get("rr_context_estimate", None)
        brk = row.get("breakout_flag", None)
        if d618 is None or rr is None or brk is None or pd.isna(d618) or pd.isna(rr) or pd.isna(brk):
            return True
        if float(rr) < 1.0 or float(brk) <= 0.0:
            return False
        return (eg > 0.0 and float(d618) > 0.0) if side > 0 else (eg < 0.0 and float(d618) < 0.0)
    if tf == "swing_hl_hh_long":
        if side < 0:
            return False
        shb = row.get("swing_high_break_flag", None)
        es = row.get("ema_slope_5", None)
        if shb is None or es is None or pd.isna(shb) or pd.isna(es):
            return True
        return float(shb) > 0.0 and float(es) > 0.0
    if tf == "swing_lh_ll_short":
        if side > 0:
            return False
        slb = row.get("swing_low_break_flag", None)
        es = row.get("ema_slope_5", None)
        if slb is None or es is None or pd.isna(slb) or pd.isna(es):
            return True
        return float(slb) > 0.0 and float(es) < 0.0
    if tf == "bos_continuation_confirm":
        up = row.get("bos_up_flag", None)
        dn = row.get("bos_down_flag", None)
        rt = row.get("retest_flag", None)
        if up is None or dn is None or rt is None or pd.isna(up) or pd.isna(dn) or pd.isna(rt):
            return True
        if side > 0:
            return float(up) > 0.0 and float(rt) > 0.0
        return float(dn) > 0.0 and float(rt) > 0.0
    if tf == "min_max_range_revert":
        pos = row.get("position_in_range", None)
        brk = row.get("breakout_flag", None)
        if pos is None or brk is None or pd.isna(pos) or pd.isna(brk):
            return True
        if float(brk) > 0.0:
            return False
        return float(pos) <= 0.15 if side > 0 else float(pos) >= 0.85
    if tf == "max_low_pullback_long":
        if side < 0:
            return False
        sd = row.get("support_distance", None)
        tcp = row.get("trend_channel_pos", None)
        if sd is None or tcp is None or pd.isna(sd) or pd.isna(tcp):
            return True
        return float(sd) <= max(0.01, threshold_fine * 6.0) and float(tcp) <= imbalance_threshold and eg > 0.0
    if tf == "hvn_lvn_density_reaction":
        d60 = row.get("density_vpoc_distance_60", None)
        c60 = row.get("density_cluster_share_60", None)
        r60 = row.get("density_cluster_ratio_60_240", None)
        if d60 is None or c60 is None or r60 is None or pd.isna(d60) or pd.isna(c60) or pd.isna(r60):
            return True
        near_hvn = abs(float(d60)) <= max(0.002, threshold_fine * 2.0)
        if not near_hvn or float(c60) < imbalance_threshold or float(r60) < 1.0:
            return False
        return eg > 0.0 if side > 0 else eg < 0.0
    if tf == "volume_profile_poc_vah_val_retest":
        d60 = row.get("density_vpoc_distance_60", None)
        vp = row.get("density_vpoc_share_60", None)
        rt = row.get("retest_flag", None)
        if d60 is None or vp is None or rt is None or pd.isna(d60) or pd.isna(vp) or pd.isna(rt):
            return True
        near_poc = abs(float(d60)) <= max(0.002, threshold_fine * 2.0)
        if not near_poc or float(vp) < max(0.10, imbalance_threshold * 0.3) or float(rt) <= 0.0:
            return False
        return eg > 0.0 if side > 0 else eg < 0.0
    if tf == "value_area_rotation_vs_breakout":
        pos = row.get("position_in_range", None)
        brk = row.get("breakout_flag", None)
        bs = row.get("density_bin_share_60", None)
        if pos is None or brk is None or bs is None or pd.isna(pos) or pd.isna(brk) or pd.isna(bs):
            return True
        posf = float(pos)
        brkf = float(brk)
        bsf = float(bs)
        if side > 0:
            long_rot = (brkf <= 0.0) and (posf <= 0.20) and (bsf >= 0.12)
            long_brk = (brkf > 0.0) and (posf >= 0.55) and (bsf <= 0.20) and (eg > 0.0)
            return long_rot or long_brk
        short_rot = (brkf <= 0.0) and (posf >= 0.80) and (bsf >= 0.12)
        short_brk = (brkf > 0.0) and (posf <= 0.45) and (bsf <= 0.20) and (eg < 0.0)
        return short_rot or short_brk
    if tf == "wedge_breakout_plus_profile_acceptance":
        tcp = row.get("trend_channel_pos", None)
        brk = row.get("breakout_flag", None)
        vp = row.get("density_vpoc_share_60", None)
        if tcp is None or brk is None or vp is None or pd.isna(tcp) or pd.isna(brk) or pd.isna(vp):
            return True
        tcpf = float(tcp)
        brkf = float(brk)
        vpf = float(vp)
        if brkf <= 0.0 or vpf < 0.10:
            return False
        return (tcpf >= 0.55 and eg > 0.0) if side > 0 else (tcpf <= 0.45 and eg < 0.0)
    if tf == "orderbook_imbalance_l1_l50":
        drift = row.get("density_vpoc_drift_20", None)
        if drift is None or pd.isna(drift):
            return True
        return (float(drift) > 0.0 and eg > 0.0) if side > 0 else (float(drift) < 0.0 and eg < 0.0)
    if tf == "spread_pressure_and_delta_absorption":
        spread = row.get("hl_spread", None)
        volstd = row.get("rolling_std_20", None)
        vchg = row.get("vol_chg", None)
        if spread is None or volstd is None or vchg is None or pd.isna(spread) or pd.isna(volstd) or pd.isna(vchg):
            return True
        if float(spread) > float(volstd) * spread_z_threshold:
            return False
        return (float(vchg) > 0.0 and eg > 0.0) if side > 0 else (float(vchg) < 0.0 and eg < 0.0)
    return True


def _summarize(df: pd.DataFrame, *, fee_bps: float, slippage_bps: float, stop_loss_pct: float, take_profit_pct: float,
               min_expected_move_pct: float, min_tp_reach_prob: float, tp_min_factor: float, dynamic_tp_enabled: bool, cooldown_bars: int,
               trend_filter: str, min_abs_ema_gap: float, notional_usd: float, leverage: float, mode: str,
               execution_mode: str, order_type: str, hold_bars: int, limit_offset_bps: float,
               timeout_exit_enabled: bool = True, trend_filter_diagnostics: dict | None = None) -> dict:
    active = df[df["side"] != 0].copy()
    trades = int(len(active))
    hit_rate = float((active["net_return"] > 0).mean()) if trades > 0 else 0.0
    avg_trade_return = float(active["net_return"].mean()) if trades > 0 else 0.0
    net_return_pct = float((df["equity_curve"].iloc[-1] - 1.0) * 100.0) if len(df) else 0.0

    running_peak = df["equity_curve"].cummax()
    drawdown = df["equity_curve"] / running_peak - 1.0
    max_drawdown_pct = float(drawdown.min() * 100.0) if len(drawdown) else 0.0

    std = float(df["net_return"].std(ddof=0))
    sharpe = float((df["net_return"].mean() / std) * np.sqrt(len(df))) if std > 0 else 0.0
    downside = df["net_return"].clip(upper=0.0)
    downside_std = float(np.sqrt(np.mean(np.square(downside)))) if len(df) else 0.0
    sortino = float((df["net_return"].mean() / downside_std) * np.sqrt(len(df))) if downside_std > 0 else 0.0

    cagr = 0.0
    if "open_time_utc" in df.columns and len(df) > 1:
        ts = pd.to_datetime(df["open_time_utc"], utc=True, errors="coerce").dropna().sort_values()
        if len(ts) > 1:
            years = max((ts.iloc[-1] - ts.iloc[0]).total_seconds() / (365.25 * 24 * 3600.0), 1e-9)
            final_eq = float(df["equity_curve"].iloc[-1]) if len(df) else 1.0
            if final_eq > 0:
                expo = math.log(final_eq) / years
                if expo > 700:
                    cagr = float("inf")
                elif expo < -700:
                    cagr = -1.0
                else:
                    cagr = float(math.exp(expo) - 1.0)

    no_trade_ratio = float((df["side"] == 0).mean()) if len(df) else 1.0
    df["_date"] = pd.to_datetime(df["open_time_utc"], utc=True).dt.strftime("%Y-%m-%d")
    trades_by_day = df.groupby("_date")["side"].apply(lambda s: int((s != 0).sum()))
    no_trade_ratio_days = float((trades_by_day == 0).mean()) if len(trades_by_day) else 1.0
    trades_per_day_avg = float(trades_by_day.mean()) if len(trades_by_day) else 0.0
    trades_per_day_min = int(trades_by_day.min()) if len(trades_by_day) else 0
    trades_per_day_max = int(trades_by_day.max()) if len(trades_by_day) else 0

    summary = {
        "trades": trades,
        "hit_rate": hit_rate,
        "avg_trade_return": avg_trade_return,
        "net_return_pct": net_return_pct,
        "max_drawdown_pct": max_drawdown_pct,
        "sharpe_like": sharpe,
        "sortino": sortino,
        "cagr": cagr,
        "no_trade_ratio": no_trade_ratio,
        "no_trade_ratio_days": no_trade_ratio_days,
        "trades_per_day_avg": trades_per_day_avg,
        "trades_per_day_min": trades_per_day_min,
        "trades_per_day_max": trades_per_day_max,
        "signal_mode": mode,
        "leverage": leverage,
        "fee_bps": fee_bps,
        "slippage_bps": slippage_bps,
        "stop_loss_pct": stop_loss_pct,
        "take_profit_pct": take_profit_pct,
        "min_expected_move_pct": min_expected_move_pct,
        "min_tp_reach_prob": float(min_tp_reach_prob),
        "tp_min_factor": float(tp_min_factor),
        "dynamic_tp_enabled": bool(dynamic_tp_enabled),
        "cooldown_bars": int(cooldown_bars),
        "trend_filter": str(trend_filter),
        "min_abs_ema_gap": float(min_abs_ema_gap),
        "notional_usd": float(notional_usd),
        "effective_notional_usd": float(notional_usd) * float(leverage),
        "avg_ev": float(df.loc[df["side"] != 0, "ev"].mean()) if trades > 0 else 0.0,
        "avg_ev_usd": float(df.loc[df["side"] != 0, "ev_usd"].mean()) if trades > 0 else 0.0,
        "avg_trade_pnl_usd": float(active["net_pnl_usd"].mean()) if trades > 0 else 0.0,
        "net_pnl_total_usd": float(df["net_pnl_usd"].sum()) if len(df) else 0.0,
        "time_to_target_bars_avg": float(df["time_to_target_bars"].dropna().mean()) if df["time_to_target_bars"].notna().any() else None,
        "time_to_target_sec_avg": float(df["time_to_target_sec"].dropna().mean()) if df["time_to_target_sec"].notna().any() else None,
        "execution_mode": str(execution_mode),
        "order_type": str(order_type),
        "hold_bars": int(hold_bars),
        "timeout_exit_enabled": bool(timeout_exit_enabled),
        "limit_offset_bps": float(limit_offset_bps),
    }
    if isinstance(trend_filter_diagnostics, dict):
        summary["trend_filter_diagnostics"] = trend_filter_diagnostics
    return summary


def _run_research_backtest(
    df: pd.DataFrame,
    *,
    p_enter_long: float,
    p_enter_short: float,
    fee_bps: float,
    slippage_bps: float,
    stop_loss_pct: float,
    take_profit_pct: float,
    min_expected_move_pct: float,
    min_tp_reach_prob: float,
    tp_min_factor: float,
    dynamic_tp_enabled: bool,
    cooldown_bars: int,
    trend_filter: str,
    min_abs_ema_gap: float,
    notional_usd: float,
    leverage: float,
    signal_mode: str,
    hold_bars: int,
    limit_offset_bps: float,
    require_trend_filter_features: bool,
    calibration_params: dict[str, float] | None = None,
    active_entry_action_columns: list[str] | tuple[str, ...] | None = None,
    timeout_exit_enabled: bool = True,
) -> tuple[pd.DataFrame, dict]:
    mode = _normalize_signal_mode(signal_mode)
    trend_filter_norm = _normalize_trend_filter(trend_filter)
    trend_filter_required_columns = list(_trend_filter_required_columns(trend_filter_norm))
    trend_filter_missing_columns = _trend_filter_missing_columns(df, trend_filter_norm)
    if bool(require_trend_filter_features) and trend_filter_norm != "none" and trend_filter_missing_columns:
        raise RuntimeError(
            "trend_filter requires feature columns that are missing in OOF/backtest frame: "
            f"trend_filter={trend_filter_norm}, missing_columns={trend_filter_missing_columns}"
        )
    signal_count_raw = int(((df["prob_up"] >= p_enter_long) | (df["prob_up"] <= p_enter_short)).sum())
    df["side"] = 0
    df.loc[df["prob_up"] >= p_enter_long, "side"] = 1
    df.loc[df["prob_up"] <= p_enter_short, "side"] = -1

    if mode == "long_only":
        df.loc[df["side"] < 0, "side"] = 0
    elif mode == "short_only":
        df.loc[df["side"] > 0, "side"] = 0
    signal_count_after_mode = int((df["side"] != 0).sum())

    entry_action_gate_columns = _apply_entry_action_allow_gates(
        df,
        active_entry_action_columns=active_entry_action_columns,
        calibration_params=calibration_params,
    )
    signal_count_after_entry_action_gates = int((df["side"] != 0).sum())
    future_abs = np.abs(df.get("future_return", pd.Series(np.zeros(len(df)), index=df.index))).astype(float)
    move_values_after_action_gate = future_abs.loc[df["side"] != 0].astype(float).tolist()
    f001_ret1_gate_active = F001_RET1_ALLOW_COLUMN in entry_action_gate_columns
    signal_count_after_f001_ret1_gate = signal_count_after_entry_action_gates

    if int(cooldown_bars) > 0 and len(df) > 0:
        cd = int(cooldown_bars)
        side_vals = df["side"].to_numpy(dtype=int, copy=True)
        lock = 0
        for i in range(len(side_vals)):
            if lock > 0:
                side_vals[i] = 0
                lock -= 1
                continue
            if side_vals[i] != 0:
                lock = cd
        df["side"] = side_vals
    signal_count_after_cooldown = int((df["side"] != 0).sum())

    _apply_trend_filter_vectorized(
        df,
        trend_filter=str(trend_filter),
        min_abs_ema_gap=float(min_abs_ema_gap),
        calibration_params=calibration_params,
    )
    signal_count_after_trend_filter = int((df["side"] != 0).sum())
    move_values_after_filter = future_abs.loc[df["side"] != 0].astype(float).tolist()

    if min_expected_move_pct > 0 and "future_return" in df.columns:
        min_move = abs(min_expected_move_pct)
        df.loc[df["future_return"].abs() < min_move, "side"] = 0
    signal_count_after_min_move = int((df["side"] != 0).sum())

    roundtrip_cost = ((fee_bps + slippage_bps) / 10_000.0) * 2.0
    long_conf = ((df["prob_up"] - p_enter_short) / max(p_enter_long - p_enter_short, 1e-9)).clip(0.0, 1.0)
    short_conf = (1.0 - long_conf).clip(0.0, 1.0)
    tp_reach_prob = np.where(df["side"] > 0, long_conf, np.where(df["side"] < 0, short_conf, 0.0))
    if min_tp_reach_prob > 0:
        low_prob_mask = (df["side"] != 0) & (tp_reach_prob < float(min_tp_reach_prob))
        df.loc[low_prob_mask, "side"] = 0
        tp_reach_prob = np.where(df["side"] > 0, long_conf, np.where(df["side"] < 0, short_conf, 0.0))
    signal_count_after_tp_prob = int((df["side"] != 0).sum())
    sl_hit_prob = np.where(df["side"] == 0, 0.0, 1.0 - tp_reach_prob)
    expected_move_pct = np.abs(df.get("future_return", pd.Series(np.zeros(len(df)), index=df.index))).astype(float)
    tp_floor_pct = max(0.0, float(tp_min_factor) * abs(float(min_expected_move_pct)))
    if bool(dynamic_tp_enabled):
        dyn_tp = np.maximum(np.maximum(float(take_profit_pct), tp_floor_pct), float(tp_min_factor) * expected_move_pct)
    else:
        dyn_tp = np.full(len(df), float(take_profit_pct), dtype=float)
    ev = tp_reach_prob * dyn_tp - sl_hit_prob * float(stop_loss_pct) - roundtrip_cost

    df["expected_move_pct"] = expected_move_pct
    df["dynamic_tp_pct"] = dyn_tp
    df["tp_floor_pct"] = tp_floor_pct
    df["tp_reach_prob"] = tp_reach_prob
    df["sl_hit_prob"] = sl_hit_prob
    df["ev_unlevered"] = np.where(df["side"] == 0, 0.0, ev)
    df["ev"] = np.where(df["side"] == 0, 0.0, ev * leverage)
    df["ev_usd"] = np.where(df["side"] == 0, 0.0, ev * leverage * notional_usd)

    if "future_return" not in df.columns:
        df["future_return"] = 0.0
    df["gross_return_raw"] = df["side"] * df["future_return"]
    upper_cap = np.asarray(dyn_tp, dtype=float)
    lower_cap = -abs(float(stop_loss_pct))
    df["gross_return"] = np.minimum(np.maximum(df["gross_return_raw"].to_numpy(dtype=float), lower_cap), upper_cap)
    raw_trade_return = df["gross_return"] - roundtrip_cost
    df["net_return_unlevered"] = np.where(df["side"] == 0, 0.0, raw_trade_return)
    df["net_return"] = np.where(df["side"] == 0, 0.0, raw_trade_return * leverage)
    df["net_pnl_usd"] = np.where(df["side"] == 0, 0.0, raw_trade_return * leverage * notional_usd)
    df["target_reached"] = (df["side"] != 0) & (df["gross_return_raw"] >= abs(take_profit_pct))
    df["time_to_target_bars"] = np.where(df["target_reached"], 1.0, np.nan)
    bar_sec = _infer_bar_seconds(df)
    df["time_to_target_sec"] = np.where(df["target_reached"], bar_sec, np.nan)
    df["equity_curve"] = (1.0 + df["net_return"]).cumprod()

    summary = _summarize(
        df,
        fee_bps=fee_bps,
        slippage_bps=slippage_bps,
        stop_loss_pct=stop_loss_pct,
        take_profit_pct=take_profit_pct,
        min_expected_move_pct=min_expected_move_pct,
        min_tp_reach_prob=min_tp_reach_prob,
        tp_min_factor=tp_min_factor,
        dynamic_tp_enabled=dynamic_tp_enabled,
        cooldown_bars=cooldown_bars,
        trend_filter=trend_filter,
        min_abs_ema_gap=min_abs_ema_gap,
        notional_usd=notional_usd,
        leverage=leverage,
        mode=mode,
        execution_mode="research",
        order_type="market",
        hold_bars=hold_bars,
        limit_offset_bps=limit_offset_bps,
        timeout_exit_enabled=bool(timeout_exit_enabled),
        trend_filter_diagnostics={
            "signal_count_raw": int(signal_count_raw),
            "signal_count_after_mode": int(signal_count_after_mode),
            "signal_count_after_entry_action_gates": int(signal_count_after_entry_action_gates),
            "signal_count_after_f001_ret1_gate": int(signal_count_after_f001_ret1_gate),
            "signal_count_after_cooldown": int(signal_count_after_cooldown),
            "signal_count_after_filter": int(signal_count_after_trend_filter),
            "signal_count_after_min_move": int(signal_count_after_min_move),
            "signal_count_after_tp_prob": int(signal_count_after_tp_prob),
            "eligible_bars": int(signal_count_after_tp_prob),
            "filter_pass_ratio": (
                float(signal_count_after_trend_filter) / float(signal_count_after_cooldown)
                if signal_count_after_cooldown > 0
                else 1.0
            ),
            "F001_RET1_ALLOW_gate_active": bool(f001_ret1_gate_active),
            **_min_move_reachability_diag(
                min_expected_move_pct=float(min_expected_move_pct),
                signal_count_after_entry_action_gates=int(signal_count_after_entry_action_gates),
                signal_count_after_filter=int(signal_count_after_trend_filter),
                signal_count_after_min_move=int(signal_count_after_min_move),
                move_values_after_action_gate=move_values_after_action_gate,
                move_values_after_filter=move_values_after_filter,
            ),
            **_entry_action_gate_diag(
                df,
                columns=entry_action_gate_columns,
                active_entry_action_columns=active_entry_action_columns,
                calibration_params=calibration_params,
            ),
            "trend_filter_normalized": str(trend_filter_norm),
            "trend_filter_required_columns": trend_filter_required_columns,
            "trend_filter_missing_columns": trend_filter_missing_columns,
            "trend_filter_degraded_noop_risk": bool(trend_filter_norm != "none" and len(trend_filter_missing_columns) > 0),
            "require_trend_filter_features": bool(require_trend_filter_features),
        },
    )
    return df, summary


def _run_exchange_like_backtest(
    df: pd.DataFrame,
    *,
    p_enter_long: float,
    p_enter_short: float,
    fee_bps: float,
    slippage_bps: float,
    stop_loss_pct: float,
    take_profit_pct: float,
    min_expected_move_pct: float,
    min_tp_reach_prob: float,
    tp_min_factor: float,
    dynamic_tp_enabled: bool,
    cooldown_bars: int,
    trend_filter: str,
    min_abs_ema_gap: float,
    notional_usd: float,
    leverage: float,
    signal_mode: str,
    hold_bars: int,
    order_type: str,
    limit_offset_bps: float,
    require_trend_filter_features: bool,
    calibration_params: dict[str, float] | None = None,
    active_entry_action_columns: list[str] | tuple[str, ...] | None = None,
    timeout_exit_enabled: bool = True,
) -> tuple[pd.DataFrame, dict]:
    req = ["open", "high", "low", "close", "open_time_utc"]
    missing = [c for c in req if c not in df.columns]
    if missing:
        raise RuntimeError(
            "exchange_like requires OHLCV schema and will not fallback to research; "
            f"missing_columns={missing}"
        )

    mode = _normalize_signal_mode(signal_mode)
    trend_filter_norm = _normalize_trend_filter(trend_filter)
    trend_filter_required_columns = list(_trend_filter_required_columns(trend_filter_norm))
    trend_filter_missing_columns = _trend_filter_missing_columns(df, trend_filter_norm)
    if bool(require_trend_filter_features) and trend_filter_norm != "none" and trend_filter_missing_columns:
        raise RuntimeError(
            "trend_filter requires feature columns that are missing in OOF/backtest frame: "
            f"trend_filter={trend_filter_norm}, missing_columns={trend_filter_missing_columns}"
        )
    order = str(order_type or "market").strip().lower()
    if order not in {"market", "limit"}:
        order = "market"

    n = len(df)
    df["side"] = 0
    df["gross_return_raw"] = 0.0
    df["gross_return"] = 0.0
    df["net_return_unlevered"] = 0.0
    df["net_return"] = 0.0
    df["net_pnl_usd"] = 0.0
    df["tp_reach_prob"] = 0.0
    df["sl_hit_prob"] = 0.0
    df["expected_move_pct"] = 0.0
    df["tp_floor_pct"] = max(0.0, float(tp_min_factor) * abs(float(min_expected_move_pct)))
    df["dynamic_tp_pct"] = float(take_profit_pct)
    df["ev_unlevered"] = 0.0
    df["ev"] = 0.0
    df["ev_usd"] = 0.0
    df["target_reached"] = False
    df["time_to_target_bars"] = np.nan
    df["time_to_target_sec"] = np.nan
    df["entry_time_utc"] = ""
    df["exit_time_utc"] = ""
    df["entry_price"] = np.nan
    df["exit_price"] = np.nan
    df["exit_reason"] = ""
    df["dynamic_tp_initial_pct"] = np.nan
    df["dynamic_tp_update_count"] = 0
    df["dynamic_tp_events_json"] = ""
    df["final_tp_price"] = np.nan

    roundtrip_cost = ((fee_bps + slippage_bps) / 10_000.0) * 2.0
    slip = float(slippage_bps) / 10_000.0
    limit_off = abs(float(limit_offset_bps)) / 10_000.0
    hold = max(1, int(hold_bars))

    i = 0
    bar_sec = _infer_bar_seconds(df)
    signal_count_raw = 0
    signal_count_after_mode = 0
    signal_count_after_entry_action_gates = 0
    signal_count_after_f001_ret1_gate = 0
    signal_count_after_filter = 0
    signal_count_after_min_move = 0
    signal_count_after_tp_prob = 0
    entries_filled = 0
    move_values_after_action_gate: list[float] = []
    move_values_after_filter: list[float] = []
    entry_action_gate_columns = _entry_action_allow_columns(
        df,
        active_entry_action_columns=active_entry_action_columns,
        calibration_params=calibration_params,
    )
    f001_ret1_gate_active = F001_RET1_ALLOW_COLUMN in entry_action_gate_columns
    while i < n - 1:
        prob = float(df.iloc[i]["prob_up"])
        raw_side = 0
        if prob >= p_enter_long:
            raw_side = 1
        elif prob <= p_enter_short:
            raw_side = -1
        if raw_side != 0:
            signal_count_raw += 1
        side = int(raw_side)

        if mode == "long_only" and side < 0:
            side = 0
        if mode == "short_only" and side > 0:
            side = 0
        if side != 0:
            signal_count_after_mode += 1

        atr_proxy = abs(float(df.iloc[i].get("atr14", 0.0))) if "atr14" in df.columns else 0.0
        conf = max(0.0, min(1.0, abs(prob - 0.5) * 2.0))
        # Horizon-aware move proxy: atr14 is per-bar percent volatility proxy.
        # Scale by sqrt(hold) to approximate expected move over multi-bar horizon.
        horizon_scale = math.sqrt(max(1, int(hold)))
        pred_move_proxy = conf * max(atr_proxy, 0.0) * horizon_scale

        if side != 0 and not _entry_action_row_allows(
            df.iloc[i],
            entry_action_gate_columns,
            side=int(side),
            calibration_params=calibration_params,
        ):
            side = 0
        if side != 0:
            signal_count_after_entry_action_gates += 1
            signal_count_after_f001_ret1_gate += 1
            move_values_after_action_gate.append(float(pred_move_proxy))

        if side != 0 and not _trend_row_allows(
            df.iloc[i],
            side=int(side),
            trend_filter=str(trend_filter),
            min_abs_ema_gap=float(min_abs_ema_gap),
            calibration_params=calibration_params,
        ):
            side = 0
        if side != 0:
            signal_count_after_filter += 1
            move_values_after_filter.append(float(pred_move_proxy))

        if side != 0 and float(min_expected_move_pct) > 0 and pred_move_proxy < float(min_expected_move_pct):
            side = 0
        if side != 0:
            signal_count_after_min_move += 1
        if side != 0 and float(min_tp_reach_prob) > 0 and conf < float(min_tp_reach_prob):
            side = 0
        if side != 0:
            signal_count_after_tp_prob += 1

        if side == 0:
            i += 1
            continue

        entry_idx = i + 1
        if entry_idx >= n:
            break

        next_open = float(df.iloc[entry_idx]["open"])
        next_high = float(df.iloc[entry_idx]["high"])
        next_low = float(df.iloc[entry_idx]["low"])
        signal_close = float(df.iloc[i]["close"])

        filled = True
        if order == "market":
            entry_px = next_open * (1.0 + (slip * side))
        else:
            entry_px = signal_close * (1.0 - (limit_off * side))
            filled = (next_low <= entry_px <= next_high)

        if not filled:
            i += 1
            continue
        entries_filled += 1

        tp_floor = max(0.0, float(tp_min_factor) * abs(float(min_expected_move_pct)))
        dyn_tp = float(take_profit_pct)
        if bool(dynamic_tp_enabled):
            dyn_tp = max(float(take_profit_pct), tp_floor, float(tp_min_factor) * max(pred_move_proxy, 0.0))
        initial_dyn_tp = float(dyn_tp)

        if side > 0:
            sl_price = entry_px * (1.0 - abs(float(stop_loss_pct)))
            tp_price = entry_px * (1.0 + abs(float(dyn_tp)))
        else:
            sl_price = entry_px * (1.0 + abs(float(stop_loss_pct)))
            tp_price = entry_px * (1.0 - abs(float(dyn_tp)))
        tp_events: list[dict[str, object]] = []

        exit_idx = min(n - 1, entry_idx + hold - 1) if bool(timeout_exit_enabled) else n - 1
        exit_price = float(df.iloc[exit_idx]["close"])
        exit_reason = "timeout" if bool(timeout_exit_enabled) else "end_of_data"
        target_reached = False

        for j in range(entry_idx, exit_idx + 1):
            close_j = float(df.iloc[j]["close"])
            if bool(dynamic_tp_enabled):
                if side > 0:
                    favorable_move = max(0.0, (close_j / entry_px) - 1.0)
                else:
                    favorable_move = max(0.0, (entry_px / max(close_j, 1e-12)) - 1.0)
                candidate_dyn_tp = max(float(dyn_tp), float(take_profit_pct), tp_floor, favorable_move + tp_floor)
                if candidate_dyn_tp > float(dyn_tp) + 1e-12:
                    dyn_tp = float(candidate_dyn_tp)
                    if side > 0:
                        tp_price = entry_px * (1.0 + abs(float(dyn_tp)))
                    else:
                        tp_price = entry_px * (1.0 - abs(float(dyn_tp)))
                    event_ts = pd.to_datetime(df.iloc[j]["open_time_utc"], utc=True, errors="coerce")
                    tp_events.append(
                        {
                            "bar_index": int(j),
                            "event_time_utc": event_ts.isoformat() if pd.notna(event_ts) else "",
                            "close_price": float(close_j),
                            "dynamic_tp_pct": float(dyn_tp),
                            "tp_price": float(tp_price),
                        }
                    )
            hi = float(df.iloc[j]["high"])
            lo = float(df.iloc[j]["low"])
            if side > 0:
                hit_sl = lo <= sl_price
                hit_tp = hi >= tp_price
            else:
                hit_sl = hi >= sl_price
                hit_tp = lo <= tp_price

            if hit_sl and hit_tp:
                # conservative ordering for single-bar ambiguity
                exit_idx = j
                exit_price = sl_price
                exit_reason = "sl_ambiguous"
                target_reached = False
                break
            if hit_sl:
                exit_idx = j
                exit_price = sl_price
                exit_reason = "sl"
                target_reached = False
                break
            if hit_tp:
                exit_idx = j
                exit_price = tp_price
                exit_reason = "tp"
                target_reached = True
                break

        gross_raw = side * ((exit_price / entry_px) - 1.0)
        gross_capped = max(-abs(float(stop_loss_pct)), min(float(dyn_tp), gross_raw))
        net_unlevered = gross_capped - roundtrip_cost
        net = net_unlevered * leverage
        net_usd = net_unlevered * leverage * notional_usd

        ev_unlev = conf * dyn_tp - (1.0 - conf) * abs(float(stop_loss_pct)) - roundtrip_cost

        df.at[i, "side"] = int(side)
        df.at[i, "gross_return_raw"] = float(gross_raw)
        df.at[i, "gross_return"] = float(gross_capped)
        df.at[i, "net_return_unlevered"] = float(net_unlevered)
        df.at[i, "net_return"] = float(net)
        df.at[i, "net_pnl_usd"] = float(net_usd)
        df.at[i, "tp_reach_prob"] = float(conf)
        df.at[i, "sl_hit_prob"] = float(1.0 - conf)
        df.at[i, "expected_move_pct"] = float(pred_move_proxy)
        df.at[i, "dynamic_tp_pct"] = float(dyn_tp)
        df.at[i, "ev_unlevered"] = float(ev_unlev)
        df.at[i, "ev"] = float(ev_unlev * leverage)
        df.at[i, "ev_usd"] = float(ev_unlev * leverage * notional_usd)
        df.at[i, "target_reached"] = bool(target_reached)
        if target_reached:
            bars_to_target = (exit_idx - entry_idx) + 1
            df.at[i, "time_to_target_bars"] = float(bars_to_target)
            df.at[i, "time_to_target_sec"] = float(bars_to_target * bar_sec) if bar_sec > 0 else np.nan

        entry_ts = pd.to_datetime(df.iloc[entry_idx]["open_time_utc"], utc=True, errors="coerce")
        if "close_time_utc" in df.columns:
            exit_ts = pd.to_datetime(df.iloc[exit_idx]["close_time_utc"], utc=True, errors="coerce")
        else:
            exit_ts = pd.to_datetime(df.iloc[exit_idx]["open_time_utc"], utc=True, errors="coerce")
        df.at[i, "entry_time_utc"] = entry_ts.isoformat() if pd.notna(entry_ts) else ""
        df.at[i, "exit_time_utc"] = exit_ts.isoformat() if pd.notna(exit_ts) else ""
        df.at[i, "entry_price"] = float(entry_px)
        df.at[i, "exit_price"] = float(exit_price)
        df.at[i, "exit_reason"] = str(exit_reason)
        df.at[i, "dynamic_tp_initial_pct"] = float(initial_dyn_tp)
        df.at[i, "dynamic_tp_pct"] = float(dyn_tp)
        df.at[i, "dynamic_tp_update_count"] = int(len(tp_events))
        df.at[i, "dynamic_tp_events_json"] = json.dumps(tp_events, ensure_ascii=False)
        df.at[i, "final_tp_price"] = float(tp_price)

        i = exit_idx + 1 + max(0, int(cooldown_bars))

    df["equity_curve"] = (1.0 + df["net_return"]).cumprod()

    summary = _summarize(
        df,
        fee_bps=fee_bps,
        slippage_bps=slippage_bps,
        stop_loss_pct=stop_loss_pct,
        take_profit_pct=take_profit_pct,
        min_expected_move_pct=min_expected_move_pct,
        min_tp_reach_prob=min_tp_reach_prob,
        tp_min_factor=tp_min_factor,
        dynamic_tp_enabled=dynamic_tp_enabled,
        cooldown_bars=cooldown_bars,
        trend_filter=trend_filter,
        min_abs_ema_gap=min_abs_ema_gap,
        notional_usd=notional_usd,
        leverage=leverage,
        mode=mode,
        execution_mode="exchange_like",
        order_type=order,
        hold_bars=hold,
        limit_offset_bps=limit_offset_bps,
        timeout_exit_enabled=bool(timeout_exit_enabled),
        trend_filter_diagnostics={
            "signal_count_raw": int(signal_count_raw),
            "signal_count_after_mode": int(signal_count_after_mode),
            "signal_count_after_entry_action_gates": int(signal_count_after_entry_action_gates),
            "signal_count_after_f001_ret1_gate": int(signal_count_after_f001_ret1_gate),
            "signal_count_after_filter": int(signal_count_after_filter),
            "signal_count_after_min_move": int(signal_count_after_min_move),
            "signal_count_after_tp_prob": int(signal_count_after_tp_prob),
            "eligible_bars": int(signal_count_after_tp_prob),
            "entries_filled": int(entries_filled),
            "filter_pass_ratio": (
                float(signal_count_after_filter) / float(signal_count_after_mode)
                if signal_count_after_mode > 0
                else 1.0
            ),
            "F001_RET1_ALLOW_gate_active": bool(f001_ret1_gate_active),
            **_min_move_reachability_diag(
                min_expected_move_pct=float(min_expected_move_pct),
                signal_count_after_entry_action_gates=int(signal_count_after_entry_action_gates),
                signal_count_after_filter=int(signal_count_after_filter),
                signal_count_after_min_move=int(signal_count_after_min_move),
                move_values_after_action_gate=move_values_after_action_gate,
                move_values_after_filter=move_values_after_filter,
            ),
            **_entry_action_gate_diag(
                df,
                columns=entry_action_gate_columns,
                active_entry_action_columns=active_entry_action_columns,
                calibration_params=calibration_params,
            ),
            "trend_filter_normalized": str(trend_filter_norm),
            "trend_filter_required_columns": trend_filter_required_columns,
            "trend_filter_missing_columns": trend_filter_missing_columns,
            "trend_filter_degraded_noop_risk": bool(trend_filter_norm != "none" and len(trend_filter_missing_columns) > 0),
            "require_trend_filter_features": bool(require_trend_filter_features),
        },
    )
    return df, summary


def run_prob_backtest(
    oof: pd.DataFrame,
    *,
    p_enter_long: float = 0.55,
    p_enter_short: float = 0.45,
    fee_bps: float = 10.0,
    slippage_bps: float = 5.0,
    stop_loss_pct: float = 0.01,
    take_profit_pct: float = 0.02,
    min_expected_move_pct: float = 0.0,
    min_tp_reach_prob: float = 0.0,
    tp_min_factor: float = 0.7,
    dynamic_tp_enabled: bool = True,
    cooldown_bars: int = 0,
    trend_filter: str = "none",
    min_abs_ema_gap: float = 0.0,
    notional_usd: float = 10.0,
    leverage: float = 1.0,
    signal_mode: str = "both",
    position_size: float | None = None,
    execution_mode: str = "research",
    order_type: str = "market",
    hold_bars: int = 1,
    limit_offset_bps: float = 2.0,
    require_trend_filter_features: bool = True,
    calibration_params: dict[str, float] | None = None,
    active_entry_action_columns: list[str] | tuple[str, ...] | None = None,
    timeout_exit_enabled: bool = True,
) -> tuple[pd.DataFrame, dict]:
    if position_size is not None:
        notional_usd = float(position_size)
    notional_usd = float(notional_usd)
    leverage = max(1.0, float(leverage))
    min_expected_move_pct = normalize_min_expected_move_pct(min_expected_move_pct)

    df = oof.copy().sort_values("open_time_utc").reset_index(drop=True)
    mode = str(execution_mode or "research").strip().lower()

    if mode == "exchange_like":
        return _run_exchange_like_backtest(
            df,
            p_enter_long=p_enter_long,
            p_enter_short=p_enter_short,
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
            min_expected_move_pct=min_expected_move_pct,
            min_tp_reach_prob=min_tp_reach_prob,
            tp_min_factor=tp_min_factor,
            dynamic_tp_enabled=dynamic_tp_enabled,
            cooldown_bars=int(cooldown_bars),
            trend_filter=trend_filter,
            min_abs_ema_gap=min_abs_ema_gap,
            notional_usd=notional_usd,
            leverage=leverage,
            signal_mode=signal_mode,
            hold_bars=max(1, int(hold_bars)),
            order_type=order_type,
            limit_offset_bps=float(limit_offset_bps),
            require_trend_filter_features=bool(require_trend_filter_features),
            calibration_params=calibration_params,
            active_entry_action_columns=active_entry_action_columns,
            timeout_exit_enabled=bool(timeout_exit_enabled),
        )

    return _run_research_backtest(
        df,
        p_enter_long=p_enter_long,
        p_enter_short=p_enter_short,
        fee_bps=fee_bps,
        slippage_bps=slippage_bps,
        stop_loss_pct=stop_loss_pct,
        take_profit_pct=take_profit_pct,
        min_expected_move_pct=min_expected_move_pct,
        min_tp_reach_prob=min_tp_reach_prob,
        tp_min_factor=tp_min_factor,
        dynamic_tp_enabled=dynamic_tp_enabled,
        cooldown_bars=int(cooldown_bars),
        trend_filter=trend_filter,
        min_abs_ema_gap=min_abs_ema_gap,
        notional_usd=notional_usd,
        leverage=leverage,
        signal_mode=signal_mode,
        hold_bars=max(1, int(hold_bars)),
        limit_offset_bps=float(limit_offset_bps),
        require_trend_filter_features=bool(require_trend_filter_features),
        calibration_params=calibration_params,
        active_entry_action_columns=active_entry_action_columns,
        timeout_exit_enabled=bool(timeout_exit_enabled),
    )
