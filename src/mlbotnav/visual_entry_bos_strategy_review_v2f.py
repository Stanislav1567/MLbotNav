from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from mlbotnav.visual_entry_low_anchor_suggester import _bar_width_days, _draw_candles, _load_ohlcv, _style_axis
from mlbotnav.visual_entry_strategy_passport_overlay_v2a import (
    SYMBOL,
    TIMEFRAME,
    _causal_zigzag_before,
    _fmt_min,
    _fmt_ts,
    _load_targets,
    _raw_pivots,
    _rel,
    _row_index_at_time,
    _safe_float,
    _source_csv,
)


STATUS = "B018_BOS_STRATEGY_REVIEW_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA"
RAIL_POINT = "B018_BOS_STRATEGY_REVIEW"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _event_scan(
    df: pd.DataFrame,
    raw_pivots: list[Any],
    *,
    lookback: int = 120,
    max_age: int = 120,
    deviation_pct: float = 0.15,
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    last_emitted: tuple[str, float] | None = None
    for idx in range(len(df)):
        confirmed = _causal_zigzag_before(raw_pivots, idx, lookback=lookback, deviation_pct=deviation_pct)
        highs = [pivot for pivot in confirmed if pivot.kind == "H"]
        lows = [pivot for pivot in confirmed if pivot.kind == "L"]
        last_high = highs[-1] if highs else None
        last_low = lows[-1] if lows else None
        close = float(df.iloc[idx]["close"])
        candidates: list[tuple[str, float]] = []
        if last_high and idx - int(last_high.idx) <= max_age and close >= float(last_high.price):
            candidates.append(("BOS_UP", float(last_high.price)))
        if last_low and idx - int(last_low.idx) <= max_age and close <= float(last_low.price):
            candidates.append(("BOS_DOWN", float(last_low.price)))
        for event_name, level in candidates:
            key = (event_name, round(level, 4))
            if key == last_emitted:
                continue
            last_opposite = next(
                (event for event in reversed(events) if event["event"] != event_name and event["event"].startswith("BOS_")),
                None,
            )
            choch_like = bool(last_opposite and idx - int(last_opposite["idx"]) <= 12)
            events.append(
                {
                    "idx": idx,
                    "time_utc": _fmt_ts(pd.Timestamp(df.iloc[idx]["open_time_utc"]).tz_convert("UTC")),
                    "event": event_name,
                    "level": round(level, 8),
                    "close": round(close, 8),
                    "choch_like": choch_like,
                }
            )
            if choch_like:
                events.append(
                    {
                        "idx": idx,
                        "time_utc": _fmt_ts(pd.Timestamp(df.iloc[idx]["open_time_utc"]).tz_convert("UTC")),
                        "event": "CHOCH_LIKE",
                        "level": round(level, 8),
                        "close": round(close, 8),
                        "choch_like": True,
                    }
                )
            last_emitted = key
    return events


def _nearest_events(events: list[dict[str, Any]], signal_idx: int) -> dict[str, Any]:
    past = [event for event in events if int(event["idx"]) <= signal_idx]
    last = past[-1] if past else None
    last_up = next((event for event in reversed(past) if event["event"] == "BOS_UP"), None)
    last_down = next((event for event in reversed(past) if event["event"] == "BOS_DOWN"), None)
    last_choch = next((event for event in reversed(past) if event["event"] == "CHOCH_LIKE"), None)
    return {
        "last_event": None if last is None else last["event"],
        "last_event_age": None if last is None else signal_idx - int(last["idx"]),
        "last_bos_up_age": None if last_up is None else signal_idx - int(last_up["idx"]),
        "last_bos_down_age": None if last_down is None else signal_idx - int(last_down["idx"]),
        "last_choch_age": None if last_choch is None else signal_idx - int(last_choch["idx"]),
        "bos_up_recent": bool(last_up and signal_idx - int(last_up["idx"]) <= 20),
        "bos_down_recent": bool(last_down and signal_idx - int(last_down["idx"]) <= 20),
        "choch_recent": bool(last_choch and signal_idx - int(last_choch["idx"]) <= 12),
    }


def _target_rows(df: pd.DataFrame, targets: list[dict[str, Any]], events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for target in targets:
        signal_idx = _row_index_at_time(df, str(target["signal_time_utc"]))
        row = df.iloc[signal_idx]
        nearest = _nearest_events(events, signal_idx)
        long_context = bool(nearest["bos_up_recent"] or nearest["choch_recent"])
        down_break_before_reclaim = bool(nearest["bos_down_recent"] and nearest["choch_recent"])
        broad_support = bool(long_context or down_break_before_reclaim)
        rows.append(
            {
                "target_id": target["target_id"],
                "target_type": target["target_type"],
                "signal_time_utc": target["signal_time_utc"],
                "entry_time_utc": target["entry_time_utc"],
                "entry_open_price": target["entry_open_price"],
                "entry_price_plus_5bps": target["entry_price_plus_5bps"],
                "signal_close": round(_safe_float(row.get("close")), 8),
                **nearest,
                "b018_bos_long_context": long_context,
                "b018_down_break_before_reclaim": down_break_before_reclaim,
                "b018_broad_support": broad_support,
                "audit_note": _audit_note(nearest),
            }
        )
    return rows


def _audit_note(nearest: dict[str, Any]) -> str:
    if nearest["bos_up_recent"] and not nearest["bos_down_recent"]:
        return "bos_up_context"
    if nearest["bos_down_recent"] and nearest["choch_recent"]:
        return "down_break_then_choch_context"
    if nearest["bos_down_recent"]:
        return "down_break_only_bad_for_long_if_no_reclaim"
    if nearest["choch_recent"]:
        return "choch_context"
    return "silent"


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _render_full_day(path: Path, df: pd.DataFrame, targets: list[dict[str, Any]], events: list[dict[str, Any]], day: str) -> None:
    fig, (ax, ax_vol) = plt.subplots(
        2,
        1,
        figsize=(22, 10),
        sharex=True,
        gridspec_kw={"height_ratios": [4, 1]},
        facecolor="#0f1419",
    )
    for axis in [ax, ax_vol]:
        axis.set_facecolor("#0f1419")
        _style_axis(axis)
    _draw_candles(ax, df, TIMEFRAME)
    colors = {"BOS_UP": "#18d26e", "BOS_DOWN": "#ff5252", "CHOCH_LIKE": "#f2c94c"}
    markers = {"BOS_UP": "^", "BOS_DOWN": "v", "CHOCH_LIKE": "D"}
    for event in events:
        idx = int(event["idx"])
        if idx < 0 or idx >= len(df):
            continue
        t = df.iloc[idx]["open_time_utc"]
        y = float(event["close"])
        ax.scatter(t, y, marker=markers[event["event"]], s=28, color=colors[event["event"]], zorder=4, alpha=0.9)
    for target in targets:
        entry_ts = pd.Timestamp(target["entry_time_utc"]).tz_convert("UTC")
        entry_price = _safe_float(target["entry_open_price"])
        ax.axvline(entry_ts, color="#00e676", linewidth=1.4, alpha=0.75)
        ax.scatter(entry_ts, entry_price, marker="^", s=80, color="#00e676", edgecolor="white", linewidth=0.7, zorder=6)
        ax.text(entry_ts, entry_price, str(target["target_id"]), color="#54e0d0", fontsize=8, va="bottom")

    ax_vol.bar(df["open_time_utc"], df["volume"], width=_bar_width_days(TIMEFRAME), color="#2cb1a1", alpha=0.45)
    ax.set_ylabel("Price")
    ax_vol.set_ylabel("Volume")
    ax.set_title(
        f"{SYMBOL} {TIMEFRAME} {day} | B018 BOS/CHOCH separate review | green=BOS_UP red=BOS_DOWN yellow=CHOCH | NO ML/OPTUNA",
        color="#edf2f7",
        fontsize=16,
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=timezone.utc))
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _render_zoom_pages(
    out_dir: Path,
    df: pd.DataFrame,
    targets: list[dict[str, Any]],
    target_rows: list[dict[str, Any]],
    events: list[dict[str, Any]],
    day: str,
) -> list[Path]:
    pages: list[Path] = []
    by_id = {row["target_id"]: row for row in target_rows}
    for page_idx, start in enumerate(range(0, len(targets), 4), start=1):
        subset = targets[start : start + 4]
        fig, axes = plt.subplots(2, 2, figsize=(18, 10), facecolor="#0f1419")
        axes_flat = list(axes.ravel())
        for ax in axes_flat:
            ax.set_visible(False)
        for ax, target in zip(axes_flat, subset):
            ax.set_visible(True)
            ax.set_facecolor("#0f1419")
            _style_axis(ax)
            signal_idx = _row_index_at_time(df, str(target["signal_time_utc"]))
            left = max(0, signal_idx - 45)
            right = min(len(df), signal_idx + 46)
            win = df.iloc[left:right].reset_index(drop=True)
            _draw_candles(ax, win, TIMEFRAME)
            win_events = [event for event in events if left <= int(event["idx"]) < right]
            for event in win_events:
                idx = int(event["idx"])
                ts = df.iloc[idx]["open_time_utc"]
                color = "#18d26e" if event["event"] == "BOS_UP" else "#ff5252" if event["event"] == "BOS_DOWN" else "#f2c94c"
                marker = "^" if event["event"] == "BOS_UP" else "v" if event["event"] == "BOS_DOWN" else "D"
                ax.scatter(ts, float(event["close"]), marker=marker, s=44, color=color, zorder=4, alpha=0.95)
            entry_ts = pd.Timestamp(target["entry_time_utc"]).tz_convert("UTC")
            entry_price = _safe_float(target["entry_open_price"])
            ax.axvline(entry_ts, color="#00e676", linewidth=1.5, alpha=0.85)
            ax.scatter(entry_ts, entry_price, marker="^", s=90, color="#00e676", edgecolor="white", linewidth=0.8, zorder=6)
            row = by_id[target["target_id"]]
            ax.set_title(
                f"{target['target_id']} {target['target_type']} | {row['audit_note']} | signal {_fmt_min(target['signal_time_utc'])} -> entry {_fmt_min(target['entry_time_utc'])}",
                color="#edf2f7",
                fontsize=9,
            )
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=timezone.utc))
        fig.suptitle(f"{SYMBOL} {TIMEFRAME} {day} | B018 BOS zoom page {page_idx:02d} | visual only", color="#edf2f7")
        fig.tight_layout()
        out = out_dir / f"B018_BOS_REVIEW_ZOOM_PAGE_{page_idx:02d}_20260514.png"
        fig.savefig(out, dpi=180)
        plt.close(fig)
        pages.append(out)
    return pages


def _write_report(path: Path, *, root: Path, artifacts: dict[str, Any], rows: list[dict[str, Any]], events: list[dict[str, Any]]) -> None:
    counts = {
        "BOS_UP": sum(1 for event in events if event["event"] == "BOS_UP"),
        "BOS_DOWN": sum(1 for event in events if event["event"] == "BOS_DOWN"),
        "CHOCH_LIKE": sum(1 for event in events if event["event"] == "CHOCH_LIKE"),
    }
    support = sum(1 for row in rows if row["b018_broad_support"])
    lines = [
        "# B018 BOS Strategy Review 2026-05-14",
        "",
        f"Статус: `{STATUS}`.",
        "",
        "Назначение: отдельно повторить BOS/CHOCH-слой без остальных паспортов и проверить, годится ли он для лонг-входов.",
        "",
        "Это visual review. Это не scorer, не target-lock, не Optuna и не ML/export.",
        "",
        "## Артефакты",
        "",
        f"- `{artifacts['full_day_png']}`",
        *[f"- `{item}`" for item in artifacts["zoom_png"]],
        f"- `{artifacts['csv']}`",
        f"- `{artifacts['json']}`",
        "",
        "## Короткий аудит",
        "",
        f"- События дня: BOS_UP `{counts['BOS_UP']}`, BOS_DOWN `{counts['BOS_DOWN']}`, CHOCH-like `{counts['CHOCH_LIKE']}`.",
        f"- По ручным входам широкий B018-context поддержал `{support}/{len(rows)}`.",
        "- Текущая трактовка: BOS сам по себе слишком широкий. Для лонга полезнее не `BOS_DOWN` как вход, а связка `down break -> reclaim/CHOCH -> локальный entry`.",
        "- Поэтому B018 оставлять как structure-context/evidence, а не как самостоятельный allow.",
        "",
        "## Target notes",
        "",
    ]
    for row in rows:
        lines.append(
            f"- `{row['target_id']}` `{row['target_type']}`: `{row['audit_note']}`, last_event `{row['last_event']}`, age `{row['last_event_age']}`."
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(day: str) -> dict[str, Any]:
    if day != "2026-05-14":
        raise ValueError("B018 BOS review is fixed to 2026-05-14 M01-M19 for this pass.")
    root = _repo_root()
    out_dir = root / "reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_b018_bos_review"
    out_dir.mkdir(parents=True, exist_ok=True)
    df = _load_ohlcv(_source_csv(root, day))
    targets = _load_targets(root, day)
    raw_pivots = _raw_pivots(df, left=3, right=3)
    events = _event_scan(df, raw_pivots)
    rows = _target_rows(df, targets, events)

    full_day = out_dir / "B018_BOS_REVIEW_FULL_DAY_20260514.png"
    _render_full_day(full_day, df, targets, events, day)
    zoom_pages = _render_zoom_pages(out_dir, df, targets, rows, events, day)
    csv_path = out_dir / "B018_BOS_REVIEW_20260514.csv"
    json_path = out_dir / "B018_BOS_REVIEW_20260514.json"
    report_ru = out_dir / "B018_BOS_REVIEW_20260514_RU.md"
    _write_csv(csv_path, rows)
    payload = {
        "status": STATUS,
        "rail_point": RAIL_POINT,
        "generated_at_utc": _utc_now(),
        "day": day,
        "events": events,
        "targets": rows,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    artifacts = {
        "full_day_png": _rel(root, full_day),
        "zoom_png": [_rel(root, item) for item in zoom_pages],
        "csv": _rel(root, csv_path),
        "json": _rel(root, json_path),
        "report_ru": _rel(root, report_ru),
    }
    _write_report(report_ru, root=root, artifacts=artifacts, rows=rows, events=events)
    return {"status": STATUS, "artifacts": artifacts}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", default="2026-05-14")
    args = parser.parse_args()
    print(json.dumps(run(args.day), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
