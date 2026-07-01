from __future__ import annotations

from datetime import timedelta


_ALIAS_TO_CANONICAL = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "60m": "1h",
    "1h": "1h",
    "240m": "4h",
    "4h": "4h",
    "1d": "1d",
    "d": "1d",
    "D": "1d",
}

_CANONICAL_TO_LEGACY = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "60m",
    "4h": "240m",
    "1d": "1d",
}


def canonical_timeframe(value: str) -> str:
    tf = (value or "").strip()
    if not tf:
        raise ValueError("timeframe is empty")
    if tf in _ALIAS_TO_CANONICAL:
        return _ALIAS_TO_CANONICAL[tf]
    t = tf.lower()
    if t in _ALIAS_TO_CANONICAL:
        return _ALIAS_TO_CANONICAL[t]
    if t.endswith("m"):
        mins = int(t[:-1])
        if mins == 60:
            return "1h"
        if mins == 240:
            return "4h"
        return f"{mins}m"
    if t.endswith("h"):
        hrs = int(t[:-1])
        return f"{hrs}h"
    raise ValueError(f"Unsupported timeframe: {value}")


def timeframe_aliases(value: str) -> list[str]:
    c = canonical_timeframe(value)
    legacy = _CANONICAL_TO_LEGACY.get(c, c)
    if legacy == c:
        return [c]
    return [c, legacy]


def timeframe_delta(value: str) -> timedelta:
    c = canonical_timeframe(value)
    if c == "1d":
        return timedelta(days=1)
    if c.endswith("h"):
        return timedelta(hours=int(c[:-1]))
    if c.endswith("m"):
        return timedelta(minutes=int(c[:-1]))
    raise ValueError(f"Unsupported timeframe for delta: {value}")
