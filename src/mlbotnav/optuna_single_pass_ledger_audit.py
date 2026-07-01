from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_COLUMNS = [
    "ts_utc",
    "task_id",
    "mode",
    "symbol",
    "timeframe",
    "train_date",
    "test_date",
    "optuna_stage",
    "repeats_requested",
    "repeats_effective",
    "repeats_effective_mismatch",
    "result_status",
    "oos_net_return_pct",
    "oos_trades",
    "summary_path",
]


def _parse_bool(text: str | bool | None) -> bool:
    if isinstance(text, bool):
        return text
    t = str(text or "").strip().lower()
    return t in {"1", "true", "yes", "y", "on"}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def audit_ledger(ledger_path: Path, *, require_summary_exists: bool = True) -> dict[str, Any]:
    if not ledger_path.exists():
        return {
            "status": "FAIL",
            "reason": "ledger_missing",
            "ledger_path": str(ledger_path),
            "rows_total": 0,
            "failed_rows": [],
            "missing_columns": REQUIRED_COLUMNS,
        }

    with ledger_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        missing_columns = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
        rows = list(reader)

    failed_rows: list[dict[str, Any]] = []
    for idx, row in enumerate(rows, start=1):
        row_errors: list[str] = []

        if missing_columns:
            row_errors.append("missing_columns")
        for key in REQUIRED_COLUMNS:
            if key not in row:
                continue
            if str(row.get(key, "")).strip() == "":
                row_errors.append(f"empty:{key}")

        req = None
        eff = None
        trades = None
        oos = None
        mismatch = None
        try:
            req = int(str(row.get("repeats_requested", "")).strip())
        except Exception:
            row_errors.append("invalid_int:repeats_requested")
        try:
            eff = int(str(row.get("repeats_effective", "")).strip())
        except Exception:
            row_errors.append("invalid_int:repeats_effective")
        try:
            trades = int(str(row.get("oos_trades", "")).strip())
            if trades < 0:
                row_errors.append("negative:oos_trades")
        except Exception:
            row_errors.append("invalid_int:oos_trades")
        try:
            raw = str(row.get("oos_net_return_pct", "")).strip()
            if "," in raw:
                row_errors.append("decimal_comma:oos_net_return_pct")
            oos = float(raw)
            if not (-10000.0 <= oos <= 10000.0):
                row_errors.append("range:oos_net_return_pct")
        except Exception:
            row_errors.append("invalid_float:oos_net_return_pct")

        try:
            mismatch = _parse_bool(row.get("repeats_effective_mismatch"))
        except Exception:
            row_errors.append("invalid_bool:repeats_effective_mismatch")

        if req is not None and eff is not None and mismatch is not None:
            if mismatch is False and req != eff:
                row_errors.append("inconsistent:mismatch_false_but_req_ne_eff")
            if mismatch is True and req == eff:
                row_errors.append("inconsistent:mismatch_true_but_req_eq_eff")

        if str(row.get("mode", "")).strip() not in {"long_only", "short_only"}:
            row_errors.append("invalid_enum:mode")
        if str(row.get("result_status", "")).strip() not in {"goal_fail", "goal_pass", "train_failed", "search_failed"}:
            row_errors.append("invalid_enum:result_status")

        summary_path_raw = str(row.get("summary_path", "")).strip()
        if require_summary_exists:
            if not summary_path_raw:
                row_errors.append("empty:summary_path")
            else:
                sp = Path(summary_path_raw)
                if not sp.exists():
                    row_errors.append("missing:summary_path")

        if row_errors:
            failed_rows.append(
                {
                    "row_index": int(idx),
                    "task_id": str(row.get("task_id", "")).strip(),
                    "errors": row_errors,
                }
            )

    status = "PASS" if (not missing_columns and not failed_rows and len(rows) > 0) else "FAIL"
    return {
        "status": status,
        "ledger_path": str(ledger_path),
        "rows_total": int(len(rows)),
        "missing_columns": missing_columns,
        "failed_rows": failed_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit contract for optuna single-pass runs ledger CSV.")
    parser.add_argument("--ledger-path", default="reports/qa_gate/optuna_single_pass_runs.csv")
    parser.add_argument("--out-dir", default="reports/qa_gate")
    parser.add_argument("--no-summary-exists-check", action="store_true")
    args = parser.parse_args()

    ledger_path = Path(args.ledger_path).resolve()
    result = audit_ledger(ledger_path, require_summary_exists=(not bool(args.no_summary_exists_check)))
    now = _utc_now().strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"optuna_single_pass_ledger_audit_{now}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"status": result["status"], "report_path": str(out_path), "failed_rows": len(result.get("failed_rows", []))}))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

