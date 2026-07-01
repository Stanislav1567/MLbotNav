from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from mlbotnav.visual_entry_low_anchor_suggester import _load_ohlcv, _source_csv


STATUS = "LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_READY_NO_ML_NO_OPTUNA"


FEATURE_COLUMNS = [
    "ret_30m_pct",
    "ret_60m_pct",
    "range_pos_60",
    "range_pos_180",
    "distance_from_low_60_bps",
    "room_to_high_60_bps",
    "close_vs_ema20_bps",
    "ema20_slope_10_bps",
    "volume_ratio20",
    "range_ratio20",
    "lower_wick_to_body",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fmt_float(value: Any, digits: int = 4) -> float | None:
    try:
        if pd.isna(value):
            return None
        return round(float(value), digits)
    except Exception:
        return None


def _add_no_lookahead_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for window in [20, 60, 180]:
        out[f"rolling_low_{window}"] = out["low"].rolling(window, min_periods=1).min()
        out[f"rolling_high_{window}"] = out["high"].rolling(window, min_periods=1).max()
        denom = (out[f"rolling_high_{window}"] - out[f"rolling_low_{window}"]).replace(0, np.nan)
        out[f"range_pos_{window}"] = (out["close"] - out[f"rolling_low_{window}"]) / denom

    for window in [15, 30, 60, 120]:
        out[f"ret_{window}m_pct"] = out["close"].pct_change(window) * 100.0

    out["ema20"] = out["close"].ewm(span=20, adjust=False).mean()
    out["ema50"] = out["close"].ewm(span=50, adjust=False).mean()
    out["close_vs_ema20_bps"] = (out["close"] - out["ema20"]) / out["close"] * 10000.0
    out["close_vs_ema50_bps"] = (out["close"] - out["ema50"]) / out["close"] * 10000.0
    out["ema20_slope_10_bps"] = (out["ema20"] / out["ema20"].shift(10) - 1.0) * 10000.0
    out["ema50_slope_10_bps"] = (out["ema50"] / out["ema50"].shift(10) - 1.0) * 10000.0

    out["body"] = (out["close"] - out["open"]).abs()
    out["range"] = out["high"] - out["low"]
    out["lower_wick"] = np.minimum(out["open"], out["close"]) - out["low"]
    out["upper_wick"] = out["high"] - np.maximum(out["open"], out["close"])
    out["lower_wick_to_body"] = out["lower_wick"] / out["body"].replace(0, np.nan)
    out["green_signal"] = out["close"] >= out["open"]
    out["volume_ma20_prior"] = out["volume"].rolling(20, min_periods=1).mean().shift(1)
    out["volume_ratio20"] = out["volume"] / out["volume_ma20_prior"]
    out["range_ma20_prior"] = out["range"].rolling(20, min_periods=1).mean().shift(1)
    out["range_ratio20"] = out["range"] / out["range_ma20_prior"]
    out["distance_from_low_60_bps"] = (out["close"] - out["rolling_low_60"]) / out["close"] * 10000.0
    out["room_to_high_60_bps"] = (out["rolling_high_60"] - out["close"]) / out["close"] * 10000.0
    return out


def _row_at_signal(features: pd.DataFrame, signal_time_utc: str) -> pd.Series:
    ts = pd.Timestamp(signal_time_utc).tz_convert("UTC")
    matched = features[features["open_time_utc"] == ts]
    if matched.empty:
        raise ValueError(f"signal time not found: {signal_time_utc}")
    return matched.iloc[0]


def _feature_record(
    *,
    features: pd.DataFrame,
    item_id: str,
    group: str,
    reason: str,
    signal_time_utc: str,
    entry_time_utc: str,
    entry_price_plus_5bps: float | None,
    source_type: str,
    nearest_manual_target: str | None = None,
) -> dict[str, Any]:
    row = _row_at_signal(features, signal_time_utc)
    out: dict[str, Any] = {
        "item_id": item_id,
        "group": group,
        "reason": reason,
        "signal_time_utc": signal_time_utc,
        "entry_time_utc": entry_time_utc,
        "entry_price_plus_5bps_execution_only": entry_price_plus_5bps,
        "source_type": source_type,
        "nearest_manual_target": nearest_manual_target,
        "no_lookahead_row_index": int(row.name),
        "green_signal": bool(row["green_signal"]),
        "near_low_60": bool(float(row["range_pos_60"]) <= 0.18) if not pd.isna(row["range_pos_60"]) else False,
        "below_ema20": bool(float(row["close_vs_ema20_bps"]) < 0) if not pd.isna(row["close_vs_ema20_bps"]) else False,
        "ema20_falling": bool(float(row["ema20_slope_10_bps"]) < 0) if not pd.isna(row["ema20_slope_10_bps"]) else False,
    }
    for col in FEATURE_COLUMNS:
        out[col] = _fmt_float(row.get(col))
    return out


def _manual_good_records(target_ledger: dict[str, Any], features: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for target in target_ledger["targets"]:
        exec_price = target.get("execution_price", {}).get("entry_price_with_slippage")
        rows.append(
            _feature_record(
                features=features,
                item_id=str(target["target_id"]),
                group="manual_gold",
                reason=str(target.get("target_type") or "manual_gold"),
                signal_time_utc=str(target["signal_time_utc"]),
                entry_time_utc=str(target["entry_time_utc"]),
                entry_price_plus_5bps=float(exec_price) if exec_price is not None else None,
                source_type=str(target.get("target_type") or "UNKNOWN"),
                nearest_manual_target=str(target["target_id"]),
            )
        )
    return rows


def _extra_feedback_records(summary: dict[str, Any], features: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in summary["records"]:
        rows.append(
            _feature_record(
                features=features,
                item_id=str(item["candidate_id"]),
                group=str(item["review_label"]),
                reason=str(item["review_reason"]),
                signal_time_utc=str(item["signal_time_utc"]),
                entry_time_utc=str(item["entry_time_utc"]),
                entry_price_plus_5bps=float(item["entry_price_plus_5bps"]),
                source_type=str(item.get("suggested_type") or "UNKNOWN"),
                nearest_manual_target=str(item.get("nearest_manual_target") or ""),
            )
        )
    return rows


def _summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    df = pd.DataFrame(records)
    group_summary: dict[str, Any] = {}
    for group, gdf in df.groupby("group"):
        feature_medians = {col: _fmt_float(gdf[col].median()) for col in FEATURE_COLUMNS}
        group_summary[str(group)] = {
            "count": int(len(gdf)),
            "reason_counts": dict(Counter(gdf["reason"])),
            "green_signal_share": _fmt_float(gdf["green_signal"].mean(), 3),
            "near_low_60_share": _fmt_float(gdf["near_low_60"].mean(), 3),
            "below_ema20_share": _fmt_float(gdf["below_ema20"].mean(), 3),
            "ema20_falling_share": _fmt_float(gdf["ema20_falling"].mean(), 3),
            "feature_medians": feature_medians,
        }
    return group_summary


def _render_png(out_path: Path, summary: dict[str, Any]) -> None:
    groups = ["manual_gold", "possible_entry", "manual_shift_review", "bad_noise"]
    available_groups = [group for group in groups if group in summary["group_summary"]]
    count_values = [summary["group_summary"][group]["count"] for group in available_groups]

    heat_features = [
        "ret_60m_pct",
        "range_pos_60",
        "room_to_high_60_bps",
        "close_vs_ema20_bps",
        "ema20_slope_10_bps",
        "volume_ratio20",
        "lower_wick_to_body",
    ]
    heat_data = []
    for group in available_groups:
        med = summary["group_summary"][group]["feature_medians"]
        heat_data.append([med.get(feature) or 0 for feature in heat_features])
    arr = np.array(heat_data, dtype=float)
    if arr.size:
        normalized = arr.copy()
        for idx in range(normalized.shape[1]):
            col = normalized[:, idx]
            lo = np.nanmin(col)
            hi = np.nanmax(col)
            normalized[:, idx] = 0.5 if abs(hi - lo) < 1e-12 else (col - lo) / (hi - lo)
    else:
        normalized = arr

    fig = plt.figure(figsize=(18, 10), facecolor="#101418")
    grid = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.35], width_ratios=[0.8, 1.2], hspace=0.32, wspace=0.22)
    ax_counts = fig.add_subplot(grid[0, 0])
    ax_heat = fig.add_subplot(grid[:, 1])
    ax_text = fig.add_subplot(grid[1, 0])

    for ax in [ax_counts, ax_heat, ax_text]:
        ax.set_facecolor("#101418")
        for spine in ax.spines.values():
            spine.set_color("#34414a")

    colors = ["#00e676" if g == "manual_gold" else "#26c6da" if g == "possible_entry" else "#ffb300" if g == "manual_shift_review" else "#ff5252" for g in available_groups]
    ax_counts.bar(available_groups, count_values, color=colors)
    ax_counts.set_title("Groups after target-led feedback", color="white", fontsize=13)
    ax_counts.tick_params(colors="#cfd8dc", labelrotation=20)
    ax_counts.grid(axis="y", color="#263238", alpha=0.75)
    for idx, value in enumerate(count_values):
        ax_counts.text(idx, value + 0.6, str(value), ha="center", color="white", fontsize=11)

    im = ax_heat.imshow(normalized, aspect="auto", cmap="viridis", vmin=0, vmax=1)
    ax_heat.set_xticks(range(len(heat_features)), labels=heat_features, rotation=35, ha="right")
    ax_heat.set_yticks(range(len(available_groups)), labels=available_groups)
    ax_heat.tick_params(colors="#cfd8dc")
    ax_heat.set_title("Median no-lookahead feature contrast (normalized by feature)", color="white", fontsize=13)
    for i, group in enumerate(available_groups):
        med = summary["group_summary"][group]["feature_medians"]
        for j, feature in enumerate(heat_features):
            value = med.get(feature)
            label = "-" if value is None else f"{value:.2f}"
            ax_heat.text(j, i, label, ha="center", va="center", color="white", fontsize=8)
    cbar = fig.colorbar(im, ax=ax_heat, fraction=0.026, pad=0.02)
    cbar.ax.tick_params(colors="#cfd8dc")

    ax_text.axis("off")
    notes = [
        "NO LOOKAHEAD boundary:",
        "- signal candle is closed",
        "- entry candle OHLCV excluded",
        "- future return / TP / SL / MFE / MAE excluded",
        "",
        "Working hypotheses:",
        "1. local low alone is not enough",
        "2. trend/context filter is required",
        "3. possible_entry is not gold",
        "4. manual_shift_review needs zoom-lock",
    ]
    ax_text.text(0.02, 0.98, "\n".join(notes), color="#cfd8dc", fontsize=12, va="top", family="monospace")

    fig.suptitle("LOW_ANCHOR V1 no-lookahead feature audit | NO ML/OPTUNA", color="white", fontsize=16)
    fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = [
        "item_id",
        "group",
        "reason",
        "signal_time_utc",
        "entry_time_utc",
        "entry_price_plus_5bps_execution_only",
        "source_type",
        "nearest_manual_target",
        "green_signal",
        "near_low_60",
        "below_ema20",
        "ema20_falling",
        *FEATURE_COLUMNS,
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col) for col in columns})


def write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Low Anchor V1 No-Lookahead Feature Audit",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: сравнить ручные хорошие входы, possible, manual-shift и reject по признакам, которые видны до входа.",
        "",
        "## Граница no-lookahead",
        "",
        "- Используется закрытая `signal`-свеча и прошлый контекст.",
        "- `entry`-свеча не используется как признак выбора.",
        "- Future return, TP/SL, MFE/MAE не используются.",
        "- `entry_price_plus_5bps` хранится только как execution/control.",
        "- Это audit, не ML dataset.",
        "",
        "## Группы",
        "",
        "| group | count | green | near_low_60 | below_ema20 | ema20_falling |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for group, data in payload["group_summary"].items():
        lines.append(
            f"| `{group}` | `{data['count']}` | `{data['green_signal_share']}` | "
            f"`{data['near_low_60_share']}` | `{data['below_ema20_share']}` | `{data['ema20_falling_share']}` |"
        )
    lines.extend(["", "## Медианы признаков", ""])
    for group, data in payload["group_summary"].items():
        lines.append(f"### `{group}`")
        med = data["feature_medians"]
        for feature in FEATURE_COLUMNS:
            lines.append(f"- `{feature}`: `{med.get(feature)}`")
        lines.append("")
    lines.extend(
        [
            "## Рабочие выводы",
            "",
            "1. Локальный low сам по себе не является сигналом входа.",
            "2. Нужно отделять слабый low от рабочего low через контекст до entry: тренд, положение в диапазоне, силу reclaim, объем/диапазон signal-свечи и расстояние до ближайшего сопротивления.",
            "3. `possible_entry` не переводится в gold: это кандидаты для отдельного сравнения с ручными `Mxx`.",
            "4. `manual_shift_review` не переводится в label: сначала нужен отдельный zoom-lock с точным временем и ценой.",
            "5. Следующий шаг: либо zoom-review для `manual_shift_review`, либо draft feature checklist/passport для no-lookahead scorer без ML.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    day = "2026-05-14"
    symbol = "SOLUSDT"
    timeframe = "1m"
    out_dir = root / "reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/feature_audit_v0"
    out_dir.mkdir(parents=True, exist_ok=True)

    target_ledger_path = root / "reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_M01_M19.json"
    feedback_summary_path = root / "reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/feedback_summary_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_20260701.json"

    df = _load_ohlcv(_source_csv(root, day, timeframe, symbol))
    features = _add_no_lookahead_features(df)
    target_ledger = _read_json(target_ledger_path)
    feedback_summary = _read_json(feedback_summary_path)

    records = _manual_good_records(target_ledger, features)
    records.extend(_extra_feedback_records(feedback_summary, features))
    group_summary = _summarize(records)

    json_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701.json"
    csv_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701.csv"
    report_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701_RU.md"
    png_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701.png"

    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "rail_point": "LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_NO_ML_NO_OPTUNA",
        "symbol": symbol,
        "timeframe": timeframe,
        "day_utc": day,
        "source_target_ledger": str(target_ledger_path.relative_to(root)).replace("\\", "/"),
        "source_feedback_summary": str(feedback_summary_path.relative_to(root)).replace("\\", "/"),
        "record_count": len(records),
        "group_summary": group_summary,
        "records": records,
        "no_lookahead_boundary": {
            "signal_candle_closed_allowed": True,
            "past_context_allowed": True,
            "entry_candle_ohlcv_allowed": False,
            "future_return_allowed": False,
            "tp_sl_allowed": False,
            "mfe_mae_allowed": False,
            "entry_price_is_execution_only": True,
        },
        "artifacts": {
            "json": str(json_path.relative_to(root)).replace("\\", "/"),
            "csv": str(csv_path.relative_to(root)).replace("\\", "/"),
            "report_ru": str(report_path.relative_to(root)).replace("\\", "/"),
            "png": str(png_path.relative_to(root)).replace("\\", "/"),
        },
        "optuna_allowed": False,
        "ml_allowed": False,
    }

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(csv_path, records)
    write_report(report_path, payload)
    _render_png(png_path, payload)

    print(json.dumps(payload["artifacts"], ensure_ascii=False, indent=2))
    print(json.dumps({"record_count": len(records), "groups": {k: v["count"] for k, v in group_summary.items()}}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
