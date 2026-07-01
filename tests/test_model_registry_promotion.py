from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mlbotnav.model_registry import promote_if_pass


def _mk_report(net: float, mdd: float, sharpe: float) -> dict:
    return {
        "symbol": "SOLUSDT",
        "timeframe": "1m",
        "run_utc": "20260521T100000Z",
        "gate": {"pass": True, "reasons": []},
        "artifacts": {"model_path": "models/pipeline/m.joblib"},
        "walk_forward": {},
        "backtest": {"net_return_pct": net, "max_drawdown_pct": mdd, "sharpe_like": sharpe},
        "_report_path": "reports/pipeline/p.json",
    }


class PromotionGuardTests(unittest.TestCase):
    def test_promotion_rejects_stronger_drawdown_regression(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "configs").mkdir(parents=True, exist_ok=True)
            (root / "models" / "registry").mkdir(parents=True, exist_ok=True)
            (root / "logs").mkdir(parents=True, exist_ok=True)
            (root / "configs" / "prod_policy.yaml").write_text(
                (
                    "prod:\n"
                    "  promotion:\n"
                    "    require_vs_champion: true\n"
                    "    min_net_return_improvement_pct: 0.0\n"
                    "    max_mdd_degradation_pct: 1.0\n"
                    "    min_sharpe_improvement: -1.0\n"
                ),
                encoding="utf-8",
            )
            champion = {
                "symbol": "SOLUSDT",
                "timeframe": "1m",
                "metrics": {"backtest": {"net_return_pct": 1.0, "max_drawdown_pct": -4.0, "sharpe_like": 1.0}},
            }
            (root / "models" / "registry" / "champion.json").write_text(json.dumps(champion), encoding="utf-8")
            promoted, _path, reason = promote_if_pass(root, report=_mk_report(net=2.0, mdd=-6.5, sharpe=1.2))
            self.assertFalse(promoted)
            self.assertIn("drawdown_regression_high", reason)

    def test_promotion_writes_active_model_and_history(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "configs").mkdir(parents=True, exist_ok=True)
            (root / "models" / "registry").mkdir(parents=True, exist_ok=True)
            (root / "logs").mkdir(parents=True, exist_ok=True)
            (root / "configs" / "prod_policy.yaml").write_text(
                (
                    "prod:\n"
                    "  promotion:\n"
                    "    require_vs_champion: true\n"
                    "    min_net_return_improvement_pct: 0.0\n"
                    "    max_mdd_degradation_pct: 2.0\n"
                    "    min_sharpe_improvement: -1.0\n"
                ),
                encoding="utf-8",
            )
            promoted, _path, reason = promote_if_pass(root, report=_mk_report(net=1.0, mdd=-5.0, sharpe=1.0))
            self.assertTrue(promoted)
            self.assertEqual(reason, "promoted")
            self.assertTrue((root / "models" / "registry" / "active_model.json").exists())
            self.assertTrue((root / "models" / "registry" / "champion_history.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
