from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from mlbotnav.visual_entry_low_anchor_suggester import _load_ohlcv
from mlbotnav.visual_entry_strategy_passport_overlay_v2a import (
    _add_closed_bar_features,
    _breakout_retest_state,
    _fib_state,
    _last_structure_event,
    _nearest_levels,
    _raw_pivots,
    _row_index_at_time,
    _safe_float,
)
from mlbotnav.visual_entry_strategy_passport_overlay_v2b import _add_flow_density_features
from mlbotnav.visual_entry_strategy_passport_overlay_v2c_adx_stoch import _add_adx_stoch
from mlbotnav.visual_entry_strategy_passport_overlay_v2d_patterns import _add_pattern_features


STATUS = "TARGET_LED_DATASET_BASE_V0_READY_NO_ML_EXPORT_NO_TRAINING_NO_OPTUNA"
SYMBOL = "SOLUSDT"
TIMEFRAME = "1m"
SLIPPAGE_BPS = 5.0

SAFE_ML_CORE_BLOCKS = ["B015", "B017", "B010", "B013", "B019", "B020"]
CONTEXT_ONLY_BLOCKS = ["B014", "B018", "B008", "B024"]
BLOCKED_AS_ALLOW_BLOCKS = ["B009", "B021", "B022", "B023", "B026", "B016", "B025"]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def _source_csv(root: Path, day: str) -> Path:
    return root / "data" / "core" / "bybit_ohlcv" / f"dt={day}" / "tf=1m" / f"symbol={SYMBOL}" / "part-final.csv"


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fmt_num(value: Any, digits: int = 8) -> float | None:
    try:
        if value is None or pd.isna(value):
            return None
        val = float(value)
        if not np.isfinite(val):
            return None
        return round(val, digits)
    except Exception:
        return None


def _split_votes(value: Any) -> list[str]:
    if value is None or pd.isna(value):
        return []
    return [item.strip() for item in str(value).split(",") if item.strip()]


def _load_feature_frame(root: Path, day: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    df = _load_ohlcv(_source_csv(root, day))
    df = _add_closed_bar_features(df)
    df = _add_flow_density_features(df)
    df = _add_adx_stoch(df)
    df = _add_pattern_features(df)
    raw_pivots_3 = _raw_pivots(df, left=3, right=3)
    raw_pivots_10 = _raw_pivots(df, left=10, right=10)
    return df, {"raw_pivots_3": raw_pivots_3, "raw_pivots_10": raw_pivots_10}


def _base_sample(
    *,
    sample_id: str,
    source_day: str,
    source_table: str,
    source_role: str,
    signal_time_utc: str,
    entry_time_utc: str,
    target_type: str,
    label: str,
    ml_label: int | None,
    review_label: str,
    review_reason: str,
    user_verdict: str,
    nearest_manual_target: str = "",
    original_candidate_id: str = "",
    source_votes: list[str] | None = None,
    source_risk_flags: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "sample_id": sample_id,
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "source_day": source_day,
        "source_table": source_table,
        "source_role": source_role,
        "side": "long",
        "signal_time_utc": signal_time_utc,
        "entry_time_utc": entry_time_utc,
        "target_type": target_type,
        "label": label,
        "ml_label": "" if ml_label is None else ml_label,
        "for_future_ml_label_eligible": bool(ml_label in (0, 1)),
        "ml_use_allowed_now": False,
        "review_label": review_label,
        "review_reason": review_reason,
        "user_verdict": user_verdict,
        "nearest_manual_target": nearest_manual_target,
        "original_candidate_id": original_candidate_id,
        "source_votes": ",".join(source_votes or []),
        "source_risk_flags": ",".join(source_risk_flags or []),
    }


def _collect_samples(root: Path) -> list[dict[str, Any]]:
    base = root / "reports/final_review/visual_entry_v3/fresh_target_led"
    samples: list[dict[str, Any]] = []

    ledger14 = _read_json(base / "target_ledger_SOLUSDT_1m_2026-05-14_M01_M19.json")
    for item in ledger14.get("targets", []):
        samples.append(
            _base_sample(
                sample_id=str(item["target_id"]),
                source_day="2026-05-14",
                source_table="target_ledger_M01_M19",
                source_role="manual_gold_20260514",
                signal_time_utc=str(item["signal_time_utc"]),
                entry_time_utc=str(item["entry_time_utc"]),
                target_type=str(item.get("target_type", "")),
                label="gold_entry",
                ml_label=1,
                review_label=str(item.get("status", "gold_user_visual_confirmed")),
                review_reason="user_manual_gold_entry",
                user_verdict="entry",
            )
        )

    feedback14 = _read_csv(
        base
        / "low_anchor_entry_suggester_v0/extra_auto_review_v1/feedback_summary_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_20260701.csv"
    )
    for row in feedback14:
        review_label = str(row.get("review_label", ""))
        verdict = str(row.get("user_verdict", ""))
        if review_label == "bad_noise" and verdict == "reject":
            label = "rejected_bad_entry"
            ml_label: int | None = 0
            source_role = "manual_reject_20260514"
        elif review_label in {"possible_entry", "manual_shift_review"}:
            label = "unlabeled_review"
            ml_label = None
            source_role = "manual_review_not_training_label_20260514"
        else:
            continue
        samples.append(
            _base_sample(
                sample_id=str(row["candidate_id"]),
                source_day="2026-05-14",
                source_table="extra_auto_feedback_summary_v0",
                source_role=source_role,
                signal_time_utc=str(row["signal_time_utc"]),
                entry_time_utc=str(row["entry_time_utc"]),
                target_type=str(row.get("suggested_type", "")),
                label=label,
                ml_label=ml_label,
                review_label=review_label,
                review_reason=str(row.get("review_reason", "")),
                user_verdict=verdict,
                nearest_manual_target=str(row.get("nearest_manual_target", "")),
                original_candidate_id=str(row.get("candidate_id", "")),
            )
        )

    draft15 = _read_csv(
        base
        / "indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701.csv"
    )
    for row in draft15:
        samples.append(
            _base_sample(
                sample_id=str(row["entry_id"]),
                source_day="2026-05-15",
                source_table="T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1",
                source_role="manual_gold_20260515_corrected",
                signal_time_utc=str(row["signal_time_utc"]),
                entry_time_utc=str(row["entry_time_utc"]),
                target_type=str(row.get("source_transfer_type", "")),
                label="gold_entry",
                ml_label=1,
                review_label="user_confirmed_entry",
                review_reason="user_corrected_all_seven_entries_norm",
                user_verdict="entry",
                source_votes=_split_votes(row.get("no_lookahead_votes")),
                source_risk_flags=_split_votes(row.get("caution_votes")),
            )
        )

    feedback15 = _read_csv(
        base
        / "low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v2/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.csv"
    )
    for row in feedback15:
        if str(row.get("user_verdict", "")) != "reject":
            continue
        samples.append(
            _base_sample(
                sample_id=str(row["candidate_id"]),
                source_day="2026-05-15",
                source_table="T15_USER_FEEDBACK_V2_REJECTS",
                source_role="manual_reject_20260515",
                signal_time_utc=str(row["signal_time_utc"]),
                entry_time_utc=str(row["entry_time_utc"]),
                target_type=str(row.get("transfer_type", "")),
                label="rejected_bad_entry",
                ml_label=0,
                review_label=str(row.get("review_label", "")),
                review_reason=str(row.get("review_reason", "")),
                user_verdict=str(row.get("user_verdict", "")),
                original_candidate_id=str(row.get("candidate_id", "")),
                source_votes=_split_votes(row.get("transfer_pass_votes")),
                source_risk_flags=_split_votes(row.get("transfer_risk_votes")),
            )
        )
    return samples


def _recent_bool(df: pd.DataFrame, idx: int, column: str, lookback: int) -> bool:
    start = max(0, idx - lookback + 1)
    return bool(df.iloc[start : idx + 1][column].fillna(False).astype(bool).any())


def _attach_features(sample: dict[str, Any], frames: dict[str, tuple[pd.DataFrame, dict[str, Any]]]) -> dict[str, Any]:
    df, aux = frames[sample["source_day"]]
    signal_idx = _row_index_at_time(df, str(sample["signal_time_utc"]))
    entry_idx = _row_index_at_time(df, str(sample["entry_time_utc"]))
    row = df.iloc[signal_idx]
    entry_row = df.iloc[entry_idx]
    close = _safe_float(row.get("close"))

    levels = _nearest_levels(df, aux["raw_pivots_3"], signal_idx)
    fib = _fib_state(aux["raw_pivots_10"], signal_idx)
    retest = _breakout_retest_state(df, aux["raw_pivots_3"], signal_idx)
    structure = _last_structure_event(
        df,
        aux["raw_pivots_3"],
        signal_idx,
        lookback=120,
        max_age=120,
        deviation_pct=0.15,
    )

    fib_levels = fib.get("levels", {}) if fib.get("status") == "ok" else {}
    fib_0382 = _safe_float(fib_levels.get("0.382"), np.nan)
    fib_0618 = _safe_float(fib_levels.get("0.618"), np.nan)
    fib_0382_dist_pct = None if not np.isfinite(fib_0382) else round((close - fib_0382) / max(close, 1e-9) * 100.0, 6)
    fib_0618_dist_pct = None if not np.isfinite(fib_0618) else round((close - fib_0618) / max(close, 1e-9) * 100.0, 6)

    b010_support = bool(_safe_float(row.get("volume_ratio20")) >= 1.25 or _safe_float(row.get("volume_z20")) >= 1.0 or _safe_float(row.get("delta_volume_ratio20")) >= 0.75)
    vpoc60_dist = _safe_float(row.get("density_vpoc_distance_60_pct"))
    vpoc240_dist = _safe_float(row.get("density_vpoc_distance_240_pct"))
    cluster60 = _safe_float(row.get("density_cluster_share_60"))
    cluster_ratio = _safe_float(row.get("density_cluster_ratio_60_240"))
    b013_support = bool(abs(vpoc60_dist) <= 0.20 or abs(vpoc240_dist) <= 0.28 or cluster60 >= 0.18 or cluster_ratio >= 1.25)
    b019_support = bool(_recent_bool(df, signal_idx, "bull_candle_pattern", 3))
    b020_support = bool(
        _recent_bool(df, signal_idx, "rsi_bull_div_flag", 8)
        or _recent_bool(df, signal_idx, "macd_bull_div_flag", 8)
        or _recent_bool(df, signal_idx, "obv_bull_div_flag", 8)
    )
    b015_support = bool(fib.get("status") == "ok" and any(abs(v or 999.0) <= 0.35 for v in [fib_0382_dist_pct, fib_0618_dist_pct]))
    b017_support = bool(retest.get("retest_near_signal") or (_safe_float(retest.get("last_break_age_bars"), 999.0) <= 12))
    core_hits = {
        "B015": b015_support,
        "B017": b017_support,
        "B010": b010_support,
        "B013": b013_support,
        "B019": b019_support,
        "B020": b020_support,
    }

    enriched = dict(sample)
    enriched.update(
        {
            "row_index": signal_idx,
            "entry_open_price": _fmt_num(entry_row.get("open")),
            "entry_price_plus_5bps": _fmt_num(_safe_float(entry_row.get("open")) * (1.0 + SLIPPAGE_BPS / 10000.0)),
            "price_role": "execution_only_not_feature",
            "signal_close": _fmt_num(close),
            "ret_5m_pct": _fmt_num((close / _safe_float(df.iloc[max(0, signal_idx - 5)]["close"]) - 1.0) * 100.0, 6),
            "ret_15m_pct": _fmt_num((close / _safe_float(df.iloc[max(0, signal_idx - 15)]["close"]) - 1.0) * 100.0, 6),
            "ret_30m_pct": _fmt_num((close / _safe_float(df.iloc[max(0, signal_idx - 30)]["close"]) - 1.0) * 100.0, 6),
            "ret_60m_pct": _fmt_num((close / _safe_float(df.iloc[max(0, signal_idx - 60)]["close"]) - 1.0) * 100.0, 6),
            "ret_120m_pct": _fmt_num((close / _safe_float(df.iloc[max(0, signal_idx - 120)]["close"]) - 1.0) * 100.0, 6),
            "range_pos_60": _fmt_num(row.get("range_pos_60"), 6),
            "range_pos_180": _fmt_num(row.get("range_pos_180"), 6),
            "range_pos_240": _fmt_num(row.get("range_pos_240"), 6),
            "room_to_high_60_bps": _fmt_num(row.get("room_to_high_60_bps"), 6),
            "room_to_high_180_bps": _fmt_num(row.get("room_to_high_180_bps"), 6),
            "room_to_high_240_bps": _fmt_num(row.get("room_to_high_240_bps"), 6),
            "dist_from_low_60_bps": _fmt_num(row.get("dist_from_low_60_bps"), 6),
            "dist_from_low_180_bps": _fmt_num(row.get("dist_from_low_180_bps"), 6),
            "dist_from_low_240_bps": _fmt_num(row.get("dist_from_low_240_bps"), 6),
            "body_pct_of_price": _fmt_num(abs(_safe_float(row.get("close")) - _safe_float(row.get("open"))) / max(close, 1e-9) * 100.0, 6),
            "lower_wick_to_body": _fmt_num(_safe_float(row.get("lower_wick")) / max(_safe_float(row.get("body")), 1e-8), 6),
            "upper_wick_to_body": _fmt_num(_safe_float(row.get("upper_wick")) / max(_safe_float(row.get("body")), 1e-8), 6),
            "green_signal": bool(_safe_float(row.get("close")) >= _safe_float(row.get("open"))),
            "volume_ratio20": _fmt_num(row.get("volume_ratio20"), 6),
            "volume_z20": _fmt_num(row.get("volume_z20"), 6),
            "delta_volume_ratio20": _fmt_num(row.get("delta_volume_ratio20"), 6),
            "density_vpoc_distance_60_pct": _fmt_num(row.get("density_vpoc_distance_60_pct"), 6),
            "density_cluster_share_60": _fmt_num(row.get("density_cluster_share_60"), 6),
            "density_vpoc_distance_240_pct": _fmt_num(row.get("density_vpoc_distance_240_pct"), 6),
            "density_cluster_ratio_60_240": _fmt_num(row.get("density_cluster_ratio_60_240"), 6),
            "vwap_distance_pct": _fmt_num(row.get("vwap_distance_pct"), 6),
            "rsi14": _fmt_num(row.get("rsi14"), 6),
            "macd_hist": _fmt_num(row.get("macd_hist"), 8),
            "adx14": _fmt_num(row.get("adx14"), 6),
            "stoch_k14": _fmt_num(row.get("stoch_k14"), 6),
            "stoch_d14": _fmt_num(row.get("stoch_d14"), 6),
            "support_dist_pct": _fmt_num(levels.get("support_dist_pct"), 6),
            "resistance_dist_pct": _fmt_num(levels.get("resistance_dist_pct"), 6),
            "support_touches": levels.get("support_touches", 0),
            "resistance_touches": levels.get("resistance_touches", 0),
            "fib_status": fib.get("status"),
            "fib_direction": fib.get("direction", ""),
            "fib_0382_dist_pct": fib_0382_dist_pct,
            "fib_0618_dist_pct": fib_0618_dist_pct,
            "last_break_event": retest.get("last_break_event"),
            "last_break_age_bars": retest.get("last_break_age_bars"),
            "retest_near_signal": bool(retest.get("retest_near_signal")),
            "bos_up_now": bool(structure.get("bos_up_now")),
            "bos_down_now": bool(structure.get("bos_down_now")),
            "choch_like_near_signal": bool(structure.get("choch_like_near_signal")),
            "pattern_strength": _fmt_num(row.get("pattern_strength"), 6),
            "pattern_age_bars": _fmt_num(row.get("pattern_age_bars"), 6),
            "bull_candle_pattern_recent3": b019_support,
            "bull_divergence_recent8": b020_support,
            "B015_fibo_support": b015_support,
            "B017_retest_support": b017_support,
            "B010_volume_support": b010_support,
            "B013_density_support": b013_support,
            "B019_candle_support": b019_support,
            "B020_divergence_support": b020_support,
            "safe_core_hit_count": sum(1 for value in core_hits.values() if value),
            "safe_core_hits": ",".join([block for block, value in core_hits.items() if value]),
            "safe_ml_core_blocks": ",".join(SAFE_ML_CORE_BLOCKS),
            "context_only_blocks": ",".join(CONTEXT_ONLY_BLOCKS),
            "blocked_as_allow_blocks": ",".join(BLOCKED_AS_ALLOW_BLOCKS),
        }
    )
    return enriched


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _render_summary(path: Path, rows: list[dict[str, Any]]) -> None:
    df = pd.DataFrame(rows)
    counts = df.groupby(["source_day", "label"]).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(12, 6), facecolor="#0f1419")
    ax.set_facecolor("#0f1419")
    colors = {
        "gold_entry": "#00c853",
        "rejected_bad_entry": "#ef5350",
        "unlabeled_review": "#ffb74d",
    }
    x = np.arange(len(counts.index))
    bottom = np.zeros(len(counts.index))
    for label in ["gold_entry", "rejected_bad_entry", "unlabeled_review"]:
        values = counts[label].to_numpy() if label in counts else np.zeros(len(counts.index))
        ax.bar(x, values, bottom=bottom, label=label, color=colors[label], alpha=0.9)
        for i, value in enumerate(values):
            if value:
                ax.text(i, bottom[i] + value / 2, str(int(value)), ha="center", va="center", color="#06130e", fontweight="bold")
        bottom += values
    ax.set_xticks(x)
    ax.set_xticklabels(counts.index, color="#edf2f7")
    ax.set_ylabel("samples", color="#edf2f7")
    ax.set_title("Target-led dataset base V0 | labels collected only | NO ML EXPORT / NO TRAINING", color="#edf2f7")
    ax.legend(facecolor="#101820", edgecolor="#34424d", labelcolor="#edf2f7")
    ax.grid(axis="y", color="#26333d", alpha=0.55)
    ax.tick_params(colors="#edf2f7")
    for spine in ax.spines.values():
        spine.set_color("#34424d")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _write_report(
    path: Path,
    *,
    root: Path,
    artifacts: dict[str, str],
    rows: list[dict[str, Any]],
) -> None:
    df = pd.DataFrame(rows)
    label_counts = df.groupby(["source_day", "label"]).size().reset_index(name="count")
    eligible = int(df["for_future_ml_label_eligible"].sum())
    positives = int((df["ml_label"] == 1).sum())
    negatives = int((df["ml_label"] == 0).sum())
    unlabeled = int((df["ml_label"] == "").sum())
    lines = [
        "# Target-Led Dataset Base V0",
        "",
        f"Статус: `{STATUS}`.",
        "",
        "Назначение: собрать ручную базу good/reject из 14 и 15 мая в один dataset base для будущего ML.",
        "",
        "Это не ML-export, не обучение, не scorer, не target-lock и не Optuna.",
        "",
        "## Артефакты",
        "",
        f"- `{artifacts['csv']}`",
        f"- `{artifacts['json']}`",
        f"- `{artifacts['summary_png']}`",
        "",
        "## Состав",
        "",
        f"- Всего строк: `{len(rows)}`.",
        f"- Для будущего supervised ML размечено: `{eligible}`.",
        f"- Good `ml_label=1`: `{positives}`.",
        f"- Reject `ml_label=0`: `{negatives}`.",
        f"- Unlabeled review: `{unlabeled}`.",
        "",
        "## По дням",
        "",
    ]
    for _, row in label_counts.iterrows():
        lines.append(f"- `{row['source_day']}` `{row['label']}`: `{int(row['count'])}`.")
    lines.extend(
        [
            "",
            "## Блоки для будущего ML",
            "",
            f"- Core blocks: `{', '.join(SAFE_ML_CORE_BLOCKS)}`.",
            f"- Context-only blocks: `{', '.join(CONTEXT_ONLY_BLOCKS)}`.",
            f"- Blocked as standalone ALLOW: `{', '.join(BLOCKED_AS_ALLOW_BLOCKS)}`.",
            "",
            "## Границы",
            "",
            "- Entry open и `entry + 5 bps` сохранены только как execution/control, не как признаки выбора входа.",
            "- Все числовые признаки считаются на закрытой signal-свече или раньше.",
            "- `possible_entry` и `manual_shift_review` не входят в `ml_label`, пока пользователь не подтвердит их как good/reject.",
            "- Перед реальным ML нужен отдельный `APPROVED_FOR_ML`.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run() -> dict[str, Any]:
    root = _repo_root()
    out_dir = root / "reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_base_v0"
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = {day: _load_feature_frame(root, day) for day in ["2026-05-14", "2026-05-15"]}
    samples = _collect_samples(root)
    rows = [_attach_features(sample, frames) for sample in samples]
    rows = sorted(rows, key=lambda item: (item["source_day"], str(item["signal_time_utc"]), str(item["sample_id"])))

    csv_path = out_dir / "TARGET_LED_DATASET_BASE_V0_20260701.csv"
    json_path = out_dir / "TARGET_LED_DATASET_BASE_V0_20260701.json"
    report_ru = out_dir / "TARGET_LED_DATASET_BASE_V0_20260701_RU.md"
    summary_png = out_dir / "TARGET_LED_DATASET_BASE_V0_SUMMARY_20260701.png"
    _write_csv(csv_path, rows)
    payload = {
        "status": STATUS,
        "generated_at_utc": _utc_now(),
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "safe_ml_core_blocks": SAFE_ML_CORE_BLOCKS,
        "context_only_blocks": CONTEXT_ONLY_BLOCKS,
        "blocked_as_allow_blocks": BLOCKED_AS_ALLOW_BLOCKS,
        "rows": rows,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _render_summary(summary_png, rows)
    artifacts = {
        "csv": _rel(root, csv_path),
        "json": _rel(root, json_path),
        "report_ru": _rel(root, report_ru),
        "summary_png": _rel(root, summary_png),
    }
    _write_report(report_ru, root=root, artifacts=artifacts, rows=rows)
    return {
        "status": STATUS,
        "artifacts": artifacts,
        "counts": {
            "total": len(rows),
            "ml_labeled": sum(1 for row in rows if row["for_future_ml_label_eligible"]),
            "positive": sum(1 for row in rows if row["ml_label"] == 1),
            "negative": sum(1 for row in rows if row["ml_label"] == 0),
            "unlabeled_review": sum(1 for row in rows if row["ml_label"] == ""),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    print(json.dumps(run(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
