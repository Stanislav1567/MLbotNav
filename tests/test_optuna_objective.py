from __future__ import annotations

import unittest

from mlbotnav.optuna_objective import ObjectiveWeights, compute_trial_score


class OptunaObjectiveTests(unittest.TestCase):
    def test_no_trade_penalty_is_applied(self) -> None:
        score = compute_trial_score(
            oos_net_return_pct=5.0,
            max_drawdown_pct=-2.0,
            gate_pass=True,
            trades=0,
            active_blocks=2,
            active_hypotheses=3,
        )
        self.assertLess(score, 0.0)

    def test_higher_complexity_reduces_score(self) -> None:
        weights = ObjectiveWeights(lambda_block=1.0, lambda_hypothesis=1.0)
        low = compute_trial_score(
            oos_net_return_pct=10.0,
            max_drawdown_pct=-2.0,
            gate_pass=True,
            trades=10,
            active_blocks=1,
            active_hypotheses=1,
            weights=weights,
        )
        high = compute_trial_score(
            oos_net_return_pct=10.0,
            max_drawdown_pct=-2.0,
            gate_pass=True,
            trades=10,
            active_blocks=5,
            active_hypotheses=5,
            weights=weights,
        )
        self.assertGreater(low, high)


if __name__ == "__main__":
    unittest.main()

