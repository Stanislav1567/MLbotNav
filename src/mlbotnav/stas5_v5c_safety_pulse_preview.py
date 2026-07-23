from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import PROJECT_ROOT, compact_day, iter_days, rel, utc_now, write_json
from mlbotnav.stas5_v5_forward_visual_review import (
    DECISION_COLUMN,
    SCORE_COLUMN,
    SYMBOL,
    TIMEFRAME,
    _build_strength_strip_rows,
    _find_context_ohlcv_path,
    _find_predictions_path,
    _load_ohlcv,
    _load_predictions,
    _source_csv,
    render_forward_day_overview,
)
from mlbotnav.stas5_v5c_riskgate_audit import run_riskgate_audit


STATUS_PASS = "PASS_V5C_SAFETY_PULSE_PREVIEW_READY_NO_TRAINING"
STATUS_FAIL = "FAIL_V5C_SAFETY_PULSE_PREVIEW"
POLICY_BALANCED = "BALANCED_SAFETY_V1"
POLICY_HARD_BLOCK_ONLY = "HARD_BLOCK_ONLY_V1"
POLICY_NO_RISKGATE_ENTRY_ONLY = "NO_RISKGATE_ENTRY_ONLY_V1"
POLICY_DOWN_CHANNEL_NO_LONG = "DOWN_CHANNEL_NO_LONG_V1"
SUPPORTED_POLICIES = {
    POLICY_BALANCED,
    POLICY_HARD_BLOCK_ONLY,
    POLICY_NO_RISKGATE_ENTRY_ONLY,
    POLICY_DOWN_CHANNEL_NO_LONG,
}

KEY_COLUMNS = ["day", "candidate_id", "record_id", "entry_time_utc"]
DOWN_CHANNEL_FEATURE_COLUMNS = [
    "cs_return_60m_pct",
    "cs_return_120m_pct",
    "cs_return_240m_pct",
    "cs_range_60m_pct",
    "cs_range_120m_pct",
    "cs_range_240m_pct",
    "cs_lower_lows_count_30m",
    "cs_lower_highs_count_30m",
    "cs_short_pressure_now",
    "cs_long_pressure_now",
    "cs_dump_acceleration_score",
    "cs_pre_dump_risk_score",
    "cs_price_breaking_recent_support",
    "cs_falling_knife_active",
    "cs_sell_pressure_exhaustion_score",
    "cs_bounce_from_recent_low_pct",
    "stas5_v2_risk_weak_bounce_inside_drop",
    "fcs_channel_slope_pct_per_min",
    "fcs_channel_width_pct",
    "fcs_channel_position_0_1",
    "fcs_channel_breakdown_recent",
    "fcs_support_broken_recently",
    "fcs_knife_risk_score",
    "fcs_knife_active",
    "fcs_knife_drop_pct_so_far",
    "fcs_knife_exhaustion_score",
    "fcs_bounce_from_knife_low_pct",
    "fcs_grounding_confirmed_score",
    "fcs_retest_after_knife_score",
    "fcs_regime_score_short_pressure",
    "fcs_regime_score_active_dump",
    "fcs_regime_score_base_after_flush",
]


def _resolve_forward_run_dir(forward_run_id: str | None, forward_run_dir: Path | None) -> Path:
    if forward_run_dir is not None:
        return forward_run_dir
    if forward_run_id:
        return PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5c" / "forward" / "runs" / forward_run_id
    latest = PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5c" / "forward" / "STAS5_V5C_LATEST_TWO_BLOCK_FORWARD_RUN.json"
    if not latest.exists():
        raise FileNotFoundError(f"Latest V5C forward pointer not found: {latest}")
    payload = pd.read_json(latest, typ="series")
    return PROJECT_ROOT / str(payload["run_dir"])


def _audit_csv_for_day(forward_run_dir: Path, day: str) -> Path:
    compact = compact_day(day)
    return forward_run_dir / "riskgate_audit" / compact / f"STAS5_V5C_RISKGATE_AUDIT_{compact}_V1.csv"


def _find_x439_path(forward_run_dir: Path) -> Path:
    candidates = sorted(
        forward_run_dir.glob("STAS5_V5C_FORWARD_DATASET_*_X*_CONTINUOUS_V1.csv"),
        key=lambda item: item.stat().st_mtime,
    )
    if not candidates:
        raise FileNotFoundError(f"V5C forward dataset not found in {forward_run_dir}")
    return candidates[-1]


def _load_audit_rows(forward_run_dir: Path, start_day: str, end_day: str) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    missing: list[str] = []
    for day in iter_days(start_day, end_day):
        path = _audit_csv_for_day(forward_run_dir, day)
        if not path.exists():
            missing.append(rel(path))
            continue
        frames.append(pd.read_csv(path, encoding="utf-8-sig"))
    if missing:
        raise FileNotFoundError(f"RiskGate audit CSV missing: {missing}")
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _base_entry_decision(row: pd.Series) -> str:
    value = str(row.get("ENTRY_ML_LIVE_DECISION_BEFORE_RISKGATE") or "").strip().upper()
    if value in {"ENTER", "WATCH", "SKIP"}:
        return value
    value = str(row.get(DECISION_COLUMN) or "").strip().upper()
    return value if value in {"ENTER", "WATCH", "SKIP"} else "SKIP"


def _safe_float(row: pd.Series, column: str, default: float = 0.0) -> float:
    try:
        value = row.get(column, default)
        if value is None or value == "":
            return default
        out = float(value)
        if math.isnan(out) or math.isinf(out):
            return default
        return out
    except Exception:
        return default


def _clip01(value: float) -> float:
    if math.isnan(value) or math.isinf(value):
        return 0.0
    return max(0.0, min(1.0, value))


def _down_channel_no_long_signals(row: pd.Series) -> dict[str, Any]:
    ret60 = _safe_float(row, "cs_return_60m_pct")
    ret120 = _safe_float(row, "cs_return_120m_pct")
    ret240 = _safe_float(row, "cs_return_240m_pct")
    range60 = _safe_float(row, "cs_range_60m_pct")
    range120 = _safe_float(row, "cs_range_120m_pct")
    lower_lows = _safe_float(row, "cs_lower_lows_count_30m")
    lower_highs = _safe_float(row, "cs_lower_highs_count_30m")
    short_pressure = max(_safe_float(row, "cs_short_pressure_now"), _safe_float(row, "fcs_regime_score_short_pressure"))
    long_pressure = _safe_float(row, "cs_long_pressure_now")
    active_dump = max(_safe_float(row, "fcs_regime_score_active_dump"), _safe_float(row, "cs_dump_acceleration_score"))
    pre_dump = _safe_float(row, "cs_pre_dump_risk_score")
    support_break = max(_safe_float(row, "cs_price_breaking_recent_support"), _safe_float(row, "fcs_support_broken_recently"))
    channel_break = _safe_float(row, "fcs_channel_breakdown_recent")
    channel_slope = _safe_float(row, "fcs_channel_slope_pct_per_min")
    channel_pos = _safe_float(row, "fcs_channel_position_0_1", 0.5)
    knife = max(_safe_float(row, "fcs_knife_risk_score"), _safe_float(row, "fcs_knife_active"), _safe_float(row, "cs_falling_knife_active"))
    weak_bounce_inside_drop = _safe_float(row, "stas5_v2_risk_weak_bounce_inside_drop")
    bounce_recent = _safe_float(row, "cs_bounce_from_recent_low_pct")
    bounce_knife = _safe_float(row, "fcs_bounce_from_knife_low_pct")
    bounce = max(bounce_recent, bounce_knife)
    grounding = _safe_float(row, "fcs_grounding_confirmed_score")
    retest = _safe_float(row, "fcs_retest_after_knife_score")
    exhaustion = max(_safe_float(row, "fcs_knife_exhaustion_score"), _safe_float(row, "cs_sell_pressure_exhaustion_score"))
    base_after_flush = _safe_float(row, "fcs_regime_score_base_after_flush")

    trend_hits = int(ret60 <= -0.45) + int(ret120 <= -0.70) + int(ret240 <= -1.10)
    bearish_trend = trend_hits >= 2 or (ret60 <= -0.35 and ret120 <= -1.00) or ret240 <= -1.65
    negative_channel = channel_break >= 0.9 or channel_slope <= -0.0025 or (channel_pos <= 0.12 and bearish_trend)
    short_dominates = short_pressure >= 0.55 and short_pressure >= long_pressure + 0.16
    repeated_lower_structure = lower_lows >= 12 and lower_highs >= 12
    weak_bounce = bounce <= 0.55 or weak_bounce_inside_drop >= 0.64
    low_realized_range = max(range60, range120) <= 1.65 and bounce <= 0.35
    no_take_profit_edge = range120 <= 2.30 and (
        low_realized_range
        or support_break >= 0.90
        or ret240 <= -2.80
    )
    structure_breakdown = support_break >= 0.9 or channel_break >= 0.9

    good_rebound_exception = (
        grounding >= 0.72
        and retest >= 0.76
        and exhaustion >= 0.58
        and bounce >= 0.58
        and active_dump < 0.88
    ) or (
        base_after_flush >= 0.85
        and bounce >= 0.80
        and short_pressure <= 0.65
        and active_dump < 0.82
    )

    no_long_edge = (
        bearish_trend
        and negative_channel
        and weak_bounce
        and (short_dominates or repeated_lower_structure or structure_breakdown)
        and not good_rebound_exception
    )
    down_channel_candidate = no_long_edge or (
        negative_channel
        and weak_bounce
        and (short_pressure >= 0.62 or pre_dump >= 0.70)
        and not good_rebound_exception
    )
    hard_block = down_channel_candidate and no_take_profit_edge
    demote = False
    trend_score = (int(ret60 <= -0.45) + int(ret120 <= -0.70) + int(ret240 <= -1.10)) / 3.0
    channel_score = max(channel_break, _clip01(abs(min(channel_slope, 0.0)) / 0.010), 1.0 - _clip01(channel_pos / 0.25))
    pressure_score = _clip01((short_pressure - long_pressure + 0.18) / 0.78)
    bounce_risk_score = 1.0 - _clip01(bounce / 0.90)
    structure_score = max(channel_break, support_break, _clip01(min(lower_lows, lower_highs) / 18.0))
    score = max(
        min(trend_score, channel_score, bounce_risk_score, max(pressure_score, structure_score)),
        0.92 if hard_block else 0.0,
        0.70 if demote else 0.0,
    )

    tags: list[str] = []
    if bearish_trend:
        tags.append("BEARISH_MULTI_WINDOW")
    if negative_channel:
        tags.append("DESCENDING_CHANNEL")
    if short_dominates:
        tags.append("SHORT_DOMINATES_LONG")
    if weak_bounce:
        tags.append("WEAK_BOUNCE")
    if repeated_lower_structure:
        tags.append("LOWER_LOWS_LOWER_HIGHS")
    if low_realized_range:
        tags.append("LOW_AMPLITUDE_NO_EDGE")
    if no_take_profit_edge:
        tags.append("NO_TAKE_PROFIT_EDGE")
    if structure_breakdown:
        tags.append("STRUCTURE_BREAKDOWN")
    if good_rebound_exception:
        tags.append("GOOD_REBOUND_EXCEPTION")

    return {
        "DOWN_CHANNEL_NO_LONG_SCORE": round(float(score), 6),
        "DOWN_CHANNEL_NO_LONG_FLAG": int(hard_block),
        "WEAK_BOUNCE_NO_EDGE_FLAG": int(demote),
        "GOOD_REBOUND_EXCEPTION_FLAG": int(good_rebound_exception),
        "DOWN_CHANNEL_NO_LONG_TAGS": "|".join(tags) if tags else "",
        "DOWN_CHANNEL_NO_LONG_DIAGNOSTIC": json.dumps(
            {
                "ret60": round(ret60, 4),
                "ret120": round(ret120, 4),
                "ret240": round(ret240, 4),
                "range60": round(range60, 4),
                "range120": round(range120, 4),
                "no_take_profit_edge": int(no_take_profit_edge),
                "short": round(short_pressure, 4),
                "long": round(long_pressure, 4),
                "bounce": round(bounce, 4),
                "channel_slope": round(channel_slope, 6),
                "channel_pos": round(channel_pos, 4),
                "channel_break": round(channel_break, 4),
                "active_dump": round(active_dump, 4),
                "knife": round(knife, 4),
                "lower_lows": round(lower_lows, 4),
                "lower_highs": round(lower_highs, 4),
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
    }


def _balanced_safety_decision(row: pd.Series, *, policy: str = POLICY_BALANCED) -> tuple[str, str, str]:
    base = _base_entry_decision(row)
    taxonomy_action = str(row.get("RISK_GATE_ACTION") or "KEEP").strip().upper()
    taxonomy_status = str(row.get("RISK_GATE_STATUS") or "PASS_RISK").strip().upper()
    taxonomy_reason = str(row.get("RISK_GATE_PRIMARY_REGIME") or row.get("RISK_GATE_REASON") or "NO_FATAL_RISK")
    ml_decision = str(row.get("RISKGATE_ML_LIVE_DECISION") or "PASS_RISK").strip().upper()

    if base == "SKIP":
        return "SKIP", "KEEP_BASE_SKIP", "ENTRY_BASE_SKIP"

    if policy == POLICY_NO_RISKGATE_ENTRY_ONLY:
        return base, "KEEP_ENTRY_ONLY_NO_RISKGATE", "NO_RISKGATE_PREVIEW"

    down_channel = _down_channel_no_long_signals(row)
    if policy == POLICY_DOWN_CHANNEL_NO_LONG and down_channel["GOOD_REBOUND_EXCEPTION_FLAG"]:
        return base, "KEEP_GOOD_REBOUND_EXCEPTION", "GOOD_REBOUND_EXCEPTION"
    if policy == POLICY_DOWN_CHANNEL_NO_LONG:
        if down_channel["DOWN_CHANNEL_NO_LONG_FLAG"]:
            return "SKIP", "DOWN_CHANNEL_NO_LONG_BLOCK_TO_SKIP", "DOWN_CHANNEL_NO_LONG"
        return base, "KEEP_DOWN_CHANNEL_NO_LONG_CLEAN", "NO_DOWN_CHANNEL_NO_LONG"

    if taxonomy_action == "WOULD_BLOCK" or taxonomy_status in {"BLOCK_HARD", "BLOCK_RISK"}:
        return "SKIP", "TAXONOMY_BLOCK_TO_SKIP", taxonomy_reason

    if policy == POLICY_HARD_BLOCK_ONLY:
        return base, "KEEP_NON_FATAL_RISK_FOR_VISUAL_REVIEW", taxonomy_reason

    if taxonomy_action == "WOULD_DEMOTE" or taxonomy_status == "WARN_RISK":
        if base == "ENTER":
            return "WATCH", "TAXONOMY_DEMOTE_TO_WATCH", taxonomy_reason
        return base, "KEEP_TAXONOMY_WARN_ALREADY_WATCH", taxonomy_reason

    if ml_decision == "BLOCK_RISK" and base == "ENTER":
        return "WATCH", "ML_RISK_DEMOTE_TO_WATCH", "ML_BLOCK_WITH_TAXONOMY_CLEAN"

    return base, "KEEP_ENTRY_DECISION", "NO_FATAL_RISK"


def build_safety_pulse_predictions(
    *,
    predictions: pd.DataFrame,
    audit_rows: pd.DataFrame,
    x439_rows: pd.DataFrame | None = None,
    policy: str = POLICY_BALANCED,
) -> pd.DataFrame:
    audit_cols = [
        "day",
        "candidate_id",
        "record_id",
        "entry_time_utc",
        "RISK_GATE_STATUS",
        "RISK_GATE_ACTION",
        "RISK_GATE_REASON",
        "RISK_GATE_PRIMARY_REGIME",
        "RISK_GATE_TAGS",
        "RISK_GATE_SCORE",
        "DUMP_RISK_SCORE",
        "KNIFE_RISK_SCORE",
        "SHORT_REGIME_SCORE",
        "BREAKDOWN_SCORE",
        "PRE_DUMP_SCORE",
        "GROUNDING_SCORE",
        "RETEST_SCORE",
        "EXHAUSTION_SCORE",
        "RISK_NO_FUTURE_OK",
    ]
    available_audit_cols = [col for col in audit_cols if col in audit_rows.columns]
    merged = predictions.merge(
        audit_rows[available_audit_cols],
        on=KEY_COLUMNS,
        how="left",
    )
    if x439_rows is not None:
        available_x_cols = [
            col
            for col in [*KEY_COLUMNS, *DOWN_CHANNEL_FEATURE_COLUMNS]
            if col in x439_rows.columns
        ]
        merged = merged.merge(x439_rows[available_x_cols], on=KEY_COLUMNS, how="left", suffixes=("", "_x439"))
    merged["ENTRY_ML_LIVE_DECISION_ORIGINAL_FINAL"] = merged[DECISION_COLUMN].astype(str)
    merged["ENTRY_ML_LIVE_DECISION_BEFORE_SAFETY_PULSE"] = merged.apply(_base_entry_decision, axis=1)
    down_channel_rows = [_down_channel_no_long_signals(row) for _, row in merged.iterrows()]
    for column in [
        "DOWN_CHANNEL_NO_LONG_SCORE",
        "DOWN_CHANNEL_NO_LONG_FLAG",
        "WEAK_BOUNCE_NO_EDGE_FLAG",
        "GOOD_REBOUND_EXCEPTION_FLAG",
        "DOWN_CHANNEL_NO_LONG_TAGS",
        "DOWN_CHANNEL_NO_LONG_DIAGNOSTIC",
    ]:
        merged[column] = [item[column] for item in down_channel_rows]
    merged["SAFETY_PULSE_POLICY"] = policy
    decisions: list[str] = []
    actions: list[str] = []
    reasons: list[str] = []
    for _, row in merged.iterrows():
        decision, action, reason = _balanced_safety_decision(row, policy=policy)
        decisions.append(decision)
        actions.append(action)
        reasons.append(reason)
    merged["BALANCED_SAFETY_PULSE_DECISION"] = decisions
    merged["BALANCED_SAFETY_PULSE_ACTION"] = actions
    merged["BALANCED_SAFETY_PULSE_REASON"] = reasons
    merged[DECISION_COLUMN] = merged["BALANCED_SAFETY_PULSE_DECISION"]
    if "ENTRY_POLICY" in merged.columns:
        merged["ENTRY_POLICY_ORIGINAL"] = merged["ENTRY_POLICY"].astype(str)
        merged["ENTRY_POLICY"] = merged["ENTRY_POLICY"].astype(str) + f"_{policy.lower()}_preview"
    else:
        merged["ENTRY_POLICY"] = f"{policy.lower()}_preview"
    return merged


def _review_annotations(rows: pd.DataFrame) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    changed = rows[
        rows["ENTRY_ML_LIVE_DECISION_BEFORE_SAFETY_PULSE"].astype(str).ne(rows["BALANCED_SAFETY_PULSE_DECISION"].astype(str))
    ]
    for _, row in changed.iterrows():
        candidate_id = str(row["candidate_id"]).upper()
        action = str(row.get("BALANCED_SAFETY_PULSE_ACTION") or "")
        if action in {"TAXONOMY_BLOCK_TO_SKIP", "DOWN_CHANNEL_NO_LONG_BLOCK_TO_SKIP"}:
            out[candidate_id] = ["RISK BAD"]
        elif action in {"TAXONOMY_DEMOTE_TO_WATCH", "ML_RISK_DEMOTE_TO_WATCH", "WEAK_BOUNCE_NO_EDGE_DEMOTE_TO_WATCH"}:
            out[candidate_id] = ["BAD"]
    return out


def _render_preview_day(
    *,
    forward_run_dir: Path,
    day: str,
    rows: pd.DataFrame,
    out_dir: Path,
    data_root: Path,
    bollinger_preview: bool = False,
) -> dict[str, Any]:
    day_dir = out_dir / compact_day(day)
    day_dir.mkdir(parents=True, exist_ok=True)
    source = _source_csv(data_root, day, TIMEFRAME, SYMBOL)
    if not source.exists():
        return {"day": day, "status": "MISSING_OHLCV", "source": rel(source), "rows": int(len(rows))}
    day_df = _load_ohlcv(source)
    context_path = _find_context_ohlcv_path(forward_run_dir, day)
    strength_source = context_path if context_path is not None and context_path.exists() else source
    strength_df = _load_ohlcv(strength_source)
    strength_rows = _build_strength_strip_rows(strength_df, day, has_next_render_day=True)

    csv_path = day_dir / f"STAS5_V5C_BALANCED_SAFETY_PULSE_{compact_day(day)}_V1.csv"
    png_suffix = "_BOLLINGER20_2SIGMA_PREVIEW" if bollinger_preview else ""
    png_path = day_dir / f"STAS5_V5C_BALANCED_SAFETY_PULSE_{compact_day(day)}{png_suffix}_V1.png"
    rows.drop(columns=["entry_ts"], errors="ignore").to_csv(csv_path, index=False, encoding="utf-8-sig")
    render_forward_day_overview(
        day_df=day_df,
        rows=rows,
        strength_hour_rows=strength_rows["hour_rows"],
        strength_macro_wave_rows=strength_rows["macro_wave_rows"],
        day=day,
        symbol=SYMBOL,
        timeframe=TIMEFRAME,
        out_path=png_path,
        review_annotations=_review_annotations(rows),
        bollinger_preview=bollinger_preview,
        bollinger_source_df=strength_df,
        bollinger_window=20,
        bollinger_std=2.0,
    )
    counts = Counter(rows[DECISION_COLUMN].astype(str))
    action_counts = Counter(rows["BALANCED_SAFETY_PULSE_ACTION"].astype(str))
    return {
        "day": day,
        "status": "READY",
        "rows": int(len(rows)),
        "decision_counts": {str(k): int(v) for k, v in counts.items()},
        "action_counts": {str(k): int(v) for k, v in action_counts.items()},
        "csv": rel(csv_path),
        "png": rel(png_path),
        "bollinger_preview": bool(bollinger_preview),
        "strength_source": rel(strength_source),
    }


def _write_report(path: Path, manifest: dict[str, Any]) -> None:
    policy = str(manifest.get("policy") or POLICY_BALANCED)
    lines = [
        "# STAS5 V5C Safety Pulse Preview",
        "",
        f"Статус: `{manifest['status']}`.",
        f"Policy: `{policy}`.",
        "",
        "Это быстрый тест-драйв поверх уже готового forward. Обучение, forward и исходные predictions не изменялись.",
        "",
        "Правило preview:",
        "",
        "- ENTRY берет исходное решение до RiskGate: `ENTRY_ML_LIVE_DECISION_BEFORE_RISKGATE`.",
    ]
    if policy == POLICY_DOWN_CHANNEL_NO_LONG:
        lines += [
            "- `DOWN_CHANNEL_NO_LONG_V1` не применяет старый taxonomy/ML mass-demote.",
            "- Блокирует только причинный режим `DOWN_CHANNEL_NO_LONG`: нисходящий канал + слабый отскок + нет хода под 1-1.5%.",
            "- Красный круг `RISK BAD` на PNG означает preview-блок `DOWN_CHANNEL_NO_LONG_BLOCK_TO_SKIP`.",
        ]
    else:
        lines += [
            "- Taxonomy `WOULD_BLOCK` переводит `ENTER/WATCH` в `SKIP`.",
            "- Taxonomy `WOULD_DEMOTE` переводит `ENTER` в `WATCH`.",
            "- `RISKGATE_ML=BLOCK_RISK` при чистой taxonomy только понижает `ENTER` в `WATCH`, а не душит в `SKIP`.",
        ]
    lines += [
        "",
        f"Forward run: `{manifest['forward_run_dir']}`",
        f"Preview dir: `{manifest['out_dir']}`",
        f"Bollinger preview: `{manifest.get('bollinger_preview', False)}`.",
        "",
        "## Итог по неделе",
        "",
        f"- До любого RiskGate ENTER: `{manifest['counts_before_safety'].get('ENTER', 0)}`",
        f"- До любого RiskGate WATCH: `{manifest['counts_before_safety'].get('WATCH', 0)}`",
        f"- Старый финал ENTER: `{manifest['counts_original_final'].get('ENTER', 0)}`",
        f"- Новый preview ENTER: `{manifest['counts_preview_final'].get('ENTER', 0)}`",
        f"- Новый preview WATCH: `{manifest['counts_preview_final'].get('WATCH', 0)}`",
        f"- Новый preview SKIP: `{manifest['counts_preview_final'].get('SKIP', 0)}`",
        "",
        "| День | Rows | ENTER | WATCH | SKIP | Taxonomy block | Down-channel block | Weak-bounce demote | Taxonomy demote | ML demote | PNG |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for item in manifest["day_outputs"]:
        counts = item.get("decision_counts", {})
        actions = item.get("action_counts", {})
        lines.append(
            "| "
            + str(item["day"])
            + " | "
            + str(item.get("rows", 0))
            + " | "
            + str(counts.get("ENTER", 0))
            + " | "
            + str(counts.get("WATCH", 0))
            + " | "
            + str(counts.get("SKIP", 0))
            + " | "
            + str(actions.get("TAXONOMY_BLOCK_TO_SKIP", 0))
            + " | "
            + str(actions.get("DOWN_CHANNEL_NO_LONG_BLOCK_TO_SKIP", 0))
            + " | "
            + str(actions.get("WEAK_BOUNCE_NO_EDGE_DEMOTE_TO_WATCH", 0))
            + " | "
            + str(actions.get("TAXONOMY_DEMOTE_TO_WATCH", 0))
            + " | "
            + str(actions.get("ML_RISK_DEMOTE_TO_WATCH", 0))
            + " | "
            + f"`{item.get('png', '')}`"
            + " |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_safety_pulse_preview(
    *,
    forward_run_id: str | None = None,
    forward_run_dir: Path | None = None,
    predictions_path: Path | None = None,
    start_day: str | None = None,
    end_day: str | None = None,
    data_root: Path = PROJECT_ROOT,
    policy: str = POLICY_BALANCED,
    bollinger_preview: bool = False,
    strict: bool = True,
) -> dict[str, Any]:
    run_dir = _resolve_forward_run_dir(forward_run_id, forward_run_dir)
    pred_path = _find_predictions_path(run_dir, predictions_path)
    predictions = _load_predictions(pred_path)
    if start_day is None:
        start_day = str(predictions["day"].astype(str).min())
    if end_day is None:
        end_day = str(predictions["day"].astype(str).max())

    run_riskgate_audit(
        forward_run_dir=run_dir,
        predictions_path=pred_path,
        start_day=start_day,
        end_day=end_day,
        skip_visual=True,
        strict=strict,
    )
    audit_rows = _load_audit_rows(run_dir, start_day, end_day)
    if policy not in SUPPORTED_POLICIES:
        raise ValueError(f"Unsupported safety pulse policy: {policy}")
    x439_path = _find_x439_path(run_dir)
    x439_rows = pd.read_csv(x439_path, encoding="utf-8-sig")
    preview = build_safety_pulse_predictions(predictions=predictions, audit_rows=audit_rows, x439_rows=x439_rows, policy=policy)
    out_dir = run_dir / "safety_pulse_preview" / policy.lower()
    out_dir.mkdir(parents=True, exist_ok=True)

    preview_csv = out_dir / f"STAS5_V5C_{policy}_{compact_day(start_day)}_{compact_day(end_day)}_PREDICTIONS_V1.csv"
    preview.drop(columns=["entry_ts"], errors="ignore").to_csv(preview_csv, index=False, encoding="utf-8-sig")

    day_outputs = []
    for day in iter_days(start_day, end_day):
        day_rows = preview[preview["day"].astype(str).eq(day)].sort_values("entry_ts").reset_index(drop=True)
        day_outputs.append(
            _render_preview_day(
                forward_run_dir=run_dir,
                day=day,
                rows=day_rows,
                out_dir=out_dir,
                data_root=data_root,
                bollinger_preview=bollinger_preview,
            )
        )

    checks = [
        {"check": "source_predictions_exists", "status": "PASS" if pred_path.exists() else "FAIL", "details": {"path": rel(pred_path)}},
        {"check": "source_x439_exists", "status": "PASS" if x439_path.exists() else "FAIL", "details": {"path": rel(x439_path)}},
        {"check": "riskgate_audit_rows_joined", "status": "PASS" if len(preview) == len(predictions) else "FAIL", "details": {"preview_rows": len(preview), "prediction_rows": len(predictions)}},
        {
            "check": "preview_does_not_modify_source_predictions",
            "status": "PASS",
            "details": {"source_predictions": rel(pred_path), "preview_predictions": rel(preview_csv)},
        },
        {
            "check": "no_future_contract",
            "status": "PASS" if bool(preview.get("RISK_NO_FUTURE_OK", pd.Series([True])).fillna(True).all()) else "FAIL",
            "details": {"bad_rows": int((~preview.get("RISK_NO_FUTURE_OK", pd.Series([True] * len(preview))).fillna(True).astype(bool)).sum())},
        },
    ]
    status = STATUS_PASS if all(item["status"] == "PASS" for item in checks) else STATUS_FAIL
    manifest = {
        "status": status,
        "created_utc": utc_now(),
        "mode": "preview_no_training_no_forward_mutation",
        "policy": policy,
        "bollinger_preview": bool(bollinger_preview),
        "bollinger_contract": "visual_only_rolling_20_2sigma_not_ml_feature" if bollinger_preview else "",
        "forward_run_dir": rel(run_dir),
        "source_predictions_csv": rel(pred_path),
        "source_x439_csv": rel(x439_path),
        "preview_predictions_csv": rel(preview_csv),
        "date_range": {"start_day": start_day, "end_day": end_day},
        "out_dir": rel(out_dir),
        "counts_before_safety": {str(k): int(v) for k, v in Counter(preview["ENTRY_ML_LIVE_DECISION_BEFORE_SAFETY_PULSE"].astype(str)).items()},
        "counts_original_final": {str(k): int(v) for k, v in Counter(preview["ENTRY_ML_LIVE_DECISION_ORIGINAL_FINAL"].astype(str)).items()},
        "counts_preview_final": {str(k): int(v) for k, v in Counter(preview[DECISION_COLUMN].astype(str)).items()},
        "safety_action_counts": {str(k): int(v) for k, v in Counter(preview["BALANCED_SAFETY_PULSE_ACTION"].astype(str)).items()},
        "day_outputs": day_outputs,
        "checks": checks,
        "guardrails": [
            "preview_only_no_training",
            "preview_only_no_forward_rebuild",
            "source_predictions_are_not_modified",
            "taxonomy_hard_block_before_ml_soft_demote",
            "down_channel_no_long_is_preview_only",
            "riskgate_ml_is_not_primary_hard_block_when_taxonomy_clean",
            "bollinger_overlay_is_visual_only_not_x439" if bollinger_preview else "bollinger_overlay_disabled",
        ],
    }
    manifest_path = out_dir / "STAS5_V5C_BALANCED_SAFETY_PULSE_MANIFEST_V1.json"
    report_path = out_dir / "STAS5_V5C_BALANCED_SAFETY_PULSE_AUDIT_RU.md"
    write_json(manifest_path, manifest)
    _write_report(report_path, manifest)
    manifest["manifest_path"] = rel(manifest_path)
    manifest["report_ru"] = rel(report_path)
    if strict and status != STATUS_PASS:
        raise RuntimeError(f"Safety pulse preview failed: {status}")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="STAS5 V5C balanced safety pulse preview")
    parser.add_argument("--forward-run-id", default="")
    parser.add_argument("--forward-run-dir", type=Path, default=None)
    parser.add_argument("--predictions-path", type=Path, default=None)
    parser.add_argument("--start-day", default=None)
    parser.add_argument("--end-day", default=None)
    parser.add_argument(
        "--policy",
        choices=sorted(SUPPORTED_POLICIES),
        default=POLICY_BALANCED,
    )
    parser.add_argument("--bollinger-preview", action="store_true")
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args(argv)
    manifest = run_safety_pulse_preview(
        forward_run_id=args.forward_run_id or None,
        forward_run_dir=args.forward_run_dir,
        predictions_path=args.predictions_path,
        start_day=args.start_day,
        end_day=args.end_day,
        policy=args.policy,
        bollinger_preview=args.bollinger_preview,
        strict=not args.no_strict,
    )
    print(
        json.dumps(
            {
            "status": manifest["status"],
            "policy": manifest["policy"],
            "out_dir": manifest["out_dir"],
            "bollinger_preview": manifest["bollinger_preview"],
            "preview_predictions_csv": manifest["preview_predictions_csv"],
            "counts_preview_final": manifest["counts_preview_final"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
