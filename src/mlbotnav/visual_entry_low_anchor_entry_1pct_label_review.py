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


STATUS = "LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA"
SLIPPAGE_BANDS_BPS = [0.0, 5.0, 10.0]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def _first_hit(
    df: pd.DataFrame,
    *,
    entry_idx: int,
    target_price: float,
    outcome_end_time: pd.Timestamp | None = None,
) -> tuple[bool, str, str, float, float]:
    future = df.iloc[entry_idx + 1 :].copy()
    if outcome_end_time is not None and not future.empty:
        future = future[future["open_time_utc"] <= outcome_end_time]
    max_high = float(future["high"].max()) if not future.empty else float("nan")
    hit_rows = future[future["high"] >= target_price]
    if hit_rows.empty:
        return False, "", "", max_high, float("nan")
    first = hit_rows.iloc[0]
    bars_to_hit = int(int(first.name) - entry_idx)
    return True, _fmt_ts(pd.Timestamp(first["open_time_utc"])), str(bars_to_hit), max_high, float(first["high"])


def _label_candidates(
    df: pd.DataFrame,
    candidates: list[dict[str, Any]],
    *,
    target_pct: float,
    outcome_lookahead_hours: float | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in candidates:
        entry_idx = int(item["entry_idx"])
        entry_open = float(item["entry_open_price"])
        entry_time = pd.Timestamp(item["entry_time_utc"])
        if entry_time.tzinfo is None:
            entry_time = entry_time.tz_localize("UTC")
        outcome_end_time = None
        if outcome_lookahead_hours and outcome_lookahead_hours > 0:
            outcome_end_time = entry_time + pd.Timedelta(hours=float(outcome_lookahead_hours))
        execution: dict[str, dict[str, Any]] = {}
        hits: dict[float, bool] = {}
        for bps in SLIPPAGE_BANDS_BPS:
            entry_price = entry_open * (1.0 + bps / 10000.0)
            target_price = entry_price * (1.0 + target_pct / 100.0)
            hit, hit_time, bars_to_hit, max_high, hit_high = _first_hit(
                df,
                entry_idx=entry_idx,
                target_price=target_price,
                outcome_end_time=outcome_end_time,
            )
            hits[bps] = hit
            execution[f"{bps:g}bps"] = {
                "entry_price": entry_price,
                "target_1pct_price": target_price,
                "hit_1pct": hit,
                "hit_time_utc": hit_time,
                "bars_to_hit": bars_to_hit,
                "max_high_after_entry": max_high,
                "hit_high": hit_high,
            }

        if hits[10.0]:
            review_label = "GOOD_STRONG_HIT_1PCT_AT_10BPS"
        elif hits[5.0]:
            review_label = "GOOD_NORMAL_HIT_1PCT_AT_5BPS"
        elif hits[0.0]:
            review_label = "GOOD_SOFT_HIT_1PCT_AT_0BPS"
        else:
            review_label = "BAD_NO_1PCT_EVEN_0BPS"

        main_hit_time = execution["5bps"]["hit_time_utc"] or execution["0bps"]["hit_time_utc"] or execution["10bps"]["hit_time_utc"]
        hit_day_utc = ""
        hold_minutes_to_target = ""
        carried_overnight = False
        if main_hit_time:
            hit_ts = pd.Timestamp(main_hit_time)
            if hit_ts.tzinfo is None:
                hit_ts = hit_ts.tz_localize("UTC")
            hit_day_utc = hit_ts.strftime("%Y-%m-%d")
            hold_minutes_to_target = str(int((hit_ts - entry_time).total_seconds() // 60))
            carried_overnight = hit_day_utc != entry_time.strftime("%Y-%m-%d")

        if review_label.startswith("GOOD") and carried_overnight:
            outcome_status = "GOOD_CARRIED_OVERNIGHT"
        elif review_label.startswith("GOOD"):
            outcome_status = "GOOD_SAME_DAY"
        elif outcome_lookahead_hours and outcome_lookahead_hours > 0:
            outcome_status = "BAD_TIMEOUT_NO_TARGET_IN_WINDOW"
        else:
            outcome_status = "BAD_NO_TARGET_IN_DAY_WINDOW"

        rows.append(
            {
                **item,
                "target_pct": float(target_pct),
                "outcome_lookahead_hours": float(outcome_lookahead_hours or 0.0),
                "outcome_check_end_time_utc": _fmt_ts(outcome_end_time) if outcome_end_time is not None else "",
                "entry_price_0bps": execution["0bps"]["entry_price"],
                "target_1pct_0bps": execution["0bps"]["target_1pct_price"],
                "hit_1pct_0bps": execution["0bps"]["hit_1pct"],
                "hit_time_0bps": execution["0bps"]["hit_time_utc"],
                "entry_price_5bps": execution["5bps"]["entry_price"],
                "target_1pct_5bps": execution["5bps"]["target_1pct_price"],
                "hit_1pct_5bps": execution["5bps"]["hit_1pct"],
                "hit_time_5bps": execution["5bps"]["hit_time_utc"],
                "entry_price_10bps": execution["10bps"]["entry_price"],
                "target_1pct_10bps": execution["10bps"]["target_1pct_price"],
                "hit_1pct_10bps": execution["10bps"]["hit_1pct"],
                "hit_time_10bps": execution["10bps"]["hit_time_utc"],
                "review_label": review_label,
                "hit_day_utc": hit_day_utc,
                "hold_minutes_to_target": hold_minutes_to_target,
                "carried_overnight": carried_overnight,
                "outcome_status": outcome_status,
                "execution_band": execution,
                "outcome_usage": "offline_label_only_not_feature_not_scorer",
            }
        )
    return rows


def _label_color(label: str) -> str:
    if label.startswith("GOOD_STRONG"):
        return "#00e676"
    if label.startswith("GOOD_NORMAL"):
        return "#64dd17"
    if label.startswith("GOOD_SOFT"):
        return "#ffd54f"
    return "#ff5252"


def _label_short(label: str) -> str:
    if label.startswith("GOOD_STRONG"):
        return "STRONG"
    if label.startswith("GOOD_NORMAL"):
        return "NORMAL"
    if label.startswith("GOOD_SOFT"):
        return "SOFT"
    return "BAD"


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
        "entry_price_0bps",
        "target_1pct_0bps",
        "hit_1pct_0bps",
        "hit_time_0bps",
        "entry_price_5bps",
        "target_1pct_5bps",
        "hit_1pct_5bps",
        "hit_time_5bps",
        "entry_price_10bps",
        "target_1pct_10bps",
        "hit_1pct_10bps",
        "hit_time_10bps",
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
        entry_price = float(row["entry_price_5bps"])
        target_price = float(row["target_1pct_5bps"])
        label = str(row["review_label"])
        color = _label_color(label)
        is_good = not label.startswith("BAD")
        hit_time_raw = str(row["hit_time_5bps"] or row["hit_time_0bps"] or "")
        line_end = pd.Timestamp(hit_time_raw).tz_convert(None) if hit_time_raw else eod

        ax_price.axvline(entry_time, color=color, alpha=0.11 if is_good else 0.05, linewidth=0.85)
        ax_price.plot([entry_time, line_end], [target_price, target_price], color=color, alpha=0.36 if is_good else 0.13, linewidth=0.9)
        ax_price.scatter([anchor_time], [anchor_low], s=25 if is_good else 14, color="#ff5252", edgecolors="#0b0f12", linewidths=0.35, alpha=0.78, zorder=6)
        ax_price.scatter([entry_time], [entry_price], marker="^", s=64 if is_good else 28, color=color, edgecolors="white", linewidths=0.35, alpha=0.86, zorder=7)
        if is_good and hit_time_raw:
            ax_price.scatter([line_end], [target_price], marker="*", s=90, color="#ffd54f", edgecolors="#0b0f12", linewidths=0.4, zorder=8)
            ax_price.annotate(
                f"{row['candidate_id']} {_label_short(label)}",
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
        f"{symbol} {timeframe} {day} | LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1 | entry next open, 0/5/10bps band | NO ML/OPTUNA",
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
            entry_0 = float(row["entry_price_0bps"])
            entry_5 = float(row["entry_price_5bps"])
            entry_10 = float(row["entry_price_10bps"])
            target_5 = float(row["target_1pct_5bps"])
            label = str(row["review_label"])
            color = _label_color(label)
            is_good = not label.startswith("BAD")
            hit_time_raw = str(row["hit_time_5bps"] or row["hit_time_0bps"] or "")
            line_end = (
                pd.Timestamp(hit_time_raw).tz_convert(None)
                if hit_time_raw
                else min((entry_time + pd.Timedelta(minutes=42)).tz_convert(None), pd.Timestamp(f"{day} 23:59:00"))
            )

            ax.axvline(entry_naive, color=color, linewidth=1.0, alpha=0.65)
            ax.plot([entry_naive, line_end], [target_5, target_5], color=color, alpha=0.52 if is_good else 0.22, linewidth=1.1)
            ax.scatter([anchor_time], [anchor_low], s=70, color="#ff5252", edgecolors="#0b0f12", zorder=5)
            ax.scatter([entry_naive], [entry_5], marker="^", s=112, color=color, edgecolors="white", linewidths=0.45, zorder=7)
            ax.vlines(entry_naive, entry_0, entry_10, color="#ffffff", linewidth=2.0, alpha=0.72, zorder=6)
            if is_good and hit_time_raw:
                ax.scatter([line_end], [target_5], marker="*", s=130, color="#ffd54f", edgecolors="#0b0f12", zorder=8)
            ax.annotate(
                f"signal low {_fmt_minute(pd.Timestamp(row['signal_time_utc']))}\nentry {_fmt_minute(entry_time)} +5bps {entry_5:.4f}\n+1% {target_5:.4f}",
                xy=(entry_naive, entry_5),
                xytext=(6, 10),
                textcoords="offset points",
                color=color,
                fontsize=8,
                arrowprops={"arrowstyle": "->", "color": color, "linewidth": 1.0},
            )
            ax.set_title(f"{row['candidate_id']} {_label_short(label)} | {row['suggested_type']} | score {float(row['score']):.2f}", color="white", fontsize=9)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            ax.tick_params(axis="x", labelrotation=25)
        for ax in flat[len(page_rows) :]:
            ax.axis("off")
            ax.set_facecolor("#101418")
        page_no = page_idx // per_page + 1
        fig.suptitle(
            f"{symbol} {timeframe} {day} | LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1 zoom page {page_no} | 0/5/10bps execution band",
            color="white",
            fontsize=15,
        )
        fig.tight_layout(rect=[0, 0, 1, 0.975])
        out_path = out_dir / f"LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_ZOOM_PAGE_{page_no:02d}_{day.replace('-', '')}.png"
        fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor())
        plt.close(fig)
        paths.append(out_path)
    return paths


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Low Anchor Entry 1pct Label Review V1",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Правило: значимый low = signal, вход = open следующей свечи. Для обучения/аудита считаются три execution-цены: `0bps`, `5bps`, `10bps`.",
        "",
        "## Сводка",
        "",
        f"- День: `{payload['day_utc']}`.",
        f"- Кандидатов: `{payload['summary']['candidates']}`.",
        f"- GOOD_STRONG hit `+1%` даже при `10bps`: `{payload['summary']['good_strong_10bps']}`.",
        f"- GOOD_NORMAL hit `+1%` при `5bps`: `{payload['summary']['good_normal_5bps']}`.",
        f"- GOOD_SOFT hit `+1%` только при `0bps`: `{payload['summary']['good_soft_0bps']}`.",
        f"- BAD нет `+1%` даже при `0bps`: `{payload['summary']['bad_no_1pct']}`.",
        "",
        "## Границы",
        "",
        "- Это не ML, не export, не scorer, не target-lock и не Optuna.",
        "- Future hit/no-hit используется только как outcome label после найденного low-кандидата.",
        "- Для будущего ML causal features должны заканчиваться на signal-свече; execution/outcome поля хранить отдельно.",
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
        slippage_bps=5.0,
    )
    rows = _label_candidates(df, candidates, target_pct=target_pct)

    day_compact = day.replace("-", "")
    csv_path = out_dir / f"LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1_{day_compact}.csv"
    json_path = out_dir / f"LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1_{day_compact}.json"
    report_path = out_dir / f"LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1_{day_compact}_RU.md"
    full_day_png = out_dir / f"LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_FULL_DAY_{day_compact}.png"

    _write_csv(csv_path, rows)
    _render_full_day(df=df, rows=rows, day=day, symbol=symbol, timeframe=timeframe, out_path=full_day_png)
    zoom_paths = _render_zoom_pages(df=df, rows=rows, day=day, symbol=symbol, timeframe=timeframe, out_dir=out_dir)

    summary = {
        "candidates": len(rows),
        "good_strong_10bps": sum(1 for row in rows if str(row["review_label"]).startswith("GOOD_STRONG")),
        "good_normal_5bps": sum(1 for row in rows if str(row["review_label"]).startswith("GOOD_NORMAL")),
        "good_soft_0bps": sum(1 for row in rows if str(row["review_label"]).startswith("GOOD_SOFT")),
        "bad_no_1pct": sum(1 for row in rows if str(row["review_label"]).startswith("BAD")),
    }
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
            "target_pct_from_execution_entry": target_pct,
            "execution_band_bps": SLIPPAGE_BANDS_BPS,
        },
        "summary": summary,
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
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_1pct_label_review_v1")
    parser.add_argument("--min-score", type=float, default=2.5)
    parser.add_argument("--cooldown-minutes", type=int, default=4)
    parser.add_argument("--anchor-lookback", type=int, default=12)
    parser.add_argument("--max-anchor-age", type=int, default=3)
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
        target_pct=args.target_pct,
    )
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "artifacts": payload["artifacts"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
