from __future__ import annotations

import time
from typing import Any

import requests


class BybitClient:
    def __init__(self, *, base_url: str, timeout_sec: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_sec = timeout_sec

    def _request(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        resp = requests.get(f"{self.base_url}{path}", params=params, timeout=self.timeout_sec)
        resp.raise_for_status()
        payload = resp.json()
        if payload.get("retCode", 0) != 0:
            raise RuntimeError(f"Bybit error {payload.get('retCode')}: {payload.get('retMsg')}")
        return payload

    def get_klines(
        self,
        *,
        category: str,
        symbol: str,
        interval: str,
        start_ms: int,
        end_ms: int,
        limit: int = 1000,
        sleep_sec: float = 0.1,
    ) -> list[list[str]]:
        rows: list[list[str]] = []
        end_cursor = end_ms - 1

        while end_cursor >= start_ms:
            payload = self._request(
                "/v5/market/kline",
                {
                    "category": category,
                    "symbol": symbol,
                    "interval": interval,
                    "start": start_ms,
                    "end": end_cursor,
                    "limit": limit,
                },
            )
            page = (payload.get("result") or {}).get("list") or []
            if not page:
                break

            parsed: list[tuple[int, list[str]]] = []
            for item in page:
                open_ms = int(item[0])
                if start_ms <= open_ms < end_ms:
                    parsed.append((open_ms, item))

            if not parsed:
                break

            parsed.sort(key=lambda x: x[0])
            rows.extend([x[1] for x in parsed])
            oldest_open = parsed[0][0]
            end_cursor = oldest_open - 1
            time.sleep(sleep_sec)

            if len(page) < limit:
                break

        # De-duplicate by open time to keep retries/idempotency safe.
        by_open: dict[str, list[str]] = {}
        for r in rows:
            by_open[r[0]] = r
        return [by_open[k] for k in sorted(by_open.keys(), key=lambda x: int(x))]

    def get_funding_history(
        self,
        *,
        category: str,
        symbol: str,
        start_ms: int,
        end_ms: int,
        limit: int = 200,
        sleep_sec: float = 0.05,
    ) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        end_cursor = end_ms - 1
        while end_cursor >= start_ms:
            payload = self._request(
                "/v5/market/funding/history",
                {
                    "category": category,
                    "symbol": symbol,
                    "startTime": start_ms,
                    "endTime": end_cursor,
                    "limit": limit,
                },
            )
            page = (payload.get("result") or {}).get("list") or []
            if not page:
                break
            parsed: list[tuple[int, dict[str, str]]] = []
            for item in page:
                ts = int(item.get("fundingRateTimestamp", "0"))
                if start_ms <= ts < end_ms:
                    parsed.append((ts, item))
            if not parsed:
                break
            parsed.sort(key=lambda x: x[0])
            rows.extend([x[1] for x in parsed])
            oldest = parsed[0][0]
            if oldest <= start_ms:
                break
            end_cursor = oldest - 1
            time.sleep(sleep_sec)
            if len(page) < limit:
                break
        by_ts: dict[str, dict[str, str]] = {}
        for r in rows:
            by_ts[str(r.get("fundingRateTimestamp"))] = r
        return [by_ts[k] for k in sorted(by_ts.keys(), key=lambda x: int(x))]

    def get_open_interest(
        self,
        *,
        category: str,
        symbol: str,
        interval_time: str,
        start_ms: int,
        end_ms: int,
        limit: int = 200,
        sleep_sec: float = 0.05,
    ) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        cursor = ""
        while True:
            params = {
                "category": category,
                "symbol": symbol,
                "intervalTime": interval_time,
                "startTime": start_ms,
                "endTime": end_ms - 1,
                "limit": limit,
            }
            if cursor:
                params["cursor"] = cursor
            payload = self._request("/v5/market/open-interest", params)
            result = payload.get("result") or {}
            page = result.get("list") or []
            if not page:
                break
            for item in page:
                ts = int(item.get("timestamp", "0"))
                if start_ms <= ts < end_ms:
                    rows.append(item)
            cursor = str(result.get("nextPageCursor", "") or "").strip()
            if not cursor:
                break
            time.sleep(sleep_sec)
        by_ts: dict[str, dict[str, str]] = {}
        for r in rows:
            by_ts[str(r.get("timestamp"))] = r
        return [by_ts[k] for k in sorted(by_ts.keys(), key=lambda x: int(x))]

    def get_orderbook(
        self,
        *,
        category: str,
        symbol: str,
        limit: int = 50,
    ) -> dict[str, Any]:
        payload = self._request(
            "/v5/market/orderbook",
            {
                "category": category,
                "symbol": symbol,
                "limit": int(limit),
            },
        )
        return (payload.get("result") or {}) if isinstance(payload, dict) else {}


def _interval_to_ms(interval: str) -> int:
    mapping = {
        "1": 60_000,
        "3": 3 * 60_000,
        "5": 5 * 60_000,
        "15": 15 * 60_000,
        "30": 30 * 60_000,
        "60": 60 * 60_000,
        "120": 120 * 60_000,
        "240": 240 * 60_000,
        "360": 360 * 60_000,
        "720": 720 * 60_000,
        "D": 24 * 60 * 60_000,
    }
    if interval not in mapping:
        raise ValueError(f"Unsupported interval: {interval}")
    return mapping[interval]


def interval_to_tf(interval: str) -> str:
    if interval == "D":
        return "1d"
    if interval == "60":
        return "1h"
    if interval == "240":
        return "4h"
    return f"{interval}m"


def interval_to_oi_interval_time(interval: str) -> str:
    mapping = {
        "3": "5min",
        "5": "5min",
        "15": "15min",
        "30": "30min",
        "60": "1h",
        "120": "1h",
        "240": "4h",
        "360": "4h",
        "720": "4h",
        "D": "1d",
    }
    if interval not in mapping:
        raise ValueError(f"Unsupported open-interest interval: {interval}")
    return mapping[interval]


def is_oi_supported_interval(interval: str) -> bool:
    return interval in {"3", "5", "15", "30", "60", "120", "240", "360", "720", "D"}
