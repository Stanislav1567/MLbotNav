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

from mlbotnav.visual_entry_low_anchor_suggester import (
    _draw_candles,
    _load_ohlcv,
    _source_csv,
    _style_axis,
)


STATUS = "SIGNIFICANT_LOW_MANUAL_REANCHORS_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA"


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
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    return ts


def _naive(value: Any) -> pd.Timestamp:
    return _ts(value).tz_convert(None)


def _minute(value: Any) -> str:
    return _ts(value).strftime("%H:%M")


def _iso(value: Any) -> str:
    return _ts(value).strftime("%Y-%m-%dT%H:%M:%SZ")


def _row_at(df: pd.DataFrame, ts: pd.Timestamp) -> pd.Series:
    hits = df[df["open_time_utc"] == ts]
    if hits.empty:
        raise ValueError(f"Нет свечи {ts.isoformat()}")
    return hits.iloc[0]


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


def _load_config(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_and_enrich(
    *,
    df: pd.DataFrame,
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    slippage_bps = float(config.get("slippage_bps", 5))
    out: list[dict[str, Any]] = []
    for idx, entry in enumerate(config.get("entries", []), start=1):
        signal_time = _ts(entry["signal_time_utc"])
        entry_time = _ts(entry["entry_time_utc"])
        anchor_time = _ts(entry.get("anchor_time_utc") or entry["signal_time_utc"])
        visual_time = _ts(entry.get("visual_marker_time_utc") or entry["entry_time_utc"])
        signal = _row_at(df, signal_time)
        candle = _row_at(df, entry_time)
        anchor = _row_at(df, anchor_time)
        visual_marker_price = float(entry.get("visual_marker_price", candle["low"]))

        entry_open = float(candle["open"])
        entry_5bps = entry_open * (1.0 + slippage_bps / 10000.0)
        target_1pct = entry_5bps * 1.01

        next_open_expected = signal_time + pd.Timedelta(minutes=1)
        rule_note = "OK_NEXT_OPEN" if entry_time == next_open_expected else "MANUAL_EXECUTION_OVERRIDE"

        row = {
            "order": idx,
            "manual_id": entry["manual_id"],
            "source_candidate_id": entry.get("source_candidate_id", ""),
            "status": entry["status"],
            "review_status": entry.get("review_status", ""),
            "user_marker_role": entry.get("user_marker_role", ""),
            "signal_time_utc": _iso(signal_time),
            "entry_time_utc": _iso(entry_time),
            "anchor_time_utc": _iso(anchor_time),
            "visual_marker_time_utc": _iso(visual_time),
            "signal_open": float(signal["open"]),
            "signal_high": float(signal["high"]),
            "signal_low": float(signal["low"]),
            "signal_close": float(signal["close"]),
            "entry_open_price": entry_open,
            "entry_high": float(candle["high"]),
            "entry_low": float(candle["low"]),
            "entry_close": float(candle["close"]),
            "anchor_low_price": float(anchor["low"]),
            "visual_marker_price": visual_marker_price,
            "entry_price_5bps": entry_5bps,
            "target_1pct_from_5bps": target_1pct,
            "slippage_bps": slippage_bps,
            "execution_rule_check": rule_note,
            "include_in_clean_overview": bool(entry.get("include_in_clean_overview", False)),
            "include_in_review_sheet": bool(entry.get("include_in_review_sheet", True)),
            "user_note": entry.get("user_note", ""),
        }
        out.append(row)
    return out


def _color(row: dict[str, Any]) -> str:
    status = str(row["status"])
    if status.startswith("CONFIRMED"):
        return "#00e676"
    if status.startswith("PENDING"):
        return "#ffb300"
    return "#ff5252"


def _plot_entry(
    ax: Any,
    row: dict[str, Any],
    *,
    label_prefix: str = "",
    compact: bool = False,
) -> None:
    color = _color(row)
    signal_time = _naive(row["signal_time_utc"])
    entry_time = _naive(row["entry_time_utc"])
    visual_time = _naive(row["visual_marker_time_utc"])
    entry_open = float(row["entry_open_price"])
    entry_5bps = float(row["entry_price_5bps"])
    visual_price = float(row["visual_marker_price"])

    ax.axvline(signal_time, color="#ff5252", linewidth=0.95, alpha=0.45)
    ax.axvline(entry_time, color=color, linewidth=1.45, alpha=0.9)
    ax.scatter([entry_time], [entry_open], marker="^", s=110 if not compact else 70, color=color, edgecolors="white", linewidths=0.7, zorder=9)
    ax.scatter([entry_time], [entry_5bps], marker="_", s=130 if not compact else 90, color="#ffffff", linewidths=1.35, alpha=0.86, zorder=10)
    ax.scatter([visual_time], [visual_price], marker="o", s=26 if not compact else 16, color="#ff5252", edgecolors="#111820", linewidths=0.35, zorder=8)

    if not compact:
        text = (
            f"{label_prefix}{row['manual_id']}\n"
            f"signal {_minute(row['signal_time_utc'])} -> entry {_minute(row['entry_time_utc'])}\n"
            f"open {entry_open:.5f} | +5bps {entry_5bps:.5f}"
        )
        if row["execution_rule_check"] != "OK_NEXT_OPEN":
            text += "\nmanual execution override"
        ax.annotate(
            text,
            xy=(entry_time, entry_open),
            xytext=(8, 12),
            textcoords="offset points",
            fontsize=7,
            color=color,
            arrowprops={"arrowstyle": "->", "color": color, "linewidth": 0.9},
            bbox={"boxstyle": "round,pad=0.25", "facecolor": "#0c2018", "edgecolor": color, "alpha": 0.80},
        )
    else:
        ax.annotate(
            str(row["manual_id"]).replace("_", "\n", 1),
            xy=(entry_time, entry_open),
            xytext=(4, 6),
            textcoords="offset points",
            fontsize=6,
            color=color,
            fontweight="bold",
        )


def _render_overview(
    *,
    df: pd.DataFrame,
    rows: list[dict[str, Any]],
    out_path: Path,
    title: str,
    confirmed_only: bool,
) -> Path:
    if confirmed_only:
        rows = [row for row in rows if row["include_in_clean_overview"]]
    else:
        rows = [row for row in rows if row["include_in_review_sheet"]]

    fig, (ax_price, ax_vol) = plt.subplots(
        2,
        1,
        figsize=(24, 11),
        sharex=True,
        gridspec_kw={"height_ratios": [4.2, 1.0]},
    )
    fig.patch.set_facecolor("#101418")
    _style_axis(ax_price)
    _style_axis(ax_vol)
    _draw_candles(ax_price, df.reset_index(drop=True), "1m", linewidth=0.34)
    colors = ["#26a69a" if close >= open_ else "#ef5350" for open_, close in zip(df["open"], df["close"])]
    ax_vol.bar(df["open_time_utc"].dt.tz_convert(None), df["volume"].astype(float), width=0.00055, color=colors, alpha=0.55)
    ax_vol.set_ylabel("Volume", color="white", fontsize=9)

    for row in rows:
        _plot_entry(ax_price, row, compact=True)

    counts = Counter(row["status"] for row in rows)
    fig.text(0.012, 0.012, " | ".join(f"{k}={v}" for k, v in sorted(counts.items())), color="#d8dee9", fontsize=9)
    ax_price.set_title(title, color="white", fontsize=15)
    ax_price.set_ylabel("Price", color="white", fontsize=10)
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax_vol.tick_params(axis="x", labelrotation=25, labelsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    fig.savefig(out_path, dpi=165, facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_path


def _render_review_sheet(
    *,
    df: pd.DataFrame,
    rows: list[dict[str, Any]],
    out_path: Path,
    title: str,
) -> Path:
    sheet_rows = [row for row in rows if row["include_in_review_sheet"]]
    n = max(1, len(sheet_rows))
    fig, axes = plt.subplots(n, 1, figsize=(18, max(4.2, 3.5 * n)), sharex=False)
    if n == 1:
        axes = [axes]
    fig.patch.set_facecolor("#101418")
    for ax, row in zip(axes, sheet_rows):
        _style_axis(ax)
        entry_time = _ts(row["entry_time_utc"])
        start = entry_time - pd.Timedelta(minutes=35)
        end = entry_time + pd.Timedelta(minutes=45)
        win = df[(df["open_time_utc"] >= start) & (df["open_time_utc"] <= end)].reset_index(drop=True)
        _draw_candles(ax, win, "1m", linewidth=0.72)
        _plot_entry(ax, row)
        low = min(float(win["low"].min()), float(row["visual_marker_price"]), float(row["entry_open_price"]))
        high = max(float(win["high"].max()), float(row["visual_marker_price"]), float(row["entry_open_price"]))
        pad = max((high - low) * 0.16, 0.025)
        ax.set_ylim(low - pad, high + pad)
        ax.set_xlim(start.tz_convert(None).to_pydatetime(), end.tz_convert(None).to_pydatetime())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.tick_params(axis="x", labelrotation=25, labelsize=8)
        ax.set_title(
            f"{row['manual_id']} | {row['status']} | {row['review_status']} | {row['execution_rule_check']}",
            color="white",
            fontsize=9,
        )
        ax.set_ylabel("Price", color="white", fontsize=8)

    fig.suptitle(title, color="white", fontsize=14)
    fig.tight_layout(rect=(0, 0.01, 1, 0.965))
    fig.savefig(out_path, dpi=165, facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_path


def _render_close_zoom(
    *,
    df: pd.DataFrame,
    row: dict[str, Any],
    out_path: Path,
    title: str,
) -> Path:
    entry_time = _ts(row["entry_time_utc"])
    start = entry_time - pd.Timedelta(minutes=20)
    end = entry_time + pd.Timedelta(minutes=40)
    win = df[(df["open_time_utc"] >= start) & (df["open_time_utc"] <= end)].reset_index(drop=True)

    fig, (ax_price, ax_vol) = plt.subplots(
        2,
        1,
        figsize=(18, 8.5),
        sharex=True,
        gridspec_kw={"height_ratios": [4.0, 1.0]},
    )
    fig.patch.set_facecolor("#101418")
    _style_axis(ax_price)
    _style_axis(ax_vol)
    _draw_candles(ax_price, win, "1m", linewidth=0.88)
    _plot_entry(ax_price, row)
    colors = ["#26a69a" if close >= open_ else "#ef5350" for open_, close in zip(win["open"], win["close"])]
    ax_vol.bar(win["open_time_utc"].dt.tz_convert(None), win["volume"].astype(float), width=0.00055, color=colors, alpha=0.60)
    low = min(float(win["low"].min()), float(row["visual_marker_price"]), float(row["entry_open_price"]))
    high = max(float(win["high"].max()), float(row["visual_marker_price"]), float(row["entry_open_price"]))
    pad = max((high - low) * 0.18, 0.025)
    ax_price.set_ylim(low - pad, high + pad)
    ax_price.set_xlim(start.tz_convert(None).to_pydatetime(), end.tz_convert(None).to_pydatetime())
    ax_price.set_title(title, color="white", fontsize=14)
    ax_price.set_ylabel("Price", color="white", fontsize=9)
    ax_vol.set_ylabel("Volume", color="white", fontsize=8)
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax_vol.tick_params(axis="x", labelrotation=25, labelsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_path


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Manual Reanchors V0",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: один воспроизводимый источник ручных точных входов. Этот слой не читает `GOOD_1PCT`, DCA-пулы, старые rejected/soft сделки и не запускает ML/Optuna.",
        "",
        "## Главное правило",
        "",
        "`signal_time_utc` и `entry_time_utc` - контракт исполнения. `visual_marker_*` - только точка для глаз, чтобы не смешивать low и market-entry.",
        "",
        "## Сводка",
        "",
    ]
    for key, value in payload["summary"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Артефакты", ""])
    for key, value in payload["artifacts"].items():
        if isinstance(value, list):
            lines.append(f"- `{key}`:")
            for item in value:
                lines.append(f"  - `{item}`")
        else:
            lines.append(f"- `{key}`: `{value}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_review(*, config_path: Path, out_dir: Path, run_label: str) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    if not config_path.is_absolute():
        config_path = root / config_path
    if not out_dir.is_absolute():
        out_dir = root / out_dir

    config = _load_config(config_path)
    symbol = str(config["symbol"])
    timeframe = str(config["timeframe"])
    day = str(config["day_utc"])
    run_id = f"{run_label}_{_run_stamp()}" if run_label else f"manual_reanchors_v0_{_run_stamp()}"
    run_dir = out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    source = _source_csv(root, day, timeframe, symbol)
    df = _load_ohlcv(source)
    rows = _validate_and_enrich(df=df, config=config)

    csv_path = run_dir / f"SIGNIFICANT_LOW_MANUAL_REANCHORS_V0_{day.replace('-', '')}.csv"
    json_path = run_dir / f"SIGNIFICANT_LOW_MANUAL_REANCHORS_V0_{day.replace('-', '')}.json"
    report_path = run_dir / f"SIGNIFICANT_LOW_MANUAL_REANCHORS_V0_{day.replace('-', '')}_RU.md"
    overview_path = run_dir / f"SIGNIFICANT_LOW_MANUAL_REANCHORS_V0_{day.replace('-', '')}_CONFIRMED_OVERVIEW.png"
    review_path = run_dir / f"SIGNIFICANT_LOW_MANUAL_REANCHORS_V0_{day.replace('-', '')}_REVIEW_SHEET.png"
    close_paths: list[Path] = []

    _render_overview(
        df=df,
        rows=rows,
        out_path=overview_path,
        title=f"{symbol} {timeframe} {day} | MANUAL REANCHORS V0 | confirmed only | NO ML/OPTUNA",
        confirmed_only=True,
    )
    _render_review_sheet(
        df=df,
        rows=rows,
        out_path=review_path,
        title=f"{symbol} {timeframe} {day} | MANUAL REANCHORS V0 | review sheet | NO ML/OPTUNA",
    )
    for row in rows:
        if row["manual_id"] in {"RA003_SHIFT_LEFT_LA050", "RA004_USER_ENTRY_2049"}:
            path = run_dir / f"SIGNIFICANT_LOW_MANUAL_REANCHORS_V0_{day.replace('-', '')}_{row['manual_id']}_CLOSE_ZOOM.png"
            _render_close_zoom(
                df=df,
                row=row,
                out_path=path,
                title=f"{symbol} {timeframe} {day} | {row['manual_id']} close zoom | NO ML/OPTUNA",
            )
            close_paths.append(path)

    _write_csv(csv_path, rows)
    status_counts = dict(Counter(row["status"] for row in rows))
    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "run_id": run_id,
        "source_config": _rel(root, config_path),
        "source_ohlcv": _rel(root, source),
        "symbol": symbol,
        "timeframe": timeframe,
        "day_utc": day,
        "summary": {
            "rows_total": len(rows),
            "confirmed_clean_overview": sum(1 for row in rows if row["include_in_clean_overview"]),
            "pending_review": sum(1 for row in rows if str(row["status"]).startswith("PENDING")),
            "manual_execution_overrides": sum(1 for row in rows if row["execution_rule_check"] != "OK_NEXT_OPEN"),
        },
        "status_counts": status_counts,
        "rows": rows,
        "artifacts": {
            "run_dir": _rel(root, run_dir),
            "csv": _rel(root, csv_path),
            "json": _rel(root, json_path),
            "report_ru": _rel(root, report_path),
            "confirmed_overview_png": _rel(root, overview_path),
            "review_sheet_png": _rel(root, review_path),
            "close_zoom_png": [_rel(root, path) for path in close_paths],
        },
        "guardrails": ["NO_ML", "NO_OPTUNA", "NO_SCORER", "NO_TARGET_LOCK", "NO_API"],
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    _write_report(report_path, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="configs/visual_entry/manual_reanchors/SOLUSDT_1m_2026-05-02_SIGNIFICANT_LOW_MANUAL_REANCHORS_V0.json",
    )
    parser.add_argument(
        "--out-dir",
        default="reports/final_review/visual_entry_v3/fresh_target_led/significant_low_manual_reanchors_v0",
    )
    parser.add_argument("--run-label", default="siglow_manual_reanchors_v0")
    args = parser.parse_args()

    payload = run_review(config_path=Path(args.config), out_dir=Path(args.out_dir), run_label=args.run_label)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "run_id": payload["run_id"],
                "summary": payload["summary"],
                "status_counts": payload["status_counts"],
                "artifacts": payload["artifacts"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
