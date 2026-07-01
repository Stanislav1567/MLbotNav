from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from mlbotnav.ml_trade_dataset_contract import REQUIRED_COLUMNS, validate_trade_dataset_csv


def _valid_row() -> dict[str, str]:
    return {
        "run_id": "run-001",
        "symbol": "SOLUSDT",
        "timeframe": "1m",
        "data_layer": "core",
        "train_start": "2026-05-11",
        "train_end": "2026-05-24",
        "test_start": "2026-05-25",
        "test_end": "2026-05-31",
        "block_id": "B050",
        "passport_id": "F051",
        "action_id": "F051_BOSDOWN_ALLOW",
        "side": "SHORT",
        "calibration_params_json": '{"F051_break_buffer_pct":0.06,"F051_confirm_bars":1.0}',
        "entry_signal_time_utc": "2026-05-25T01:00:00+00:00",
        "entry_time_utc": "2026-05-25T01:01:00+00:00",
        "exit_time_utc": "2026-05-25T01:05:00+00:00",
        "entry_price": "1.5",
        "exit_price": "1.48",
        "exit_reason": "tp",
        "net_return": "0.05",
        "net_pnl_usd": "0.50",
        "trade_id": "run-001:1:SHORT:2026-05-25T01:01:00+00:00",
        "bars_in_trade": "5",
        "tp_hit": "true",
        "sl_hit": "false",
        "timeout_hit": "false",
        "mae_pct": "-0.01",
        "mfe_pct": "0.08",
    }


def _write_csv(path: Path, rows: list[dict[str, str]], *, columns: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(columns or REQUIRED_COLUMNS)
    with path.open("w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=fieldnames)
        wr.writeheader()
        for row in rows:
            wr.writerow({k: row.get(k, "") for k in fieldnames})


class MLTradeDatasetContractTests(unittest.TestCase):
    def test_valid_trade_row_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "trade_log.csv"
            _write_csv(path, [_valid_row()])
            out = validate_trade_dataset_csv(path)
            self.assertEqual(out["status"], "PASS")
            self.assertEqual(out["missing_columns"], [])
            self.assertEqual(out["failed_rows"], [])

    def test_missing_required_column_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "trade_log.csv"
            columns = [c for c in REQUIRED_COLUMNS if c != "calibration_params_json"]
            _write_csv(path, [_valid_row()], columns=columns)
            out = validate_trade_dataset_csv(path)
            self.assertEqual(out["status"], "FAIL")
            self.assertIn("calibration_params_json", out["missing_columns"])

    def test_hit_labels_must_match_exit_reason(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "trade_log.csv"
            row = _valid_row()
            row["exit_reason"] = "sl"
            row["tp_hit"] = "true"
            row["sl_hit"] = "false"
            _write_csv(path, [row])
            out = validate_trade_dataset_csv(path)
            self.assertEqual(out["status"], "FAIL")
            errors = out["failed_rows"][0]["errors"]
            self.assertIn("inconsistent:hit_labels_vs_exit_reason", errors)

    def test_raw_layer_denied_for_clean_contract(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "trade_log.csv"
            row = _valid_row()
            row["data_layer"] = "raw"
            _write_csv(path, [row])
            out = validate_trade_dataset_csv(path)
            self.assertEqual(out["status"], "FAIL")
            errors = out["failed_rows"][0]["errors"]
            self.assertIn("invalid:data_layer_not_core", errors)


if __name__ == "__main__":
    unittest.main()
