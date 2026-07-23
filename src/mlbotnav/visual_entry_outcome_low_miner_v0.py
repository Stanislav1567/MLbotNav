from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from mlbotnav.visual_entry_low_anchor_suggester import (
    ManualTarget,
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


STATUS = "OUTCOME_LOW_MINER_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA_NO_SCORER"
RAIL_POINT = "OUTCOME_MINER_TEST_DOES_NOT_BREAK_PASSPORT_CHAIN"
DEFAULT_DAYS = ["2026-05-14", "2026-05-15"]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _manual_targets_20260514(root: Path) -> list[ManualTarget]:
    path = root / "reports/final_review/visual_entry_v3/fresh_target_led/user_marked_development_order/user_marked_development_order_20260514.json"
    if not path.exists():
        return []
    payload = _read_json(path)
    out: list[ManualTarget] = []
    for item in payload.get("items", []):
        if str(item.get("status")) != "gold_user_visual_confirmed":
            continue
        signal = item.get("inferred_signal_time_utc")
        entry = item.get("inferred_entry_time_utc")
        if not signal or not entry:
            continue
        out.append(
            ManualTarget(
                target_id=str(item["order_id"]),
                signal_time=pd.Timestamp(signal).tz_convert("UTC"),
                entry_time=pd.Timestamp(entry).tz_convert("UTC"),
                target_type=str(item.get("suggested_type") or item.get("target_type") or "USER_MARKED_ENTRY"),
            )
        )
    return out


def _manual_targets_20260515(root: Path) -> list[ManualTarget]:
    path = (
        root
        / "reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/"
        "priority_zoom_review_v0/user_verdict_v1/T15_USER_VERDICT_V1_20260701.csv"
    )
    if not path.exists():
        return []
    rows = pd.read_csv(path)
    out: list[ManualTarget] = []
    for _, row in rows.iterrows():
        if str(row.get("user_verdict")) != "entry":
            continue
        out.append(
            ManualTarget(
                target_id=str(row["candidate_id"]),
                signal_time=pd.Timestamp(row["signal_time_utc"]).tz_convert("UTC"),
                entry_time=pd.Timestamp(row["entry_time_utc"]).tz_convert("UTC"),
                target_type=str(row.get("transfer_type") or "USER_MARKED_ENTRY"),
            )
        )
    return out


def _targets_for_day(root: Path, day: str) -> list[ManualTarget]:
    if day == "2026-05-14":
        return _manual_targets_20260514(root)
    if day == "2026-05-15":
        return _manual_targets_20260515(root)
    return []


def _outcome_for_candidate(
    df: pd.DataFrame,
    item: dict[str, Any],
    *,
    target_pct: float,
    lookahead_minutes: int,
) -> dict[str, Any]:
    entry_idx = int(item["entry_idx"])
    entry_price = float(item["entry_price_plus_5bps"])
    target_price = entry_price * (1.0 + target_pct / 100.0)
    end_idx = min(len(df), entry_idx + 1 + lookahead_minutes)
    future = df.iloc[entry_idx + 1 : end_idx].copy()
    hit_rows = future[future["high"] >= target_price]
    hit = not hit_rows.empty
    target_label = f"{str(float(target_pct)).replace('.', 'p')}pct"
    max_high = float(future["high"].max()) if not future.empty else float("nan")
    max_move_pct = ((max_high / entry_price) - 1.0) * 100.0 if entry_price else float("nan")
    out = {
        "outcome_label": f"hit_{target_label}" if hit else f"no_hit_{target_label}",
        "target_pct": float(target_pct),
        "target_price": target_price,
        "target_price_1p5": target_price,
        "hit_time_utc": "",
        "bars_to_hit": "",
        "max_future_high_in_window": max_high,
        "max_future_move_pct_in_window": max_move_pct,
        "lookahead_minutes": int(lookahead_minutes),
        "outcome_usage": "offline_label_only_not_feature_not_scorer",
    }
    if hit:
        first = hit_rows.iloc[0]
        hit_idx = int(first.name)
        out["hit_time_utc"] = _fmt_ts(pd.Timestamp(first["open_time_utc"]))
        out["bars_to_hit"] = int(hit_idx - entry_idx)
    return out


def _build_day_records(
    root: Path,
    *,
    day: str,
    symbol: str,
    timeframe: str,
    min_score: float,
    target_pct: float,
    lookahead_minutes: int,
    cooldown_minutes: int,
    slippage_bps: float,
    anchor_lookback: int,
    max_anchor_age: int,
) -> tuple[pd.DataFrame, list[dict[str, Any]], list[ManualTarget]]:
    source = _source_csv(root, day, timeframe, symbol)
    df = _add_features(_load_ohlcv(source))
    targets = _targets_for_day(root, day)
    candidates = build_candidates(
        df,
        targets=targets,
        anchor_lookback=anchor_lookback,
        max_anchor_age=max_anchor_age,
        cooldown_minutes=cooldown_minutes,
        min_score=min_score,
        slippage_bps=slippage_bps,
    )
    records: list[dict[str, Any]] = []
    for item in candidates:
        outcome = _outcome_for_candidate(df, item, target_pct=target_pct, lookahead_minutes=lookahead_minutes)
        records.append(
            {
                **item,
                **outcome,
                "day_utc": day,
                "symbol": symbol,
                "timeframe": timeframe,
                "source_csv": _rel(root, source),
                "record_status": "outcome_miner_candidate_needs_user_review",
            }
        )
    return df, records, targets


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = [
        "candidate_id",
        "day_utc",
        "outcome_label",
        "signal_time_utc",
        "entry_time_utc",
        "anchor_time_utc",
        "anchor_low_price",
        "entry_open_price",
        "entry_price_plus_5bps",
        "target_pct",
        "target_price",
        "target_price_1p5",
        "hit_time_utc",
        "bars_to_hit",
        "max_future_move_pct_in_window",
        "lookahead_minutes",
        "score",
        "suggested_type",
        "nearest_manual_target",
        "signal_diff_minutes_to_nearest_target",
        "matched_manual_target_within_3m",
        "record_status",
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
    records: list[dict[str, Any]],
    targets: list[ManualTarget],
    day: str,
    symbol: str,
    timeframe: str,
    out_path: Path,
) -> None:
    fig, (ax_price, ax_vol) = plt.subplots(2, 1, figsize=(30, 13), sharex=True, gridspec_kw={"height_ratios": [4.7, 1.15]})
    fig.patch.set_facecolor("#101418")
    _style_axis(ax_price)
    _style_axis(ax_vol)
    _draw_candles(ax_price, df, timeframe, linewidth=0.34)
    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(df["open"], df["close"])]
    ax_vol.bar(df["open_time_utc"].dt.tz_convert(None), df["volume"], width=_bar_width_days(timeframe), color=colors, alpha=0.70)

    for target in targets:
        ax_price.axvline(target.signal_time.tz_convert(None), color="#ffca28", alpha=0.18, linewidth=0.9)
        ax_price.text(target.entry_time.tz_convert(None), ax_price.get_ylim()[0], target.target_id, color="#ffca28", fontsize=7, rotation=90, va="bottom")

    for row in records:
        target_pct = float(row.get("target_pct") or 1.5)
        signal = pd.Timestamp(row["signal_time_utc"]).tz_convert(None)
        entry = pd.Timestamp(row["entry_time_utc"]).tz_convert(None)
        anchor = pd.Timestamp(row["anchor_time_utc"]).tz_convert(None)
        entry_price = float(row["entry_price_plus_5bps"])
        anchor_low = float(row["anchor_low_price"])
        target_price = float(row.get("target_price") or row["target_price_1p5"])
        hit = str(row["outcome_label"]).startswith("hit_")
        color = "#00e676" if hit else "#78909c"
        alpha = 0.85 if hit else 0.32
        ax_price.axvline(signal, color=color, alpha=0.20 if hit else 0.08, linewidth=1.0)
        ax_price.scatter([anchor], [anchor_low], s=34 if hit else 16, color="#ff5252", edgecolors="#0b0f12", linewidths=0.4, alpha=alpha, zorder=6)
        ax_price.scatter([entry], [entry_price], marker="^", s=80 if hit else 34, color=color, edgecolors="white", linewidths=0.45, alpha=alpha, zorder=7)
        line_end = pd.Timestamp(row["hit_time_utc"]).tz_convert(None) if hit else entry + pd.Timedelta(minutes=int(row["lookahead_minutes"]))
        ax_price.plot([entry, line_end], [target_price, target_price], color=color, alpha=0.38 if hit else 0.14, linewidth=1.0)
        if hit:
            ax_price.scatter([line_end], [target_price], marker="*", s=110, color="#ffd54f", edgecolors="#0b0f12", linewidths=0.45, zorder=8)
            ax_price.annotate(
                f"{row['candidate_id']} +{target_pct:g}% {_fmt_minute(pd.Timestamp(row['hit_time_utc']))}",
                xy=(entry, entry_price),
                xytext=(5, 10),
                textcoords="offset points",
                color=color,
                fontsize=8,
                arrowprops={"arrowstyle": "->", "color": color, "linewidth": 0.8},
            )

    start = pd.Timestamp(f"{day}T00:00:00")
    ax_price.set_xlim(start.to_pydatetime(), (start + pd.Timedelta(days=1)).to_pydatetime())
    ax_price.set_title(
        f"{symbol} {timeframe} {day} | OUTCOME_LOW_MINER_V0 | green=hit target within 6h | gray=no hit | NO ML/OPTUNA",
        color="white",
        fontsize=15,
    )
    ax_price.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    ax_vol.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 3)))
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path, dpi=170, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def _render_hit_zoom_sheet(
    *,
    frames_by_day: dict[str, pd.DataFrame],
    hit_records: list[dict[str, Any]],
    symbol: str,
    timeframe: str,
    out_path: Path,
) -> None:
    rows = max(1, len(hit_records))
    fig, axes = plt.subplots(rows, 1, figsize=(24, max(5.2, rows * 4.4)), sharex=False)
    fig.patch.set_facecolor("#101418")
    if rows == 1:
        axes = [axes]
    for ax, row in zip(axes, hit_records):
        target_pct = float(row.get("target_pct") or 1.5)
        _style_axis(ax)
        df = frames_by_day[str(row["day_utc"])]
        signal = pd.Timestamp(row["signal_time_utc"])
        entry = pd.Timestamp(row["entry_time_utc"])
        hit_time = pd.Timestamp(row["hit_time_utc"])
        start = signal - pd.Timedelta(minutes=35)
        end = hit_time + pd.Timedelta(minutes=35)
        win = df[(df["open_time_utc"] >= start) & (df["open_time_utc"] <= end)].reset_index(drop=True)
        _draw_candles(ax, win, timeframe, linewidth=0.55)
        signal_x = signal.tz_convert(None)
        entry_x = entry.tz_convert(None)
        hit_x = hit_time.tz_convert(None)
        entry_price = float(row["entry_price_plus_5bps"])
        target_price = float(row.get("target_price") or row["target_price_1p5"])
        anchor_time = pd.Timestamp(row["anchor_time_utc"]).tz_convert(None)
        anchor_low = float(row["anchor_low_price"])
        ax.axvline(signal_x, color="#00e676", linewidth=1.2, alpha=0.50)
        ax.axvline(entry_x, color="#00e676", linewidth=2.0, alpha=0.78)
        ax.scatter([anchor_time], [anchor_low], s=75, color="#ff5252", edgecolors="#0b0f12", linewidths=0.6, zorder=6)
        ax.scatter([entry_x], [entry_price], marker="^", s=130, color="#00e676", edgecolors="white", linewidths=0.7, zorder=7)
        ax.plot([entry_x, hit_x], [target_price, target_price], color="#ffd54f", linewidth=1.5, alpha=0.82)
        ax.scatter([hit_x], [target_price], marker="*", s=160, color="#ffd54f", edgecolors="#0b0f12", linewidths=0.6, zorder=8)
        ax.annotate(
            f"{row['candidate_id']} entry {_fmt_minute(entry)} p={entry_price:.4f}\\ntarget +{target_pct:g}% {target_price:.4f} hit {_fmt_minute(hit_time)}",
            xy=(entry_x, entry_price),
            xytext=(8, 14),
            textcoords="offset points",
            color="#00e676",
            fontsize=10,
            arrowprops={"arrowstyle": "->", "color": "#00e676", "linewidth": 1.0},
            bbox={"boxstyle": "round,pad=0.25", "facecolor": "#003d28", "edgecolor": "#00e676", "alpha": 0.88},
        )
        nearest = row.get("nearest_manual_target") or "-"
        ax.set_title(
            f"{row['day_utc']} {row['candidate_id']} | nearest manual {nearest} diff {row.get('signal_diff_minutes_to_nearest_target')}m | score {float(row['score']):.2f}",
            color="white",
            fontsize=11,
        )
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.tick_params(axis="x", labelrotation=20)
    fig.suptitle(f"{symbol} {timeframe} | OUTCOME_LOW_MINER_V0 hit zoom sheet | offline target outcome only", color="white", fontsize=15)
    fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.985])
    fig.savefig(out_path, dpi=165, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Outcome Low Miner V0",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: проверить идею пользователя без поломки паспортной цепочки: автоматически предложить значимые low, затем offline проверить, дошла ли цена от execution-entry до `+1.5%` на `1x`.",
        "",
        "Это не ML, не export, не scorer, не target-lock и не Optuna. Будущий `+1.5%` используется только как метка исхода для ручного review, а не как признак выбора входа.",
        "",
        "## Настройки V0",
        "",
        f"- Дни: `{', '.join(payload['days'])}`.",
        f"- Entry: `open` следующей свечи после сигнальной свечи + `{payload['slippage_bps']}` bps.",
        f"- Target: `entry_price_plus_5bps * (1 + {payload['target_pct']}%)`.",
        f"- Окно проверки исхода: `{payload['lookahead_minutes']}` минут после entry.",
        f"- Кандидат low строится по past-only low-anchor признакам из текущего visual-entry suggester; future target не участвует в выборе кандидата.",
        "",
        "## Счетчики",
        "",
        "| day | candidates | hit target | no hit | nearest manual within 3m |",
        "|---|---:|---:|---:|---:|",
    ]
    for item in payload["day_summary"]:
        lines.append(
            f"| `{item['day_utc']}` | `{item['candidates']}` | `{item['hit_target_pct']}` | `{item['no_hit_target_pct']}` | `{item['nearest_manual_within_3m']}` |"
        )
    lines.extend(
        [
            "",
            "## Как читать",
            "",
            "Зеленая точка на PNG означает только одно: этот auto-low candidate после entry дал заданный target-процент в заданном окне. Это еще не значит, что вход красивый или годится для паспорта.",
            "",
            "Серые точки не достигли target-процента в окне. Их можно использовать как negative outcome examples только после отдельного ручного решения.",
            "",
            "## Что видно сразу",
            "",
            payload["quick_read"],
            "",
            "## Артефакты",
            "",
        ]
    )
    for value in payload["artifacts"].values():
        lines.append(f"- `{value}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(
    *,
    out_dir: Path,
    days: list[str],
    symbol: str,
    timeframe: str,
    min_score: float,
    target_pct: float,
    lookahead_minutes: int,
    cooldown_minutes: int,
    slippage_bps: float,
    anchor_lookback: int,
    max_anchor_age: int,
) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    all_records: list[dict[str, Any]] = []
    frames_by_day: dict[str, pd.DataFrame] = {}
    targets_by_day: dict[str, list[ManualTarget]] = {}
    day_summary: list[dict[str, Any]] = []

    for day in days:
        df, records, targets = _build_day_records(
            root,
            day=day,
            symbol=symbol,
            timeframe=timeframe,
            min_score=min_score,
            target_pct=target_pct,
            lookahead_minutes=lookahead_minutes,
            cooldown_minutes=cooldown_minutes,
            slippage_bps=slippage_bps,
            anchor_lookback=anchor_lookback,
            max_anchor_age=max_anchor_age,
        )
        frames_by_day[day] = df
        targets_by_day[day] = targets
        for number, row in enumerate(records, 1):
            row["candidate_id"] = f"OL{day.replace('-', '')}_{number:03d}"
        all_records.extend(records)
        hit_count = sum(1 for row in records if str(row["outcome_label"]).startswith("hit_"))
        day_summary.append(
            {
                "day_utc": day,
                "candidates": len(records),
                "hit_target_pct": hit_count,
                "no_hit_target_pct": len(records) - hit_count,
                "nearest_manual_within_3m": sum(1 for row in records if bool(row.get("matched_manual_target_within_3m"))),
            }
        )

    csv_path = out_dir / "OUTCOME_LOW_MINER_V0_CANDIDATES_20260702.csv"
    json_path = out_dir / "OUTCOME_LOW_MINER_V0_20260702.json"
    report_path = out_dir / "OUTCOME_LOW_MINER_V0_20260702_RU.md"
    zoom_path = out_dir / "OUTCOME_LOW_MINER_V0_HIT_ZOOM_SHEET_20260702.png"
    _write_csv(csv_path, all_records)

    full_day_paths: dict[str, str] = {}
    for day in days:
        day_records = [row for row in all_records if row["day_utc"] == day]
        full_path = out_dir / f"OUTCOME_LOW_MINER_V0_FULL_DAY_{day.replace('-', '')}_20260702.png"
        _render_full_day(
            df=frames_by_day[day],
            records=day_records,
            targets=targets_by_day[day],
            day=day,
            symbol=symbol,
            timeframe=timeframe,
            out_path=full_path,
        )
        full_day_paths[day] = _rel(root, full_path)

    hit_records = [row for row in all_records if str(row["outcome_label"]).startswith("hit_")]
    hit_records = sorted(hit_records, key=lambda row: (str(row["day_utc"]), str(row["signal_time_utc"])))
    _render_hit_zoom_sheet(frames_by_day=frames_by_day, hit_records=hit_records, symbol=symbol, timeframe=timeframe, out_path=zoom_path)

    hit_day_paths: dict[str, str] = {}
    for day in days:
        day_hits = [row for row in hit_records if row["day_utc"] == day]
        if not day_hits:
            continue
        day_zoom_path = out_dir / f"OUTCOME_LOW_MINER_V0_HIT_ZOOM_{day.replace('-', '')}_20260702.png"
        _render_hit_zoom_sheet(frames_by_day=frames_by_day, hit_records=day_hits, symbol=symbol, timeframe=timeframe, out_path=day_zoom_path)
        hit_day_paths[day] = _rel(root, day_zoom_path)

    quick_read = (
        f"Порог `+{target_pct:g}%` отобрал только те low-кандидаты, которые дали заданный ход в пределах окна. "
        "Это хорошо как быстрый фильтр движения, но не заменяет ручную target-led проверку качества входа. "
        "После review можно сравнить этот прогон с соседними порогами и оставить outcome-label только как слой отбора кандидатов."
    )
    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "rail_point": RAIL_POINT,
        "symbol": symbol,
        "timeframe": timeframe,
        "days": days,
        "min_score": min_score,
        "target_pct": target_pct,
        "lookahead_minutes": lookahead_minutes,
        "cooldown_minutes": cooldown_minutes,
        "slippage_bps": slippage_bps,
        "anchor_lookback": anchor_lookback,
        "max_anchor_age": max_anchor_age,
        "day_summary": day_summary,
        "records": all_records,
        "manual_targets": {day: [asdict(item) for item in targets_by_day[day]] for day in days},
        "quick_read": quick_read,
        "artifacts": {
            "csv": _rel(root, csv_path),
            "json": _rel(root, json_path),
            "report_ru": _rel(root, report_path),
            "hit_zoom_sheet_png": _rel(root, zoom_path),
            **{f"full_day_{day}": path for day, path in full_day_paths.items()},
            **{f"hit_zoom_{day}": path for day, path in hit_day_paths.items()},
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
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0")
    parser.add_argument("--days", nargs="+", default=DEFAULT_DAYS)
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--min-score", type=float, default=4.0)
    parser.add_argument("--target-pct", type=float, default=1.5)
    parser.add_argument("--lookahead-minutes", type=int, default=360)
    parser.add_argument("--cooldown-minutes", type=int, default=30)
    parser.add_argument("--slippage-bps", type=float, default=5.0)
    parser.add_argument("--anchor-lookback", type=int, default=60)
    parser.add_argument("--max-anchor-age", type=int, default=6)
    args = parser.parse_args()
    payload = run(
        out_dir=Path(args.out_dir),
        days=list(args.days),
        symbol=args.symbol,
        timeframe=args.timeframe,
        min_score=args.min_score,
        target_pct=args.target_pct,
        lookahead_minutes=args.lookahead_minutes,
        cooldown_minutes=args.cooldown_minutes,
        slippage_bps=args.slippage_bps,
        anchor_lookback=args.anchor_lookback,
        max_anchor_age=args.max_anchor_age,
    )
    print(json.dumps({"status": payload["status"], "day_summary": payload["day_summary"], "artifacts": payload["artifacts"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
