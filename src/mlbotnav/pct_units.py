from __future__ import annotations

import math
from typing import Any


def normalize_min_expected_move_pct(value: Any) -> float:
    """
    Canonical runtime unit for min_expected_move_pct is a fraction:
    0.01 == 1%.

    To keep backward compatibility with historical configs/spec fragments
    where values were sometimes written in percent points (e.g. 1.0 for 1%),
    values > 1.0 are interpreted as percent points and converted to fraction.
    """
    try:
        v = float(value)
    except Exception:
        return 0.0
    if not math.isfinite(v):
        return 0.0
    v = abs(v)
    if v == 0.0:
        return 0.0
    if v >= 1.0:
        return v / 100.0
    return v
