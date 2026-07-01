from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from mlbotnav.bybit_client import BybitClient
from mlbotnav.settings import load_settings


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_float(x: str | float | int) -> float:
    try:
        return float(x)
    except Exception:
        return 0.0


def _sum_notional(levels: list[list[str]]) -> float:
    total = 0.0
    for row in levels:
        if len(row) < 2:
            continue
        p = _to_float(row[0])
        q = _to_float(row[1])
        total += p * q
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch one Bybit L1-L50 orderbook snapshot and save source files.")
    parser.add_argument("--symbol", default=None, help="e.g. SOLUSDT")
    parser.add_argument("--category", default=None, help="linear/spot/inverse")
    parser.add_argument("--limit", type=int, default=50, help="Book depth (1..200 by Bybit)")
    args = parser.parse_args()

    settings = load_settings()
    symbol = str(args.symbol or settings.symbol)
    category = str(args.category or settings.bybit_category)
    limit = int(args.limit)

    if limit <= 0:
        raise ValueError("--limit must be positive")

    client = BybitClient(base_url=settings.bybit_base_url)
    now = _utc_now()
    day = now.strftime("%Y-%m-%d")
    ts = now.strftime("%Y%m%dT%H%M%SZ")

    result = client.get_orderbook(category=category, symbol=symbol, limit=limit)
    bids = result.get("b") or result.get("bids") or []
    asks = result.get("a") or result.get("asks") or []
    bids = bids if isinstance(bids, list) else []
    asks = asks if isinstance(asks, list) else []

    best_bid = _to_float(bids[0][0]) if bids and len(bids[0]) >= 1 else 0.0
    best_ask = _to_float(asks[0][0]) if asks and len(asks[0]) >= 1 else 0.0
    spread_abs = max(best_ask - best_bid, 0.0)
    mid = (best_ask + best_bid) / 2.0 if (best_ask > 0 and best_bid > 0) else 0.0
    spread_bps = (spread_abs / mid * 10_000.0) if mid > 0 else 0.0

    bid_notional = _sum_notional(bids[:limit])
    ask_notional = _sum_notional(asks[:limit])
    denom = bid_notional + ask_notional
    imbalance = (bid_notional - ask_notional) / denom if denom > 0 else 0.0
    delta_absorption = bid_notional - ask_notional

    out_orderbook_dir = Path("data") / "orderbook" / f"dt={day}" / f"symbol={symbol}"
    out_micro_dir = Path("data") / "microstructure" / f"dt={day}" / f"symbol={symbol}"
    out_orderbook_dir.mkdir(parents=True, exist_ok=True)
    out_micro_dir.mkdir(parents=True, exist_ok=True)

    raw_payload = {
        "source": "bybit_v5",
        "captured_at_utc": now.isoformat(),
        "symbol": symbol,
        "category": category,
        "limit": limit,
        "u": result.get("u"),
        "seq": result.get("seq"),
        "cts": result.get("cts"),
        "bids": bids,
        "asks": asks,
    }
    raw_path = out_orderbook_dir / f"orderbook_l50_snapshot_{ts}.json"
    raw_path.write_text(json.dumps(raw_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    micro_row = {
        "source": "bybit_v5",
        "captured_at_utc": now.isoformat(),
        "symbol": symbol,
        "category": category,
        "best_bid": best_bid,
        "best_ask": best_ask,
        "spread_abs": spread_abs,
        "spread_bps": spread_bps,
        "bid_notional_l50": bid_notional,
        "ask_notional_l50": ask_notional,
        "orderbook_imbalance_l50": imbalance,
        "delta_absorption_l50": delta_absorption,
    }
    micro_csv = out_micro_dir / "microstructure_spread_delta.csv"
    header = (not micro_csv.exists()) or micro_csv.stat().st_size == 0
    line = ",".join(str(micro_row[k]) for k in micro_row.keys())
    if header:
        micro_csv.write_text(",".join(micro_row.keys()) + "\n" + line + "\n", encoding="utf-8")
    else:
        with micro_csv.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    print(
        json.dumps(
            {
                "status": "ok",
                "symbol": symbol,
                "category": category,
                "limit": limit,
                "orderbook_snapshot": str(raw_path.resolve()),
                "microstructure_csv": str(micro_csv.resolve()),
                "spread_bps": spread_bps,
                "imbalance_l50": imbalance,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
