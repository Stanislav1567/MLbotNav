from __future__ import annotations

from pathlib import Path
import unittest

import pandas as pd

from mlbotnav.ml_trade_dataset_contract import RUN_CONTEXT_COLUMNS
from mlbotnav.ml_trade_dataset_enrichment import (
    add_duration_label_columns,
    add_hit_label_columns,
    add_mae_mfe_columns,
    add_passport_context_columns,
    add_run_context_columns,
    add_trade_identity_columns,
)


class MLTradeDatasetEnrichmentTests(unittest.TestCase):
    def test_add_run_context_columns_prepends_required_context(self) -> None:
        df = pd.DataFrame(
            [
                {
                    "open_time_utc": "2026-05-25T00:00:00+00:00",
                    "side": 1,
                    "net_return": 0.01,
                }
            ]
        )

        out = add_run_context_columns(
            df,
            run_id="oos_SOLUSDT_1m_2026-05-25_long_only_20260623T000000Z",
            symbol="SOLUSDT",
            timeframe="1m",
            data_layer="core",
            train_start="2026-05-11",
            train_end="2026-05-24",
            test_start="2026-05-25",
            test_end="2026-05-31",
        )

        self.assertEqual(list(out.columns[: len(RUN_CONTEXT_COLUMNS)]), RUN_CONTEXT_COLUMNS)
        self.assertEqual(out.loc[0, "run_id"], "oos_SOLUSDT_1m_2026-05-25_long_only_20260623T000000Z")
        self.assertEqual(out.loc[0, "symbol"], "SOLUSDT")
        self.assertEqual(out.loc[0, "timeframe"], "1m")
        self.assertEqual(out.loc[0, "data_layer"], "core")
        self.assertEqual(out.loc[0, "train_start"], "2026-05-11")
        self.assertEqual(out.loc[0, "train_end"], "2026-05-24")
        self.assertEqual(out.loc[0, "test_start"], "2026-05-25")
        self.assertEqual(out.loc[0, "test_end"], "2026-05-31")
        self.assertEqual(out.loc[0, "side"], 1)

    def test_add_passport_context_resolves_from_action_column(self) -> None:
        df = pd.DataFrame([{"side": -1, "net_return": 0.02}])

        out = add_passport_context_columns(
            df,
            project_root=Path.cwd(),
            calibration_params={
                "F051_structure_scope": 1,
                "F051_break_buffer_pct": 0.07,
                "F051_confirm_bars": 2,
                "F051_require_bias": 2,
            },
            entry_action_gate_columns=["F051_BOSDOWN_ALLOW"],
        )

        self.assertEqual(out.loc[0, "block_id"], "B018")
        self.assertEqual(out.loc[0, "passport_id"], "F051")
        self.assertEqual(out.loc[0, "action_id"], "F051_BOSDOWN_ALLOW")
        self.assertEqual(
            out.loc[0, "calibration_params_json"],
            '{"F051_break_buffer_pct":0.07,"F051_confirm_bars":2,"F051_require_bias":2,"F051_structure_scope":1}',
        )
        self.assertEqual(out.loc[0, "entry_action_gate_columns"], '["F051_BOSDOWN_ALLOW"]')

    def test_add_passport_context_resolves_from_allowed_params(self) -> None:
        df = pd.DataFrame([{"side": 1, "net_return": -0.01}])

        out = add_passport_context_columns(
            df,
            project_root=Path.cwd(),
            calibration_params={"F006_cmp": -1, "F006_thr_pct": 0.75},
        )

        self.assertEqual(out.loc[0, "block_id"], "B002")
        self.assertEqual(out.loc[0, "passport_id"], "F006")
        self.assertEqual(out.loc[0, "action_id"], "F006_HLSPREAD_ALLOW")
        self.assertEqual(out.loc[0, "entry_action_gate_columns"], '["F006_HLSPREAD_ALLOW"]')

    def test_add_trade_identity_columns_adds_stable_ids_for_trade_rows(self) -> None:
        df = pd.DataFrame(
            [
                {
                    "run_id": "oos_SOLUSDT_1m_2026-05-25_long_only_20260623T000000Z",
                    "action_id": "F006_HLSPREAD_ALLOW",
                    "open_time_utc": "2026-05-25T00:00:00+00:00",
                    "entry_time_utc": "2026-05-25T00:01:00+00:00",
                    "side": 1,
                    "net_return": 0.01,
                },
                {
                    "run_id": "oos_SOLUSDT_1m_2026-05-25_long_only_20260623T000000Z",
                    "action_id": "F006_HLSPREAD_ALLOW",
                    "open_time_utc": "2026-05-25T00:02:00+00:00",
                    "entry_time_utc": "",
                    "side": 0,
                    "net_return": 0.0,
                },
            ]
        )

        out1 = add_trade_identity_columns(df)
        out2 = add_trade_identity_columns(df)

        self.assertTrue(str(out1.loc[0, "trade_id"]).startswith("T000000_"))
        self.assertEqual(out1.loc[0, "trade_id"], out2.loc[0, "trade_id"])
        self.assertEqual(out1.loc[0, "entry_signal_time_utc"], "2026-05-25T00:00:00+00:00")
        self.assertEqual(out1.loc[1, "trade_id"], "")
        self.assertEqual(out1.loc[1, "entry_signal_time_utc"], "")

    def test_add_duration_label_columns_calculates_trade_duration(self) -> None:
        df = pd.DataFrame(
            [
                {
                    "open_time_utc": "2026-05-25T00:00:00+00:00",
                    "entry_time_utc": "2026-05-25T00:01:00+00:00",
                    "exit_time_utc": "2026-05-25T00:04:00+00:00",
                    "side": 1,
                    "net_return": 0.01,
                },
                {
                    "open_time_utc": "2026-05-25T00:01:00+00:00",
                    "entry_time_utc": "",
                    "exit_time_utc": "",
                    "side": 0,
                    "net_return": 0.0,
                },
                {
                    "open_time_utc": "2026-05-25T00:02:00+00:00",
                    "entry_time_utc": "",
                    "exit_time_utc": "",
                    "side": 0,
                    "net_return": 0.0,
                },
            ]
        )

        out = add_duration_label_columns(df)

        self.assertEqual(out.loc[0, "bars_in_trade"], 3)
        self.assertEqual(out.loc[0, "holding_seconds"], 180.0)
        self.assertEqual(out.loc[1, "bars_in_trade"], "")
        self.assertEqual(out.loc[1, "holding_seconds"], "")

    def test_add_hit_label_columns_derives_labels_from_exit_reason(self) -> None:
        df = pd.DataFrame(
            [
                {"side": 1, "exit_reason": "tp"},
                {"side": -1, "exit_reason": "sl_ambiguous"},
                {"side": 1, "exit_reason": "timeout"},
                {"side": -1, "exit_reason": "end_of_data"},
                {"side": 0, "exit_reason": ""},
            ]
        )

        out = add_hit_label_columns(df)

        self.assertEqual(out.loc[0, "tp_hit"], "true")
        self.assertEqual(out.loc[0, "sl_hit"], "false")
        self.assertEqual(out.loc[0, "timeout_hit"], "false")
        self.assertEqual(out.loc[0, "end_of_data_hit"], "false")
        self.assertEqual(out.loc[0, "sl_ambiguous_hit"], "false")

        self.assertEqual(out.loc[1, "tp_hit"], "false")
        self.assertEqual(out.loc[1, "sl_hit"], "true")
        self.assertEqual(out.loc[1, "timeout_hit"], "false")
        self.assertEqual(out.loc[1, "end_of_data_hit"], "false")
        self.assertEqual(out.loc[1, "sl_ambiguous_hit"], "true")

        self.assertEqual(out.loc[2, "timeout_hit"], "true")
        self.assertEqual(out.loc[3, "end_of_data_hit"], "true")
        self.assertEqual(out.loc[4, "tp_hit"], "")
        self.assertEqual(out.loc[4, "sl_hit"], "")
        self.assertEqual(out.loc[4, "timeout_hit"], "")

    def test_add_mae_mfe_columns_calculates_long_and_short_excursions(self) -> None:
        df = pd.DataFrame(
            [
                {
                    "open_time_utc": "2026-05-25T00:00:00+00:00",
                    "entry_time_utc": "2026-05-25T00:01:00+00:00",
                    "exit_time_utc": "2026-05-25T00:02:00+00:00",
                    "entry_price": 100.0,
                    "high": 101.0,
                    "low": 99.0,
                    "side": 1,
                },
                {
                    "open_time_utc": "2026-05-25T00:01:00+00:00",
                    "entry_time_utc": "",
                    "exit_time_utc": "",
                    "entry_price": "",
                    "high": 104.0,
                    "low": 98.0,
                    "side": 0,
                },
                {
                    "open_time_utc": "2026-05-25T00:02:00+00:00",
                    "entry_time_utc": "",
                    "exit_time_utc": "",
                    "entry_price": "",
                    "high": 105.0,
                    "low": 99.5,
                    "side": 0,
                },
                {
                    "open_time_utc": "2026-05-25T00:03:00+00:00",
                    "entry_time_utc": "2026-05-25T00:01:00+00:00",
                    "exit_time_utc": "2026-05-25T00:03:00+00:00",
                    "entry_price": 100.0,
                    "high": 103.0,
                    "low": 95.0,
                    "side": -1,
                },
            ]
        )

        out = add_mae_mfe_columns(df)

        self.assertAlmostEqual(out.loc[0, "mae_pct"], -0.02)
        self.assertAlmostEqual(out.loc[0, "mfe_pct"], 0.05)
        self.assertEqual(out.loc[1, "mae_pct"], "")
        self.assertEqual(out.loc[1, "mfe_pct"], "")
        self.assertAlmostEqual(out.loc[3, "mae_pct"], 100.0 / 105.0 - 1.0)
        self.assertAlmostEqual(out.loc[3, "mfe_pct"], 100.0 / 95.0 - 1.0)


if __name__ == "__main__":
    unittest.main()
