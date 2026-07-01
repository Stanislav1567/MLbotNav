from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CONTRACT_VERSION = "ml-trade-dataset-v1"

RUN_CONTEXT_COLUMNS = [
    "run_id",
    "symbol",
    "timeframe",
    "data_layer",
    "train_start",
    "train_end",
    "test_start",
    "test_end",
]

PASSPORT_CONTEXT_COLUMNS = [
    "block_id",
    "passport_id",
    "action_id",
    "side",
    "calibration_params_json",
]

ENTRY_EXIT_COLUMNS = [
    "entry_signal_time_utc",
    "entry_time_utc",
    "exit_time_utc",
    "entry_price",
    "exit_price",
    "exit_reason",
    "net_return",
    "net_pnl_usd",
]

OUTCOME_LABEL_COLUMNS = [
    "trade_id",
    "bars_in_trade",
    "tp_hit",
    "sl_hit",
    "timeout_hit",
    "mae_pct",
    "mfe_pct",
]

REQUIRED_COLUMNS = RUN_CONTEXT_COLUMNS + PASSPORT_CONTEXT_COLUMNS + ENTRY_EXIT_COLUMNS + OUTCOME_LABEL_COLUMNS

ALLOWED_EXIT_REASONS = {"tp", "sl", "sl_ambiguous", "timeout", "end_of_data", "manual_close", "unknown"}

HIT_LABELS_BY_EXIT_REASON = {
    "tp": (True, False, False),
    "sl": (False, True, False),
    "sl_ambiguous": (False, True, False),
    "timeout": (False, False, True),
    "end_of_data": (False, False, False),
    "manual_close": (False, False, False),
}


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _non_empty(value: object) -> bool:
    return str(value if value is not None else "").strip() != ""


def _parse_date(value: object) -> datetime | None:
    raw = str(value if value is not None else "").strip()
    try:
        return datetime.strptime(raw, "%Y-%m-%d")
    except Exception:
        return None


def _parse_timestamp(value: object) -> datetime | None:
    raw = str(value if value is not None else "").strip()
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        return None


def _parse_float(value: object) -> float | None:
    raw = str(value if value is not None else "").strip()
    if not raw or "," in raw:
        return None
    try:
        return float(raw)
    except Exception:
        return None


def _parse_int(value: object) -> int | None:
    raw = str(value if value is not None else "").strip()
    try:
        return int(raw)
    except Exception:
        return None


def _parse_bool(value: object) -> bool | None:
    raw = str(value if value is not None else "").strip().lower()
    if raw in {"1", "true", "yes", "y", "on"}:
        return True
    if raw in {"0", "false", "no", "n", "off"}:
        return False
    return None


def _normalize_side(value: object) -> str | None:
    raw = str(value if value is not None else "").strip().upper()
    if raw in {"1", "LONG"}:
        return "LONG"
    if raw in {"-1", "SHORT"}:
        return "SHORT"
    if raw in {"0", "NO_TRADE", "NONE"}:
        return "NO_TRADE"
    return None


def _is_trade_side(side: str | None) -> bool:
    return side in {"LONG", "SHORT"}


def _read_csv(csv_path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def _validate_common_row(row: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for col in RUN_CONTEXT_COLUMNS + PASSPORT_CONTEXT_COLUMNS:
        if not _non_empty(row.get(col)):
            errors.append(f"empty:{col}")

    if str(row.get("data_layer", "")).strip() != "core":
        errors.append("invalid:data_layer_not_core")

    train_start = _parse_date(row.get("train_start"))
    train_end = _parse_date(row.get("train_end"))
    test_start = _parse_date(row.get("test_start"))
    test_end = _parse_date(row.get("test_end"))
    for key, val in (
        ("train_start", train_start),
        ("train_end", train_end),
        ("test_start", test_start),
        ("test_end", test_end),
    ):
        if val is None:
            errors.append(f"invalid_date:{key}")
    if train_start and train_end and train_start > train_end:
        errors.append("invalid_window:train_start_gt_train_end")
    if test_start and test_end and test_start > test_end:
        errors.append("invalid_window:test_start_gt_test_end")

    try:
        cp = json.loads(str(row.get("calibration_params_json", "")).strip())
        if not isinstance(cp, dict) or not cp:
            errors.append("invalid_json:calibration_params_json_not_nonempty_object")
    except Exception:
        errors.append("invalid_json:calibration_params_json")

    if _normalize_side(row.get("side")) is None:
        errors.append("invalid_enum:side")
    return errors


def _validate_trade_row(row: dict[str, str], *, approved_mode: bool = True) -> list[str]:
    errors: list[str] = []
    for col in ENTRY_EXIT_COLUMNS + OUTCOME_LABEL_COLUMNS:
        if not _non_empty(row.get(col)):
            errors.append(f"empty:{col}")

    signal_ts = _parse_timestamp(row.get("entry_signal_time_utc"))
    entry_ts = _parse_timestamp(row.get("entry_time_utc"))
    exit_ts = _parse_timestamp(row.get("exit_time_utc"))
    if signal_ts is None:
        errors.append("invalid_ts:entry_signal_time_utc")
    if entry_ts is None:
        errors.append("invalid_ts:entry_time_utc")
    if exit_ts is None:
        errors.append("invalid_ts:exit_time_utc")
    if signal_ts and entry_ts and entry_ts < signal_ts:
        errors.append("invalid_time:entry_before_signal")
    if entry_ts and exit_ts and exit_ts < entry_ts:
        errors.append("invalid_time:exit_before_entry")

    entry_price = _parse_float(row.get("entry_price"))
    exit_price = _parse_float(row.get("exit_price"))
    if entry_price is None or entry_price <= 0:
        errors.append("invalid_positive_float:entry_price")
    if exit_price is None or exit_price <= 0:
        errors.append("invalid_positive_float:exit_price")

    if _parse_float(row.get("net_return")) is None:
        errors.append("invalid_float:net_return")
    if _parse_float(row.get("net_pnl_usd")) is None:
        errors.append("invalid_float:net_pnl_usd")

    exit_reason = str(row.get("exit_reason", "")).strip()
    if exit_reason not in ALLOWED_EXIT_REASONS:
        errors.append("invalid_enum:exit_reason")
    if approved_mode and exit_reason == "unknown":
        errors.append("invalid_for_approved:exit_reason_unknown")

    bars = _parse_int(row.get("bars_in_trade"))
    if bars is None or bars < 1:
        errors.append("invalid_int:bars_in_trade")

    tp_hit = _parse_bool(row.get("tp_hit"))
    sl_hit = _parse_bool(row.get("sl_hit"))
    timeout_hit = _parse_bool(row.get("timeout_hit"))
    if tp_hit is None:
        errors.append("invalid_bool:tp_hit")
    if sl_hit is None:
        errors.append("invalid_bool:sl_hit")
    if timeout_hit is None:
        errors.append("invalid_bool:timeout_hit")
    if exit_reason in HIT_LABELS_BY_EXIT_REASON and None not in {tp_hit, sl_hit, timeout_hit}:
        expected = HIT_LABELS_BY_EXIT_REASON[exit_reason]
        actual = (bool(tp_hit), bool(sl_hit), bool(timeout_hit))
        if actual != expected:
            errors.append("inconsistent:hit_labels_vs_exit_reason")

    mae = _parse_float(row.get("mae_pct"))
    mfe = _parse_float(row.get("mfe_pct"))
    if mae is None:
        errors.append("invalid_float:mae_pct")
    elif mae > 0:
        errors.append("invalid_range:mae_pct_gt_0")
    if mfe is None:
        errors.append("invalid_float:mfe_pct")
    elif mfe < 0:
        errors.append("invalid_range:mfe_pct_lt_0")

    return errors


def validate_trade_dataset_csv(csv_path: Path, *, approved_mode: bool = True) -> dict[str, Any]:
    if not csv_path.exists():
        return {
            "status": "FAIL",
            "contract_version": CONTRACT_VERSION,
            "reason": "csv_missing",
            "csv_path": str(csv_path),
            "rows_total": 0,
            "missing_columns": REQUIRED_COLUMNS,
            "failed_rows": [],
        }

    fieldnames, rows = _read_csv(csv_path)
    missing_columns = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
    failed_rows: list[dict[str, Any]] = []
    seen_trade_ids: set[tuple[str, str]] = set()

    for idx, row in enumerate(rows, start=1):
        row_errors = _validate_common_row(row)
        side = _normalize_side(row.get("side"))
        if _is_trade_side(side):
            row_errors.extend(_validate_trade_row(row, approved_mode=approved_mode))
            run_id = str(row.get("run_id", "")).strip()
            trade_id = str(row.get("trade_id", "")).strip()
            key = (run_id, trade_id)
            if trade_id and key in seen_trade_ids:
                row_errors.append("duplicate:trade_id_within_run_id")
            if trade_id:
                seen_trade_ids.add(key)

        if missing_columns and idx == 1:
            row_errors.append("missing_columns")
        if row_errors:
            failed_rows.append(
                {
                    "row_index": int(idx),
                    "run_id": str(row.get("run_id", "")).strip(),
                    "trade_id": str(row.get("trade_id", "")).strip(),
                    "errors": row_errors,
                }
            )

    status = "PASS" if (not missing_columns and not failed_rows and len(rows) > 0) else "FAIL"
    return {
        "status": status,
        "contract_version": CONTRACT_VERSION,
        "csv_path": str(csv_path),
        "rows_total": int(len(rows)),
        "missing_columns": missing_columns,
        "failed_rows": failed_rows,
        "approved_mode": bool(approved_mode),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ML trade dataset CSV contract.")
    parser.add_argument("--csv-path", required=True, help="Trade dataset CSV to validate.")
    parser.add_argument("--out-dir", default="reports/qa_gate", help="Where to write validation report JSON.")
    parser.add_argument("--debug-allow-unknown-exit", action="store_true", help="Allow exit_reason=unknown for debug-only validation.")
    args = parser.parse_args()

    csv_path = Path(args.csv_path).resolve()
    result = validate_trade_dataset_csv(csv_path, approved_mode=(not bool(args.debug_allow_unknown_exit)))

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"ml_trade_dataset_contract_audit_{_utc_tag()}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": result["status"],
                "report_path": str(out_path),
                "rows_total": result.get("rows_total"),
                "failed_rows": len(result.get("failed_rows", [])),
                "missing_columns": len(result.get("missing_columns", [])),
            },
            ensure_ascii=False,
        )
    )
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
