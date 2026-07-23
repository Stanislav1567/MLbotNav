from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from mlbotnav.visual_entry_low_anchor_suggester import (
    _add_features,
    _bar_width_days,
    _draw_candles,
    _fmt_minute,
    _fmt_ts,
    _load_ohlcv,
    _source_csv,
    _style_axis,
    build_candidates,
)


STATUS = "LOW_ANCHOR_1PCT_LABEL_REVIEW_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def _label_candidates(
    df: pd.DataFrame,
    candidates: list[dict[str, Any]],
    *,
    target_pct: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in candidates:
        entry_idx = int(item["entry_idx"])
        anchor_low = float(item["anchor_low_price"])
        entry_price = float(item["entry_price_plus_5bps"])
        anchor_target_price = anchor_low * (1.0 + target_pct / 100.0)
        entry_target_price = entry_price * (1.0 + target_pct / 100.0)
        future = df.iloc[entry_idx + 1 :].copy()
        hit_rows = future[future["high"] >= anchor_target_price]
        hit = not hit_rows.empty
        hit_time = ""
        bars_to_hit = ""
        if hit:
            first = hit_rows.iloc[0]
            hit_time = _fmt_ts(pd.Timestamp(first["open_time_utc"]))
            bars_to_hit = int(int(first.name) - entry_idx)
        entry_already_above_anchor_target = entry_price >= anchor_target_price
        max_high_after_entry = float(future["high"].max()) if not future.empty else float("nan")
        rows.append(
            {
                **item,
                "target_pct": float(target_pct),
                "anchor_target_1pct_price": anchor_target_price,
                "entry_target_1pct_price": entry_target_price,
                "anchor_1pct_hit_after_entry": bool(hit),
                "anchor_1pct_hit_time_utc": hit_time,
                "anchor_1pct_bars_to_hit": bars_to_hit,
                "entry_already_above_anchor_target": bool(entry_already_above_anchor_target),
                "max_high_after_entry": max_high_after_entry,
                "max_move_from_anchor_low_pct_after_entry": ((max_high_after_entry / anchor_low) - 1.0) * 100.0
                if anchor_low
                else float("nan"),
                "review_label": "GOOD_ANCHOR_1PCT_POTENTIAL" if hit else "BAD_NO_ANCHOR_1PCT",
                "outcome_usage": "offline_label_only_not_feature_not_scorer",
            }
        )
    return rows


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = [
        "candidate_id",
        "review_label",
        "suggested_type",
        "score",
        "anchor_time_utc",
        "anchor_low_price",
        "signal_time_utc",
        "entry_time_utc",
        "entry_open_price",
        "entry_price_plus_5bps",
        "target_pct",
        "anchor_target_1pct_price",
        "entry_target_1pct_price",
        "anchor_1pct_hit_after_entry",
        "anchor_1pct_hit_time_utc",
        "anchor_1pct_bars_to_hit",
        "entry_already_above_anchor_target",
        "max_move_from_anchor_low_pct_after_entry",
        "outcome_usage",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def _render_full_day(
    *,
    df: pd.DataFrame,
    rows: list[dict[str, Any]],
    day: str,
    symbol: str,
    timeframe: str,
    out_path: Path,
) -> None:
    fig, (ax_price, ax_vol) = plt.subplots(2, 1, figsize=(32, 13), sharex=True, gridspec_kw={"height_ratios": [4.7, 1.15]})
    fig.patch.set_facecolor("#101418")
    _style_axis(ax_price)
    _style_axis(ax_vol)
    _draw_candles(ax_price, df, timeframe, linewidth=0.32)
    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(df["open"], df["close"])]
    ax_vol.bar(df["open_time_utc"].dt.tz_convert(None), df["volume"], width=_bar_width_days(timeframe), color=colors, alpha=0.70)

    eod = pd.Timestamp(f"{day} 23:59:00")
    for row in rows:
        anchor_time = pd.Timestamp(row["anchor_time_utc"]).tz_convert(None)
        entry_time = pd.Timestamp(row["entry_time_utc"]).tz_convert(None)
        anchor_low = float(row["anchor_low_price"])
        entry_price = float(row["entry_price_plus_5bps"])
        target_price = float(row["anchor_target_1pct_price"])
        hit = bool(row["anchor_1pct_hit_after_entry"])
        color = "#00e676" if hit else "#ff5252"
        alpha = 0.82 if hit else 0.36
        line_end = pd.Timestamp(row["anchor_1pct_hit_time_utc"]).tz_convert(None) if hit else eod

        ax_price.axvline(entry_time, color=color, alpha=0.12 if hit else 0.06, linewidth=0.85)
        ax_price.plot([anchor_time, anchor_time], [anchor_low, target_price], color=color, alpha=0.34, linewidth=0.9)
        ax_price.plot([anchor_time, line_end], [target_price, target_price], color=color, alpha=0.34 if hit else 0.16, linewidth=0.9)
        ax_price.scatter([anchor_time], [anchor_low], s=26 if hit else 15, color="#ff5252", edgecolors="#0b0f12", linewidths=0.35, alpha=alpha, zorder=6)
        ax_price.scatter([entry_time], [entry_price], marker="^", s=58 if hit else 30, color=color, edgecolors="white", linewidths=0.35, alpha=alpha, zorder=7)
        if hit:
            ax_price.scatter([line_end], [target_price], marker="*", s=95, color="#ffd54f", edgecolors="#0b0f12", linewidths=0.4, zorder=8)
            ax_price.annotate(
                f"{row['candidate_id']} +1%",
                xy=(entry_time, entry_price),
                xytext=(3, 7),
                textcoords="offset points",
                color=color,
                fontsize=6,
            )

    start = pd.Timestamp(f"{day} 00:00:00")
    end = start + pd.Timedelta(days=1)
    ax_price.set_xlim(start.to_pydatetime(), end.to_pydatetime())
    ax_price.set_title(
        f"{symbol} {timeframe} {day} | LOW_ANCHOR_1PCT_LABEL_REVIEW | green=hit +1% from low | red=no hit | NO ML/OPTUNA",
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


def _render_zoom_pages(
    *,
    df: pd.DataFrame,
    rows: list[dict[str, Any]],
    day: str,
    symbol: str,
    timeframe: str,
    out_dir: Path,
) -> list[Path]:
    paths: list[Path] = []
    per_page = 16
    for page_idx in range(0, len(rows), per_page):
        page_rows = rows[page_idx : page_idx + per_page]
        fig, axes = plt.subplots(4, 4, figsize=(24, 17), sharex=False)
        fig.patch.set_facecolor("#101418")
        flat = list(axes.flatten())
        for ax, row in zip(flat, page_rows):
            _style_axis(ax)
            entry_time = pd.Timestamp(row["entry_time_utc"])
            start = entry_time - pd.Timedelta(minutes=24)
            end = entry_time + pd.Timedelta(minutes=42)
            win = df[(df["open_time_utc"] >= start) & (df["open_time_utc"] <= end)].reset_index(drop=True)
            _draw_candles(ax, win, timeframe, linewidth=0.55)
            anchor_time = pd.Timestamp(row["anchor_time_utc"]).tz_convert(None)
            entry_naive = entry_time.tz_convert(None)
            anchor_low = float(row["anchor_low_price"])
            entry_price = float(row["entry_price_plus_5bps"])
            target_price = float(row["anchor_target_1pct_price"])
            hit = bool(row["anchor_1pct_hit_after_entry"])
            color = "#00e676" if hit else "#ff5252"
            line_end = (
                pd.Timestamp(row["anchor_1pct_hit_time_utc"]).tz_convert(None)
                if hit
                else min((entry_time + pd.Timedelta(minutes=42)).tz_convert(None), pd.Timestamp(f"{day} 23:59:00"))
            )
            ax.plot([anchor_time, anchor_time], [anchor_low, target_price], color=color, alpha=0.55, linewidth=1.1)
            ax.plot([anchor_time, line_end], [target_price, target_price], color=color, alpha=0.50, linewidth=1.1)
            ax.axvline(entry_naive, color=color, linewidth=1.0, alpha=0.65)
            ax.scatter([anchor_time], [anchor_low], s=70, color="#ff5252", edgecolors="#0b0f12", zorder=5)
            ax.scatter([entry_naive], [entry_price], marker="^", s=105, color=color, edgecolors="white", linewidths=0.45, zorder=6)
            if hit:
                ax.scatter([line_end], [target_price], marker="*", s=130, color="#ffd54f", edgecolors="#0b0f12", zorder=7)
            ax.annotate(
                f"entry {_fmt_minute(entry_time)}\nlow {anchor_low:.4f} -> +1% {target_price:.4f}",
                xy=(entry_naive, entry_price),
                xytext=(6, 10),
                textcoords="offset points",
                color=color,
                fontsize=8,
                arrowprops={"arrowstyle": "->", "color": color, "linewidth": 1.0},
            )
            label = "GOOD" if hit else "BAD"
            ax.set_title(f"{row['candidate_id']} {label} | {row['suggested_type']} | score {float(row['score']):.2f}", color="white", fontsize=9)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            ax.tick_params(axis="x", labelrotation=25)
        for ax in flat[len(page_rows) :]:
            ax.axis("off")
            ax.set_facecolor("#101418")
        page_no = page_idx // per_page + 1
        fig.suptitle(
            f"{symbol} {timeframe} {day} | LOW_ANCHOR_1PCT_LABEL_REVIEW zoom page {page_no} | green=GOOD red=BAD",
            color="white",
            fontsize=15,
        )
        fig.tight_layout(rect=[0, 0, 1, 0.975])
        out_path = out_dir / f"LOW_ANCHOR_1PCT_LABEL_REVIEW_ZOOM_PAGE_{page_no:02d}_{day.replace('-', '')}.png"
        fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor())
        plt.close(fig)
        paths.append(out_path)
    return paths


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Low Anchor 1pct Label Review V0",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: взять значимые low-anchor кандидаты по всему дню, протянуть от anchor-low цель `+1%`, затем пометить good/bad только как offline outcome label.",
        "",
        "## Сводка",
        "",
        f"- День: `{payload['day_utc']}`.",
        f"- Кандидатов: `{payload['summary']['candidates']}`.",
        f"- GOOD, дошли до `+1%` от low после entry: `{payload['summary']['good_anchor_1pct']}`.",
        f"- BAD, не дошли до `+1%` от low после entry: `{payload['summary']['bad_no_anchor_1pct']}`.",
        f"- Target: `anchor_low_price * 1.01`.",
        f"- Entry: `next open + {payload['params']['slippage_bps']} bps`.",
        "",
        "## Границы",
        "",
        "- Это не ML, не export, не scorer, не target-lock и не Optuna.",
        "- `anchor_1pct_hit_after_entry` является только label/audit после уже найденного low-кандидата.",
        "- Future outcome не используется для выбора low-кандидата.",
        "- Для будущего ML признаки брать только до `signal_time_utc`; outcome-поля держать отдельно как label.",
        "",
        "## Артефакты",
        "",
    ]
    for value in payload["artifacts"].values():
        if isinstance(value, list):
            for item in value:
                lines.append(f"- `{item}`")
        else:
            lines.append(f"- `{value}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(
    *,
    day: str,
    symbol: str,
    timeframe: str,
    out_dir: Path,
    min_score: float,
    cooldown_minutes: int,
    anchor_lookback: int,
    max_anchor_age: int,
    slippage_bps: float,
    target_pct: float,
) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    source = _source_csv(root, day, timeframe, symbol)
    df = _add_features(_load_ohlcv(source))
    candidates = build_candidates(
        df,
        targets=[],
        anchor_lookback=anchor_lookback,
        max_anchor_age=max_anchor_age,
        cooldown_minutes=cooldown_minutes,
        min_score=min_score,
        slippage_bps=slippage_bps,
    )
    rows = _label_candidates(df, candidates, target_pct=target_pct)

    day_compact = day.replace("-", "")
    csv_path = out_dir / f"LOW_ANCHOR_1PCT_LABEL_REVIEW_V0_{day_compact}.csv"
    json_path = out_dir / f"LOW_ANCHOR_1PCT_LABEL_REVIEW_V0_{day_compact}.json"
    report_path = out_dir / f"LOW_ANCHOR_1PCT_LABEL_REVIEW_V0_{day_compact}_RU.md"
    full_day_png = out_dir / f"LOW_ANCHOR_1PCT_LABEL_REVIEW_FULL_DAY_{day_compact}.png"

    _write_csv(csv_path, rows)
    _render_full_day(df=df, rows=rows, day=day, symbol=symbol, timeframe=timeframe, out_path=full_day_png)
    zoom_paths = _render_zoom_pages(df=df, rows=rows, day=day, symbol=symbol, timeframe=timeframe, out_dir=out_dir)

    good = sum(1 for row in rows if row["review_label"] == "GOOD_ANCHOR_1PCT_POTENTIAL")
    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "day_utc": day,
        "symbol": symbol,
        "timeframe": timeframe,
        "source_csv": _rel(root, source),
        "params": {
            "min_score": min_score,
            "cooldown_minutes": cooldown_minutes,
            "anchor_lookback": anchor_lookback,
            "max_anchor_age": max_anchor_age,
            "slippage_bps": slippage_bps,
            "target_pct_from_anchor_low": target_pct,
        },
        "summary": {
            "candidates": len(rows),
            "good_anchor_1pct": good,
            "bad_no_anchor_1pct": len(rows) - good,
        },
        "records": rows,
        "artifacts": {
            "csv": _rel(root, csv_path),
            "json": _rel(root, json_path),
            "report_ru": _rel(root, report_path),
            "full_day_png": _rel(root, full_day_png),
            "zoom_pages": [_rel(root, path) for path in zoom_paths],
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
    parser.add_argument("--day", default="2026-05-13")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_1pct_label_review_v0")
    parser.add_argument("--min-score", type=float, default=2.5)
    parser.add_argument("--cooldown-minutes", type=int, default=4)
    parser.add_argument("--anchor-lookback", type=int, default=12)
    parser.add_argument("--max-anchor-age", type=int, default=3)
    parser.add_argument("--slippage-bps", type=float, default=5.0)
    parser.add_argument("--target-pct", type=float, default=1.0)
    args = parser.parse_args()
    payload = run(
        day=args.day,
        symbol=args.symbol,
        timeframe=args.timeframe,
        out_dir=Path(args.out_dir),
        min_score=args.min_score,
        cooldown_minutes=args.cooldown_minutes,
        anchor_lookback=args.anchor_lookback,
        max_anchor_age=args.max_anchor_age,
        slippage_bps=args.slippage_bps,
        target_pct=args.target_pct,
    )
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "artifacts": payload["artifacts"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
