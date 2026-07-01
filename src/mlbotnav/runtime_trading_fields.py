from __future__ import annotations

from typing import Any


RUNTIME_TRADING_FIELDS_KEYS: tuple[str, ...] = (
    "symbol",
    "timeframe",
    "signal_mode",
    "execution_mode",
    "order_type",
    "stop_loss_pct",
    "take_profit_pct",
    "min_expected_move_pct",
    "min_tp_reach_prob",
    "trades",
    "net_return_pct",
    "goal_pass",
)


def _flt(v: Any) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except Exception:
        return None


def _int(v: Any) -> int | None:
    if v is None:
        return None
    try:
        return int(v)
    except Exception:
        return None


def _bool(v: Any) -> bool | None:
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in {"true", "1", "yes"}:
        return True
    if s in {"false", "0", "no"}:
        return False
    return None


def build_runtime_trading_fields(
    *,
    symbol: Any = None,
    timeframe: Any = None,
    signal_mode: Any = None,
    execution_mode: Any = None,
    order_type: Any = None,
    stop_loss_pct: Any = None,
    take_profit_pct: Any = None,
    min_expected_move_pct: Any = None,
    min_tp_reach_prob: Any = None,
    trades: Any = None,
    net_return_pct: Any = None,
    goal_pass: Any = None,
) -> dict[str, Any]:
    return {
        "symbol": str(symbol) if symbol is not None else None,
        "timeframe": str(timeframe) if timeframe is not None else None,
        "signal_mode": str(signal_mode) if signal_mode is not None else None,
        "execution_mode": str(execution_mode) if execution_mode is not None else None,
        "order_type": str(order_type) if order_type is not None else None,
        "stop_loss_pct": _flt(stop_loss_pct),
        "take_profit_pct": _flt(take_profit_pct),
        "min_expected_move_pct": _flt(min_expected_move_pct),
        "min_tp_reach_prob": _flt(min_tp_reach_prob),
        "trades": _int(trades),
        "net_return_pct": _flt(net_return_pct),
        "goal_pass": _bool(goal_pass),
    }


def validate_runtime_trading_fields(fields: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for key in RUNTIME_TRADING_FIELDS_KEYS:
        if key not in fields:
            missing.append(key)
    return missing
