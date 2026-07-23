from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from mlbotnav.visual_entry_good_1pct_review_pool import _is_good
from mlbotnav.visual_entry_low_anchor_entry_1pct_label_review import _label_color, _label_short
from mlbotnav.visual_entry_low_anchor_suggester import (
    _add_features,
    _bar_width_days,
    _draw_candles,
    _load_ohlcv,
    _source_csv,
    _style_axis,
)


STATUS = "DCA_RISK_AUDIT_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA_NO_API"
PHASE_PCTS = (0.5, 1.0, 1.5, 2.0, 4.0)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def _ts(value: Any) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        return ts.tz_localize("UTC")
    return ts.tz_convert("UTC")


def _fmt_ts(value: Any) -> str:
    return _ts(value).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fmt_minute(value: Any) -> str:
    return _ts(value).strftime("%H:%M")


def _phase_key(phase_pct: float) -> str:
    return str(phase_pct).replace(".", "p")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def _load_pool_records(pool_run_dir: Path) -> list[dict[str, Any]]:
    csv_path = pool_run_dir / "GOOD_1PCT_REVIEW_POOL_RECORDS.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Не найден входной CSV пула: {csv_path}")
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _load_feedback(path: Path | None) -> dict[str, dict[str, str]]:
    if path is None or not str(path):
        return {}
    if not path.exists():
        raise FileNotFoundError(f"Не найден CSV ручной правки: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {str(row["record_id"]): row for row in rows}


def _classify_trade(
    *,
    hit_1pct: bool,
    time_to_1pct_min: float | None,
    mae_pct: float,
    max_active_all_good_at_entry: int,
    late_hold_minutes: int,
    overload_open_count: int,
) -> str:
    if max_active_all_good_at_entry > overload_open_count:
        return "D_CLUSTER_OVERLOAD"
    if mae_pct <= -1.0 and not hit_1pct:
        return "E_FALLING_KNIFE_NO_1PCT"
    if mae_pct <= -1.5:
        return "E_FALLING_KNIFE_DEEP_DD"
    if not hit_1pct:
        return "F_NO_1PCT_ROOM"
    if time_to_1pct_min is not None and time_to_1pct_min > late_hold_minutes:
        return "C_LATE_PUMP_DEPENDENT"
    if mae_pct >= -0.35 and time_to_1pct_min is not None and time_to_1pct_min <= 180:
        return "A_FAST_CLEAN"
    return "B_DCA_SURVIVABLE"


def _session_utc(ts: pd.Timestamp) -> str:
    hour = int(ts.hour)
    if hour < 6:
        return "S1_00_06_UTC"
    if hour < 12:
        return "S2_06_12_UTC"
    if hour < 18:
        return "S3_12_18_UTC"
    return "S4_18_24_UTC"


def _compute_trade_rows(
    *,
    root: Path,
    pool_rows: list[dict[str, Any]],
    symbol: str,
    timeframe: str,
    selected_limit_per_day: int,
    late_hold_minutes: int,
    overload_open_count: int,
) -> tuple[list[dict[str, Any]], dict[str, pd.DataFrame], list[str]]:
    frames_by_day: dict[str, pd.DataFrame] = {}
    missing_sources: list[str] = []
    by_day: dict[str, list[dict[str, Any]]] = {}
    for row in pool_rows:
        by_day.setdefault(str(row["day_utc"]), []).append(row)

    out_rows: list[dict[str, Any]] = []
    for day, rows in sorted(by_day.items()):
        source = _source_csv(root, day, timeframe, symbol)
        if not source.exists():
            missing_sources.append(_rel(root, source))
            continue
        df = _add_features(_load_ohlcv(source))
        frames_by_day[day] = df

        good_index = 0
        for row in sorted(rows, key=lambda item: str(item["entry_time_utc"])):
            entry_time = _ts(row["entry_time_utc"])
            signal_time = _ts(row["signal_time_utc"])
            entry_price = _safe_float(row.get("entry_price_5bps"))
            entry_open = _safe_float(row.get("entry_open_price"))
            is_good = _is_good(row)
            if is_good:
                good_index += 1
            selected_chrono10 = bool(is_good and good_index <= selected_limit_per_day)

            future = df[df["open_time_utc"] >= entry_time].reset_index(drop=True)
            if future.empty or entry_price <= 0:
                continue

            phase_payload: dict[str, Any] = {}
            first_exit_time: pd.Timestamp | None = None
            first_exit_label = ""
            phase_hits: list[float] = []
            for phase_pct in PHASE_PCTS:
                key = _phase_key(phase_pct)
                target_price = entry_price * (1.0 + phase_pct / 100.0)
                hit_rows = future[future["high"] >= target_price]
                hit = not hit_rows.empty
                hit_time: pd.Timestamp | None = _ts(hit_rows.iloc[0]["open_time_utc"]) if hit else None
                if hit:
                    phase_hits.append(phase_pct)
                    if first_exit_time is None:
                        first_exit_time = hit_time
                        first_exit_label = f"{phase_pct:.1f}%"
                phase_payload[f"target_{key}_price"] = round(target_price, 8)
                phase_payload[f"hit_{key}pct"] = bool(hit)
                phase_payload[f"hit_time_{key}pct"] = _fmt_ts(hit_time) if hit_time is not None else ""
                phase_payload[f"time_to_{key}pct_min"] = (
                    round((hit_time - entry_time).total_seconds() / 60.0, 3) if hit_time is not None else ""
                )

            hit_1pct = bool(phase_payload.get("hit_1p0pct"))
            hit_time_1pct = phase_payload.get("hit_time_1p0pct") or ""
            exit_time = _ts(hit_time_1pct) if hit_time_1pct else future.iloc[-1]["open_time_utc"]
            time_to_1pct_min = (
                float(phase_payload["time_to_1p0pct_min"]) if phase_payload.get("time_to_1p0pct_min") != "" else None
            )

            until = future[future["open_time_utc"] <= _ts(exit_time)]
            min_low_until_exit = float(until["low"].min()) if not until.empty else float(future["low"].min())
            mae_pct = (min_low_until_exit / entry_price - 1.0) * 100.0
            max_high_eod = float(future["high"].max())
            max_room_eod_pct = (max_high_eod / entry_price - 1.0) * 100.0

            out_rows.append(
                {
                    "day_utc": day,
                    "record_id": row.get("record_id"),
                    "candidate_id": row.get("candidate_id"),
                    "review_label": row.get("review_label"),
                    "suggested_type": row.get("suggested_type"),
                    "score": row.get("score"),
                    "is_good_1pct_pool": bool(is_good),
                    "good_order_in_day": good_index if is_good else "",
                    "selected_chrono10": selected_chrono10,
                    "session_utc": _session_utc(entry_time),
                    "signal_time_utc": _fmt_ts(signal_time),
                    "entry_time_utc": _fmt_ts(entry_time),
                    "entry_open_price": round(entry_open, 8),
                    "entry_price_5bps": round(entry_price, 8),
                    "anchor_time_utc": row.get("anchor_time_utc"),
                    "anchor_low_price": row.get("anchor_low_price"),
                    "exit_reference_time_utc": _fmt_ts(exit_time),
                    "exit_reference_reason": "hit_1pct_5bps" if hit_1pct else "end_of_day_no_1pct",
                    "first_phase_hit": first_exit_label,
                    "first_phase_hit_time_utc": _fmt_ts(first_exit_time) if first_exit_time is not None else "",
                    "max_phase_hit_pct": max(phase_hits) if phase_hits else 0.0,
                    "hit_1pct": hit_1pct,
                    "hit_time_1pct_utc": hit_time_1pct,
                    "time_to_1pct_min": round(time_to_1pct_min, 3) if time_to_1pct_min is not None else "",
                    "mae_until_exit_pct": round(mae_pct, 6),
                    "min_low_until_exit": round(min_low_until_exit, 8),
                    "max_room_eod_pct": round(max_room_eod_pct, 6),
                    "max_high_eod": round(max_high_eod, 8),
                    "late_pump_dependent": bool(time_to_1pct_min is not None and time_to_1pct_min > late_hold_minutes),
                    "ml_usage": "audit_only_not_ml_label",
                    **phase_payload,
                }
            )

    _add_active_counts(out_rows, overload_open_count=overload_open_count, late_hold_minutes=late_hold_minutes)
    return out_rows, frames_by_day, missing_sources


def _add_active_counts(
    rows: list[dict[str, Any]],
    *,
    overload_open_count: int,
    late_hold_minutes: int,
) -> None:
    by_day: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_day.setdefault(str(row["day_utc"]), []).append(row)

    for day_rows in by_day.values():
        day_rows.sort(key=lambda item: item["entry_time_utc"])
        good_rows = [row for row in day_rows if row["is_good_1pct_pool"]]
        selected_rows = [row for row in day_rows if row["selected_chrono10"]]
        for row in day_rows:
            entry_time = _ts(row["entry_time_utc"])
            active_all = sum(
                1
                for item in good_rows
                if _ts(item["entry_time_utc"]) <= entry_time < _ts(item["exit_reference_time_utc"])
            )
            active_selected = sum(
                1
                for item in selected_rows
                if _ts(item["entry_time_utc"]) <= entry_time < _ts(item["exit_reference_time_utc"])
            )
            row["active_all_good_at_entry"] = active_all if row["is_good_1pct_pool"] else ""
            row["active_selected10_at_entry"] = active_selected if row["selected_chrono10"] else ""
            row["risk_class_v0"] = _classify_trade(
                hit_1pct=bool(row["hit_1pct"]),
                time_to_1pct_min=float(row["time_to_1pct_min"]) if row["time_to_1pct_min"] != "" else None,
                mae_pct=float(row["mae_until_exit_pct"]),
                max_active_all_good_at_entry=active_all,
                late_hold_minutes=late_hold_minutes,
                overload_open_count=overload_open_count,
            )


def _build_baskets(rows: list[dict[str, Any]], *, selected_only: bool) -> list[dict[str, Any]]:
    baskets: list[dict[str, Any]] = []
    by_day: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if not row["is_good_1pct_pool"]:
            continue
        if selected_only and not row["selected_chrono10"]:
            continue
        by_day.setdefault(str(row["day_utc"]), []).append(row)

    for day, day_rows in sorted(by_day.items()):
        sorted_rows = sorted(day_rows, key=lambda item: item["entry_time_utc"])
        basket_rows: list[dict[str, Any]] = []
        basket_end: pd.Timestamp | None = None
        basket_index = 0
        for row in sorted_rows:
            entry_time = _ts(row["entry_time_utc"])
            exit_time = _ts(row["exit_reference_time_utc"])
            if basket_rows and basket_end is not None and entry_time > basket_end:
                basket_index += 1
                baskets.append(_summarize_basket(day, basket_index, basket_rows, selected_only=selected_only))
                basket_rows = []
                basket_end = None
            basket_rows.append(row)
            basket_end = exit_time if basket_end is None else max(basket_end, exit_time)
        if basket_rows:
            basket_index += 1
            baskets.append(_summarize_basket(day, basket_index, basket_rows, selected_only=selected_only))
    return baskets


def _summarize_basket(day: str, basket_index: int, rows: list[dict[str, Any]], *, selected_only: bool) -> dict[str, Any]:
    first_entry = min(_ts(row["entry_time_utc"]) for row in rows)
    last_entry = max(_ts(row["entry_time_utc"]) for row in rows)
    basket_exit = max(_ts(row["exit_reference_time_utc"]) for row in rows)
    avg_entry = sum(float(row["entry_price_5bps"]) for row in rows) / max(len(rows), 1)
    min_low = min(float(row["min_low_until_exit"]) for row in rows)
    max_hold = max(
        (_ts(row["exit_reference_time_utc"]) - _ts(row["entry_time_utc"])).total_seconds() / 60.0 for row in rows
    )
    return {
        "basket_scope": "selected_chrono10" if selected_only else "all_good",
        "day_utc": day,
        "basket_id": f"{day.replace('-', '')}_{'SEL10' if selected_only else 'ALL'}_{basket_index:02d}",
        "trade_count": len(rows),
        "first_entry_utc": _fmt_ts(first_entry),
        "last_entry_utc": _fmt_ts(last_entry),
        "basket_exit_reference_utc": _fmt_ts(basket_exit),
        "avg_entry_5bps": round(avg_entry, 8),
        "basket_min_low_until_exit": round(min_low, 8),
        "basket_dd_from_avg_entry_pct": round((min_low / avg_entry - 1.0) * 100.0, 6),
        "max_single_hold_min": round(max_hold, 3),
        "late_pump_count": sum(1 for row in rows if row["late_pump_dependent"]),
        "classes": json.dumps(Counter(row["risk_class_v0"] for row in rows), ensure_ascii=False, sort_keys=True),
        "record_ids": ",".join(str(row["record_id"]) for row in rows),
    }


def _summarize_days(rows: list[dict[str, Any]], baskets: list[dict[str, Any]], *, selected_limit_per_day: int) -> list[dict[str, Any]]:
    by_day: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_day.setdefault(str(row["day_utc"]), []).append(row)

    baskets_by_day_scope: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for basket in baskets:
        baskets_by_day_scope.setdefault((str(basket["day_utc"]), str(basket["basket_scope"])), []).append(basket)

    out: list[dict[str, Any]] = []
    for day, day_rows in sorted(by_day.items()):
        good_rows = [row for row in day_rows if row["is_good_1pct_pool"]]
        selected_rows = [row for row in day_rows if row["selected_chrono10"]]
        active_all = [int(row["active_all_good_at_entry"]) for row in good_rows if row["active_all_good_at_entry"] != ""]
        active_sel = [int(row["active_selected10_at_entry"]) for row in selected_rows if row["active_selected10_at_entry"] != ""]
        cls = Counter(str(row["risk_class_v0"]) for row in good_rows)
        selected_cls = Counter(str(row["risk_class_v0"]) for row in selected_rows)
        out.append(
            {
                "day_utc": day,
                "records_total": len(day_rows),
                "good_1pct_pool_total": len(good_rows),
                "bad_pool_total": len(day_rows) - len(good_rows),
                "selected_chrono_limit": selected_limit_per_day,
                "selected_chrono10_total": len(selected_rows),
                "selected_chrono10_hit_1pct": sum(1 for row in selected_rows if row["hit_1pct"]),
                "selected_chrono10_late_pump": sum(1 for row in selected_rows if row["late_pump_dependent"]),
                "max_active_all_good": max(active_all) if active_all else 0,
                "max_active_selected10": max(active_sel) if active_sel else 0,
                "max_hold_all_good_min": round(
                    max(
                        ((_ts(row["exit_reference_time_utc"]) - _ts(row["entry_time_utc"])).total_seconds() / 60.0)
                        for row in good_rows
                    ),
                    3,
                )
                if good_rows
                else 0.0,
                "worst_trade_mae_all_good_pct": min((float(row["mae_until_exit_pct"]) for row in good_rows), default=0.0),
                "worst_basket_dd_all_good_pct": min(
                    (float(item["basket_dd_from_avg_entry_pct"]) for item in baskets_by_day_scope.get((day, "all_good"), [])),
                    default=0.0,
                ),
                "worst_basket_dd_selected10_pct": min(
                    (
                        float(item["basket_dd_from_avg_entry_pct"])
                        for item in baskets_by_day_scope.get((day, "selected_chrono10"), [])
                    ),
                    default=0.0,
                ),
                "risk_classes_all_good": json.dumps(cls, ensure_ascii=False, sort_keys=True),
                "risk_classes_selected10": json.dumps(selected_cls, ensure_ascii=False, sort_keys=True),
            }
        )
    return out


def _render_summary_png(*, days: list[dict[str, Any]], out_path: Path, run_label: str) -> None:
    if not days:
        return
    fig, axes = plt.subplots(3, 1, figsize=(24, 15), sharex=True)
    fig.patch.set_facecolor("#101418")
    for ax in axes:
        _style_axis(ax)

    x = [item["day_utc"][5:] for item in days]
    good = [int(item["good_1pct_pool_total"]) for item in days]
    selected = [int(item["selected_chrono10_total"]) for item in days]
    max_all = [int(item["max_active_all_good"]) for item in days]
    max_sel = [int(item["max_active_selected10"]) for item in days]
    dd_all = [float(item["worst_basket_dd_all_good_pct"]) for item in days]
    late_sel = [int(item["selected_chrono10_late_pump"]) for item in days]

    axes[0].bar(x, good, color="#00c853", alpha=0.55, label="all GOOD")
    axes[0].bar(x, selected, color="#ffd54f", alpha=0.80, label="first 10/day")
    axes[0].set_ylabel("Trades")
    axes[0].legend(facecolor="#101418", edgecolor="#3a4652", labelcolor="white")

    axes[1].plot(x, max_all, color="#00e676", marker="o", label="max active all GOOD")
    axes[1].plot(x, max_sel, color="#ffd54f", marker="o", label="max active first 10")
    axes[1].bar(x, late_sel, color="#ff5252", alpha=0.35, label="late pump first 10")
    axes[1].set_ylabel("Open count")
    axes[1].legend(facecolor="#101418", edgecolor="#3a4652", labelcolor="white")

    axes[2].bar(x, dd_all, color="#ef5350", alpha=0.75, label="worst basket DD all GOOD")
    axes[2].axhline(-1.0, color="#ffd54f", linewidth=1.2, alpha=0.65)
    axes[2].set_ylabel("DD %")
    axes[2].legend(facecolor="#101418", edgecolor="#3a4652", labelcolor="white")
    axes[2].tick_params(axis="x", labelrotation=45)

    fig.suptitle(f"DCA_RISK_AUDIT_V0 | {run_label} | first 10/day vs all GOOD | NO ML/OPTUNA/API", color="white", fontsize=17)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def _render_day_risk_png(
    *,
    df: pd.DataFrame,
    rows: list[dict[str, Any]],
    day: str,
    symbol: str,
    timeframe: str,
    out_path: Path,
) -> None:
    day_rows = [row for row in rows if row["day_utc"] == day and row["is_good_1pct_pool"]]
    if not day_rows:
        return
    fig, (ax_price, ax_vol) = plt.subplots(
        2,
        1,
        figsize=(32, 13),
        sharex=True,
        gridspec_kw={"height_ratios": [4.7, 1.15]},
    )
    fig.patch.set_facecolor("#101418")
    _style_axis(ax_price)
    _style_axis(ax_vol)
    _draw_candles(ax_price, df, timeframe, linewidth=0.28)
    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(df["open"], df["close"])]
    ax_vol.bar(df["open_time_utc"].dt.tz_convert(None), df["volume"], width=_bar_width_days(timeframe), color=colors, alpha=0.70)

    for row in day_rows:
        entry_time = _ts(row["entry_time_utc"]).tz_convert(None)
        exit_time = _ts(row["exit_reference_time_utc"]).tz_convert(None)
        entry_open = float(row["entry_open_price"])
        entry_exec_5bps = float(row["entry_price_5bps"])
        target_price = float(row["target_1p0_price"])
        cls = str(row["risk_class_v0"])
        color = "#00e676" if cls.startswith(("A_", "B_")) else "#ffd54f" if cls.startswith("C_") else "#ff5252"
        alpha = 0.62 if bool(row["selected_chrono10"]) else 0.22
        ax_price.axvline(entry_time, color=color, linewidth=1.0, alpha=alpha)
        ax_price.plot([entry_time, exit_time], [target_price, target_price], color=color, linewidth=0.8, alpha=alpha)
        ax_price.scatter([entry_time], [entry_open], marker="^", s=52 if row["selected_chrono10"] else 25, color=color, edgecolors="white", linewidths=0.35, zorder=7)
        ax_price.scatter([entry_time], [entry_exec_5bps], marker="_", s=75 if row["selected_chrono10"] else 35, color="#ffffff", linewidths=1.1, alpha=0.75, zorder=8)
        if bool(row["selected_chrono10"]):
            ax_price.annotate(
                f"{row['record_id']}\n{cls}\nopen {entry_open:.4f} | +5bps {entry_exec_5bps:.4f}\nactive {row['active_all_good_at_entry']} | DD {float(row['mae_until_exit_pct']):.2f}%",
                xy=(entry_time, entry_open),
                xytext=(4, 8),
                textcoords="offset points",
                color=color,
                fontsize=6,
                arrowprops={"arrowstyle": "->", "color": color, "linewidth": 0.65},
            )

    start = pd.Timestamp(f"{day} 00:00:00")
    end = start + pd.Timedelta(days=1)
    ax_price.set_xlim(start.to_pydatetime(), end.to_pydatetime())
    ax_price.set_title(
        f"{symbol} {timeframe} {day} | DCA_RISK_AUDIT_V0 | selected first 10 labeled | lines=+1% | NO ML/OPTUNA/API",
        color="white",
        fontsize=15,
    )
    ax_price.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    ax_vol.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 3)))
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor())
    plt.close(fig)


def _render_day_closeup_pages(
    *,
    df: pd.DataFrame,
    rows: list[dict[str, Any]],
    day: str,
    symbol: str,
    timeframe: str,
    out_dir: Path,
    per_page: int,
    feedback_map: dict[str, dict[str, str]] | None = None,
) -> list[Path]:
    day_rows = [
        row
        for row in rows
        if row["day_utc"] == day and row["is_good_1pct_pool"]
    ]
    day_rows = sorted(day_rows, key=lambda item: item["entry_time_utc"])
    if not day_rows:
        return []

    cols = 3
    rows_per_page = 3
    per_page = max(1, min(per_page, cols * rows_per_page))
    paths: list[Path] = []
    for page_start in range(0, len(day_rows), per_page):
        page_items = day_rows[page_start : page_start + per_page]
        page_no = page_start // per_page + 1
        fig, axes = plt.subplots(rows_per_page, cols, figsize=(22, 16), sharex=False)
        fig.patch.set_facecolor("#101418")
        flat_axes = list(axes.flatten())

        for ax in flat_axes:
            _style_axis(ax)

        for ax, row in zip(flat_axes, page_items):
            feedback = (feedback_map or {}).get(str(row["record_id"]), {})
            user_status = str(feedback.get("user_status") or "USER_PENDING_REVIEW")
            entry_time = _ts(row["entry_time_utc"])
            signal_time = _ts(row["signal_time_utc"])
            anchor_time = _ts(row["anchor_time_utc"])
            start = entry_time - pd.Timedelta(minutes=25)
            end = entry_time + pd.Timedelta(minutes=55)
            win = df[(df["open_time_utc"] >= start) & (df["open_time_utc"] <= end)].reset_index(drop=True)
            _draw_candles(ax, win, timeframe, linewidth=0.55)

            entry_open = float(row["entry_open_price"])
            entry_exec_5bps = float(row["entry_price_5bps"])
            anchor_low = float(row["anchor_low_price"])
            target_1pct = float(row["target_1p0_price"])
            cls = str(row["risk_class_v0"])
            color = "#00e676" if cls.startswith(("A_", "B_")) else "#ffd54f" if cls.startswith("C_") else "#ff5252"
            if user_status.startswith("USER_REJECT"):
                color = "#ff5252"
            elif "SHIFT_PENDING" in user_status:
                color = "#ffb300"

            entry_naive = entry_time.tz_convert(None)
            signal_naive = signal_time.tz_convert(None)
            anchor_naive = anchor_time.tz_convert(None)
            ax.axvline(signal_naive, color="#ff5252", linewidth=1.0, alpha=0.50)
            ax.axvline(entry_naive, color=color, linewidth=1.4, alpha=0.90)
            ax.scatter([anchor_naive], [anchor_low], s=34, color="#ff5252", edgecolors="#0b0f12", linewidths=0.35, zorder=6)
            ax.scatter([entry_naive], [entry_open], marker="^", s=105, color=color, edgecolors="white", linewidths=0.60, zorder=8)
            ax.scatter([entry_naive], [entry_exec_5bps], marker="_", s=120, color="#ffffff", linewidths=1.3, alpha=0.82, zorder=9)

            hit_time = row.get("hit_time_1pct_utc") or ""
            hit_in_view = False
            if hit_time:
                hit_ts = _ts(hit_time)
                hit_in_view = start <= hit_ts <= end
                if hit_in_view:
                    ax.scatter(
                        [hit_ts.tz_convert(None)],
                        [target_1pct],
                        marker="*",
                        s=120,
                        color="#ffd54f",
                        edgecolors="#0b0f12",
                        linewidths=0.40,
                        zorder=9,
                    )

            price_low = float(win["low"].min()) if not win.empty else min(anchor_low, entry_open)
            price_high = float(win["high"].max()) if not win.empty else max(anchor_low, entry_open)
            local_low = min(price_low, anchor_low, entry_open, entry_exec_5bps)
            local_high = max(price_high, anchor_low, entry_open, entry_exec_5bps)
            if hit_in_view:
                local_high = max(local_high, target_1pct)
            pad = max((local_high - local_low) * 0.18, 0.03)
            ax.set_ylim(local_low - pad, local_high + pad)
            ax.set_xlim(start.tz_convert(None).to_pydatetime(), end.tz_convert(None).to_pydatetime())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            ax.tick_params(axis="x", labelrotation=25, labelsize=7)
            ax.tick_params(axis="y", labelsize=7)

            order = row.get("good_order_in_day") or ""
            target_note = "hit in view" if hit_in_view else f"target {target_1pct:.4f}"
            ax.set_title(
                f"#{order} {row['record_id']} | {_label_short(str(row['review_label']))}\n"
                f"signal {_fmt_minute(signal_time)} -> entry {_fmt_minute(entry_time)} | {cls}\n"
                f"{user_status}",
                color="white",
                fontsize=7,
            )
            ax.annotate(
                f"open {entry_open:.4f}\n+5bps {entry_exec_5bps:.4f}\n{target_note}",
                xy=(entry_naive, entry_open),
                xytext=(7, 10),
                textcoords="offset points",
                color=color,
                fontsize=7,
                arrowprops={"arrowstyle": "->", "color": color, "linewidth": 0.8},
            )
            if user_status.startswith("USER_REJECT"):
                ax.text(
                    0.5,
                    0.5,
                    "REJECT\nCURRENT",
                    transform=ax.transAxes,
                    color="#ff5252",
                    fontsize=20,
                    fontweight="bold",
                    alpha=0.32,
                    ha="center",
                    va="center",
                    rotation=18,
                )
            elif "SHIFT_PENDING" in user_status:
                ax.text(
                    0.5,
                    0.5,
                    "SHIFT\nPENDING",
                    transform=ax.transAxes,
                    color="#ffb300",
                    fontsize=18,
                    fontweight="bold",
                    alpha=0.28,
                    ha="center",
                    va="center",
                    rotation=18,
                )

        for ax in flat_axes[len(page_items) :]:
            ax.set_visible(False)

        total_pages = (len(day_rows) + per_page - 1) // per_page
        fig.suptitle(
            f"{symbol} {timeframe} {day} | DCA closeup review | all GOOD {len(day_rows)} | page {page_no}/{total_pages} | triangle=entry open | white=+5bps | USER_FEEDBACK | NO ML/OPTUNA/API",
            color="white",
            fontsize=15,
        )
        fig.tight_layout(rect=(0, 0, 1, 0.965))
        path = out_dir / f"DCA_RISK_AUDIT_V0_CLOSEUP_{day.replace('-', '')}_PAGE_{page_no:02d}.png"
        fig.savefig(path, dpi=165, facecolor=fig.get_facecolor())
        plt.close(fig)
        paths.append(path)
    return paths


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# DCA Risk Audit V0",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: проверить риск DCA/набора нескольких long-входов из уже готового `GOOD_1PCT` пула. Это не ML, не Optuna, не scorer и не торговый API.",
        "",
        "## Сводка",
        "",
        f"- Ранс: `{payload['run_id']}`.",
        f"- Входной пул: `{payload['input_pool_run_dir']}`.",
        f"- Дней обработано: `{summary['days_processed']}`.",
        f"- Записей пула: `{summary['records_total']}`.",
        f"- GOOD из пула: `{summary['good_total']}`.",
        f"- BAD из пула: `{summary['bad_total']}`.",
        f"- Правило дневного отбора: первые `{payload['params']['selected_limit_per_day']}` GOOD-сигналов по времени, без знания будущего.",
        f"- Порог late-pump: `{payload['params']['late_hold_minutes']}` минут до +1%.",
        f"- Порог перегруза: больше `{payload['params']['overload_open_count']}` одновременно открытых GOOD-сделок.",
        "",
        "## Что это значит",
        "",
        "- `A_FAST_CLEAN`: быстрый чистый отскок, малая просадка.",
        "- `B_DCA_SURVIVABLE`: +1% есть, но вход может требовать терпения/поддержки.",
        "- `C_LATE_PUMP_DEPENDENT`: +1% добит поздно, сделка зависит от дальнего пампа.",
        "- `D_CLUSTER_OVERLOAD`: вокруг входа слишком много одновременно открытых сделок.",
        "- `E_FALLING_KNIFE_*`: нож/глубокая просадка, опасный класс.",
        "- `F_NO_1PCT_ROOM`: +1% до конца дня не был достигнут.",
        "",
        "## Дни",
        "",
        "| day | good | selected10 | max active all | max active selected | late selected | worst basket DD all | classes selected |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for item in payload["daily_summary"]:
        lines.append(
            f"| {item['day_utc']} | {item['good_1pct_pool_total']} | {item['selected_chrono10_total']} | "
            f"{item['max_active_all_good']} | {item['max_active_selected10']} | {item['selected_chrono10_late_pump']} | "
            f"{float(item['worst_basket_dd_all_good_pct']):.3f}% | `{item['risk_classes_selected10']}` |"
        )
    lines.extend(["", "## Артефакты", ""])
    for key, value in payload["artifacts"].items():
        if isinstance(value, list):
            lines.append(f"- `{key}`:")
            for item in value:
                lines.append(f"  - `{item}`")
        else:
            lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Границы",
            "",
            "- Future outcome используется только для аудита результата, не как входная фича.",
            "- Hedge/DCA money-management здесь не оптимизируется, только помечается риск перегруза.",
            "- Следующий шаг после просмотра PNG: вручную подтвердить, какие классы разрешать в датасет, а какие отправлять в hard-negative.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_audit(
    *,
    pool_run_dir: Path,
    symbol: str,
    timeframe: str,
    out_dir: Path,
    run_label: str,
    selected_limit_per_day: int,
    late_hold_minutes: int,
    overload_open_count: int,
    render_top_days: int,
    closeup_days: list[str],
    closeup_per_page: int,
    feedback_csv: Path | None,
) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    if not pool_run_dir.is_absolute():
        pool_run_dir = root / pool_run_dir
    if not out_dir.is_absolute():
        out_dir = root / out_dir

    run_id = f"{run_label}_{_run_stamp()}" if run_label else f"dca_risk_{_run_stamp()}"
    run_dir = out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    pool_rows = _load_pool_records(pool_run_dir)
    feedback_map = _load_feedback(feedback_csv)
    trade_rows, frames_by_day, missing_sources = _compute_trade_rows(
        root=root,
        pool_rows=pool_rows,
        symbol=symbol,
        timeframe=timeframe,
        selected_limit_per_day=selected_limit_per_day,
        late_hold_minutes=late_hold_minutes,
        overload_open_count=overload_open_count,
    )
    baskets_all = _build_baskets(trade_rows, selected_only=False)
    baskets_selected = _build_baskets(trade_rows, selected_only=True)
    basket_rows = baskets_all + baskets_selected
    daily_summary = _summarize_days(trade_rows, basket_rows, selected_limit_per_day=selected_limit_per_day)

    trades_csv = run_dir / "DCA_RISK_AUDIT_V0_TRADES.csv"
    days_csv = run_dir / "DCA_RISK_AUDIT_V0_DAYS.csv"
    baskets_csv = run_dir / "DCA_RISK_AUDIT_V0_BASKETS.csv"
    payload_json = run_dir / "DCA_RISK_AUDIT_V0_PAYLOAD.json"
    report_ru = run_dir / "DCA_RISK_AUDIT_V0_REPORT_RU.md"
    summary_png = run_dir / "DCA_RISK_AUDIT_V0_SUMMARY.png"

    _write_csv(trades_csv, trade_rows)
    _write_csv(days_csv, daily_summary)
    _write_csv(baskets_csv, basket_rows)
    _render_summary_png(days=daily_summary, out_path=summary_png, run_label=run_id)

    top_days = sorted(daily_summary, key=lambda item: (int(item["max_active_all_good"]), int(item["good_1pct_pool_total"])), reverse=True)
    day_pngs: list[Path] = []
    for item in top_days[: max(render_top_days, 0)]:
        day = str(item["day_utc"])
        if day not in frames_by_day:
            continue
        png = run_dir / f"DCA_RISK_AUDIT_V0_TOP_DAY_{day.replace('-', '')}.png"
        _render_day_risk_png(df=frames_by_day[day], rows=trade_rows, day=day, symbol=symbol, timeframe=timeframe, out_path=png)
        day_pngs.append(png)

    closeup_pngs: list[Path] = []
    for day in closeup_days:
        if day not in frames_by_day:
            continue
        closeup_pngs.extend(
            _render_day_closeup_pages(
                df=frames_by_day[day],
                rows=trade_rows,
                day=day,
                symbol=symbol,
                timeframe=timeframe,
                out_dir=run_dir,
                per_page=closeup_per_page,
                feedback_map=feedback_map,
            )
        )

    good_total = sum(1 for row in trade_rows if row["is_good_1pct_pool"])
    selected_total = sum(1 for row in trade_rows if row["selected_chrono10"])
    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "run_id": run_id,
        "input_pool_run_dir": _rel(root, pool_run_dir),
        "symbol": symbol,
        "timeframe": timeframe,
        "params": {
            "selected_limit_per_day": selected_limit_per_day,
            "phase_pcts": PHASE_PCTS,
            "entry_execution_price": "entry_price_5bps",
            "late_hold_minutes": late_hold_minutes,
            "overload_open_count": overload_open_count,
            "render_top_days": render_top_days,
            "closeup_days": closeup_days,
            "closeup_per_page": closeup_per_page,
            "feedback_csv": _rel(root, feedback_csv) if feedback_csv else "",
        },
        "summary": {
            "days_processed": len(frames_by_day),
            "records_total": len(trade_rows),
            "good_total": good_total,
            "bad_total": len(trade_rows) - good_total,
            "selected_chrono10_total": selected_total,
            "missing_sources": len(missing_sources),
            "max_active_all_good_global": max((int(item["max_active_all_good"]) for item in daily_summary), default=0),
            "max_active_selected10_global": max((int(item["max_active_selected10"]) for item in daily_summary), default=0),
            "worst_basket_dd_all_good_global_pct": min(
                (float(item["worst_basket_dd_all_good_pct"]) for item in daily_summary),
                default=0.0,
            ),
        },
        "risk_class_counts_all_good": dict(
            Counter(str(row["risk_class_v0"]) for row in trade_rows if row["is_good_1pct_pool"])
        ),
        "risk_class_counts_selected10": dict(
            Counter(str(row["risk_class_v0"]) for row in trade_rows if row["selected_chrono10"])
        ),
        "daily_summary": daily_summary,
        "missing_sources": missing_sources,
        "artifacts": {
            "run_dir": _rel(root, run_dir),
            "trades_csv": _rel(root, trades_csv),
            "days_csv": _rel(root, days_csv),
            "baskets_csv": _rel(root, baskets_csv),
            "payload_json": _rel(root, payload_json),
            "report_ru": _rel(root, report_ru),
            "summary_png": _rel(root, summary_png),
            "top_day_pngs": [_rel(root, path) for path in day_pngs],
            "closeup_pngs": [_rel(root, path) for path in closeup_pngs],
        },
        "guardrails": [
            "NO_ML_EXPORT_TRAINING",
            "NO_OPTUNA",
            "NO_SCORER",
            "NO_TARGET_LOCK",
            "NO_API_TRADING",
            "FUTURE_OUTCOME_AUDIT_ONLY",
        ],
    }
    payload_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    _write_report(report_ru, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pool-run-dir",
        default="reports/final_review/visual_entry_v3/fresh_target_led/good_1pct_review_pool/W18_W20_learning_20260702_082819",
    )
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0")
    parser.add_argument("--run-label", default="W18_W20_dca_risk")
    parser.add_argument("--selected-limit-per-day", type=int, default=10)
    parser.add_argument("--late-hold-minutes", type=int, default=360)
    parser.add_argument("--overload-open-count", type=int, default=10)
    parser.add_argument("--render-top-days", type=int, default=3)
    parser.add_argument("--closeup-day", action="append", default=[])
    parser.add_argument("--closeup-per-page", type=int, default=9)
    parser.add_argument("--feedback-csv", default="")
    args = parser.parse_args()

    payload = run_audit(
        pool_run_dir=Path(args.pool_run_dir),
        symbol=args.symbol,
        timeframe=args.timeframe,
        out_dir=Path(args.out_dir),
        run_label=args.run_label,
        selected_limit_per_day=args.selected_limit_per_day,
        late_hold_minutes=args.late_hold_minutes,
        overload_open_count=args.overload_open_count,
        render_top_days=args.render_top_days,
        closeup_days=args.closeup_day,
        closeup_per_page=args.closeup_per_page,
        feedback_csv=Path(args.feedback_csv) if args.feedback_csv else None,
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "run_id": payload["run_id"],
                "summary": payload["summary"],
                "risk_class_counts_selected10": payload["risk_class_counts_selected10"],
                "artifacts": payload["artifacts"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
