from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from mlbotnav.visual_entry_low_anchor_entry_1pct_label_review import (
    SLIPPAGE_BANDS_BPS,
    _label_candidates,
    _label_color,
    _label_short,
)
from mlbotnav.visual_entry_low_anchor_suggester import (
    _add_features,
    _bar_width_days,
    _draw_candles,
    _fmt_minute,
    _load_ohlcv,
    _source_csv,
    _style_axis,
    build_candidates,
)


STATUS = "GOOD_1PCT_REVIEW_POOL_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def _iter_days(start_day: str, end_day: str) -> list[str]:
    start = pd.Timestamp(start_day)
    end = pd.Timestamp(end_day)
    if end < start:
        raise ValueError("--end-day must be >= --start-day")
    return [item.strftime("%Y-%m-%d") for item in pd.date_range(start, end, freq="D")]


def _tail_days_for_hours(hours: float) -> int:
    if hours <= 0:
        return 0
    return max(0, int(math.ceil(hours / 24.0)))


def _is_good(row: dict[str, Any]) -> bool:
    return not str(row.get("review_label", "")).startswith("BAD")


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _record_id(day: str, candidate_id: str) -> str:
    return f"G1P_{day.replace('-', '')}_{candidate_id}"


def _sort_rows_for_review(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            str(row.get("day_utc", "")),
            pd.Timestamp(row["entry_time_utc"]),
            str(row.get("record_id", "")),
        ),
    )


def _flatten_for_csv(row: dict[str, Any]) -> dict[str, Any]:
    features = row.get("features_at_signal_close") or {}
    out = {
        "run_id": row.get("run_id"),
        "day_utc": row.get("day_utc"),
        "record_id": row.get("record_id"),
        "candidate_id": row.get("candidate_id"),
        "review_label": row.get("review_label"),
        "suggested_type": row.get("suggested_type"),
        "score": row.get("score"),
        "anchor_idx": row.get("anchor_idx"),
        "signal_idx": row.get("signal_idx"),
        "confirmation_idx": row.get("confirmation_idx"),
        "entry_idx": row.get("entry_idx"),
        "anchor_age_bars": row.get("anchor_age_bars"),
        "execution_delay_bars_from_anchor": row.get("execution_delay_bars_from_anchor"),
        "anchor_time_utc": row.get("anchor_time_utc"),
        "anchor_low_price": row.get("anchor_low_price"),
        "signal_time_utc": row.get("signal_time_utc"),
        "confirmation_time_utc": row.get("confirmation_time_utc"),
        "entry_time_utc": row.get("entry_time_utc"),
        "entry_open_price": row.get("entry_open_price"),
        "entry_price_0bps": row.get("entry_price_0bps"),
        "entry_price_5bps": row.get("entry_price_5bps"),
        "entry_price_10bps": row.get("entry_price_10bps"),
        "target_1pct_0bps": row.get("target_1pct_0bps"),
        "target_1pct_5bps": row.get("target_1pct_5bps"),
        "target_1pct_10bps": row.get("target_1pct_10bps"),
        "hit_1pct_0bps": row.get("hit_1pct_0bps"),
        "hit_time_0bps": row.get("hit_time_0bps"),
        "hit_1pct_5bps": row.get("hit_1pct_5bps"),
        "hit_time_5bps": row.get("hit_time_5bps"),
        "hit_1pct_10bps": row.get("hit_1pct_10bps"),
        "hit_time_10bps": row.get("hit_time_10bps"),
        "outcome_lookahead_hours": row.get("outcome_lookahead_hours"),
        "outcome_check_end_time_utc": row.get("outcome_check_end_time_utc"),
        "hit_day_utc": row.get("hit_day_utc"),
        "hold_minutes_to_target": row.get("hold_minutes_to_target"),
        "carried_overnight": row.get("carried_overnight"),
        "outcome_status": row.get("outcome_status"),
        "risk_flags": _safe_text(row.get("risk_flags")),
        "outcome_usage": row.get("outcome_usage"),
    }
    for key, value in sorted(features.items()):
        out[f"feature_{key}"] = value
    return out


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    flat = [_flatten_for_csv(row) for row in rows]
    columns: list[str] = []
    for row in flat:
        for key in row:
            if key not in columns:
                columns.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(flat)


def _render_day_overview(
    *,
    df: pd.DataFrame,
    rows: list[dict[str, Any]],
    day: str,
    symbol: str,
    timeframe: str,
    out_path: Path,
) -> None:
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
    _draw_candles(ax_price, df, timeframe, linewidth=0.30)
    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(df["open"], df["close"])]
    ax_vol.bar(df["open_time_utc"].dt.tz_convert(None), df["volume"], width=_bar_width_days(timeframe), color=colors, alpha=0.70)

    end_of_day = pd.Timestamp(f"{day} 23:59:00")
    for row in rows:
        entry_time = pd.Timestamp(row["entry_time_utc"]).tz_convert(None)
        anchor_time = pd.Timestamp(row["anchor_time_utc"]).tz_convert(None)
        entry_open = float(row["entry_open_price"])
        entry_5 = float(row["entry_price_5bps"])
        target_5 = float(row["target_1pct_5bps"])
        anchor_low = float(row["anchor_low_price"])
        label = str(row["review_label"])
        color = _label_color(label)
        is_good = _is_good(row)
        hit_time_raw = str(row.get("hit_time_5bps") or row.get("hit_time_0bps") or "")
        line_end = pd.Timestamp(hit_time_raw).tz_convert(None) if hit_time_raw else end_of_day
        alpha = 0.90 if is_good else 0.32

        ax_price.axvline(entry_time, color=color, alpha=0.18 if is_good else 0.10, linewidth=0.9)
        ax_price.plot([entry_time, line_end], [target_5, target_5], color=color, alpha=0.42 if is_good else 0.10, linewidth=0.9)
        ax_price.scatter([anchor_time], [anchor_low], s=20 if is_good else 14, color="#ff5252", edgecolors="#0b0f12", linewidths=0.35, alpha=alpha, zorder=6)
        if is_good:
            ax_price.scatter([entry_time], [entry_open], marker="^", s=58, color=color, edgecolors="white", linewidths=0.35, alpha=alpha, zorder=7)
            ax_price.vlines(entry_time, float(row["entry_price_0bps"]), float(row["entry_price_10bps"]), color="#ffffff", linewidth=1.2, alpha=0.62, zorder=6)
            ax_price.annotate(
                f"{row['record_id']} {_label_short(label)}\nopen {entry_open:.4f} +5bps {entry_5:.4f}",
                xy=(entry_time, entry_open),
                xytext=(4, 8),
                textcoords="offset points",
                color=color,
                fontsize=6,
                arrowprops={"arrowstyle": "->", "color": color, "linewidth": 0.7},
            )
        else:
            ax_price.scatter([entry_time], [entry_open], marker="x", s=64, color="#ff5252", linewidths=1.2, alpha=0.55, zorder=7)

    start = pd.Timestamp(f"{day} 00:00:00")
    end = start + pd.Timedelta(days=1)
    ax_price.set_xlim(start.to_pydatetime(), end.to_pydatetime())
    ax_price.set_title(
        f"{symbol} {timeframe} {day} | GOOD_1PCT_REVIEW_POOL | triangle=entry open | line=+1% from +5bps | NO ML/OPTUNA",
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


def _render_good_closeup_pages(
    *,
    frames_by_day: dict[str, pd.DataFrame],
    rows: list[dict[str, Any]],
    symbol: str,
    timeframe: str,
    out_dir: Path,
    render_limit: int,
) -> list[Path]:
    good_rows = _sort_rows_for_review([row for row in rows if _is_good(row)])
    if render_limit > 0:
        good_rows = good_rows[:render_limit]

    paths: list[Path] = []
    per_page = 8
    for page_start in range(0, len(good_rows), per_page):
        page_rows = good_rows[page_start : page_start + per_page]
        fig, axes = plt.subplots(4, 2, figsize=(21, 22), sharex=False)
        fig.patch.set_facecolor("#101418")
        flat = list(axes.flatten())

        for ax, row in zip(flat, page_rows):
            _style_axis(ax)
            day = str(row["day_utc"])
            df = frames_by_day[day]
            entry_time = pd.Timestamp(row["entry_time_utc"])
            hit_time_raw = str(row.get("hit_time_5bps") or row.get("hit_time_0bps") or "")
            hit_ts = pd.Timestamp(hit_time_raw) if hit_time_raw else None
            start = entry_time - pd.Timedelta(minutes=30)
            end = entry_time + pd.Timedelta(minutes=60)
            if hit_ts is not None and hit_ts > end:
                end = min(hit_ts + pd.Timedelta(minutes=15), entry_time + pd.Timedelta(hours=12))
            start_naive = start.tz_convert(None)
            end_naive = end.tz_convert(None)
            win = df[(df["open_time_utc"] >= start) & (df["open_time_utc"] <= end)].reset_index(drop=True)
            _draw_candles(ax, win, timeframe, linewidth=0.58)

            anchor_time = pd.Timestamp(row["anchor_time_utc"]).tz_convert(None)
            entry_naive = entry_time.tz_convert(None)
            anchor_low = float(row["anchor_low_price"])
            entry_open = float(row["entry_open_price"])
            entry_0 = float(row["entry_price_0bps"])
            entry_5 = float(row["entry_price_5bps"])
            entry_10 = float(row["entry_price_10bps"])
            target_5 = float(row["target_1pct_5bps"])
            label = str(row["review_label"])
            color = _label_color(label)
            hit_naive = pd.Timestamp(hit_time_raw).tz_convert(None) if hit_time_raw else None
            line_end = min(hit_naive, end_naive) if hit_naive is not None else end_naive

            ax.axvline(entry_naive, color=color, linewidth=1.1, alpha=0.68)
            ax.plot([entry_naive, line_end], [target_5, target_5], color=color, alpha=0.58, linewidth=1.15)
            ax.scatter([anchor_time], [anchor_low], s=68, color="#ff5252", edgecolors="#0b0f12", zorder=5)
            ax.scatter([entry_naive], [entry_open], marker="^", s=116, color=color, edgecolors="white", linewidths=0.55, zorder=7)
            ax.vlines(entry_naive, entry_0, entry_10, color="#ffffff", linewidth=2.0, alpha=0.72, zorder=6)
            if hit_naive is not None and hit_naive <= end_naive:
                ax.scatter([hit_naive], [target_5], marker="*", s=135, color="#ffd54f", edgecolors="#0b0f12", linewidths=0.45, zorder=8)
            ax.set_xlim(start_naive.to_pydatetime(), end_naive.to_pydatetime())
            ax.annotate(
                f"{row['record_id']}\nsignal {_fmt_minute(pd.Timestamp(row['signal_time_utc']))} -> entry {_fmt_minute(entry_time)}\nopen {entry_open:.4f} | +5bps {entry_5:.4f}\n+1% target {target_5:.4f}",
                xy=(entry_naive, entry_open),
                xytext=(7, 10),
                textcoords="offset points",
                color=color,
                fontsize=8,
                arrowprops={"arrowstyle": "->", "color": color, "linewidth": 1.0},
            )
            ax.set_title(f"{day} | {_label_short(label)} | {row['suggested_type']} | score {float(row['score']):.2f}", color="white", fontsize=9)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            ax.tick_params(axis="x", labelrotation=25)

        for ax in flat[len(page_rows) :]:
            ax.axis("off")
            ax.set_facecolor("#101418")

        page_no = page_start // per_page + 1
        fig.suptitle(
            f"{symbol} {timeframe} | GOOD 1pct closeups page {page_no} | entry open + 0/5/10bps band | NO ML/OPTUNA",
            color="white",
            fontsize=15,
        )
        fig.tight_layout(rect=[0, 0, 1, 0.975])
        out_path = out_dir / f"GOOD_1PCT_REVIEW_POOL_GOOD_CLOSEUPS_PAGE_{page_no:02d}.png"
        fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor())
        plt.close(fig)
        paths.append(out_path)
    return paths


def _render_all_closeup_pages(
    *,
    frames_by_day: dict[str, pd.DataFrame],
    rows: list[dict[str, Any]],
    symbol: str,
    timeframe: str,
    out_dir: Path,
    render_limit: int,
    file_prefix: str = "GOOD_1PCT_REVIEW_POOL_ALL_CLOSEUPS_PAGE",
    numbered_file_prefix: bool = False,
) -> list[Path]:
    page_rows_all = _sort_rows_for_review(list(rows))
    if render_limit > 0:
        page_rows_all = page_rows_all[:render_limit]

    paths: list[Path] = []
    per_page = 8
    for page_start in range(0, len(page_rows_all), per_page):
        page_rows = page_rows_all[page_start : page_start + per_page]
        fig, axes = plt.subplots(4, 2, figsize=(21, 22), sharex=False)
        fig.patch.set_facecolor("#101418")
        flat = list(axes.flatten())

        for ax, row in zip(flat, page_rows):
            _style_axis(ax)
            day = str(row["day_utc"])
            df = frames_by_day[day]
            entry_time = pd.Timestamp(row["entry_time_utc"])
            hit_time_raw = str(row.get("hit_time_5bps") or row.get("hit_time_0bps") or "")
            hit_ts = pd.Timestamp(hit_time_raw) if hit_time_raw else None
            start = entry_time - pd.Timedelta(minutes=30)
            end = entry_time + pd.Timedelta(minutes=60)
            if hit_ts is not None and hit_ts > end:
                end = min(hit_ts + pd.Timedelta(minutes=15), entry_time + pd.Timedelta(hours=12))
            start_naive = start.tz_convert(None)
            end_naive = end.tz_convert(None)
            win = df[(df["open_time_utc"] >= start) & (df["open_time_utc"] <= end)].reset_index(drop=True)
            _draw_candles(ax, win, timeframe, linewidth=0.58)

            anchor_time = pd.Timestamp(row["anchor_time_utc"]).tz_convert(None)
            entry_naive = entry_time.tz_convert(None)
            anchor_low = float(row["anchor_low_price"])
            entry_open = float(row["entry_open_price"])
            entry_0 = float(row["entry_price_0bps"])
            entry_5 = float(row["entry_price_5bps"])
            entry_10 = float(row["entry_price_10bps"])
            target_5 = float(row["target_1pct_5bps"])
            label = str(row["review_label"])
            is_good = _is_good(row)
            color = _label_color(label) if is_good else "#ff5252"
            hit_naive = pd.Timestamp(hit_time_raw).tz_convert(None) if hit_time_raw else None
            line_end = min(hit_naive, end_naive) if hit_naive is not None else end_naive

            ax.axvline(entry_naive, color=color, linewidth=1.1, alpha=0.68 if is_good else 0.28)
            ax.plot([entry_naive, line_end], [target_5, target_5], color=color, alpha=0.58 if is_good else 0.16, linewidth=1.15)
            ax.scatter([anchor_time], [anchor_low], s=68 if is_good else 44, color="#ff5252", edgecolors="#0b0f12", alpha=0.92 if is_good else 0.55, zorder=5)
            if is_good:
                ax.scatter([entry_naive], [entry_open], marker="^", s=116, color=color, edgecolors="white", linewidths=0.55, zorder=7)
                ax.vlines(entry_naive, entry_0, entry_10, color="#ffffff", linewidth=2.0, alpha=0.72, zorder=6)
                if hit_naive is not None and hit_naive <= end_naive:
                    ax.scatter([hit_naive], [target_5], marker="*", s=135, color="#ffd54f", edgecolors="#0b0f12", linewidths=0.45, zorder=8)
                marker_note = "GOOD entry"
            else:
                ax.scatter([entry_naive], [entry_open], marker="x", s=145, color=color, linewidths=2.0, alpha=0.62, zorder=7)
                ax.vlines(entry_naive, entry_0, entry_10, color=color, linewidth=1.4, alpha=0.24, zorder=6)
                marker_note = "BAD reject"

            ax.set_xlim(start_naive.to_pydatetime(), end_naive.to_pydatetime())
            ax.annotate(
                f"{row['record_id']}\n{marker_note}: signal {_fmt_minute(pd.Timestamp(row['signal_time_utc']))} -> entry {_fmt_minute(entry_time)}\nopen {entry_open:.4f} | +5bps {entry_5:.4f}\n+1% target {target_5:.4f}\n{str(row.get('outcome_status') or '').replace('_', ' ').lower()}",
                xy=(entry_naive, entry_open),
                xytext=(7, 10),
                textcoords="offset points",
                color=color,
                fontsize=8,
                alpha=0.98 if is_good else 0.72,
                arrowprops={"arrowstyle": "->", "color": color, "linewidth": 1.0, "alpha": 0.95 if is_good else 0.50},
            )
            ax.set_title(f"{day} | {_label_short(label)} | {row['suggested_type']} | score {float(row['score']):.2f}", color="white", fontsize=9)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            ax.tick_params(axis="x", labelrotation=25)

        for ax in flat[len(page_rows) :]:
            ax.axis("off")
            ax.set_facecolor("#101418")

        page_no = page_start // per_page + 1
        fig.suptitle(
            f"{symbol} {timeframe} | ALL 1pct closeups page {page_no} | green=GOOD red-x=BAD | NO ML/OPTUNA",
            color="white",
            fontsize=15,
        )
        fig.tight_layout(rect=[0, 0, 1, 0.975])
        if numbered_file_prefix:
            out_path = out_dir / f"{page_no:02d}_{file_prefix}_{page_no:02d}.png"
        else:
            out_path = out_dir / f"{file_prefix}_{page_no:02d}.png"
        fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor())
        plt.close(fig)
        paths.append(out_path)
    return paths


def _write_day_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    _write_csv(path, _sort_rows_for_review(rows))


def _render_run_index(
    *,
    daily_summary: list[dict[str, Any]],
    symbol: str,
    timeframe: str,
    out_path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(16, max(4.5, 1.0 + len(daily_summary) * 0.65)))
    fig.patch.set_facecolor("#101418")
    ax.set_facecolor("#101418")
    ax.axis("off")
    ax.set_title(
        f"{symbol} {timeframe} | STAS1 BROWSE INDEX | open day folder, then use arrows | NO ML/OPTUNA",
        color="white",
        fontsize=15,
        pad=18,
    )

    lines = [
        "Порядок просмотра:",
        "1. открыть папку нужного дня;",
        "2. открыть 00_OVERVIEW;",
        "3. листать стрелками: overview -> сделки дня по времени.",
        "",
        "Дни в этом run:",
    ]
    for item in daily_summary:
        day = item["day_utc"]
        lines.append(
            f"{day}: candidates={item['candidates']} | GOOD={item['good']} | BAD={item['bad']}"
        )
    ax.text(
        0.035,
        0.92,
        "\n".join(lines),
        transform=ax.transAxes,
        color="#d8dee9",
        fontsize=13,
        va="top",
        family="monospace",
        linespacing=1.45,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor())
    plt.close(fig)


def _build_browse_by_day(
    *,
    run_dir: Path,
    frames_by_day: dict[str, pd.DataFrame],
    rows: list[dict[str, Any]],
    daily_summary: list[dict[str, Any]],
    day_overview_by_day: dict[str, Path],
    symbol: str,
    timeframe: str,
    render_limit: int,
) -> dict[str, Any]:
    browse_dir = run_dir / "BROWSE_BY_DAY"
    browse_dir.mkdir(parents=True, exist_ok=True)
    index_png = browse_dir / "00_RUN_INDEX.png"
    index_md = browse_dir / "00_RUN_INDEX_RU.md"

    rows_by_day: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        rows_by_day.setdefault(str(row["day_utc"]), []).append(row)

    days_payload: list[dict[str, Any]] = []
    for item in daily_summary:
        day = str(item["day_utc"])
        compact_day = day.replace("-", "")
        day_dir = browse_dir / day
        day_dir.mkdir(parents=True, exist_ok=True)

        day_rows = _sort_rows_for_review(rows_by_day.get(day, []))
        overview_dst: Path | None = None
        overview_src = day_overview_by_day.get(day)
        if overview_src and overview_src.exists():
            overview_dst = day_dir / f"00_{compact_day}_OVERVIEW.png"
            shutil.copy2(overview_src, overview_dst)

        closeups = _render_all_closeup_pages(
            frames_by_day=frames_by_day,
            rows=day_rows,
            symbol=symbol,
            timeframe=timeframe,
            out_dir=day_dir,
            render_limit=render_limit,
            file_prefix=f"{compact_day}_ALL_CLOSEUPS_PAGE",
            numbered_file_prefix=True,
        )
        csv_path = day_dir / f"{compact_day}_RECORDS.csv"
        _write_day_csv(csv_path, day_rows)

        days_payload.append(
            {
                "day_utc": day,
                "folder": day_dir,
                "overview": overview_dst,
                "all_closeups": closeups,
                "records_csv": csv_path,
                "candidates": item["candidates"],
                "good": item["good"],
                "bad": item["bad"],
            }
        )

    _render_run_index(
        daily_summary=daily_summary,
        symbol=symbol,
        timeframe=timeframe,
        out_path=index_png,
    )

    lines = [
        "# STAS1 browse by day",
        "",
        "Назначение: удобный просмотр run без открытия десятков окон.",
        "",
        "Порядок: открыть папку дня, открыть `00_OVERVIEW`, дальше листать PNG стрелками.",
        "",
        "| day | candidates | good | bad | folder |",
        "|---|---:|---:|---:|---|",
    ]
    for item in days_payload:
        lines.append(
            f"| {item['day_utc']} | {item['candidates']} | {item['good']} | {item['bad']} | `{item['folder'].name}` |"
        )
    index_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "browse_dir": browse_dir,
        "index_png": index_png,
        "index_md": index_md,
        "days": days_payload,
    }


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Good 1pct Review Pool",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: быстро собрать low-кандидаты по диапазону дней, проверить достижение `+1%` от `entry open + 5bps` и сохранить материал для ручного просмотра глазами.",
        "",
        "## Правило",
        "",
        "- Значимый low = `signal`.",
        "- Вход = `entry open` следующей свечи.",
        "- Расчетная цена исполнения = `entry open + 5bps`.",
        "- Цель = `+1%` от расчетной цены исполнения.",
        "- `0/5/10bps` хранятся как execution band для аудита проскальзывания.",
        "- Future outcome используется только как offline label после найденного low-кандидата, не как фича сигнала.",
        "",
        "## Сводка",
        "",
        f"- Запуск: `{payload['run_id']}`.",
        f"- Диапазон: `{payload['date_range']['start_day']}` .. `{payload['date_range']['end_day']}`.",
        f"- Дней обработано: `{payload['summary']['days_processed']}`.",
        f"- Кандидатов всего: `{payload['summary']['records_total']}`.",
        f"- GOOD всего: `{payload['summary']['good_total']}`.",
        f"- BAD всего: `{payload['summary']['bad_total']}`.",
        "",
        "## По дням",
        "",
        "| day | candidates | good | bad | same day | carried | timeout | strong | normal | soft |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in payload["daily_summary"]:
        lines.append(
            f"| {item['day_utc']} | {item['candidates']} | {item['good']} | {item['bad']} | {item.get('good_same_day', 0)} | {item.get('good_carried_overnight', 0)} | {item.get('bad_timeout', 0)} | {item['good_strong']} | {item['good_normal']} | {item['good_soft']} |"
        )
    lines.extend(
        [
            "",
            "## Артефакты",
            "",
        ]
    )
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
            "- Это не ML/export/training/promotion.",
            "- Это не Optuna, не scorer и не target-lock.",
            "- Следующий шаг после просмотра PNG: пользователь руками подтверждает/отклоняет хорошие входы, потом только собираем датасет-кандидат.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_pool(
    *,
    start_day: str,
    end_day: str,
    symbol: str,
    timeframe: str,
    out_dir: Path,
    run_label: str,
    min_score: float,
    cooldown_minutes: int,
    anchor_lookback: int,
    max_anchor_age: int,
    target_pct: float,
    outcome_lookahead_hours: float,
    render_good_limit: int,
    render_day_overview: bool,
) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    if not out_dir.is_absolute():
        out_dir = root / out_dir

    run_id = f"{run_label}_{_run_stamp()}" if run_label else f"run_{_run_stamp()}"
    run_dir = out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict[str, Any]] = []
    frames_by_day: dict[str, pd.DataFrame] = {}
    outcome_frames_by_day: dict[str, pd.DataFrame] = {}
    daily_summary: list[dict[str, Any]] = []
    day_overviews: list[Path] = []
    day_overview_by_day: dict[str, Path] = {}
    missing_sources: list[str] = []
    missing_outcome_sources: list[str] = []
    outcome_tail_days = _tail_days_for_hours(outcome_lookahead_hours)

    for day in _iter_days(start_day, end_day):
        source = _source_csv(root, day, timeframe, symbol)
        if not source.exists():
            missing_sources.append(_rel(root, source))
            continue

        df = _add_features(_load_ohlcv(source))
        frames_by_day[day] = df
        outcome_parts = [df]
        if outcome_tail_days > 0:
            tail_start = (pd.Timestamp(day) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
            tail_end = (pd.Timestamp(day) + pd.Timedelta(days=outcome_tail_days)).strftime("%Y-%m-%d")
            for tail_day in _iter_days(tail_start, tail_end):
                tail_source = _source_csv(root, tail_day, timeframe, symbol)
                if not tail_source.exists():
                    missing_outcome_sources.append(_rel(root, tail_source))
                    continue
                outcome_parts.append(_load_ohlcv(tail_source))
        outcome_df = pd.concat(outcome_parts, ignore_index=True)
        outcome_frames_by_day[day] = outcome_df
        candidates = build_candidates(
            df,
            targets=[],
            anchor_lookback=anchor_lookback,
            max_anchor_age=max_anchor_age,
            cooldown_minutes=cooldown_minutes,
            min_score=min_score,
            slippage_bps=5.0,
        )
        rows = _label_candidates(
            outcome_df,
            candidates,
            target_pct=target_pct,
            outcome_lookahead_hours=outcome_lookahead_hours,
        )
        for row in rows:
            row["run_id"] = run_id
            row["day_utc"] = day
            row["source_csv"] = _rel(root, source)
            row["record_id"] = _record_id(day, str(row["candidate_id"]))
            row["target_rule"] = "entry_open_plus_5bps_then_plus_1pct"
            row["ml_status"] = "not_ml_label_review_only"
        all_rows.extend(rows)

        counts = Counter(str(row["review_label"]) for row in rows)
        outcome_counts = Counter(str(row.get("outcome_status") or "") for row in rows)
        good = sum(1 for row in rows if _is_good(row))
        daily_summary.append(
            {
                "day_utc": day,
                "candidates": len(rows),
                "good": good,
                "bad": len(rows) - good,
                "good_strong": counts.get("GOOD_STRONG_HIT_1PCT_AT_10BPS", 0),
                "good_normal": counts.get("GOOD_NORMAL_HIT_1PCT_AT_5BPS", 0),
                "good_soft": counts.get("GOOD_SOFT_HIT_1PCT_AT_0BPS", 0),
                "good_same_day": outcome_counts.get("GOOD_SAME_DAY", 0),
                "good_carried_overnight": outcome_counts.get("GOOD_CARRIED_OVERNIGHT", 0),
                "bad_timeout": outcome_counts.get("BAD_TIMEOUT_NO_TARGET_IN_WINDOW", 0),
                "bad_no_day_target": outcome_counts.get("BAD_NO_TARGET_IN_DAY_WINDOW", 0),
            }
        )

        if render_day_overview:
            day_png = run_dir / f"GOOD_1PCT_REVIEW_POOL_DAY_OVERVIEW_{day.replace('-', '')}.png"
            _render_day_overview(df=df, rows=rows, day=day, symbol=symbol, timeframe=timeframe, out_path=day_png)
            day_overviews.append(day_png)
            day_overview_by_day[day] = day_png

    csv_path = run_dir / "GOOD_1PCT_REVIEW_POOL_RECORDS.csv"
    json_path = run_dir / "GOOD_1PCT_REVIEW_POOL_PAYLOAD.json"
    report_path = run_dir / "GOOD_1PCT_REVIEW_POOL_REPORT_RU.md"
    good_closeups = _render_good_closeup_pages(
        frames_by_day=outcome_frames_by_day,
        rows=all_rows,
        symbol=symbol,
        timeframe=timeframe,
        out_dir=run_dir,
        render_limit=render_good_limit,
    )
    all_closeups = _render_all_closeup_pages(
        frames_by_day=outcome_frames_by_day,
        rows=all_rows,
        symbol=symbol,
        timeframe=timeframe,
        out_dir=run_dir,
        render_limit=render_good_limit,
    )
    browse_payload = _build_browse_by_day(
        run_dir=run_dir,
        frames_by_day=outcome_frames_by_day,
        rows=all_rows,
        daily_summary=daily_summary,
        day_overview_by_day=day_overview_by_day,
        symbol=symbol,
        timeframe=timeframe,
        render_limit=render_good_limit,
    )
    _write_csv(csv_path, all_rows)

    good_total = sum(1 for row in all_rows if _is_good(row))
    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "run_id": run_id,
        "date_range": {"start_day": start_day, "end_day": end_day},
        "symbol": symbol,
        "timeframe": timeframe,
        "params": {
            "min_score": min_score,
            "cooldown_minutes": cooldown_minutes,
            "anchor_lookback": anchor_lookback,
            "max_anchor_age": max_anchor_age,
            "target_pct_from_execution_entry": target_pct,
            "outcome_lookahead_hours": outcome_lookahead_hours,
            "outcome_tail_days_loaded": outcome_tail_days,
            "execution_band_bps": SLIPPAGE_BANDS_BPS,
            "render_good_limit": render_good_limit,
            "render_day_overview": render_day_overview,
        },
        "summary": {
            "days_requested": len(_iter_days(start_day, end_day)),
            "days_processed": len(frames_by_day),
            "records_total": len(all_rows),
            "good_total": good_total,
            "bad_total": len(all_rows) - good_total,
            "missing_sources": len(missing_sources),
            "missing_outcome_sources": len(missing_outcome_sources),
        },
        "daily_summary": daily_summary,
        "records": all_rows,
        "missing_sources": missing_sources,
        "missing_outcome_sources": missing_outcome_sources,
        "artifacts": {
            "run_dir": _rel(root, run_dir),
            "csv": _rel(root, csv_path),
            "json": _rel(root, json_path),
            "report_ru": _rel(root, report_path),
            "day_overviews": [_rel(root, path) for path in day_overviews],
            "good_closeups": [_rel(root, path) for path in good_closeups],
            "all_closeups": [_rel(root, path) for path in all_closeups],
            "browse_dir": _rel(root, browse_payload["browse_dir"]),
            "browse_index_png": _rel(root, browse_payload["index_png"]),
            "browse_index_md": _rel(root, browse_payload["index_md"]),
            "browse_days": [
                {
                    "day_utc": item["day_utc"],
                    "folder": _rel(root, item["folder"]),
                    "overview": _rel(root, item["overview"]) if item["overview"] else "",
                    "all_closeups": [_rel(root, path) for path in item["all_closeups"]],
                    "records_csv": _rel(root, item["records_csv"]),
                    "candidates": item["candidates"],
                    "good": item["good"],
                    "bad": item["bad"],
                }
                for item in browse_payload["days"]
            ],
        },
        "guardrails": [
            "NO_ML_EXPORT_TRAINING",
            "NO_OPTUNA",
            "NO_SCORER",
            "NO_TARGET_LOCK",
            "FUTURE_OUTCOME_LABEL_ONLY_NOT_FEATURE",
        ],
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    _write_report(report_path, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-day", required=True)
    parser.add_argument("--end-day", required=True)
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/fresh_target_led/good_1pct_review_pool")
    parser.add_argument("--run-label", default="")
    parser.add_argument("--min-score", type=float, default=2.5)
    parser.add_argument("--cooldown-minutes", type=int, default=4)
    parser.add_argument("--anchor-lookback", type=int, default=12)
    parser.add_argument("--max-anchor-age", type=int, default=3)
    parser.add_argument("--target-pct", type=float, default=1.0)
    parser.add_argument("--outcome-lookahead-hours", type=float, default=0.0)
    parser.add_argument("--render-good-limit", type=int, default=80)
    parser.add_argument("--no-day-overview", action="store_true")
    args = parser.parse_args()

    payload = run_pool(
        start_day=args.start_day,
        end_day=args.end_day,
        symbol=args.symbol,
        timeframe=args.timeframe,
        out_dir=Path(args.out_dir),
        run_label=args.run_label,
        min_score=args.min_score,
        cooldown_minutes=args.cooldown_minutes,
        anchor_lookback=args.anchor_lookback,
        max_anchor_age=args.max_anchor_age,
        target_pct=args.target_pct,
        outcome_lookahead_hours=args.outcome_lookahead_hours,
        render_good_limit=args.render_good_limit,
        render_day_overview=not args.no_day_overview,
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "run_id": payload["run_id"],
                "summary": payload["summary"],
                "artifacts": payload["artifacts"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
