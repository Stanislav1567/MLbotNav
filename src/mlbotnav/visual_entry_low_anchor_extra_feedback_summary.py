from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS = "LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_COMPLETE_NO_ML_NO_OPTUNA"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _feedback_paths(root: Path) -> list[Path]:
    base = root / "reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1"
    return [
        base / f"user_feedback_page{page:02d}_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE{page:02d}_FEEDBACK_20260701.json"
        for page in range(1, 7)
    ]


def _rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def build_summary(root: Path, out_dir: Path) -> dict[str, Any]:
    paths = _feedback_paths(root)
    payloads = [_read_json(path) for path in paths]
    all_records: list[dict[str, Any]] = []
    pages: list[dict[str, Any]] = []
    for path, payload in zip(paths, payloads):
        records = list(payload["records"])
        page_label_counts = Counter(str(row["review_label"]) for row in records)
        page_reason_counts = Counter(str(row["review_reason"]) for row in records)
        all_records.extend(records)
        pages.append(
            {
                "page": payload["page"],
                "candidate_count": payload["candidate_count"],
                "label_counts": payload.get("label_counts") or dict(sorted(page_label_counts.items())),
                "reason_counts": payload.get("reason_counts") or dict(sorted(page_reason_counts.items())),
                "source_json": _rel(root, path),
                "png": payload["artifacts"]["png"],
            }
        )

    label_counts = Counter(str(row["review_label"]) for row in all_records)
    reason_counts = Counter(str(row["review_reason"]) for row in all_records)
    records_by_label: dict[str, list[str]] = {}
    for row in all_records:
        records_by_label.setdefault(str(row["review_label"]), []).append(str(row["candidate_id"]))

    summary_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_20260701.json"
    csv_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_20260701.csv"
    report_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_20260701_RU.md"
    return {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "rail_point": "LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_NO_ML_NO_OPTUNA",
        "candidate_count": len(all_records),
        "page_count": len(pages),
        "label_counts": dict(sorted(label_counts.items())),
        "reason_counts": dict(sorted(reason_counts.items())),
        "records_by_label": records_by_label,
        "pages": pages,
        "records": all_records,
        "conclusion_ru": [
            "Extra auto pool полностью разобран пользователем на 6 страницах.",
            "Большинство extra-кандидатов стали явными anti-label, а не pending pool.",
            "possible_entry не является gold и требует отдельного сравнения с ручными good-входами.",
            "manual_shift_review не является обучающей меткой: это запрос на отдельный zoom-review и точную ручную фиксацию.",
            "Optuna, ML/export/promotion не разрешены и не запускались.",
        ],
        "artifacts": {
            "json": _rel(root, summary_path),
            "csv": _rel(root, csv_path),
            "report_ru": _rel(root, report_path),
        },
        "optuna_allowed": False,
        "ml_allowed": False,
    }


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    columns = [
        "candidate_id",
        "page",
        "review_label",
        "review_reason",
        "user_verdict",
        "signal_time_utc",
        "entry_time_utc",
        "entry_price_plus_5bps",
        "suggested_type",
        "nearest_manual_target",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in records:
            writer.writerow({col: row.get(col) for col in columns})


def write_report(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Low Anchor Extra Auto Feedback Summary",
        "",
        f"Статус: `{summary['status']}`.",
        "",
        f"Кандидатов: `{summary['candidate_count']}`.",
        f"Страниц: `{summary['page_count']}`.",
        "",
        "## Итоговые метки",
        "",
        "| label | count |",
        "|---|---:|",
    ]
    for label, count in summary["label_counts"].items():
        lines.append(f"| `{label}` | `{count}` |")
    lines.extend(["", "## Причины", "", "| reason | count |", "|---|---:|"])
    for reason, count in summary["reason_counts"].items():
        lines.append(f"| `{reason}` | `{count}` |")
    lines.extend(["", "## По страницам", "", "| page | count | labels | reasons |", "|---:|---:|---|---|"])
    for page in summary["pages"]:
        labels = ", ".join(f"{k}: {v}" for k, v in page["label_counts"].items())
        reasons = ", ".join(f"{k}: {v}" for k, v in page["reason_counts"].items())
        lines.append(f"| `{page['page']}` | `{page['candidate_count']}` | {labels} | {reasons} |")
    lines.extend(["", "## Вывод", ""])
    for item in summary["conclusion_ru"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Граница",
            "",
            "- Это feedback summary, не ML dataset.",
            "- `possible_entry` и `manual_shift_review` не являются gold labels.",
            "- ML/export/promotion запрещены без отдельного `APPROVED_FOR_ML`.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    out_dir = root / "reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/feedback_summary_v0"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = build_summary(root, out_dir)

    json_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_20260701.json"
    csv_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_20260701.csv"
    report_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_20260701_RU.md"

    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(csv_path, summary["records"])
    write_report(report_path, summary)
    print(json.dumps(summary["artifacts"], ensure_ascii=False, indent=2))
    print(json.dumps({"candidate_count": summary["candidate_count"], "label_counts": summary["label_counts"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
