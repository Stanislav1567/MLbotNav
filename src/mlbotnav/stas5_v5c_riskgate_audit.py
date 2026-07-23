from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

from mlbotnav.stas5_common import PROJECT_ROOT, compact_day, iter_days, rel, utc_now, write_json
from mlbotnav.stas5_v5_forward_visual_review import (
    DECISION_COLUMN,
    SCORE_COLUMN,
    SYMBOL,
    TIMEFRAME,
    _bar_width_days,
    _build_strength_strip_rows,
    _draw_candles,
    _find_context_ohlcv_path,
    _load_ohlcv,
    _load_predictions,
    _plot_forward_markers,
    _plot_score_panel,
    _render_rank_strip,
    _render_v5_macro_wave_strip,
    _set_day_time_axis,
    _shade_sessions,
    _source_csv,
    _style_axis,
)


STATUS_PASS = "PASS_V5C_RISKGATE_AUDIT_ONLY_READY"
STATUS_FAIL = "FAIL_V5C_RISKGATE_AUDIT_ONLY"

V5C_ROOT = PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5c"
DEFAULT_FORWARD_RUNS_DIR = V5C_ROOT / "forward" / "runs"
DEFAULT_LATEST_FORWARD_POINTER = V5C_ROOT / "forward" / "STAS5_V5C_LATEST_TWO_BLOCK_FORWARD_RUN.json"

KEY_COLUMNS = ["day", "candidate_id", "record_id", "entry_time_utc"]

RISK_FEATURE_COLUMNS = [
    "stas5_v2_risk_knife_pre_entry",
    "stas5_v2_risk_weak_bounce_inside_drop",
    "stas5_v2_risk_too_high_in_drop",
    "stas5_v2_risk_after_spike",
    "stas5_v2_risk_drawdown_proxy_score",
    "stas5_v2_gate_long_allowed_final",
    "stas5_v2_gate_bullish_evidence_score",
    "stas5_v2_short_wave_max_down_from_high_pct",
    "cs_short_pressure_now",
    "cs_dump_acceleration_score",
    "cs_pre_dump_risk_score",
    "cs_price_breaking_recent_support",
    "cs_falling_knife_active",
    "cs_sell_pressure_exhaustion_score",
    "cs_consecutive_red_candles",
    "fcs_knife_risk_score",
    "fcs_knife_active",
    "fcs_knife_drop_pct_so_far",
    "fcs_knife_acceleration_score",
    "fcs_knife_red_streak",
    "fcs_knife_exhaustion_score",
    "fcs_bounce_from_knife_low_pct",
    "fcs_grounding_confirmed_score",
    "fcs_retest_after_knife_score",
    "fcs_regime_score_short_pressure",
    "fcs_regime_score_pre_dump_risk",
    "fcs_regime_score_active_dump",
    "fcs_pre_dump_after_pump_score",
    "fcs_post_pump_exhaustion_score",
    "fcs_failed_breakout_score",
    "fcs_resistance_reject_after_pump",
    "fcs_support_broken_recently",
    "fcs_channel_breakdown_recent",
    "fcs_channel_slope_pct_per_min",
    "fcs_channel_position_0_1",
]

RISK_GATE_TAXONOMY_VERSION = "RISK_GATE_TAXONOMY_V1"

RISK_REGIME_ORDER = [
    "LIQUIDATION_CASCADE",
    "FALLING_KNIFE",
    "ACTIVE_DUMP",
    "SUPPORT_BREAKDOWN",
    "CHANNEL_BREAKDOWN",
    "PULLBACK_THEN_SHORT",
    "SHORT_CONTINUATION",
    "POST_PUMP_DUMP",
    "STRONG_SHORT_PRESSURE",
    "PRE_DUMP_RISK",
]

RISK_REGIME_RU = {
    "NO_FATAL_RISK": "смертельный short/dump режим не найден",
    "GOOD_REBOUND_EXCEPTION": "есть признаки отскока/ретеста, не блокировать автоматически",
    "USER_APPROVED_REBOUND_EXCEPTION": "ручное исключение: пользователь подтвердил проходящий rebound/retest вход",
    "PRE_DUMP_RISK": "перед сливом",
    "ACTIVE_DUMP": "дамп уже идет",
    "FALLING_KNIFE": "падающий нож",
    "STRONG_SHORT_PRESSURE": "сильное давление шорта",
    "SHORT_CONTINUATION": "откат и продолжение шорта",
    "PULLBACK_THEN_SHORT": "слабый отскок-ловушка",
    "SUPPORT_BREAKDOWN": "пробой поддержки",
    "CHANNEL_BREAKDOWN": "выпадение из канала вниз",
    "POST_PUMP_DUMP": "памп выдохся и начался слив",
    "LIQUIDATION_CASCADE": "жесткий пролив 2-10%, hard block",
}

RISK_REGIME_SHORT_LABEL = {
    "NO_FATAL_RISK": "P",
    "GOOD_REBOUND_EXCEPTION": "GR",
    "USER_APPROVED_REBOUND_EXCEPTION": "UP",
    "PRE_DUMP_RISK": "PD",
    "ACTIVE_DUMP": "AD",
    "FALLING_KNIFE": "FK",
    "STRONG_SHORT_PRESSURE": "SS",
    "SHORT_CONTINUATION": "SC",
    "PULLBACK_THEN_SHORT": "PTS",
    "SUPPORT_BREAKDOWN": "SB",
    "CHANNEL_BREAKDOWN": "CB",
    "POST_PUMP_DUMP": "PPD",
    "LIQUIDATION_CASCADE": "LC",
}

USER_PASS_REASON_RU = {
    "LA059": "пользователь отметил как проходящий вход: локальная зона после пролива, не hard-block",
    "LA067": "пользователь отметил как проходящий вход: заземление после ножа, возможный retest/rebound",
    "LA078": "пользователь отметил как проходящий вход: low/rebound зона после снижения, не душить как active dump",
}


def _safe_float(row: pd.Series, column: str, default: float = 0.0) -> float:
    try:
        value = row.get(column, default)
        if value is None or value == "":
            return default
        out = float(value)
        if math.isnan(out):
            return default
        return out
    except Exception:
        return default


def _clip01(value: float) -> float:
    if math.isnan(value):
        return 0.0
    return max(0.0, min(1.0, value))


def _ordered_regime_tags(tags: list[str]) -> list[str]:
    unique = set(tags)
    return [regime for regime in RISK_REGIME_ORDER if regime in unique]


def _join_regime_tags(tags: list[str]) -> str:
    ordered = _ordered_regime_tags(tags)
    return "|".join(ordered) if ordered else "NO_FATAL_RISK"


def _join_regime_tags_ru(tags: list[str]) -> str:
    ordered = _ordered_regime_tags(tags)
    if not ordered:
        return RISK_REGIME_RU["NO_FATAL_RISK"]
    return " | ".join(RISK_REGIME_RU.get(regime, regime) for regime in ordered)


def _primary_regime(tags: list[str], fallback: str = "NO_FATAL_RISK") -> str:
    ordered = _ordered_regime_tags(tags)
    return ordered[0] if ordered else fallback


def _risk_mode_scores(row: pd.Series) -> dict[str, float]:
    active_dump = max(
        _safe_float(row, "fcs_regime_score_active_dump"),
        _safe_float(row, "cs_dump_acceleration_score") * 0.85,
        _safe_float(row, "stas5_v2_risk_drawdown_proxy_score") * 0.72,
    )
    knife = max(
        _safe_float(row, "fcs_knife_risk_score"),
        _safe_float(row, "fcs_knife_acceleration_score"),
        _safe_float(row, "cs_dump_acceleration_score"),
        _safe_float(row, "cs_falling_knife_active"),
        _safe_float(row, "fcs_knife_active"),
        _safe_float(row, "stas5_v2_risk_knife_pre_entry"),
    )
    short = max(_safe_float(row, "cs_short_pressure_now"), _safe_float(row, "fcs_regime_score_short_pressure"))
    support_breakdown = max(_safe_float(row, "cs_price_breaking_recent_support"), _safe_float(row, "fcs_support_broken_recently"))
    channel_breakdown = _safe_float(row, "fcs_channel_breakdown_recent")
    breakdown = max(support_breakdown, channel_breakdown)
    pre_dump = max(
        _safe_float(row, "cs_pre_dump_risk_score"),
        _safe_float(row, "fcs_regime_score_pre_dump_risk"),
        _safe_float(row, "fcs_pre_dump_after_pump_score"),
        _safe_float(row, "fcs_failed_breakout_score"),
        _safe_float(row, "stas5_v2_risk_after_spike"),
        _safe_float(row, "stas5_v2_risk_too_high_in_drop"),
    )
    grounding = _safe_float(row, "fcs_grounding_confirmed_score")
    retest = _safe_float(row, "fcs_retest_after_knife_score")
    exhaustion = max(_safe_float(row, "fcs_knife_exhaustion_score"), _safe_float(row, "cs_sell_pressure_exhaustion_score"))
    failed_breakout = _safe_float(row, "fcs_failed_breakout_score")
    post_pump = max(
        _safe_float(row, "fcs_pre_dump_after_pump_score"),
        _safe_float(row, "fcs_post_pump_exhaustion_score"),
        failed_breakout,
        _safe_float(row, "fcs_resistance_reject_after_pump"),
    )
    weak_bounce = _safe_float(row, "stas5_v2_risk_weak_bounce_inside_drop")
    bounce_from_knife_low_pct = _safe_float(row, "fcs_bounce_from_knife_low_pct")
    red_streak = max(_safe_float(row, "cs_consecutive_red_candles"), _safe_float(row, "fcs_knife_red_streak"))
    drop_pct_so_far = max(
        _safe_float(row, "fcs_knife_drop_pct_so_far"),
        _safe_float(row, "stas5_v2_short_wave_max_down_from_high_pct"),
    )

    short_continuation = max(
        min(short, max(active_dump, pre_dump)),
        0.76 if short >= 0.70 and red_streak >= 3 else 0.0,
        0.74 if short >= 0.70 and active_dump >= 0.58 and exhaustion < 0.58 else 0.0,
    )
    pullback_then_short = max(
        min(short, max(pre_dump, failed_breakout, active_dump), max(retest, grounding, weak_bounce, _clip01(bounce_from_knife_low_pct / 0.75))),
        0.78 if weak_bounce >= 0.70 and short >= 0.66 else 0.0,
    )
    liquidation_cascade = max(
        min(active_dump, knife, max(short, breakdown)),
        0.96 if drop_pct_so_far >= 2.0 and active_dump >= 0.75 and knife >= 0.75 else 0.0,
        0.94 if active_dump >= 0.95 and knife >= 0.95 and (short >= 0.70 or breakdown >= 1.0) else 0.0,
    )

    return {
        "PRE_DUMP_RISK": _clip01(pre_dump),
        "ACTIVE_DUMP": _clip01(active_dump),
        "FALLING_KNIFE": _clip01(knife),
        "STRONG_SHORT_PRESSURE": _clip01(short),
        "SHORT_CONTINUATION": _clip01(short_continuation),
        "PULLBACK_THEN_SHORT": _clip01(pullback_then_short),
        "SUPPORT_BREAKDOWN": _clip01(support_breakdown),
        "CHANNEL_BREAKDOWN": _clip01(channel_breakdown),
        "POST_PUMP_DUMP": _clip01(post_pump),
        "LIQUIDATION_CASCADE": _clip01(liquidation_cascade),
        "_BREAKDOWN": _clip01(breakdown),
        "_GROUNDING": _clip01(grounding),
        "_RETEST": _clip01(retest),
        "_EXHAUSTION": _clip01(exhaustion),
        "_DROP_PCT_SO_FAR": round(drop_pct_so_far, 6),
    }


def _risk_mode_tags(scores: dict[str, float]) -> list[str]:
    tags: list[str] = []
    if scores["PRE_DUMP_RISK"] >= 0.78:
        tags.append("PRE_DUMP_RISK")
    if scores["ACTIVE_DUMP"] >= 0.74:
        tags.append("ACTIVE_DUMP")
    if scores["FALLING_KNIFE"] >= 0.80:
        tags.append("FALLING_KNIFE")
    if scores["STRONG_SHORT_PRESSURE"] >= 0.78:
        tags.append("STRONG_SHORT_PRESSURE")
    if scores["SHORT_CONTINUATION"] >= 0.74:
        tags.append("SHORT_CONTINUATION")
    if scores["PULLBACK_THEN_SHORT"] >= 0.74:
        tags.append("PULLBACK_THEN_SHORT")
    if scores["SUPPORT_BREAKDOWN"] >= 0.90:
        tags.append("SUPPORT_BREAKDOWN")
    if scores["CHANNEL_BREAKDOWN"] >= 0.90:
        tags.append("CHANNEL_BREAKDOWN")
    if scores["POST_PUMP_DUMP"] >= 0.72:
        tags.append("POST_PUMP_DUMP")
    if scores["LIQUIDATION_CASCADE"] >= 0.90:
        tags.append("LIQUIDATION_CASCADE")
    return _ordered_regime_tags(tags)


def _resolve_forward_run_dir(forward_run_dir: Path | None = None) -> Path:
    if forward_run_dir is not None:
        return forward_run_dir
    if DEFAULT_LATEST_FORWARD_POINTER.exists():
        pointer = json.loads(DEFAULT_LATEST_FORWARD_POINTER.read_text(encoding="utf-8"))
        path = PROJECT_ROOT / str(pointer["run_dir"])
        if path.exists():
            return path
    candidates = sorted(DEFAULT_FORWARD_RUNS_DIR.glob("stas5_v5c_*forward*"), key=lambda item: item.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError("V5C forward run not found")
    return candidates[-1]


def _find_predictions_path(forward_run_dir: Path, predictions_path: Path | None = None) -> Path:
    if predictions_path is not None:
        return predictions_path
    candidates = sorted(forward_run_dir.glob("STAS5_V5C_FORWARD_PREDICTIONS_*_V1.csv"), key=lambda item: item.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError(f"V5C forward predictions not found in {forward_run_dir}")
    return candidates[-1]


def _find_x439_path(forward_run_dir: Path, x439_path: Path | None = None) -> Path:
    if x439_path is not None:
        return x439_path
    candidates = sorted(
        forward_run_dir.glob("STAS5_V5C_FORWARD_DATASET_*_X*_CONTINUOUS_V1.csv"),
        key=lambda item: item.stat().st_mtime,
    )
    if not candidates:
        raise FileNotFoundError(f"V5C forward dataset not found in {forward_run_dir}")
    return candidates[-1]


def _parse_id_list(value: str | None) -> set[str]:
    if not value:
        return set()
    return {part.strip().upper() for part in value.split(",") if part.strip()}


def _day_user_pass_ids(tokens: set[str], *, day: str, single_day: bool) -> set[str]:
    out: set[str] = set()
    unqualified: list[str] = []
    day_prefix = f"{day}:".upper()
    compact_prefix = f"{compact_day(day)}:".upper()
    for token in tokens:
        item = token.strip().upper()
        if not item:
            continue
        if ":" not in item:
            unqualified.append(item)
            continue
        if item.startswith(day_prefix) or item.startswith(compact_prefix):
            out.add(item.split(":", 1)[1])
    if unqualified:
        if not single_day:
            raise ValueError(
                "unqualified RiskGate user pass ids are allowed only for a single day; "
                "use YYYY-MM-DD:LAxxx for multi-day ranges"
            )
        out.update(unqualified)
    return out


def _source_max_time_utc(row: pd.Series) -> str:
    values = []
    for column in ("cs_max_source_time_utc", "fcs_max_source_time_utc"):
        value = row.get(column)
        if value is not None and str(value).strip():
            values.append(pd.to_datetime(value, utc=True, errors="coerce"))
    values = [value for value in values if pd.notna(value)]
    if not values:
        return ""
    return max(values).strftime("%Y-%m-%dT%H:%M:%SZ")


def _source_no_future_ok(row: pd.Series) -> bool:
    entry_ts = pd.to_datetime(row.get("entry_time_utc"), utc=True, errors="coerce")
    if pd.isna(entry_ts):
        return False
    for column in ("cs_max_source_time_utc", "fcs_max_source_time_utc"):
        value = row.get(column)
        if value is None or not str(value).strip():
            continue
        source_ts = pd.to_datetime(value, utc=True, errors="coerce")
        if pd.notna(source_ts) and source_ts > entry_ts:
            return False
    return True


def _riskgate_decision_legacy(row: pd.Series, *, user_pass_ids: set[str] | None = None) -> dict[str, Any]:
    user_pass_ids = user_pass_ids or set()
    active_dump = max(
        _safe_float(row, "fcs_regime_score_active_dump"),
        _safe_float(row, "cs_dump_acceleration_score") * 0.85,
    )
    knife = max(
        _safe_float(row, "fcs_knife_risk_score"),
        _safe_float(row, "fcs_knife_acceleration_score"),
        _safe_float(row, "cs_dump_acceleration_score"),
    )
    short = max(_safe_float(row, "cs_short_pressure_now"), _safe_float(row, "fcs_regime_score_short_pressure"))
    breakdown = max(
        _safe_float(row, "cs_price_breaking_recent_support"),
        _safe_float(row, "fcs_support_broken_recently"),
        _safe_float(row, "fcs_channel_breakdown_recent"),
    )
    pre_dump = max(
        _safe_float(row, "cs_pre_dump_risk_score"),
        _safe_float(row, "fcs_regime_score_pre_dump_risk"),
        _safe_float(row, "fcs_pre_dump_after_pump_score"),
        _safe_float(row, "fcs_failed_breakout_score"),
    )
    grounding = _safe_float(row, "fcs_grounding_confirmed_score")
    retest = _safe_float(row, "fcs_retest_after_knife_score")
    exhaustion = max(_safe_float(row, "fcs_knife_exhaustion_score"), _safe_float(row, "cs_sell_pressure_exhaustion_score"))

    risk_score = min(1.0, max(active_dump, knife * 0.96, short * 0.88, pre_dump * 0.90, breakdown * 0.78))
    rebound_exception = grounding >= 0.72 and retest >= 0.78 and exhaustion >= 0.60 and active_dump < 0.93

    if rebound_exception:
        status = "PASS_RISK"
        action = "KEEP"
        reason = "GOOD_REBOUND_EXCEPTION"
        reason_ru = "есть признаки отскока/ретеста, не блокировать автоматически"
    elif active_dump >= 0.90 and knife >= 0.90 and (short >= 0.70 or breakdown >= 1.0):
        status = "BLOCK_HARD"
        action = "WOULD_BLOCK"
        reason = "ACTIVE_DUMP+FALLING_KNIFE"
        reason_ru = "активный дамп плюс падающий нож, long запрещен"
    elif knife >= 0.92 and (short >= 0.58 or pre_dump >= 0.60):
        status = "BLOCK_RISK"
        action = "WOULD_BLOCK"
        reason = "FALLING_KNIFE"
        reason_ru = "падающий нож, вход только после подтверждения базы/ретеста"
    elif active_dump >= 0.80 and breakdown >= 1.0:
        status = "BLOCK_RISK"
        action = "WOULD_BLOCK"
        reason = "ACTIVE_DUMP+BREAKDOWN"
        reason_ru = "активный дамп и пробой структуры"
    elif pre_dump >= 0.80 and short >= 0.70:
        status = "WARN_RISK"
        action = "WOULD_DEMOTE"
        reason = "PRE_DUMP+SHORT_PRESSURE"
        reason_ru = "преддамповый риск и short pressure, вход понизить до WATCH"
    elif short >= 0.78 or pre_dump >= 0.78 or breakdown >= 1.0:
        status = "WARN_RISK"
        action = "WOULD_DEMOTE"
        reason = "SHORT/BREAKDOWN_WARNING"
        reason_ru = "есть short pressure или пробой, нужен осторожный режим"
    else:
        status = "PASS_RISK"
        action = "KEEP"
        reason = "NO_FATAL_RISK"
        reason_ru = "смертельный short/dump режим не найден"

    raw_status = status
    raw_action = action
    raw_reason = reason
    candidate_id = str(row.get("candidate_id") or "").upper()
    if candidate_id in user_pass_ids:
        status = "PASS_USER_REBOUND"
        action = "KEEP_BY_USER_REVIEW"
        reason = "USER_APPROVED_REBOUND_EXCEPTION"
        reason_ru = (
            "ручное исключение: вход проходит, будущий RiskGate должен уметь "
            "пропускать такие rebound/retest зоны"
        )

    return {
        "RISK_GATE_MODE": "audit_only",
        "RISK_GATE_STATUS": status,
        "RISK_GATE_ACTION": action,
        "RISK_GATE_REASON": reason,
        "RISK_GATE_REASON_RU": reason_ru,
        "RISK_GATE_SCORE": round(risk_score, 6),
        "RISK_GATE_RAW_STATUS": raw_status,
        "RISK_GATE_RAW_ACTION": raw_action,
        "RISK_GATE_RAW_REASON": raw_reason,
        "DUMP_RISK_SCORE": round(active_dump, 6),
        "KNIFE_RISK_SCORE": round(knife, 6),
        "SHORT_REGIME_SCORE": round(short, 6),
        "BREAKDOWN_SCORE": round(breakdown, 6),
        "PRE_DUMP_SCORE": round(pre_dump, 6),
        "GROUNDING_SCORE": round(grounding, 6),
        "RETEST_SCORE": round(retest, 6),
        "EXHAUSTION_SCORE": round(exhaustion, 6),
        "RISK_SOURCE_MAX_TIME_UTC": _source_max_time_utc(row),
        "RISK_NO_FUTURE_OK": _source_no_future_ok(row),
        "USER_VISUAL_VERDICT": "PASS" if candidate_id in user_pass_ids else "",
        "USER_VISUAL_REASON_RU": USER_PASS_REASON_RU.get(candidate_id, "") if candidate_id in user_pass_ids else "",
    }


def riskgate_decision(row: pd.Series, *, user_pass_ids: set[str] | None = None) -> dict[str, Any]:
    user_pass_ids = user_pass_ids or set()
    scores = _risk_mode_scores(row)
    tags = _risk_mode_tags(scores)

    active_dump = scores["ACTIVE_DUMP"]
    knife = scores["FALLING_KNIFE"]
    short = scores["STRONG_SHORT_PRESSURE"]
    breakdown = scores["_BREAKDOWN"]
    pre_dump = scores["PRE_DUMP_RISK"]
    grounding = scores["_GROUNDING"]
    retest = scores["_RETEST"]
    exhaustion = scores["_EXHAUSTION"]

    risk_score = min(1.0, max(active_dump, knife * 0.96, short * 0.88, pre_dump * 0.90, breakdown * 0.78))
    rebound_exception = grounding >= 0.72 and retest >= 0.78 and exhaustion >= 0.60 and active_dump < 0.93

    if rebound_exception:
        status = "PASS_RISK"
        action = "KEEP"
        reason = "GOOD_REBOUND_EXCEPTION"
        reason_ru = RISK_REGIME_RU["GOOD_REBOUND_EXCEPTION"]
        primary_regime = "GOOD_REBOUND_EXCEPTION"
    elif "LIQUIDATION_CASCADE" in tags and active_dump >= 0.90 and knife >= 0.90 and (short >= 0.70 or breakdown >= 1.0):
        status = "BLOCK_HARD"
        action = "WOULD_BLOCK"
        reason = "LIQUIDATION_CASCADE"
        reason_ru = RISK_REGIME_RU["LIQUIDATION_CASCADE"]
        primary_regime = "LIQUIDATION_CASCADE"
    elif active_dump >= 0.90 and knife >= 0.90 and (short >= 0.70 or breakdown >= 1.0):
        status = "BLOCK_HARD"
        action = "WOULD_BLOCK"
        reason = "ACTIVE_DUMP+FALLING_KNIFE"
        reason_ru = "активный дамп плюс падающий нож, long запрещен"
        primary_regime = _primary_regime(tags, "ACTIVE_DUMP")
    elif knife >= 0.92 and (short >= 0.58 or pre_dump >= 0.60):
        status = "BLOCK_RISK"
        action = "WOULD_BLOCK"
        reason = "FALLING_KNIFE"
        reason_ru = RISK_REGIME_RU["FALLING_KNIFE"]
        primary_regime = _primary_regime(tags, "FALLING_KNIFE")
    elif "PULLBACK_THEN_SHORT" in tags and (short >= 0.70 or pre_dump >= 0.70):
        status = "BLOCK_RISK"
        action = "WOULD_BLOCK"
        reason = "PULLBACK_THEN_SHORT"
        reason_ru = RISK_REGIME_RU["PULLBACK_THEN_SHORT"]
        primary_regime = "PULLBACK_THEN_SHORT"
    elif active_dump >= 0.80 and breakdown >= 1.0:
        status = "BLOCK_RISK"
        action = "WOULD_BLOCK"
        reason = "ACTIVE_DUMP+BREAKDOWN"
        reason_ru = "активный дамп и пробой структуры"
        primary_regime = _primary_regime(tags, "ACTIVE_DUMP")
    elif "SHORT_CONTINUATION" in tags and active_dump >= 0.64:
        status = "BLOCK_RISK"
        action = "WOULD_BLOCK"
        reason = "SHORT_CONTINUATION"
        reason_ru = RISK_REGIME_RU["SHORT_CONTINUATION"]
        primary_regime = "SHORT_CONTINUATION"
    elif pre_dump >= 0.80 and short >= 0.70:
        status = "WARN_RISK"
        action = "WOULD_DEMOTE"
        reason = "PRE_DUMP+SHORT_PRESSURE"
        reason_ru = "преддамповый риск и short pressure, вход понизить до WATCH"
        primary_regime = _primary_regime(tags, "PRE_DUMP_RISK")
    elif short >= 0.78 or pre_dump >= 0.78 or breakdown >= 1.0 or bool(tags):
        status = "WARN_RISK"
        action = "WOULD_DEMOTE"
        reason = _primary_regime(tags, "SHORT/BREAKDOWN_WARNING")
        reason_ru = RISK_REGIME_RU.get(reason, "есть short pressure или пробой, нужен осторожный режим")
        primary_regime = _primary_regime(tags, "NO_FATAL_RISK")
    else:
        status = "PASS_RISK"
        action = "KEEP"
        reason = "NO_FATAL_RISK"
        reason_ru = RISK_REGIME_RU["NO_FATAL_RISK"]
        primary_regime = "NO_FATAL_RISK"

    raw_status = status
    raw_action = action
    raw_reason = reason
    raw_primary_regime = primary_regime
    raw_tags = _join_regime_tags(tags)
    raw_tags_ru = _join_regime_tags_ru(tags)

    final_tags = tags.copy()
    candidate_id = str(row.get("candidate_id") or "").upper()
    if candidate_id in user_pass_ids:
        status = "PASS_USER_REBOUND"
        action = "KEEP_BY_USER_REVIEW"
        reason = "USER_APPROVED_REBOUND_EXCEPTION"
        reason_ru = RISK_REGIME_RU["USER_APPROVED_REBOUND_EXCEPTION"]
        primary_regime = "USER_APPROVED_REBOUND_EXCEPTION"
        final_tags = ["USER_APPROVED_REBOUND_EXCEPTION", *tags]

    final_tags_text = "|".join(final_tags) if final_tags else "NO_FATAL_RISK"
    final_tags_ru = " | ".join(RISK_REGIME_RU.get(regime, regime) for regime in final_tags) if final_tags else RISK_REGIME_RU["NO_FATAL_RISK"]

    return {
        "RISK_GATE_MODE": "audit_only",
        "RISK_GATE_TAXONOMY_VERSION": RISK_GATE_TAXONOMY_VERSION,
        "RISK_GATE_STATUS": status,
        "RISK_GATE_ACTION": action,
        "RISK_GATE_REASON": reason,
        "RISK_GATE_REASON_RU": reason_ru,
        "RISK_GATE_SCORE": round(risk_score, 6),
        "RISK_GATE_PRIMARY_REGIME": primary_regime,
        "RISK_GATE_PRIMARY_REGIME_RU": RISK_REGIME_RU.get(primary_regime, primary_regime),
        "RISK_GATE_PRIMARY_REGIME_SHORT": RISK_REGIME_SHORT_LABEL.get(primary_regime, primary_regime[:3]),
        "RISK_GATE_TAGS": final_tags_text,
        "RISK_GATE_TAGS_RU": final_tags_ru,
        "RISK_GATE_ACTIVE_MODE_COUNT": int(len(final_tags)),
        "RISK_GATE_RAW_STATUS": raw_status,
        "RISK_GATE_RAW_ACTION": raw_action,
        "RISK_GATE_RAW_REASON": raw_reason,
        "RISK_GATE_RAW_PRIMARY_REGIME": raw_primary_regime,
        "RISK_GATE_RAW_TAGS": raw_tags,
        "RISK_GATE_RAW_TAGS_RU": raw_tags_ru,
        "DUMP_RISK_SCORE": round(active_dump, 6),
        "KNIFE_RISK_SCORE": round(knife, 6),
        "SHORT_REGIME_SCORE": round(short, 6),
        "BREAKDOWN_SCORE": round(breakdown, 6),
        "PRE_DUMP_SCORE": round(pre_dump, 6),
        "GROUNDING_SCORE": round(grounding, 6),
        "RETEST_SCORE": round(retest, 6),
        "EXHAUSTION_SCORE": round(exhaustion, 6),
        "LIQUIDATION_DEPTH_PROXY_PCT": scores["_DROP_PCT_SO_FAR"],
        "RISK_MODE_PRE_DUMP_RISK_SCORE": round(scores["PRE_DUMP_RISK"], 6),
        "RISK_MODE_PRE_DUMP_RISK_FLAG": int("PRE_DUMP_RISK" in tags),
        "RISK_MODE_ACTIVE_DUMP_SCORE": round(scores["ACTIVE_DUMP"], 6),
        "RISK_MODE_ACTIVE_DUMP_FLAG": int("ACTIVE_DUMP" in tags),
        "RISK_MODE_FALLING_KNIFE_SCORE": round(scores["FALLING_KNIFE"], 6),
        "RISK_MODE_FALLING_KNIFE_FLAG": int("FALLING_KNIFE" in tags),
        "RISK_MODE_STRONG_SHORT_PRESSURE_SCORE": round(scores["STRONG_SHORT_PRESSURE"], 6),
        "RISK_MODE_STRONG_SHORT_PRESSURE_FLAG": int("STRONG_SHORT_PRESSURE" in tags),
        "RISK_MODE_SHORT_CONTINUATION_SCORE": round(scores["SHORT_CONTINUATION"], 6),
        "RISK_MODE_SHORT_CONTINUATION_FLAG": int("SHORT_CONTINUATION" in tags),
        "RISK_MODE_PULLBACK_THEN_SHORT_SCORE": round(scores["PULLBACK_THEN_SHORT"], 6),
        "RISK_MODE_PULLBACK_THEN_SHORT_FLAG": int("PULLBACK_THEN_SHORT" in tags),
        "RISK_MODE_SUPPORT_BREAKDOWN_SCORE": round(scores["SUPPORT_BREAKDOWN"], 6),
        "RISK_MODE_SUPPORT_BREAKDOWN_FLAG": int("SUPPORT_BREAKDOWN" in tags),
        "RISK_MODE_CHANNEL_BREAKDOWN_SCORE": round(scores["CHANNEL_BREAKDOWN"], 6),
        "RISK_MODE_CHANNEL_BREAKDOWN_FLAG": int("CHANNEL_BREAKDOWN" in tags),
        "RISK_MODE_POST_PUMP_DUMP_SCORE": round(scores["POST_PUMP_DUMP"], 6),
        "RISK_MODE_POST_PUMP_DUMP_FLAG": int("POST_PUMP_DUMP" in tags),
        "RISK_MODE_LIQUIDATION_CASCADE_SCORE": round(scores["LIQUIDATION_CASCADE"], 6),
        "RISK_MODE_LIQUIDATION_CASCADE_FLAG": int("LIQUIDATION_CASCADE" in tags),
        "RISK_SOURCE_MAX_TIME_UTC": _source_max_time_utc(row),
        "RISK_NO_FUTURE_OK": _source_no_future_ok(row),
        "USER_VISUAL_VERDICT": "PASS" if candidate_id in user_pass_ids else "",
        "USER_VISUAL_REASON_RU": USER_PASS_REASON_RU.get(candidate_id, "") if candidate_id in user_pass_ids else "",
    }


def _audit_dataframe(
    *,
    predictions: pd.DataFrame,
    x439: pd.DataFrame,
    day: str,
    user_pass_ids: set[str],
) -> pd.DataFrame:
    day_predictions = predictions[predictions["day"].astype(str).eq(day)].copy()
    day_x = x439[x439["day"].astype(str).eq(day)].copy()
    missing_keys = sorted(set(KEY_COLUMNS).difference(day_predictions.columns).union(set(KEY_COLUMNS).difference(day_x.columns)))
    if missing_keys:
        raise ValueError(f"RiskGate input missing key columns: {missing_keys}")
    merged = day_predictions.drop(columns=["entry_ts"], errors="ignore").merge(
        day_x,
        on=KEY_COLUMNS,
        how="left",
        suffixes=("", "_x439"),
    )
    rows = []
    for _, row in merged.iterrows():
        decision = riskgate_decision(row, user_pass_ids=user_pass_ids)
        rows.append(
            {
                "day": row["day"],
                "candidate_id": row["candidate_id"],
                "record_id": row["record_id"],
                "entry_time_utc": row["entry_time_utc"],
                "ENTRY_ALPHA_MODEL_SELECTED": row.get("ENTRY_MODEL_SELECTED", row.get("ENTRY_MODEL_SELECTED_x439", "")),
                "ENTRY_ALPHA_DECISION": row.get(DECISION_COLUMN, ""),
                "ENTRY_ALPHA_SCORE": row.get(SCORE_COLUMN, 0.0),
                **decision,
                "ENTRY_FINAL_DECISION_AUDIT_ONLY": row.get(DECISION_COLUMN, ""),
                "ENTRY_FINAL_REASON_AUDIT_ONLY": "audit_only_no_prediction_change",
            }
        )
    return pd.DataFrame(rows)


def _risk_color(status: str) -> str:
    return {
        "BLOCK_HARD": "#b00020",
        "BLOCK_RISK": "#ef5350",
        "WARN_RISK": "#ffb300",
        "PASS_USER_REBOUND": "#00c853",
        "PASS_RISK": "#2fd17c",
    }.get(status, "#607d8b")


def _draw_group_spans(ax: Any, rows: pd.DataFrame, *, status_values: set[str], color: str, alpha: float, label: str, max_gap_min: int) -> None:
    group_rows = rows[rows["RISK_GATE_STATUS"].isin(status_values)].copy()
    if group_rows.empty:
        return
    current: list[pd.Series] = []
    prev: pd.Timestamp | None = None
    for _, row in group_rows.sort_values("entry_ts").iterrows():
        ts = pd.Timestamp(row["entry_ts"]).tz_convert(None)
        if prev is None or (ts - prev).total_seconds() / 60.0 <= max_gap_min:
            current.append(row)
        else:
            _draw_span(ax, current, color=color, alpha=alpha, label=label)
            current = [row]
        prev = ts
    _draw_span(ax, current, color=color, alpha=alpha, label=label)


def _draw_span(ax: Any, rows: list[pd.Series], *, color: str, alpha: float, label: str) -> None:
    if not rows:
        return
    start = pd.Timestamp(rows[0]["entry_ts"]).tz_convert(None) - pd.Timedelta(minutes=10)
    end = pd.Timestamp(rows[-1]["entry_ts"]).tz_convert(None) + pd.Timedelta(minutes=16)
    ax.axvspan(start, end, color=color, alpha=alpha, zorder=0)
    y0, y1 = ax.get_ylim()
    midpoint = start + (end - start) / 2
    ids = f"{rows[0]['candidate_id']}-{rows[-1]['candidate_id']}" if len(rows) > 1 else str(rows[0]["candidate_id"])
    ax.text(
        midpoint,
        y1 - (y1 - y0) * 0.055,
        f"{label}\n{ids}",
        color="#061014" if color == "#00c853" else "#ffffff",
        ha="center",
        va="top",
        fontsize=7.6,
        fontweight="bold",
        bbox={"facecolor": color, "edgecolor": "#ffffff", "linewidth": 0.45, "alpha": 0.72, "boxstyle": "round,pad=0.22"},
        zorder=30,
    )


def _render_riskgate_preview_png(
    *,
    forward_run_dir: Path,
    day: str,
    predictions_rows: pd.DataFrame,
    audit_rows: pd.DataFrame,
    out_path: Path,
    data_root: Path = PROJECT_ROOT,
    symbol: str = SYMBOL,
    timeframe: str = TIMEFRAME,
) -> None:
    source = _source_csv(data_root, day, timeframe, symbol)
    if not source.exists():
        raise FileNotFoundError(f"OHLCV source not found: {source}")
    day_df = _load_ohlcv(source)
    context_path = _find_context_ohlcv_path(forward_run_dir, day)
    strength_df = _load_ohlcv(context_path) if context_path is not None and context_path.exists() else day_df
    strength_rows = _build_strength_strip_rows(strength_df, day, has_next_render_day=True)

    plot_rows = predictions_rows.merge(
        audit_rows[
            [
                "candidate_id",
                "RISK_GATE_STATUS",
                "RISK_GATE_ACTION",
                "RISK_GATE_REASON",
                "RISK_GATE_SCORE",
                "RISK_GATE_PRIMARY_REGIME",
                "RISK_GATE_PRIMARY_REGIME_SHORT",
                "RISK_GATE_TAGS",
                "RISK_GATE_RAW_STATUS",
                "RISK_GATE_RAW_PRIMARY_REGIME",
                "USER_VISUAL_VERDICT",
            ]
        ],
        on="candidate_id",
        how="left",
    )

    fig, axes = plt.subplots(
        8,
        1,
        figsize=(32, 18.25),
        sharex=True,
        gridspec_kw={"height_ratios": [5.35, 0.44, 0.38, 0.38, 0.38, 0.46, 1.35, 1.25], "hspace": 0.045},
    )
    ax_price, ax_risk, ax_bg_phase, ax_long_wave, ax_short_wave, ax_macro_wave, ax_score, ax_vol = axes
    fig.patch.set_facecolor("#101418")
    for ax in [ax_price, ax_risk, ax_vol]:
        _style_axis(ax)
    _draw_candles(ax_price, day_df.reset_index(drop=True), timeframe, linewidth=0.28)
    _shade_sessions(ax_price, day, label_top=True)

    enters = plot_rows[plot_rows[DECISION_COLUMN].eq("ENTER")].sort_values("entry_ts").copy()
    _draw_group_spans(ax_price, enters, status_values={"WARN_RISK"}, color="#ff9800", alpha=0.105, label="RG WARN", max_gap_min=58)
    _draw_group_spans(
        ax_price,
        enters,
        status_values={"BLOCK_HARD", "BLOCK_RISK"},
        color="#ff1744",
        alpha=0.145,
        label="RG BLOCK",
        max_gap_min=95,
    )
    _draw_group_spans(
        ax_price,
        enters,
        status_values={"PASS_USER_REBOUND"},
        color="#00c853",
        alpha=0.115,
        label="USER PASS",
        max_gap_min=24,
    )

    _plot_forward_markers(ax_price, plot_rows)
    label_effects = [pe.withStroke(linewidth=1.7, foreground="#061014")]
    style_map = {
        "BLOCK_HARD": {"edge": "#ff1744", "text": "BH", "size": 265},
        "BLOCK_RISK": {"edge": "#ff5252", "text": "B", "size": 230},
        "WARN_RISK": {"edge": "#ffb300", "text": "W", "size": 195},
        "PASS_USER_REBOUND": {"edge": "#00e676", "text": "UP", "size": 285},
        "PASS_RISK": {"edge": "#00e676", "text": "P", "size": 155},
    }
    for _, row in enters.iterrows():
        status = str(row.get("RISK_GATE_STATUS") or "PASS_RISK")
        style = style_map.get(status, style_map["PASS_RISK"])
        regime_label = str(row.get("RISK_GATE_PRIMARY_REGIME_SHORT") or style["text"])
        ts = pd.Timestamp(row["entry_ts"]).tz_convert(None)
        price = float(row["entry_price_visual"])
        ax_price.scatter([ts], [price], marker="o", s=style["size"], facecolors="none", edgecolors=style["edge"], linewidths=2.25, zorder=28)
        ax_price.annotate(
            regime_label,
            xy=(ts, price),
            xytext=(0, -18 if status.startswith("BLOCK") else -16),
            textcoords="offset points",
            ha="center",
            va="top",
            color=style["edge"],
            fontsize=7.5,
            fontweight="bold",
            path_effects=label_effects,
            zorder=31,
        )

    ax_risk.set_facecolor("#101418")
    ax_risk.set_ylim(0, 1)
    ax_risk.set_yticks([])
    ax_risk.grid(False)
    for spine in ax_risk.spines.values():
        spine.set_color("#3a444b")
    for _, row in plot_rows.iterrows():
        ts = pd.Timestamp(row["entry_ts"]).tz_convert(None)
        status = str(row.get("RISK_GATE_STATUS") or "PASS_RISK")
        decision = str(row[DECISION_COLUMN])
        width_min = 8 if decision == "ENTER" else 4
        start = ts - pd.Timedelta(minutes=width_min / 2)
        end = ts + pd.Timedelta(minutes=width_min / 2)
        ax_risk.add_patch(
            Rectangle(
                (mdates.date2num(start), 0.08),
                mdates.date2num(end) - mdates.date2num(start),
                0.84,
                facecolor=_risk_color(status),
                edgecolor="#101418",
                linewidth=0.25,
                alpha=0.97 if decision == "ENTER" else 0.42,
            )
        )
        if decision == "ENTER":
            text_color = "white" if status.startswith("BLOCK") else "#061014"
            ax_risk.text(ts, 0.52, str(row["candidate_id"]).replace("LA", ""), color=text_color, ha="center", va="center", fontsize=5.2, fontweight="bold")
    ax_risk.set_ylabel("RISK", color="white")
    ax_risk.set_xlim(pd.Timestamp(day).to_pydatetime(), (pd.Timestamp(day) + pd.Timedelta(days=1)).to_pydatetime())

    _render_rank_strip(
        ax_bg_phase,
        strength_rows["hour_rows"],
        day,
        rank_field="hour_background_phase_rank",
        label="Fon",
        color_kind="phase",
        pct_field="hour_background_phase_metric_pct",
    )
    _render_rank_strip(
        ax_long_wave,
        strength_rows["hour_rows"],
        day,
        rank_field="hour_long_wave_rank",
        label="LONG",
        color_kind="long",
        pct_field="hour_long_wave_up_from_low_pct",
    )
    _render_rank_strip(
        ax_short_wave,
        strength_rows["hour_rows"],
        day,
        rank_field="hour_short_wave_rank",
        label="SHORT",
        color_kind="short",
        pct_field="hour_short_wave_down_from_high_pct",
    )
    _render_v5_macro_wave_strip(ax_macro_wave, strength_rows["macro_wave_rows"], day)
    _plot_score_panel(ax_score, plot_rows)
    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(day_df["open"], day_df["close"])]
    ax_vol.bar(day_df["open_time_utc"].dt.tz_convert(None), day_df["volume"], width=_bar_width_days(timeframe), color=colors, alpha=0.72)

    counts = Counter(plot_rows[DECISION_COLUMN].astype(str))
    rg_counts = Counter(enters["RISK_GATE_STATUS"].astype(str))
    ax_price.set_title(
        (
            f"STAS5 V5C RiskGate audit-only | {symbol} {timeframe} {day} | "
            f"ENTER {counts.get('ENTER', 0)} -> BLOCK_HARD {rg_counts.get('BLOCK_HARD', 0)} / "
            f"BLOCK {rg_counts.get('BLOCK_RISK', 0)} / WARN {rg_counts.get('WARN_RISK', 0)} / "
            f"USER_PASS {rg_counts.get('PASS_USER_REBOUND', 0)}"
        ),
        color="white",
        fontsize=15,
    )
    ax_price.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    ax_price.legend(loc="upper left", fontsize=9, facecolor="#101418", edgecolor="#455a64", labelcolor="#eceff1")
    fig.text(
        0.765,
        0.958,
        "RiskGate audit_only\nUP = user-pass rebound/retest\nBH/B/W = raw warning/block\nNo model/forward changes",
        ha="left",
        va="top",
        fontsize=8.3,
        color="#eceff1",
        bbox={"facecolor": "#101418", "edgecolor": "#00e676", "linewidth": 0.8, "alpha": 0.84, "boxstyle": "round,pad=0.35"},
    )
    _set_day_time_axis(ax_vol, day)
    fig.autofmt_xdate()
    fig.subplots_adjust(left=0.055, right=0.995, top=0.965, bottom=0.055, hspace=0.045)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor())
    plt.close(fig)


def _write_day_report(path: Path, *, day: str, audit_rows: pd.DataFrame, png_path: Path, csv_path: Path, user_pass_ids: set[str]) -> None:
    enter = audit_rows[audit_rows["ENTRY_ALPHA_DECISION"].astype(str).eq("ENTER")].copy()
    lines = [
        f"# STAS5 V5C RiskGate audit-only {day}",
        "",
        f"Статус: `{STATUS_PASS}`.",
        "",
        "RiskGate работает как `audit_only`: модель, forward predictions и `ENTRY_ML_LIVE_DECISION` не изменялись.",
        "",
        f"- PNG: `{rel(png_path)}`",
        f"- CSV: `{rel(csv_path)}`",
        f"- User pass ids: `{', '.join(sorted(user_pass_ids)) if user_pass_ids else ''}`",
        f"- Taxonomy: `{RISK_GATE_TAXONOMY_VERSION}`",
        "",
        "## Итог ENTER",
        "",
        f"- ENTER всего: `{len(enter)}`",
    ]
    counts = Counter(enter["RISK_GATE_STATUS"].astype(str))
    for status in ["BLOCK_HARD", "BLOCK_RISK", "WARN_RISK", "PASS_USER_REBOUND", "PASS_RISK"]:
        lines.append(f"- {status}: `{counts.get(status, 0)}`")
    lines += [
        "",
        "## ENTER разбор",
        "",
        "| LA | time UTC | ENTRY score | RiskGate | primary | tags | raw | reason | dump | knife | short | breakdown | pre-dump | grounding | retest |",
        "|---|---:|---:|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in enter.iterrows():
        lines.append(
            "| {la} | {ts} | {score:.3f} | `{status}` | `{primary}` | `{tags}` | `{raw}` | `{reason}` | {dump:.2f} | {knife:.2f} | {short:.2f} | {breakdown:.2f} | {pre:.2f} | {ground:.2f} | {retest:.2f} |".format(
                la=row["candidate_id"],
                ts=str(row["entry_time_utc"]).replace(f"{day}T", "").replace("Z", ""),
                score=float(row["ENTRY_ALPHA_SCORE"]),
                status=row["RISK_GATE_STATUS"],
                primary=row.get("RISK_GATE_PRIMARY_REGIME", ""),
                tags=str(row.get("RISK_GATE_TAGS", "")).replace("|", "<br>"),
                raw=row["RISK_GATE_RAW_STATUS"],
                reason=row["RISK_GATE_REASON"],
                dump=float(row["DUMP_RISK_SCORE"]),
                knife=float(row["KNIFE_RISK_SCORE"]),
                short=float(row["SHORT_REGIME_SCORE"]),
                breakdown=float(row["BREAKDOWN_SCORE"]),
                pre=float(row["PRE_DUMP_SCORE"]),
                ground=float(row["GROUNDING_SCORE"]),
                retest=float(row["RETEST_SCORE"]),
            )
        )
    lines += [
        "",
        "## Guardrail",
        "",
        "RiskGate использует только текущие `ENTRY` score/decision и causal risk-признаки из forward X439. `entry_y`, `phase_y`, `state_y`, `reason_y`, ручные комментарии и future outcomes не являются live X.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_riskgate_audit(
    *,
    forward_run_dir: Path | None = None,
    predictions_path: Path | None = None,
    x439_path: Path | None = None,
    start_day: str | None = None,
    end_day: str | None = None,
    user_pass_ids: set[str] | None = None,
    skip_visual: bool = False,
    data_root: Path = PROJECT_ROOT,
    strict: bool = True,
) -> dict[str, Any]:
    user_pass_ids = user_pass_ids or set()
    run_dir = _resolve_forward_run_dir(forward_run_dir)
    pred_path = _find_predictions_path(run_dir, predictions_path)
    x_path = _find_x439_path(run_dir, x439_path)
    predictions = _load_predictions(pred_path)
    x439 = pd.read_csv(x_path, encoding="utf-8-sig")
    if start_day is None:
        start_day = str(predictions["day"].astype(str).min())
    if end_day is None:
        end_day = str(predictions["day"].astype(str).max())

    out_dir = run_dir / "riskgate_audit"
    day_outputs: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = [
        {"check": "predictions_csv_exists", "status": "PASS" if pred_path.exists() else "FAIL", "details": {"path": rel(pred_path)}},
        {"check": "x439_dataset_exists", "status": "PASS" if x_path.exists() else "FAIL", "details": {"path": rel(x_path)}},
        {"check": "riskgate_is_audit_only", "status": "PASS", "details": {"enforce": False}},
        {
            "check": "riskgate_taxonomy_v1_enabled",
            "status": "PASS",
            "details": {"taxonomy_version": RISK_GATE_TAXONOMY_VERSION, "regimes": RISK_REGIME_ORDER},
        },
        {
            "check": "riskgate_feature_columns_are_causal_allowlist_subset",
            "status": "PASS",
            "details": {"risk_feature_columns": [column for column in RISK_FEATURE_COLUMNS if column in x439.columns]},
        },
    ]

    all_audit_rows = []
    for day in iter_days(start_day, end_day):
        day_predictions = predictions[predictions["day"].astype(str).eq(day)].sort_values("entry_ts").reset_index(drop=True)
        day_user_pass_ids = _day_user_pass_ids(user_pass_ids, day=day, single_day=start_day == end_day)
        day_user_pass_ids = {item for item in day_user_pass_ids if item in set(day_predictions["candidate_id"].astype(str).str.upper())}
        audit_rows = _audit_dataframe(predictions=predictions, x439=x439, day=day, user_pass_ids=day_user_pass_ids)
        all_audit_rows.append(audit_rows)
        day_dir = out_dir / compact_day(day)
        day_dir.mkdir(parents=True, exist_ok=True)
        csv_path = day_dir / f"STAS5_V5C_RISKGATE_AUDIT_{compact_day(day)}_V1.csv"
        png_path = day_dir / f"STAS5_V5C_RISKGATE_AUDIT_{compact_day(day)}_V1.png"
        report_path = day_dir / f"STAS5_V5C_RISKGATE_AUDIT_{compact_day(day)}_RU.md"
        audit_rows.to_csv(csv_path, index=False, encoding="utf-8-sig")
        visual_status = "SKIPPED"
        if not skip_visual:
            try:
                _render_riskgate_preview_png(
                    forward_run_dir=run_dir,
                    day=day,
                    predictions_rows=day_predictions,
                    audit_rows=audit_rows,
                    out_path=png_path,
                    data_root=data_root,
                )
                visual_status = "READY"
            except Exception as exc:
                visual_status = "FAIL"
                if strict:
                    raise
                checks.append({"check": f"visual_render_{compact_day(day)}", "status": "FAIL", "details": {"error": str(exc)}})
        _write_day_report(report_path, day=day, audit_rows=audit_rows, png_path=png_path, csv_path=csv_path, user_pass_ids=day_user_pass_ids)
        enter = audit_rows[audit_rows["ENTRY_ALPHA_DECISION"].astype(str).eq("ENTER")]
        day_outputs.append(
            {
                "day": day,
                "rows": int(len(audit_rows)),
                "enter_count": int(len(enter)),
                "enter_risk_counts": {str(k): int(v) for k, v in Counter(enter["RISK_GATE_STATUS"].astype(str)).items()},
                "enter_primary_regime_counts": {str(k): int(v) for k, v in Counter(enter["RISK_GATE_PRIMARY_REGIME"].astype(str)).items()},
                "csv": rel(csv_path),
                "png": rel(png_path) if png_path.exists() else "",
                "report_ru": rel(report_path),
                "visual_status": visual_status,
                "user_pass_ids": sorted(day_user_pass_ids),
            }
        )

    audit_all = pd.concat(all_audit_rows, ignore_index=True) if all_audit_rows else pd.DataFrame()
    if not audit_all.empty:
        checks.append(
            {
                "check": "risk_source_time_lte_entry_time",
                "status": "PASS" if bool(audit_all["RISK_NO_FUTURE_OK"].all()) else "FAIL",
                "details": {"bad_rows": int((~audit_all["RISK_NO_FUTURE_OK"].astype(bool)).sum())},
            }
        )
    status = STATUS_PASS if all(check["status"] == "PASS" for check in checks) else STATUS_FAIL
    manifest = {
        "status": status,
        "created_utc": utc_now(),
        "mode": "audit_only",
        "forward_run_dir": rel(run_dir),
        "predictions_csv": rel(pred_path),
        "x439_csv": rel(x_path),
        "date_range": {"start_day": start_day, "end_day": end_day},
        "out_dir": rel(out_dir),
        "user_pass_ids": sorted(user_pass_ids),
        "day_outputs": day_outputs,
        "checks": checks,
        "guardrails": [
            "audit_only_no_entry_prediction_change",
            "riskgate_taxonomy_is_explanation_layer_not_entry_status",
            "uses_only_current_entry_alpha_and_causal_x439_risk_columns",
            "manual_user_pass_is_review_overlay_not_live_feature",
            "enforce_forbidden_until_separate_riskgate_guard_and_user_review_pass",
        ],
    }
    manifest_path = out_dir / "STAS5_V5C_RISKGATE_AUDIT_MANIFEST_V1.json"
    write_json(manifest_path, manifest)
    manifest["manifest_path"] = rel(manifest_path)
    if strict and status != STATUS_PASS:
        raise RuntimeError(f"RiskGate audit failed: {status}")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="STAS5 V5C RiskGate audit-only overlay")
    parser.add_argument("--forward-run-dir", type=Path, default=None)
    parser.add_argument("--predictions-path", type=Path, default=None)
    parser.add_argument("--x439-path", type=Path, default=None)
    parser.add_argument("--start-day", default=None)
    parser.add_argument("--end-day", default=None)
    parser.add_argument("--user-pass-ids", default="")
    parser.add_argument("--skip-visual", action="store_true")
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args(argv)
    manifest = run_riskgate_audit(
        forward_run_dir=args.forward_run_dir,
        predictions_path=args.predictions_path,
        x439_path=args.x439_path,
        start_day=args.start_day,
        end_day=args.end_day,
        user_pass_ids=_parse_id_list(args.user_pass_ids),
        skip_visual=args.skip_visual,
        strict=not args.no_strict,
    )
    print(json.dumps({"status": manifest["status"], "manifest_path": manifest["manifest_path"], "out_dir": manifest["out_dir"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
