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

from mlbotnav.visual_entry_indicator_hypothesis_review import (
    SLIPPAGE_BPS,
    _add_indicators,
    _draw_candles,
    _draw_fibo,
    _draw_structure,
    _draw_targets,
    _indicator_votes,
    _load_ohlcv,
    _plot_volume_profile,
    _rel,
    _render_full_day,
    _source_csv,
    _style_axis,
)
from mlbotnav.visual_entry_low_anchor_suggester import _bar_width_days


STATUS = "INDICATOR_HYPOTHESIS_REVIEW_V1_M01_M19_T15V1_READY_NO_SCORER_NO_ML_NO_OPTUNA"
RAIL_POINT = "SECOND_LAYER_FEATURE_EVIDENCE_M01_M19_AND_T15V1_BEFORE_PASSPORT_NO_ML_NO_OPTUNA"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_m01_m19(root: Path) -> list[dict[str, Any]]:
    path = root / "reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_M01_M19.json"
    payload = _read_json(path)
    rows: list[dict[str, Any]] = []
    for item in payload["targets"]:
        execution = item.get("execution_price", {})
        rows.append(
            {
                "target_id": str(item["target_id"]),
                "source_group": "M01_M19_20260514_reference",
                "day_utc": "2026-05-14",
                "signal_time_utc": str(item["signal_time_utc"]),
                "entry_time_utc": str(item["entry_time_utc"]),
                "entry_price_plus_5bps": float(execution.get("entry_price_with_slippage")),
                "review_label": "manual_gold",
                "target_type": str(item.get("target_type") or "UNKNOWN"),
            }
        )
    return rows


def _load_t15_v1(root: Path) -> list[dict[str, Any]]:
    path = root / (
        "reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/"
        "priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/"
        "T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701.json"
    )
    payload = _read_json(path)
    rows: list[dict[str, Any]] = []
    for item in payload["entries"]:
        rows.append(
            {
                "target_id": str(item["entry_id"]),
                "source_group": "T15_USER_CONFIRMED_7_V1_RED_ARROW_FIXED",
                "day_utc": "2026-05-15",
                "signal_time_utc": str(item["signal_time_utc"]),
                "entry_time_utc": str(item["entry_time_utc"]),
                "entry_price_plus_5bps": float(item["entry_price_plus_5bps"]),
                "entry_open_price": float(item["entry_open_price"]),
                "review_label": "manual_gold",
                "target_type": str(item.get("source_transfer_type") or item.get("draft_cluster_id") or "UNKNOWN"),
                "draft_cluster_id": str(item.get("draft_cluster_id") or ""),
                "user_red_arrow_corrected": bool(item.get("user_red_arrow_corrected")),
            }
        )
    return rows


def _render_zoom_sheet(*, df: pd.DataFrame, targets: list[dict[str, Any]], out_path: Path) -> None:
    rows = len(targets)
    fig = plt.figure(figsize=(22, max(4.5 * rows, 8)), facecolor="#101418")
    grid = fig.add_gridspec(rows * 3, 1, hspace=0.07)
    for idx, target in enumerate(targets):
        ax_price = fig.add_subplot(grid[idx * 3, 0])
        ax_rsi = fig.add_subplot(grid[idx * 3 + 1, 0], sharex=ax_price)
        ax_macd = fig.add_subplot(grid[idx * 3 + 2, 0], sharex=ax_price)
        for ax in [ax_price, ax_rsi, ax_macd]:
            _style_axis(ax)
        signal = pd.Timestamp(target["signal_time_utc"]).tz_convert("UTC")
        start = signal - pd.Timedelta(minutes=34)
        end = signal + pd.Timedelta(minutes=44)
        win = df[(df["open_time_utc"] >= start) & (df["open_time_utc"] <= end)].reset_index(drop=True)

        _draw_candles(ax_price, win, "1m", linewidth=0.62)
        _draw_structure(ax_price, win)
        _draw_targets(ax_price, [target], show_price=True)
        ax_price.set_xlim(start.tz_convert(None).to_pydatetime(), end.tz_convert(None).to_pydatetime())
        _draw_fibo(ax_price, win, signal)
        _plot_volume_profile(ax_price, win, bins=24)

        votes = _indicator_votes(df, target)
        votes_text = ",".join(votes.get("votes", []))[:95]
        caution_text = ",".join(votes.get("cautions", []))[:70]
        ax_price.set_title(
            f"{target['target_id']} {target['target_type']} | signal {pd.Timestamp(target['signal_time_utc']).strftime('%H:%M')} "
            f"-> entry {pd.Timestamp(target['entry_time_utc']).strftime('%H:%M')} | +5bps {float(target['entry_price_plus_5bps']):.4f} "
            f"| votes={votes_text} | cautions={caution_text}",
            color="white",
            fontsize=8.5,
        )

        colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(win["open"], win["close"])]
        price_floor = float(win["low"].min())
        price_span = max(float(win["high"].max()) - price_floor, 0.01)
        volume_height = win["volume"] / max(float(win["volume"].max()), 1.0) * price_span * 0.18
        ax_price.bar(
            win["open_time_utc"].dt.tz_convert(None),
            volume_height,
            bottom=price_floor,
            width=_bar_width_days("1m"),
            color=colors,
            alpha=0.16,
            zorder=0,
        )

        ax_rsi.plot(win["open_time_utc"].dt.tz_convert(None), win["rsi14"], color="#7e57c2", linewidth=0.9)
        for level, color in [(30, "#00e676"), (50, "#cfd8dc"), (70, "#ff5252")]:
            ax_rsi.axhline(level, color=color, linewidth=0.7, alpha=0.45)
        ax_rsi.set_ylim(0, 100)
        ax_rsi.set_ylabel("RSI", color="white")

        hist_colors = ["#26a69a" if value >= 0 else "#ef5350" for value in win["macd_hist"]]
        ax_macd.bar(win["open_time_utc"].dt.tz_convert(None), win["macd_hist"], width=_bar_width_days("1m"), color=hist_colors, alpha=0.56)
        ax_macd.plot(win["open_time_utc"].dt.tz_convert(None), win["macd"], color="#4fc3f7", linewidth=0.8)
        ax_macd.plot(win["open_time_utc"].dt.tz_convert(None), win["macd_signal"], color="#ffcc80", linewidth=0.8)
        ax_macd.axhline(0, color="#cfd8dc", linewidth=0.7, alpha=0.45)
        ax_macd.set_ylabel("MACD", color="white")
        ax_macd.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    fig.suptitle(
        "SOLUSDT 1m 2026-05-15 | T15 confirmed 7 feature evidence layer | RSI/MACD/Fibo/BOS/Volume | NO ML/OPTUNA",
        color="white",
        fontsize=14,
    )
    fig.savefig(out_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = [
        "target_id",
        "source_group",
        "day_utc",
        "target_type",
        "signal_time_utc",
        "entry_time_utc",
        "entry_price_plus_5bps",
        "votes",
        "cautions",
        "rsi14",
        "macd_hist",
        "volume_ratio20",
        "volume_z20",
        "range_pos_60",
        "room_to_high_60_bps",
        "lower_wick_to_body",
        "close_pos_candle",
        "bos_up_60",
        "bos_down_60",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            out = dict(row)
            out["votes"] = ",".join(out.get("votes") or [])
            out["cautions"] = ",".join(out.get("cautions") or [])
            writer.writerow({col: out.get(col) for col in columns})


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Indicator Hypothesis Review V1",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Это восстановленный второй слой перед паспортом: не поверх эталонных скринов, а отдельным evidence-слоем.",
        "",
        "## Что вошло",
        "",
        "- `2026-05-14`: 19 подтвержденных ручных входов `M01..M19`.",
        "- `2026-05-15`: 7 подтвержденных входов `T15L02/T15L06/T15L07/T15L08/T15L11/T15L13/T15L16` из `draft_ledger_v1` с красными правками.",
        "",
        "## Какие инструменты наложены",
        "",
        "- `RSI14`;",
        "- `MACD` и histogram;",
        "- `volume`, volume MA и volume profile / density;",
        "- trailing swing low/high;",
        "- `BOS up/down` по прошлому окну;",
        "- `Fibo` на zoom, построенный только по окну до signal.",
        "",
        "## Граница",
        "",
        "- Это не scorer, не target-lock, не Optuna и не ML dataset.",
        "- Все признаки считаются на закрытой signal-свече и прошлом контексте.",
        "- Entry price и `entry + 5 bps` только для исполнения и визуального контроля.",
        "- EMA не используется как active condition.",
        "- Future return, TP/SL, MFE/MAE и OHLCV entry-свечи запрещены для выбора входа.",
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
    lines.extend(
        [
            "",
            "## Следующий шаг",
            "",
            "Сначала визуально смотрим этот evidence-слой по 19+7. Только после твоего `норм/фиксить` возвращаемся к выбору кластера и draft-паспорту.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(out_dir: Path) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    m_targets = _load_m01_m19(root)
    t15_targets = _load_t15_v1(root)
    all_targets = m_targets + t15_targets
    records: list[dict[str, Any]] = []

    df14 = _add_indicators(_load_ohlcv(_source_csv(root, "2026-05-14")))
    df15 = _add_indicators(_load_ohlcv(_source_csv(root, "2026-05-15")))

    full14 = out_dir / "INDICATOR_HYPOTHESIS_REVIEW_V1_FULL_DAY_M01_M19_20260514.png"
    full15 = out_dir / "INDICATOR_HYPOTHESIS_REVIEW_V1_FULL_DAY_T15_7_20260515.png"
    zoom15 = out_dir / "INDICATOR_HYPOTHESIS_REVIEW_V1_ZOOM_T15_7_20260515.png"

    _render_full_day(df=df14, targets=m_targets, day="2026-05-14", out_path=full14)
    _render_full_day(df=df15, targets=t15_targets, day="2026-05-15", out_path=full15)
    _render_zoom_sheet(df=df15, targets=t15_targets, out_path=zoom15)

    for target in m_targets:
        row = _indicator_votes(df14, target)
        row["source_group"] = target["source_group"]
        records.append(row)
    for target in t15_targets:
        row = _indicator_votes(df15, target)
        row["source_group"] = target["source_group"]
        row["draft_cluster_id"] = target.get("draft_cluster_id", "")
        row["user_red_arrow_corrected"] = target.get("user_red_arrow_corrected", False)
        records.append(row)

    json_path = out_dir / "INDICATOR_HYPOTHESIS_REVIEW_V1_20260701.json"
    csv_path = out_dir / "INDICATOR_HYPOTHESIS_REVIEW_V1_20260701.csv"
    report_path = out_dir / "INDICATOR_HYPOTHESIS_REVIEW_V1_20260701_RU.md"
    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "rail_point": RAIL_POINT,
        "source_layers": {
            "m01_m19_reference": "reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_M01_M19.json",
            "t15_draft_ledger_v1": "reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701.json",
        },
        "counts": {
            "m01_m19_reference": len(m_targets),
            "t15_user_confirmed_7_v1": len(t15_targets),
            "total_records": len(records),
        },
        "records": records,
        "no_lookahead_boundary": {
            "features_end_at": "closed_signal_candle_and_past_context",
            "entry_rule": "LONG at next candle open after closed signal",
            "entry_open_price_is_execution_only": True,
            "ema_active_condition": False,
            "forbidden_features": ["future_return", "tp_sl", "mfe_mae", "entry_candle_ohlcv_for_selection"],
        },
        "artifacts": {
            "json": _rel(root, json_path),
            "csv": _rel(root, csv_path),
            "report_ru": _rel(root, report_path),
            "full_day_20260514_m01_m19_png": _rel(root, full14),
            "full_day_20260515_t15_7_png": _rel(root, full15),
            "zoom_20260515_t15_7_png": _rel(root, zoom15),
        },
        "scorer_allowed": False,
        "target_lock_allowed": False,
        "optuna_allowed": False,
        "ml_allowed": False,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_csv(csv_path, records)
    _write_report(report_path, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Render V1 feature evidence layer for M01-M19 and T15 confirmed 7.")
    parser.add_argument(
        "--out-dir",
        default="reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1",
    )
    args = parser.parse_args()
    payload = run(Path(args.out_dir))
    print(
        json.dumps(
            {
                "status": payload["status"],
                "counts": payload["counts"],
                "artifacts": payload["artifacts"],
                "scorer_allowed": payload["scorer_allowed"],
                "target_lock_allowed": payload["target_lock_allowed"],
                "optuna_allowed": payload["optuna_allowed"],
                "ml_allowed": payload["ml_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
