from __future__ import annotations

import unittest

from mlbotnav.oos_evaluate import _coerce_calibration_params
from mlbotnav.pipeline_train_eval import (
    _apply_gate_signal_mode_overrides,
    _gate_decision,
    _parse_calibration_params_json,
)


class PipelineTrainEvalGateOverrideTests(unittest.TestCase):
    def test_parse_calibration_params_json_normalizes_values(self) -> None:
        out = _parse_calibration_params_json('{"return_lookback": "9", "threshold_fine": 0.002}')

        self.assertEqual(out["return_lookback"], 9.0)
        self.assertEqual(out["threshold_fine"], 0.002)

    def test_oos_coerce_calibration_params_ignores_empty_payload(self) -> None:
        self.assertEqual(_coerce_calibration_params(None), {})
        self.assertEqual(_coerce_calibration_params({"rolling_window": "60"}), {"rolling_window": 60.0})

    def test_apply_gate_signal_mode_overrides_short_only(self) -> None:
        base = {
            "gates": {"min_trades": 20, "min_net_return_pct": 10.0},
            "gates_signal_mode_overrides": {
                "short_only": {"min_trades": 1, "min_net_return_pct": -5.0}
            },
        }
        out = _apply_gate_signal_mode_overrides(base, "short_only")
        self.assertEqual(out["gates"]["min_trades"], 1)
        self.assertEqual(out["gates"]["min_net_return_pct"], -5.0)
        self.assertEqual(base["gates"]["min_trades"], 20)

    def test_apply_gate_signal_mode_overrides_alias_key(self) -> None:
        base = {
            "gates": {"min_trades": 20},
            "gate_signal_mode_overrides": {"short_only": {"min_trades": 3}},
        }
        out = _apply_gate_signal_mode_overrides(base, "short_only")
        self.assertEqual(out["gates"]["min_trades"], 3)

    def test_gate_decision_uses_float_trades_per_day_threshold(self) -> None:
        thresholds = {
            "gates": {
                "min_auc": 0.0,
                "min_f1": 0.0,
                "max_drawdown_pct_abs": 100.0,
                "min_trades": 1,
                "max_no_trade_ratio_days": 1.0,
                "trades_per_day_min": 0.15,
                "trades_per_day_max": 100.0,
                "min_sortino": -999.0,
                "min_cagr": -1.0,
                "min_net_return_pct": -1000.0,
            }
        }
        metrics = {"auc_mean": 0.5, "f1_mean": 0.5}
        backtest = {
            "max_drawdown_pct": -1.0,
            "trades": 10,
            "no_trade_ratio_days": 0.0,
            "trades_per_day_avg": 0.12,
            "sortino": 0.0,
            "cagr": 0.0,
            "net_return_pct": 0.0,
        }

        gate_pass, reasons = _gate_decision(metrics, backtest, thresholds)
        self.assertFalse(gate_pass)
        self.assertTrue(any("trades_per_day_avg_low" in r for r in reasons))


if __name__ == "__main__":
    unittest.main()
