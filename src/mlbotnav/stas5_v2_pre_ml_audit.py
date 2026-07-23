from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import (
    STAS5_ARTIFACTS_DIR,
    forbidden_feature_matches,
    is_cut_label,
    is_keep_label,
    load_manifest_feature_columns,
    read_csv,
    rel,
    utc_now,
    write_json,
)
from mlbotnav.stas5_v2_feature_snapshot_builder import (
    DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH,
    DEFAULT_V2_FEATURE_SNAPSHOT_PATH,
)
from mlbotnav.stas5_v2_forward_error_ledger import (
    DEFAULT_FORWARD_ERROR_LEDGER_MANIFEST_PATH,
    DEFAULT_FORWARD_ERROR_LEDGER_PATH,
)
from mlbotnav.stas5_v2_leakage_guard import DEFAULT_V2_GUARD_REPORT_PATH


STATUS = "STAS5_V2_PRE_ML_AUDIT_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3"
DEFAULT_V2_PRE_ML_AUDIT_MD_PATH = STAS5_ARTIFACTS_DIR / "v2_audit" / "STAS5_V2_PRE_ML_AUDIT_20260501_20260520_RU.md"
DEFAULT_V2_PRE_ML_AUDIT_JSON_PATH = STAS5_ARTIFACTS_DIR / "v2_audit" / "stas5_v2_pre_ml_audit_20260501_20260520_v0.json"

KEY_CATEGORICAL_COLUMNS = [
    "suggested_type",
    "effective_session_code",
    "session_time_bucket_code",
    "entry_setup_quality_code",
    "pre_15m_background_phase",
    "pre_30m_long_wave_phase",
    "pre_60m_background_phase",
    "stas5_v2_gate_long_allowed_final",
    "stas5_v2_gate_no_trade_reason_code",
    "stas4_v2_combo_rsi_zone_code",
    "stas4_v2_combo_macd_state_code",
    "stas4_v2_combo_stoch_zone_code",
    "stas4_v2_density_near_vpoc60",
    "stas4_v2_density_near_vpoc240",
    "stas4_v2_structure_lower_range_flag",
    "stas4_v2_structure_high_range_flag",
    "stas4_v2_structure_near_support",
    "stas4_v2_structure_near_resistance",
    "stas4_v2_div_bullish_recent",
    "stas4_v2_div_hidden_bullish_recent",
    "stas5_v2_risk_weak_bounce_inside_drop",
    "stas5_v2_risk_too_high_in_drop",
    "stas5_v2_risk_no_clear_low",
]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
        if not math.isfinite(out):
            return default
        return out
    except Exception:
        return default


def _label_counts(df: pd.DataFrame) -> dict[str, int]:
    labels = df["human_label"].astype(str) if "human_label" in df.columns else pd.Series(dtype=str)
    return {
        "rows": int(len(df)),
        "KEEP_DRAFT": int((labels == "KEEP_DRAFT").sum()),
        "CUT_DRAFT": int((labels == "CUT_DRAFT").sum()),
        "KEEP_APPROVED": int((labels == "KEEP_APPROVED").sum()),
        "CUT_APPROVED": int((labels == "CUT_APPROVED").sum()),
        "keep_total": int(labels.map(is_keep_label).sum()),
        "cut_total": int(labels.map(is_cut_label).sum()),
    }


def _feature_group(column: str) -> str:
    if column.startswith("stas4_v2_block_"):
        return "v2_stas4_blocks"
    if column.startswith("stas4_v2_pattern_"):
        return "v2_pattern"
    if column.startswith("stas5_v2_short_wave_"):
        return "v2_short_wave"
    if column.startswith("stas5_v2_gate_"):
        return "v2_gate"
    if column.startswith("stas5_v2_risk_"):
        return "v2_risk"
    if column.startswith("stas4_v2_combo_") or column.startswith("stas4_v2_indicator_"):
        return "v2_combo_indicator"
    if column.startswith("stas4_v2_density_"):
        return "v2_density"
    if column.startswith("stas4_v2_structure_"):
        return "v2_structure"
    if column.startswith("stas4_v2_volume_"):
        return "v2_volume"
    if column.startswith("stas4_v2_div_"):
        return "v2_divergence"
    if column.startswith("stas1_") or column in {"suggested_type", "score"}:
        return "v1_stas1_candidate"
    if column.startswith("pre_"):
        return "v1_stas2_pre_windows"
    if column.startswith("session_") or column in {"day_type", "is_weekend", "effective_session_code", "real_tradfi_session_open"}:
        return "v1_session"
    if column.startswith("entry_setup_") or column.startswith("context_"):
        return "v1_entry_context"
    return "other"


def _feature_coverage(df: pd.DataFrame, feature_columns: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for column in feature_columns:
        if column not in df.columns:
            rows.append({"column": column, "group": _feature_group(column), "present": False, "non_null": 0, "coverage": 0.0})
            continue
        non_null = int(df[column].notna().sum())
        rows.append(
            {
                "column": column,
                "group": _feature_group(column),
                "present": True,
                "non_null": non_null,
                "coverage": round(non_null / max(len(df), 1), 6),
            }
        )
    return sorted(rows, key=lambda item: (item["coverage"], item["column"]))


def _numeric_feature_audit(df: pd.DataFrame, feature_columns: list[str], *, min_non_null: int = 5) -> list[dict[str, Any]]:
    labels = df["human_label"].astype(str)
    keep_mask = labels.map(is_keep_label)
    cut_mask = labels.map(is_cut_label)
    rows: list[dict[str, Any]] = []
    for column in feature_columns:
        if column not in df.columns:
            continue
        values = pd.to_numeric(df[column], errors="coerce")
        non_null = int(values.notna().sum())
        if non_null < min_non_null or values.nunique(dropna=True) <= 1:
            continue
        keep_values = values[keep_mask & values.notna()]
        cut_values = values[cut_mask & values.notna()]
        if len(keep_values) < 2 or len(cut_values) < 3:
            continue
        keep_mean = float(keep_values.mean())
        cut_mean = float(cut_values.mean())
        keep_median = float(keep_values.median())
        cut_median = float(cut_values.median())
        pooled = float(values.std(ddof=0))
        effect = 0.0 if pooled == 0 or not math.isfinite(pooled) else (keep_mean - cut_mean) / pooled
        rows.append(
            {
                "column": column,
                "group": _feature_group(column),
                "non_null": non_null,
                "keep_mean": round(keep_mean, 6),
                "cut_mean": round(cut_mean, 6),
                "delta_mean": round(keep_mean - cut_mean, 6),
                "effect": round(effect, 6),
                "abs_effect": round(abs(effect), 6),
                "keep_median": round(keep_median, 6),
                "cut_median": round(cut_median, 6),
            }
        )
    return sorted(rows, key=lambda item: (-item["abs_effect"], item["column"]))


def _categorical_keep_cut(df: pd.DataFrame, columns: list[str], *, min_rows: int = 10, limit_per_column: int = 12) -> dict[str, list[dict[str, Any]]]:
    labels = df["human_label"].astype(str)
    out: dict[str, list[dict[str, Any]]] = {}
    for column in columns:
        if column not in df.columns:
            continue
        rows: list[dict[str, Any]] = []
        for value, group in df.groupby(column, dropna=False):
            if len(group) < min_rows:
                continue
            group_labels = labels.loc[group.index]
            keep = int(group_labels.map(is_keep_label).sum())
            cut = int(group_labels.map(is_cut_label).sum())
            total = int(len(group))
            rows.append(
                {
                    "value": "" if pd.isna(value) else str(value),
                    "rows": total,
                    "keep": keep,
                    "cut": cut,
                    "keep_rate": round(keep / max(total, 1), 6),
                }
            )
        if rows:
            out[column] = sorted(rows, key=lambda item: (-item["keep_rate"], -item["rows"], item["value"]))[:limit_per_column]
    return out


def _group_summary(numeric_rows: list[dict[str, Any]], feature_columns: list[str]) -> list[dict[str, Any]]:
    group_counts = Counter(_feature_group(column) for column in feature_columns)
    by_group: dict[str, list[float]] = {}
    for row in numeric_rows:
        by_group.setdefault(str(row["group"]), []).append(float(row["abs_effect"]))
    rows: list[dict[str, Any]] = []
    for group, count in sorted(group_counts.items()):
        effects = sorted(by_group.get(group, []), reverse=True)
        rows.append(
            {
                "group": group,
                "feature_count": int(count),
                "numeric_audited": int(len(effects)),
                "top_abs_effect": round(effects[0], 6) if effects else 0.0,
                "avg_top5_abs_effect": round(sum(effects[:5]) / max(len(effects[:5]), 1), 6) if effects else 0.0,
            }
        )
    return sorted(rows, key=lambda item: (-item["avg_top5_abs_effect"], item["group"]))


def _forward_error_summary(error_ledger: pd.DataFrame) -> dict[str, Any]:
    error_counts = Counter(error_ledger["error_class"].astype(str))
    expected_counts = Counter(error_ledger["v2_expected_decision"].astype(str))
    decision_counts = Counter(error_ledger["ML_DECISION_V1"].astype(str))
    primary_counts = Counter(error_ledger.get("risk_primary_reason", pd.Series(dtype=str)).astype(str))
    rows: list[dict[str, Any]] = []
    for error_class, group in error_ledger.groupby("error_class", dropna=False):
        rows.append(
            {
                "error_class": str(error_class),
                "rows": int(len(group)),
                "avg_score": round(float(pd.to_numeric(group["ML_KEEP_SCORE_V1"], errors="coerce").mean()), 6),
                "avg_max_up": round(float(pd.to_numeric(group["postfact_max_up_pct"], errors="coerce").mean()), 6),
                "avg_drawdown": round(float(pd.to_numeric(group["postfact_max_drawdown_pct"], errors="coerce").mean()), 6),
                "avg_knife": round(float(pd.to_numeric(group.get("stas5_v2_risk_knife_pre_entry"), errors="coerce").mean()), 6),
                "avg_short_pressure": round(float(pd.to_numeric(group.get("stas4_v2_combo_short_pressure_score"), errors="coerce").mean()), 6),
                "avg_long_recovery": round(float(pd.to_numeric(group.get("stas4_v2_combo_long_recovery_score"), errors="coerce").mean()), 6),
            }
        )
    return {
        "rows": int(len(error_ledger)),
        "decision_counts_v1": {str(k): int(v) for k, v in sorted(decision_counts.items())},
        "error_class_counts": {str(k): int(v) for k, v in sorted(error_counts.items())},
        "v2_expected_decision_counts": {str(k): int(v) for k, v in sorted(expected_counts.items())},
        "risk_primary_reason_counts": {str(k): int(v) for k, v in sorted(primary_counts.items())},
        "by_error_class": sorted(rows, key=lambda item: (-item["rows"], item["error_class"])),
    }


def _audit_conclusions(summary: dict[str, Any]) -> list[str]:
    error_counts = summary["forward_error_summary"]["error_class_counts"]
    bad_green = int(error_counts.get("GREEN_BAD_FALLING_KNIFE", 0)) + int(error_counts.get("GREEN_BAD_TOO_HIGH", 0)) + int(error_counts.get("GREEN_BAD_NO_REVERSAL", 0))
    missed_good = int(error_counts.get("SKIP_MISSED_GOOD", 0))
    green_good = int(error_counts.get("GREEN_GOOD", 0))
    top_groups = summary["feature_group_summary"][:3]
    top_group_text = ", ".join(f"{row['group']}({row['avg_top5_abs_effect']})" for row in top_groups)
    return [
        f"V2 feature matrix чистая и готова к следующему audit/modeling этапу: {summary['feature_count']} признаков, guard `{summary['guard_status']}`.",
        f"Forward audit подтверждает проблему V1: плохих зеленых входов `{bad_green}`, хороших зеленых `{green_good}`, пропущенных хороших SKIP `{missed_good}`.",
        f"Самые сильные группы признаков по train KEEP/CUT сейчас: {top_group_text}.",
        "Следующий шаг может быть только ablation baseline/controlled model после этого отчета; forward `15+` нельзя использовать для подбора threshold.",
    ]


def _markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
    if not rows:
        return ["_Нет данных._"]
    out = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return out


def _write_report_md(path: Path, summary: dict[str, Any]) -> None:
    lines: list[str] = [
        "# STAS5 V2 pre-ML audit",
        "",
        f"Статус: `{summary['status']}`.",
        "",
        "## Контроль",
        "",
        f"- Train rows: `{summary['label_counts']['rows']}`.",
        f"- KEEP_DRAFT: `{summary['label_counts']['KEEP_DRAFT']}`.",
        f"- CUT_DRAFT: `{summary['label_counts']['CUT_DRAFT']}`.",
        f"- KEEP + yellow_x: `{summary['keep_yellow_x_rows']}`.",
        f"- Feature count: `{summary['feature_count']}`.",
        f"- V2 guard: `{summary['guard_status']}`.",
        f"- Forward error ledger: `{summary['forward_error_manifest_status']}`.",
        f"- Forbidden feature columns: `{len(summary['forbidden_feature_columns'])}`.",
        "",
        "## Выводы",
        "",
    ]
    lines.extend(f"- {item}" for item in summary["conclusions"])
    lines.extend(
        [
            "",
            "## Группы признаков",
            "",
            *_markdown_table(summary["feature_group_summary"], ["group", "feature_count", "numeric_audited", "top_abs_effect", "avg_top5_abs_effect"]),
            "",
            "## Top Numeric KEEP/CUT Differences",
            "",
            *_markdown_table(
                summary["top_numeric_features"][:30],
                ["column", "group", "keep_mean", "cut_mean", "delta_mean", "effect", "abs_effect"],
            ),
            "",
            "## Forward Error Classes",
            "",
            *_markdown_table(
                summary["forward_error_summary"]["by_error_class"],
                ["error_class", "rows", "avg_score", "avg_max_up", "avg_drawdown", "avg_knife", "avg_short_pressure", "avg_long_recovery"],
            ),
            "",
            "## Forward Counts",
            "",
            "### V1 decisions",
            "",
            *_markdown_table(
                [{"name": key, "rows": value} for key, value in summary["forward_error_summary"]["decision_counts_v1"].items()],
                ["name", "rows"],
            ),
            "",
            "### V2 expected decisions",
            "",
            *_markdown_table(
                [{"name": key, "rows": value} for key, value in summary["forward_error_summary"]["v2_expected_decision_counts"].items()],
                ["name", "rows"],
            ),
            "",
            "## Categorical KEEP/CUT",
            "",
        ]
    )
    for column, rows in summary["categorical_keep_cut"].items():
        lines.extend([f"### {column}", "", *_markdown_table(rows, ["value", "rows", "keep", "cut", "keep_rate"]), ""])
    lines.extend(
        [
            "## Граница",
            "",
            "Этот отчет не обучает модель, не подбирает threshold, не использует Stas3/TP/exit и не превращает forward postfact в feature.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_v2_pre_ml_audit_from_frames(
    *,
    snapshot: pd.DataFrame,
    feature_columns: list[str],
    guard_report: dict[str, Any],
    forward_error_ledger: pd.DataFrame,
    forward_error_manifest: dict[str, Any],
) -> dict[str, Any]:
    forbidden = forbidden_feature_matches(feature_columns)
    label_counts = _label_counts(snapshot)
    keep_yellow_x_rows = 0
    if "yellow_x" in snapshot.columns and "human_label" in snapshot.columns:
        yellow = pd.to_numeric(snapshot["yellow_x"], errors="coerce").fillna(0).astype(int)
        keep_yellow_x_rows = int(sum(is_keep_label(label) and flag == 1 for label, flag in zip(snapshot["human_label"], yellow)))
    coverage = _feature_coverage(snapshot, feature_columns)
    low_coverage = [row for row in coverage if row["coverage"] < 0.98]
    numeric_audit = _numeric_feature_audit(snapshot, feature_columns)
    group_summary = _group_summary(numeric_audit, feature_columns)
    categorical = _categorical_keep_cut(snapshot, [column for column in KEY_CATEGORICAL_COLUMNS if column in feature_columns or column in snapshot.columns])
    forward_summary = _forward_error_summary(forward_error_ledger)

    ready = (
        label_counts["rows"] == 972
        and label_counts["KEEP_DRAFT"] == 115
        and label_counts["CUT_DRAFT"] == 857
        and keep_yellow_x_rows == 30
        and not forbidden
        and guard_report.get("status") == "PASS"
        and forward_error_manifest.get("status") == "PASS"
        and int(forward_summary["rows"]) == int(forward_error_manifest.get("rows", -1))
    )
    summary: dict[str, Any] = {
        "status": "READY_FOR_V2_ABLATION_BASELINE" if ready else "NOT_READY",
        "pipeline_status": STATUS,
        "created_utc": utc_now(),
        "label_counts": label_counts,
        "feature_count": int(len(feature_columns)),
        "keep_yellow_x_rows": keep_yellow_x_rows,
        "guard_status": guard_report.get("status"),
        "forward_error_manifest_status": forward_error_manifest.get("status"),
        "forbidden_feature_columns": forbidden,
        "low_coverage_features": low_coverage[:30],
        "feature_group_summary": group_summary,
        "top_numeric_features": numeric_audit[:80],
        "categorical_keep_cut": categorical,
        "forward_error_summary": forward_summary,
        "guardrails": [
            "audit_only_no_training",
            "train_keep_cut_from_20260501_20260514_only",
            "forward_error_ledger_is_audit_only",
            "postfact_not_feature",
            "no_threshold_tuning_on_20260515_plus",
            "no_stas3_tp_exit",
        ],
    }
    summary["conclusions"] = _audit_conclusions(summary)
    return summary


def run_v2_pre_ml_audit(
    *,
    snapshot_path: Path = DEFAULT_V2_FEATURE_SNAPSHOT_PATH,
    snapshot_manifest_path: Path = DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH,
    guard_report_path: Path = DEFAULT_V2_GUARD_REPORT_PATH,
    forward_error_ledger_path: Path = DEFAULT_FORWARD_ERROR_LEDGER_PATH,
    forward_error_manifest_path: Path = DEFAULT_FORWARD_ERROR_LEDGER_MANIFEST_PATH,
    output_md: Path = DEFAULT_V2_PRE_ML_AUDIT_MD_PATH,
    output_json: Path = DEFAULT_V2_PRE_ML_AUDIT_JSON_PATH,
    strict: bool = True,
) -> dict[str, Any]:
    for path in [snapshot_path, snapshot_manifest_path, guard_report_path, forward_error_ledger_path, forward_error_manifest_path]:
        if not path.exists():
            raise FileNotFoundError(f"required V2 pre-ML audit input not found: {path}")
    snapshot = read_csv(snapshot_path)
    feature_columns = load_manifest_feature_columns(snapshot_manifest_path)
    guard_report = json.loads(guard_report_path.read_text(encoding="utf-8"))
    forward_error_ledger = read_csv(forward_error_ledger_path)
    forward_error_manifest = json.loads(forward_error_manifest_path.read_text(encoding="utf-8"))
    summary = run_v2_pre_ml_audit_from_frames(
        snapshot=snapshot,
        feature_columns=feature_columns,
        guard_report=guard_report,
        forward_error_ledger=forward_error_ledger,
        forward_error_manifest=forward_error_manifest,
    )
    summary.update(
        {
            "snapshot_path": rel(snapshot_path),
            "snapshot_manifest_path": rel(snapshot_manifest_path),
            "guard_report_path": rel(guard_report_path),
            "forward_error_ledger_path": rel(forward_error_ledger_path),
            "forward_error_manifest_path": rel(forward_error_manifest_path),
            "output_md": rel(output_md),
            "output_json": rel(output_json),
        }
    )
    write_json(output_json, summary)
    _write_report_md(output_md, summary)
    if strict and summary["status"] != "READY_FOR_V2_ABLATION_BASELINE":
        raise ValueError(f"STAS5 V2 pre-ML audit is not ready: {summary['status']}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Create STAS5 V2 pre-ML audit report.")
    parser.add_argument("--snapshot-path", default=str(DEFAULT_V2_FEATURE_SNAPSHOT_PATH))
    parser.add_argument("--snapshot-manifest-path", default=str(DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH))
    parser.add_argument("--guard-report-path", default=str(DEFAULT_V2_GUARD_REPORT_PATH))
    parser.add_argument("--forward-error-ledger-path", default=str(DEFAULT_FORWARD_ERROR_LEDGER_PATH))
    parser.add_argument("--forward-error-manifest-path", default=str(DEFAULT_FORWARD_ERROR_LEDGER_MANIFEST_PATH))
    parser.add_argument("--output-md", default=str(DEFAULT_V2_PRE_ML_AUDIT_MD_PATH))
    parser.add_argument("--output-json", default=str(DEFAULT_V2_PRE_ML_AUDIT_JSON_PATH))
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()
    summary = run_v2_pre_ml_audit(
        snapshot_path=Path(args.snapshot_path),
        snapshot_manifest_path=Path(args.snapshot_manifest_path),
        guard_report_path=Path(args.guard_report_path),
        forward_error_ledger_path=Path(args.forward_error_ledger_path),
        forward_error_manifest_path=Path(args.forward_error_manifest_path),
        output_md=Path(args.output_md),
        output_json=Path(args.output_json),
        strict=not args.no_strict,
    )
    print(
        {
            "status": summary["status"],
            "feature_count": summary["feature_count"],
            "label_counts": summary["label_counts"],
            "forward_error_counts": summary["forward_error_summary"]["error_class_counts"],
        }
    )
    return 0 if summary["status"] == "READY_FOR_V2_ABLATION_BASELINE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
