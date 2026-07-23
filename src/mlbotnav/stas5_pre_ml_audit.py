from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import (
    DEFAULT_AUDIT_JSON_PATH,
    DEFAULT_AUDIT_REPORT_PATH,
    DEFAULT_FEATURE_MANIFEST_PATH,
    DEFAULT_FEATURE_PATH,
    DEFAULT_GUARD_REPORT_PATH,
    DEFAULT_LEDGER_MANIFEST_PATH,
    DEFAULT_LEDGER_PATH,
    STATUS_CURRENT,
    forbidden_feature_matches,
    load_manifest_feature_columns,
    read_csv,
    rel,
    utc_now,
    write_json,
)


def _label_counts(df: pd.DataFrame) -> dict[str, int]:
    labels = df["human_label"].astype(str) if "human_label" in df else pd.Series(dtype=str)
    return {
        "rows": int(len(df)),
        "KEEP_DRAFT": int((labels == "KEEP_DRAFT").sum()),
        "CUT_DRAFT": int((labels == "CUT_DRAFT").sum()),
        "KEEP_APPROVED": int((labels == "KEEP_APPROVED").sum()),
        "CUT_APPROVED": int((labels == "CUT_APPROVED").sum()),
    }


def _group_keep_cut(df: pd.DataFrame, column: str, *, limit: int = 20) -> list[dict[str, Any]]:
    if column not in df:
        return []
    rows: list[dict[str, Any]] = []
    for value, group in df.groupby(column, dropna=False):
        labels = group["human_label"].astype(str)
        keep = int(labels.str.startswith("KEEP").sum())
        cut = int(labels.str.startswith("CUT").sum())
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
    return sorted(rows, key=lambda item: (-item["keep_rate"], -item["rows"], item["value"]))[:limit]


def _feature_coverage(df: pd.DataFrame, feature_columns: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for column in feature_columns:
        if column not in df:
            rows.append({"column": column, "present": False, "non_null": 0, "coverage": 0.0})
            continue
        non_null = int(df[column].notna().sum())
        rows.append({"column": column, "present": True, "non_null": non_null, "coverage": round(non_null / max(len(df), 1), 6)})
    return sorted(rows, key=lambda item: (item["coverage"], item["column"]))


def _markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
    if not rows:
        return ["_Нет данных._"]
    out = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return out


def run_pre_ml_audit(
    *,
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    ledger_manifest_path: Path = DEFAULT_LEDGER_MANIFEST_PATH,
    feature_path: Path = DEFAULT_FEATURE_PATH,
    feature_manifest_path: Path = DEFAULT_FEATURE_MANIFEST_PATH,
    guard_report_path: Path = DEFAULT_GUARD_REPORT_PATH,
    output_md: Path = DEFAULT_AUDIT_REPORT_PATH,
    output_json: Path = DEFAULT_AUDIT_JSON_PATH,
) -> dict[str, Any]:
    ledger = read_csv(ledger_path)
    features = read_csv(feature_path)
    feature_columns = load_manifest_feature_columns(feature_manifest_path)
    feature_manifest = json.loads(feature_manifest_path.read_text(encoding="utf-8"))
    ledger_manifest = json.loads(ledger_manifest_path.read_text(encoding="utf-8")) if ledger_manifest_path.exists() else {}
    guard_report = json.loads(guard_report_path.read_text(encoding="utf-8")) if guard_report_path.exists() else {}

    forbidden = forbidden_feature_matches(feature_columns)
    counts = _label_counts(ledger)
    yellow_conflicts = ledger[ledger.get("yellow_x_conflict", 0).astype(int) == 1].copy() if "yellow_x_conflict" in ledger else pd.DataFrame()
    context_false = int((features.get("context_before_entry_check", pd.Series(dtype=bool)).astype(str).str.lower() == "false").sum()) if "context_before_entry_check" in features else None
    coverage = _feature_coverage(features, feature_columns)
    low_coverage = [row for row in coverage if row["coverage"] < 0.98][:20]
    group_columns = [
        "effective_session_code",
        "session_time_bucket_code",
        "suggested_type",
        "entry_setup_quality_code",
        "pre_15m_background_phase",
        "pre_30m_long_wave_phase",
        "pre_60m_background_phase",
    ]
    groups = {column: _group_keep_cut(features, column) for column in group_columns}

    ready = (
        counts.get("rows") == 972
        and counts.get("KEEP_DRAFT") == 115
        and counts.get("CUT_DRAFT") == 857
        and len(yellow_conflicts) == 30
        and not forbidden
        and context_false == 0
    )
    summary = {
        "status": "READY_FOR_CONTROLLED_BASELINE" if ready else "NOT_READY",
        "pipeline_status": STATUS_CURRENT,
        "created_utc": utc_now(),
        "ledger_path": rel(ledger_path),
        "feature_path": rel(feature_path),
        "counts": counts,
        "feature_count": len(feature_columns),
        "yellow_x_conflicts": int(len(yellow_conflicts)),
        "context_before_entry_false": context_false,
        "forbidden_feature_columns": forbidden,
        "ledger_manifest_status": ledger_manifest.get("status"),
        "feature_manifest_status": feature_manifest.get("status"),
        "guard_status": guard_report.get("status"),
        "low_coverage_features": low_coverage,
        "groups": groups,
    }

    conflict_rows = yellow_conflicts[["day", "candidate_id", "record_id", "entry_time_utc", "human_label"]].to_dict("records") if not yellow_conflicts.empty else []
    lines = [
        "# STAS5 pre-ML audit",
        "",
        f"Статус: `{summary['status']}`.",
        "",
        "## Row parity",
        "",
        f"- Ledger: `{counts['rows']}` rows.",
        f"- KEEP_DRAFT: `{counts['KEEP_DRAFT']}`.",
        f"- CUT_DRAFT: `{counts['CUT_DRAFT']}`.",
        f"- KEEP_DRAFT + yellow_x: `{summary['yellow_x_conflicts']}`.",
        f"- Feature rows: `{len(features)}`.",
        f"- Feature columns для модели: `{len(feature_columns)}`.",
        f"- `context_before_entry_check = false`: `{context_false}`.",
        f"- Forbidden feature columns: `{len(forbidden)}`.",
        "",
        "## Guard",
        "",
        f"- Ledger manifest: `{summary['ledger_manifest_status']}`.",
        f"- Feature manifest: `{summary['feature_manifest_status']}`.",
        f"- Leakage guard: `{summary['guard_status']}`.",
        "",
        "## KEEP + yellow_x",
        "",
        *_markdown_table(conflict_rows, ["day", "candidate_id", "record_id", "entry_time_utc", "human_label"]),
        "",
        "## Low Coverage Features",
        "",
        *_markdown_table(low_coverage, ["column", "coverage", "non_null", "present"]),
    ]
    for column, rows in groups.items():
        lines.extend(["", f"## KEEP/CUT by {column}", "", *_markdown_table(rows, ["value", "rows", "keep", "cut", "keep_rate"])])
    lines.extend(
        [
            "",
            "## Вывод",
            "",
            (
                "Dataset готов к controlled baseline: yellow X сохранен как audit-only, forbidden features не найдены, "
                "Stas3/TP/exit/future outcome не входят в feature matrix."
                if ready
                else "Dataset пока не готов: смотри row parity, coverage или leakage guard выше."
            ),
        ]
    )

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(output_json, summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Create STAS5 pre-ML audit report.")
    parser.add_argument("--ledger-path", default=str(DEFAULT_LEDGER_PATH))
    parser.add_argument("--ledger-manifest-path", default=str(DEFAULT_LEDGER_MANIFEST_PATH))
    parser.add_argument("--feature-path", default=str(DEFAULT_FEATURE_PATH))
    parser.add_argument("--feature-manifest-path", default=str(DEFAULT_FEATURE_MANIFEST_PATH))
    parser.add_argument("--guard-report-path", default=str(DEFAULT_GUARD_REPORT_PATH))
    parser.add_argument("--output-md", default=str(DEFAULT_AUDIT_REPORT_PATH))
    parser.add_argument("--output-json", default=str(DEFAULT_AUDIT_JSON_PATH))
    args = parser.parse_args()

    summary = run_pre_ml_audit(
        ledger_path=Path(args.ledger_path),
        ledger_manifest_path=Path(args.ledger_manifest_path),
        feature_path=Path(args.feature_path),
        feature_manifest_path=Path(args.feature_manifest_path),
        guard_report_path=Path(args.guard_report_path),
        output_md=Path(args.output_md),
        output_json=Path(args.output_json),
    )
    print(
        {
            "status": summary["status"],
            "counts": summary["counts"],
            "feature_count": summary["feature_count"],
            "forbidden_feature_columns": summary["forbidden_feature_columns"],
        }
    )
    return 0 if summary["status"] == "READY_FOR_CONTROLLED_BASELINE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
