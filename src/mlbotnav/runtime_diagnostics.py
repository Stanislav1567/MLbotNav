from __future__ import annotations

from typing import Any

EMPTY_ACTION_GATE = "EMPTY_ACTION_GATE"
FILTER_EMPTY = "FILTER_EMPTY"
MIN_MOVE_UNREACHABLE = "MIN_MOVE_UNREACHABLE"
NO_TRADES_OTHER = "NO_TRADES_OTHER"
TRADEFUL_NEGATIVE = "TRADEFUL_NEGATIVE"
TRADEFUL_POSITIVE = "TRADEFUL_POSITIVE"


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return int(default)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def classify_backtest_outcome(backtest: dict[str, Any] | None) -> str:
    bt = backtest if isinstance(backtest, dict) else {}
    diag = bt.get("trend_filter_diagnostics")
    diag = diag if isinstance(diag, dict) else {}

    trades = _safe_int(bt.get("trades", 0))
    net_return = _safe_float(bt.get("net_return_pct", 0.0))
    if trades > 0:
        return TRADEFUL_POSITIVE if net_return > 0 else TRADEFUL_NEGATIVE

    after_gate = _safe_int(diag.get("signal_count_after_entry_action_gates", -1), -1)
    after_filter = _safe_int(diag.get("signal_count_after_filter", -1), -1)
    after_min_move = _safe_int(diag.get("signal_count_after_min_move", -1), -1)
    min_move = abs(_safe_float(bt.get("min_expected_move_pct", diag.get("min_expected_move_pct", 0.0))))

    if after_gate == 0:
        return EMPTY_ACTION_GATE
    if after_filter == 0:
        return FILTER_EMPTY
    if bool(diag.get("min_move_unreachable_after_action_gate", False)):
        return MIN_MOVE_UNREACHABLE
    if min_move > 0.0 and after_filter > 0 and after_min_move == 0:
        return MIN_MOVE_UNREACHABLE
    return NO_TRADES_OTHER


def is_min_move_unreachable(backtest: dict[str, Any] | None) -> bool:
    return classify_backtest_outcome(backtest) == MIN_MOVE_UNREACHABLE
