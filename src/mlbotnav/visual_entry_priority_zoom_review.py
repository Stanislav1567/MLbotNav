from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from mlbotnav.visual_entry_indicator_hypothesis_review import (
    _add_indicators,
    _draw_fibo,
    _indicator_votes,
    _load_day_targets,
    _plot_volume_profile,
    _rel,
    _source_csv,
    _utc_now,
)
from mlbotnav.visual_entry_low_anchor_suggester import _bar_width_days, _draw_candles, _load_ohlcv, _style_axis


STATUS = "T15_PRIORITY_ZOOM_REVIEW_V0_READY_NO_ML_NO_OPTUNA"
RAIL_POINT = "T15L06_T15L13_T15L16_PRIORITY_ZOOM_REVIEW_NO_ML_NO_OPTUNA"
DAY = "2026-05-15"
PRIORITY_IDS = ["T15L06", "T15L13", "T15L16"]

ASSISTANT_NOTES = {
    "T15L06": "priority strong: deep capitulation low, strong RSI/volume, large room; needs user zoom verdict",
    "T15L13": "priority strong: deep low and large room; check if it is real reclaim or only weak-day bounce",
    "T15L16": "priority strong: support/retest after stabilization; check continuation quality",
}


def _target_by_id(targets: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(item["target_id"]): item for item in targets}


def _window(df: pd.DataFrame, target: dict[str, Any]) -> pd.DataFrame:
    signal = pd.Timestamp(target["signal_time_utc"]).tz_convert("UTC")
    start = signal - pd.Timedelta(minutes=76)
    end = signal + pd.Timedelta(minutes=112)
    return df[(df["open_time_utc"] >= start) & (df["open_time_utc"] <= end)].reset_index(drop=True)


def _draw_candidate(ax_price: Any, ax_vol: Any, ax_rsi: Any, ax_macd: Any, df: pd.DataFrame, target: dict[str, Any]) -> dict[str, Any]:
    for ax in [ax_price, ax_vol, ax_rsi, ax_macd]:
        _style_axis(ax)

    win = _window(df, target)
    signal = pd.Timestamp(target["signal_time_utc"]).tz_convert("UTC")
    entry = pd.Timestamp(target["entry_time_utc"]).tz_convert("UTC")
    signal_naive = signal.tz_convert(None).to_pydatetime()
    entry_naive = entry.tz_convert(None).to_pydatetime()
    entry_price = float(target["entry_price_plus_5bps"])
    pre_win = win[win["open_time_utc"] <= signal]
    votes = _indicator_votes(df, target)

    _draw_candles(ax_price, win, "1m", linewidth=0.82)
    _plot_volume_profile(ax_price, pre_win, bins=30, color="#78909c")
    _draw_fibo(ax_price, win, signal)

    x_start = win["open_time_utc"].iloc[0].tz_convert(None).to_pydatetime()
    x_end = win["open_time_utc"].iloc[-1].tz_convert(None).to_pydatetime()
    ax_price.set_xlim(x_start, x_end)
    ax_price.axvspan(entry_naive, x_end, color="#263238", alpha=0.16, zorder=0)
    ax_price.axvline(signal_naive, color="#ffca28", linewidth=1.3, alpha=0.90)
    ax_price.axvline(entry_naive, color="#00e676", linewidth=1.8, alpha=0.95)
    ax_price.axhline(entry_price, color="#00e676", linewidth=1.0, alpha=0.72, linestyle="--")
    ax_price.scatter([entry_naive], [entry_price], marker="^", s=120, color="#00e676", edgecolors="white", linewidths=0.8, zorder=9)

    ax_price.annotate(
        f"{target['target_id']} entry {entry.strftime('%H:%M')} p+5bps {entry_price:.4f}",
        xy=(entry_naive, entry_price),
        xytext=(10, 20),
        textcoords="offset points",
        color="#00e676",
        fontsize=10,
        arrowprops={"arrowstyle": "->", "color": "#00e676", "lw": 1.0},
    )
    text = (
        f"{target['target_type']}\n"
        f"signal {signal.strftime('%H:%M')} -> entry {entry.strftime('%H:%M')}\n"
        f"price+5bps {entry_price:.4f}\n"
        f"votes: {', '.join(votes.get('votes', [])) or '-'}\n"
        f"cautions: {', '.join(votes.get('cautions', [])) or '-'}\n"
        f"note: {ASSISTANT_NOTES[target['target_id']]}"
    )
    ax_price.text(
        0.012,
        0.98,
        text,
        transform=ax_price.transAxes,
        color="#eceff1",
        fontsize=9,
        va="top",
        ha="left",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "#102027", "edgecolor": "#00e676", "alpha": 0.82},
    )
    ax_price.set_ylabel("Price", color="white")

    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(win["open"], win["close"])]
    ax_vol.bar(win["open_time_utc"].dt.tz_convert(None), win["volume"], width=_bar_width_days("1m"), color=colors, alpha=0.72)
    ax_vol.plot(win["open_time_utc"].dt.tz_convert(None), win["volume_ma20_prior"], color="#ffcc80", linewidth=0.95)
    ax_vol.axvline(signal_naive, color="#ffca28", linewidth=1.0, alpha=0.8)
    ax_vol.axvline(entry_naive, color="#00e676", linewidth=1.2, alpha=0.8)
    ax_vol.set_ylabel("Volume", color="white")

    ax_rsi.plot(win["open_time_utc"].dt.tz_convert(None), win["rsi14"], color="#7e57c2", linewidth=1.1)
    for level, color in [(30, "#00e676"), (50, "#cfd8dc"), (70, "#ff5252")]:
        ax_rsi.axhline(level, color=color, linewidth=0.75, alpha=0.45)
    ax_rsi.axvline(signal_naive, color="#ffca28", linewidth=1.0, alpha=0.8)
    ax_rsi.axvline(entry_naive, color="#00e676", linewidth=1.2, alpha=0.8)
    ax_rsi.set_ylim(0, 100)
    ax_rsi.set_ylabel("RSI14", color="white")

    hist_colors = ["#26a69a" if value >= 0 else "#ef5350" for value in win["macd_hist"]]
    ax_macd.bar(win["open_time_utc"].dt.tz_convert(None), win["macd_hist"], width=_bar_width_days("1m"), color=hist_colors, alpha=0.58)
    ax_macd.plot(win["open_time_utc"].dt.tz_convert(None), win["macd"], color="#4fc3f7", linewidth=0.95)
    ax_macd.plot(win["open_time_utc"].dt.tz_convert(None), win["macd_signal"], color="#ffcc80", linewidth=0.95)
    ax_macd.axhline(0, color="#cfd8dc", linewidth=0.75, alpha=0.45)
    ax_macd.axvline(signal_naive, color="#ffca28", linewidth=1.0, alpha=0.8)
    ax_macd.axvline(entry_naive, color="#00e676", linewidth=1.2, alpha=0.8)
    ax_macd.set_ylabel("MACD", color="white")
    ax_macd.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    return votes


def _render_one(df: pd.DataFrame, target: dict[str, Any], out_path: Path) -> dict[str, Any]:
    fig = plt.figure(figsize=(22, 12), facecolor="#101418")
    grid = fig.add_gridspec(4, 1, height_ratios=[4.7, 1.05, 1.05, 1.15], hspace=0.08)
    axes = [fig.add_subplot(grid[i, 0]) for i in range(4)]
    votes = _draw_candidate(axes[0], axes[1], axes[2], axes[3], df, target)
    fig.suptitle(
        f"SOLUSDT 1m {DAY} | {target['target_id']} priority zoom | visual review only | NO ML/OPTUNA",
        color="white",
        fontsize=15,
    )
    fig.savefig(out_path, dpi=170, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return votes


def _render_sheet(df: pd.DataFrame, targets: list[dict[str, Any]], out_path: Path) -> list[dict[str, Any]]:
    fig = plt.figure(figsize=(24, 30), facecolor="#101418")
    grid = fig.add_gridspec(len(targets) * 4, 1, height_ratios=[4.7, 1.05, 1.05, 1.15] * len(targets), hspace=0.10)
    rows: list[dict[str, Any]] = []
    for idx, target in enumerate(targets):
        base = idx * 4
        axes = [fig.add_subplot(grid[base + j, 0]) for j in range(4)]
        rows.append(_draw_candidate(axes[0], axes[1], axes[2], axes[3], df, target))
    fig.suptitle(
        f"SOLUSDT 1m {DAY} | priority zoom review T15L06/T15L13/T15L16 | visual only | NO ML/OPTUNA",
        color="white",
        fontsize=16,
    )
    fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return rows


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# T15 Priority Zoom Review V0",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: крупно проверить три приоритетных pending-кандидата `T15L06`, `T15L13`, `T15L16` после ассистентского verdict.",
        "",
        "Это не scorer, не target-lock, не ML dataset и не Optuna.",
        "",
        "## Граница",
        "",
        "- RSI/MACD/volume/Fibo используются только как визуальные подсказки.",
        "- Fibo и density строятся по pre-signal контексту.",
        "- Будущие свечи на zoom показаны только для ручного visual review, не как признак отбора.",
        "- Entry price используется только для execution/control.",
        "",
        "## Предварительный вывод",
        "",
    ]
    for item in payload["records"]:
        lines.append(f"- `{item['target_id']}`: {item['assistant_note']}.")
    lines.extend(["", "## Артефакты", ""])
    for key, value in payload["artifacts"].items():
        if isinstance(value, list):
            for item in value:
                lines.append(f"- `{item}`")
        else:
            lines.append(f"- `{value}`")
    lines.extend(
        [
            "",
            "## Следующий шаг",
            "",
            "Пользователь смотрит три priority zoom и дает verdict: `gold`, `possible`, `shift`, `duplicate` или `reject`.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(out_dir: Path) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    df = _add_indicators(_load_ohlcv(_source_csv(root, DAY)))
    targets_map = _target_by_id(_load_day_targets(root, DAY))
    targets = [targets_map[item] for item in PRIORITY_IDS]

    individual_paths: list[Path] = []
    records: list[dict[str, Any]] = []
    for target in targets:
        path = out_dir / f"{target['target_id']}_PRIORITY_ZOOM_REVIEW_V0_{DAY.replace('-', '')}.png"
        votes = _render_one(df, target, path)
        individual_paths.append(path)
        records.append(
            {
                **votes,
                "assistant_note": ASSISTANT_NOTES[target["target_id"]],
                "priority_status": "priority_zoom_pending_user_verdict",
            }
        )

    sheet_path = out_dir / f"T15_PRIORITY_ZOOM_REVIEW_V0_SHEET_{DAY.replace('-', '')}.png"
    _render_sheet(df, targets, sheet_path)

    json_path = out_dir / "T15_PRIORITY_ZOOM_REVIEW_V0_20260701.json"
    report_path = out_dir / "T15_PRIORITY_ZOOM_REVIEW_V0_20260701_RU.md"
    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "rail_point": RAIL_POINT,
        "day_utc": DAY,
        "priority_ids": PRIORITY_IDS,
        "records": records,
        "no_lookahead_boundary": {
            "indicator_features_end_at": "signal_candle_close",
            "fibo_density_context": "pre_signal_window",
            "future_candles_on_png": "visual_review_only_not_feature",
            "entry_open_price_is_execution_price_only": True,
            "ema_active_condition": False,
            "optuna_allowed": False,
            "ml_allowed": False,
        },
        "artifacts": {
            "sheet_png": _rel(root, sheet_path),
            "individual_pngs": [_rel(root, path) for path in individual_paths],
            "json": _rel(root, json_path),
            "report_ru": _rel(root, report_path),
        },
        "optuna_allowed": False,
        "ml_allowed": False,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_report(report_path, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Render priority zoom review for selected T15 pending candidates.")
    parser.add_argument(
        "--out-dir",
        default="reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0",
    )
    args = parser.parse_args()
    payload = run(Path(args.out_dir))
    print(
        json.dumps(
            {
                "status": payload["status"],
                "priority_ids": payload["priority_ids"],
                "artifacts": payload["artifacts"],
                "ml_allowed": payload["ml_allowed"],
                "optuna_allowed": payload["optuna_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
