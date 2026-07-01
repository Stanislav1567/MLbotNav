from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ObjectiveWeights:
    drawdown_penalty: float = 0.5
    gate_bonus: float = 2.0
    no_trade_penalty: float = 100.0
    lambda_block: float = 0.2
    lambda_hypothesis: float = 0.1


def complexity_penalty(
    *,
    active_blocks: int,
    active_hypotheses: int,
    weights: ObjectiveWeights,
) -> float:
    return (weights.lambda_block * float(active_blocks)) + (weights.lambda_hypothesis * float(active_hypotheses))


def compute_trial_score(
    *,
    oos_net_return_pct: float,
    max_drawdown_pct: float,
    gate_pass: bool,
    trades: int,
    active_blocks: int,
    active_hypotheses: int,
    weights: ObjectiveWeights | None = None,
) -> float:
    w = weights or ObjectiveWeights()
    score = float(oos_net_return_pct)
    score -= abs(float(max_drawdown_pct)) * w.drawdown_penalty
    if bool(gate_pass):
        score += w.gate_bonus
    if int(trades) <= 0:
        score -= w.no_trade_penalty
    score -= complexity_penalty(
        active_blocks=int(active_blocks),
        active_hypotheses=int(active_hypotheses),
        weights=w,
    )
    return float(score)

