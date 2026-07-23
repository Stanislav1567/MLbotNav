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

from mlbotnav.visual_entry_dca_risk_audit_v0 import _load_feedback, _ts
from mlbotnav.visual_entry_low_anchor_suggester import (
    _draw_candles,
    _load_ohlcv,
    _source_csv,
    _style_axis,
)


STATUS = "SIGNIFICANT_LOW_CALIBRATION_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def _fmt_ts(value: Any) -> str:
    return _ts(value).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fmt_minute(value: Any) -> str:
    return _ts(value).strftime("%H:%M")


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


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


def _load_dca_rows(dca_run_dir: Path, day: str) -> list[dict[str, Any]]:
    path = dca_run_dir / "DCA_RISK_AUDIT_V0_TRADES.csv"
    if not path.exists():
        raise FileNotFoundError(f"Не найден DCA trades CSV: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if str(row.get("day_utc")) == day]
    return sorted(rows, key=lambda row: str(row.get("signal_time_utc")))


def _row_at(df: pd.DataFrame, ts: pd.Timestamp) -> tuple[int | None, pd.Series | None]:
    matches = df.index[df["open_time_utc"] == ts].tolist()
    if not matches:
        return None, None
    idx = int(matches[0])
    return idx, df.iloc[idx]


def _window(df: pd.DataFrame, idx: int, size: int) -> pd.DataFrame:
    start = max(0, idx - size + 1)
    return df.iloc[start : idx + 1]


def _classify_significance(
    *,
    row: dict[str, Any],
    features: dict[str, Any],
    feedback_status: str,
    last_keep: dict[str, Any] | None,
    min_drop_60_pct: float,
    min_drop_180_pct: float,
    duplicate_minutes: int,
    duplicate_lower_improve_pct: float,
) -> tuple[str, str]:
    if feedback_status.startswith("USER_REJECT_CURRENT"):
        return "USER_REJECT_CURRENT_ENTRY", "user_feedback_current_entry_rejected"
    if "SHIFT_PENDING" in feedback_status:
        return "USER_SHIFT_PENDING_REANCHOR", "user_feedback_needs_new_low_time"
    if feedback_status.startswith(("USER_KEEP_CURRENT", "USER_APPROVE_CURRENT")):
        return "KEEP_SIGNIFICANT_LOW_V0", "user_feedback_current_entry_approved"

    signal_time = _ts(row["signal_time_utc"])
    anchor_low = float(features["anchor_low_price"])
    new_low_60 = bool(features["is_new_low_60"])
    new_low_180 = bool(features["is_new_low_180"])
    drop_60 = float(features["drop_from_high_60_pct"])
    drop_180 = float(features["drop_from_high_180_pct"])
    entry_from_anchor_bps = float(features["entry_from_anchor_bps"])

    base_reasons: list[str] = []
    if new_low_60 and drop_60 <= -min_drop_60_pct:
        base_reasons.append("new_low_60_with_drop")
    if new_low_180 and drop_180 <= -min_drop_180_pct:
        base_reasons.append("new_low_180_with_drop")
    if drop_180 <= -(min_drop_180_pct * 1.4):
        base_reasons.append("deep_context_drop")

    if not base_reasons:
        return "REJECT_NOT_SIGNIFICANT_LOW_V0", "not_new_or_not_deep_enough"

    if entry_from_anchor_bps > 28.0:
        return "REJECT_ENTRY_TOO_FAR_FROM_LOW_V0", f"entry_from_anchor_bps={entry_from_anchor_bps:.2f}"

    if last_keep is not None:
        prev_time = _ts(last_keep["signal_time_utc"])
        minutes = (signal_time - prev_time).total_seconds() / 60.0
        prev_low = float(last_keep["anchor_low_price"])
        lower_improve = (anchor_low / prev_low - 1.0) * 100.0
        if minutes <= duplicate_minutes and lower_improve > -duplicate_lower_improve_pct:
            return "REJECT_DUPLICATE_BASIN_LOW_V0", (
                f"duplicate_basin {minutes:.0f}m lower_improve={lower_improve:.3f}%"
            )

    return "KEEP_SIGNIFICANT_LOW_V0", "+".join(base_reasons)


def build_calibration_rows(
    *,
    df: pd.DataFrame,
    dca_rows: list[dict[str, Any]],
    feedback_map: dict[str, dict[str, str]],
    min_drop_60_pct: float,
    min_drop_180_pct: float,
    duplicate_minutes: int,
    duplicate_lower_improve_pct: float,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    last_keep: dict[str, Any] | None = None

    for row in dca_rows:
        signal_time = _ts(row["signal_time_utc"])
        anchor_time = _ts(row["anchor_time_utc"])
        entry_time = _ts(row["entry_time_utc"])
        signal_idx, signal = _row_at(df, signal_time)
        anchor_idx, anchor = _row_at(df, anchor_time)
        if signal_idx is None or signal is None or anchor_idx is None or anchor is None:
            continue

        w60 = _window(df, signal_idx, 60)
        w180 = _window(df, signal_idx, 180)
        high_60 = float(w60["high"].max())
        high_180 = float(w180["high"].max())
        low_60 = float(w60["low"].min())
        low_180 = float(w180["low"].min())
        anchor_low = _safe_float(row.get("anchor_low_price"))
        entry_open = _safe_float(row.get("entry_open_price"))
        signal_close = float(signal["close"])
        features = {
            "anchor_low_price": anchor_low,
            "is_new_low_60": anchor_low <= low_60 + 1e-9,
            "is_new_low_180": anchor_low <= low_180 + 1e-9,
            "drop_from_high_60_pct": (anchor_low / high_60 - 1.0) * 100.0 if high_60 else 0.0,
            "drop_from_high_180_pct": (anchor_low / high_180 - 1.0) * 100.0 if high_180 else 0.0,
            "signal_close_from_anchor_bps": (signal_close / anchor_low - 1.0) * 10000.0 if anchor_low else 0.0,
            "entry_from_anchor_bps": (entry_open / anchor_low - 1.0) * 10000.0 if anchor_low else 0.0,
            "anchor_age_bars": int(signal_idx - anchor_idx),
        }
        feedback = feedback_map.get(str(row["record_id"]), {})
        feedback_status = str(feedback.get("user_status") or "USER_PENDING_REVIEW")
        status, reason = _classify_significance(
            row=row,
            features=features,
            feedback_status=feedback_status,
            last_keep=last_keep,
            min_drop_60_pct=min_drop_60_pct,
            min_drop_180_pct=min_drop_180_pct,
            duplicate_minutes=duplicate_minutes,
            duplicate_lower_improve_pct=duplicate_lower_improve_pct,
        )
        out_row = {
            "day_utc": row["day_utc"],
            "record_id": row["record_id"],
            "candidate_id": row["candidate_id"],
            "good_order_in_day": row.get("good_order_in_day"),
            "signal_time_utc": _fmt_ts(signal_time),
            "entry_time_utc": _fmt_ts(entry_time),
            "entry_open_price": row.get("entry_open_price"),
            "entry_price_5bps": row.get("entry_price_5bps"),
            "anchor_time_utc": _fmt_ts(anchor_time),
            "anchor_low_price": row.get("anchor_low_price"),
            "risk_class_v0": row.get("risk_class_v0"),
            "review_label": row.get("review_label"),
            "user_status": feedback_status,
            "significant_low_status_v0": status,
            "significant_low_reason_v0": reason,
            "is_new_low_60": features["is_new_low_60"],
            "is_new_low_180": features["is_new_low_180"],
            "drop_from_high_60_pct": round(features["drop_from_high_60_pct"], 6),
            "drop_from_high_180_pct": round(features["drop_from_high_180_pct"], 6),
            "signal_close_from_anchor_bps": round(features["signal_close_from_anchor_bps"], 6),
            "entry_from_anchor_bps": round(features["entry_from_anchor_bps"], 6),
            "anchor_age_bars": features["anchor_age_bars"],
        }
        out.append(out_row)
        if status == "KEEP_SIGNIFICANT_LOW_V0":
            last_keep = out_row
    return out


def _status_color(status: str) -> str:
    if status == "KEEP_SIGNIFICANT_LOW_V0":
        return "#00e676"
    if "SHIFT" in status:
        return "#ffb300"
    return "#ff5252"


def render_pages(
    *,
    df: pd.DataFrame,
    rows: list[dict[str, Any]],
    day: str,
    symbol: str,
    timeframe: str,
    out_dir: Path,
    per_page: int,
) -> list[Path]:
    cols = 3
    rows_per_page = 3
    per_page = max(1, min(per_page, cols * rows_per_page))
    paths: list[Path] = []
    for page_start in range(0, len(rows), per_page):
        page_rows = rows[page_start : page_start + per_page]
        page_no = page_start // per_page + 1
        total_pages = (len(rows) + per_page - 1) // per_page
        fig, axes = plt.subplots(rows_per_page, cols, figsize=(22, 16), sharex=False)
        fig.patch.set_facecolor("#101418")
        flat_axes = list(axes.flatten())
        for ax in flat_axes:
            _style_axis(ax)

        for ax, row in zip(flat_axes, page_rows):
            signal_time = _ts(row["signal_time_utc"])
            entry_time = _ts(row["entry_time_utc"])
            anchor_time = _ts(row["anchor_time_utc"])
            start = entry_time - pd.Timedelta(minutes=25)
            end = entry_time + pd.Timedelta(minutes=55)
            win = df[(df["open_time_utc"] >= start) & (df["open_time_utc"] <= end)].reset_index(drop=True)
            _draw_candles(ax, win, timeframe, linewidth=0.55)

            status = str(row["significant_low_status_v0"])
            color = _status_color(status)
            entry_open = _safe_float(row["entry_open_price"])
            entry_exec = _safe_float(row["entry_price_5bps"])
            anchor_low = _safe_float(row["anchor_low_price"])
            ax.axvline(signal_time.tz_convert(None), color="#ff5252", linewidth=1.0, alpha=0.45)
            ax.axvline(entry_time.tz_convert(None), color=color, linewidth=1.4, alpha=0.85)
            ax.scatter([anchor_time.tz_convert(None)], [anchor_low], s=34, color="#ff5252", edgecolors="#0b0f12", linewidths=0.35, zorder=6)
            ax.scatter([entry_time.tz_convert(None)], [entry_open], marker="^", s=105, color=color, edgecolors="white", linewidths=0.60, zorder=8)
            ax.scatter([entry_time.tz_convert(None)], [entry_exec], marker="_", s=120, color="#ffffff", linewidths=1.3, alpha=0.82, zorder=9)

            low = min(float(win["low"].min()), anchor_low, entry_open) if not win.empty else min(anchor_low, entry_open)
            high = max(float(win["high"].max()), anchor_low, entry_open) if not win.empty else max(anchor_low, entry_open)
            pad = max((high - low) * 0.18, 0.03)
            ax.set_ylim(low - pad, high + pad)
            ax.set_xlim(start.tz_convert(None).to_pydatetime(), end.tz_convert(None).to_pydatetime())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            ax.tick_params(axis="x", labelrotation=25, labelsize=7)
            ax.tick_params(axis="y", labelsize=7)
            ax.set_title(
                f"#{row.get('good_order_in_day')} {row['record_id']} | {row['risk_class_v0']}\n"
                f"{status}\n{row['significant_low_reason_v0']}",
                color="white",
                fontsize=7,
            )
            ax.annotate(
                f"open {entry_open:.4f}\n"
                f"drop60 {float(row['drop_from_high_60_pct']):.2f}%\n"
                f"entry-low {float(row['entry_from_anchor_bps']):.1f}bps",
                xy=(entry_time.tz_convert(None), entry_open),
                xytext=(7, 10),
                textcoords="offset points",
                color=color,
                fontsize=7,
                arrowprops={"arrowstyle": "->", "color": color, "linewidth": 0.8},
            )
            if status != "KEEP_SIGNIFICANT_LOW_V0":
                ax.text(
                    0.5,
                    0.5,
                    status.replace("_", "\n", 2),
                    transform=ax.transAxes,
                    color=color,
                    fontsize=16,
                    fontweight="bold",
                    alpha=0.25,
                    ha="center",
                    va="center",
                    rotation=18,
                )

        for ax in flat_axes[len(page_rows) :]:
            ax.set_visible(False)
        fig.suptitle(
            f"{symbol} {timeframe} {day} | SIGNIFICANT_LOW_CALIBRATION_V0 | page {page_no}/{total_pages} | NO ML/OPTUNA",
            color="white",
            fontsize=15,
        )
        fig.tight_layout(rect=(0, 0, 1, 0.965))
        path = out_dir / f"SIGNIFICANT_LOW_CALIBRATION_V0_{day.replace('-', '')}_PAGE_{page_no:02d}.png"
        fig.savefig(path, dpi=165, facecolor=fig.get_facecolor())
        plt.close(fig)
        paths.append(path)
    return paths


def render_overview(
    *,
    df: pd.DataFrame,
    rows: list[dict[str, Any]],
    day: str,
    symbol: str,
    timeframe: str,
    out_path: Path,
) -> Path:
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
    _draw_candles(ax_price, df.reset_index(drop=True), timeframe, linewidth=0.34)

    if "volume" in df.columns:
        vol_colors = ["#26a69a" if close >= open_ else "#ef5350" for open_, close in zip(df["open"], df["close"])]
        ax_vol.bar(
            df["open_time_utc"].dt.tz_convert(None),
            df["volume"].astype(float),
            width=0.00055,
            color=vol_colors,
            alpha=0.55,
        )
    ax_vol.set_ylabel("Volume", color="white", fontsize=9)

    label_counts: Counter[str] = Counter()
    for row in rows:
        status = str(row["significant_low_status_v0"])
        color = _status_color(status)
        entry_time = _ts(row["entry_time_utc"]).tz_convert(None)
        signal_time = _ts(row["signal_time_utc"]).tz_convert(None)
        entry_open = _safe_float(row["entry_open_price"])
        anchor_time = _ts(row["anchor_time_utc"]).tz_convert(None)
        anchor_low = _safe_float(row["anchor_low_price"])
        label_counts[status] += 1

        if status == "KEEP_SIGNIFICANT_LOW_V0":
            ax_price.axvline(entry_time, color=color, linewidth=1.0, alpha=0.55)
            ax_price.scatter([entry_time], [entry_open], marker="^", s=72, color=color, edgecolors="white", linewidths=0.45, zorder=8)
            ax_price.annotate(
                str(row["candidate_id"]),
                xy=(entry_time, entry_open),
                xytext=(4, 6),
                textcoords="offset points",
                color=color,
                fontsize=7,
                fontweight="bold",
            )
        elif "SHIFT" in status:
            ax_price.axvline(entry_time, color=color, linewidth=0.9, alpha=0.42)
            ax_price.scatter([entry_time], [entry_open], marker="^", s=55, color=color, edgecolors="white", linewidths=0.35, zorder=7)
            ax_price.scatter([anchor_time], [anchor_low], s=18, color="#ff5252", edgecolors="#0b0f12", linewidths=0.25, zorder=6)
            ax_price.annotate(
                str(row["candidate_id"]),
                xy=(entry_time, entry_open),
                xytext=(4, -10),
                textcoords="offset points",
                color=color,
                fontsize=6,
                alpha=0.9,
            )
        else:
            ax_price.axvline(entry_time, color=color, linewidth=0.65, alpha=0.32)
            ax_price.scatter([entry_time], [entry_open], marker="x", s=46, color=color, linewidths=1.10, alpha=0.62, zorder=7)

    ax_price.set_title(
        f"{symbol} {timeframe} {day} | SIGNIFICANT LOW CALIBRATION V0 | green=keep yellow=reanchor red=reject | NO ML/OPTUNA",
        color="white",
        fontsize=15,
    )
    ax_price.set_ylabel("Price", color="white", fontsize=10)
    ax_price.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax_vol.tick_params(axis="x", labelrotation=25, labelsize=8)
    summary = " | ".join(f"{key}={value}" for key, value in sorted(label_counts.items()))
    fig.text(0.012, 0.012, summary, color="#d8dee9", fontsize=9)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    fig.savefig(out_path, dpi=165, facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_path


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Significant Low Calibration V0",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: откалибровать low-кандидаты так, чтобы не брать все микролои подряд. Это не ML, не Optuna, не scorer и не target-lock.",
        "",
        "## Правило V0",
        "",
        "- текущие входы с пользовательским крестом считаются `USER_REJECT_CURRENT_ENTRY`;",
        "- текущие входы со стрелкой считаются `USER_SHIFT_PENDING_REANCHOR`, точную новую свечу надо снимать отдельным zoom;",
        "- без user reject low должен быть новым low в 60/180m контексте и иметь достаточное падение от prior high;",
        "- повтор внутри одного basin отбрасывается, если нет свежего более низкого low.",
        "",
        "## Сводка",
        "",
    ]
    for key, value in payload["summary"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Статусы", ""])
    for key, value in sorted(payload["status_counts"].items()):
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


def run_calibration(
    *,
    dca_run_dir: Path,
    feedback_csv: Path,
    day: str,
    symbol: str,
    timeframe: str,
    out_dir: Path,
    run_label: str,
    min_drop_60_pct: float,
    min_drop_180_pct: float,
    duplicate_minutes: int,
    duplicate_lower_improve_pct: float,
    per_page: int,
) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    if not dca_run_dir.is_absolute():
        dca_run_dir = root / dca_run_dir
    if not feedback_csv.is_absolute():
        feedback_csv = root / feedback_csv
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    run_id = f"{run_label}_{_run_stamp()}" if run_label else f"significant_low_{_run_stamp()}"
    run_dir = out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    source = _source_csv(root, day, timeframe, symbol)
    df = _load_ohlcv(source)
    dca_rows = _load_dca_rows(dca_run_dir, day)
    feedback = _load_feedback(feedback_csv)
    rows = build_calibration_rows(
        df=df,
        dca_rows=dca_rows,
        feedback_map=feedback,
        min_drop_60_pct=min_drop_60_pct,
        min_drop_180_pct=min_drop_180_pct,
        duplicate_minutes=duplicate_minutes,
        duplicate_lower_improve_pct=duplicate_lower_improve_pct,
    )

    csv_path = run_dir / f"SIGNIFICANT_LOW_CALIBRATION_V0_{day.replace('-', '')}.csv"
    json_path = run_dir / f"SIGNIFICANT_LOW_CALIBRATION_V0_{day.replace('-', '')}.json"
    report_path = run_dir / f"SIGNIFICANT_LOW_CALIBRATION_V0_{day.replace('-', '')}_RU.md"
    overview_path = run_dir / f"SIGNIFICANT_LOW_CALIBRATION_V0_{day.replace('-', '')}_OVERVIEW.png"
    render_overview(df=df, rows=rows, day=day, symbol=symbol, timeframe=timeframe, out_path=overview_path)
    pages = render_pages(df=df, rows=rows, day=day, symbol=symbol, timeframe=timeframe, out_dir=run_dir, per_page=per_page)
    _write_csv(csv_path, rows)
    status_counts = dict(Counter(row["significant_low_status_v0"] for row in rows))
    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "run_id": run_id,
        "day_utc": day,
        "params": {
            "min_drop_60_pct": min_drop_60_pct,
            "min_drop_180_pct": min_drop_180_pct,
            "duplicate_minutes": duplicate_minutes,
            "duplicate_lower_improve_pct": duplicate_lower_improve_pct,
        },
        "summary": {
            "rows_total": len(rows),
            "keep_significant": status_counts.get("KEEP_SIGNIFICANT_LOW_V0", 0),
            "user_reject_or_shift": sum(
                count for status, count in status_counts.items() if status.startswith("USER_")
            ),
            "machine_reject": sum(
                count for status, count in status_counts.items() if status.startswith("REJECT_")
            ),
        },
        "status_counts": status_counts,
        "artifacts": {
            "run_dir": _rel(root, run_dir),
            "csv": _rel(root, csv_path),
            "json": _rel(root, json_path),
            "report_ru": _rel(root, report_path),
            "overview_png": _rel(root, overview_path),
            "pages": [_rel(root, path) for path in pages],
        },
        "guardrails": ["NO_ML", "NO_OPTUNA", "NO_SCORER", "NO_TARGET_LOCK", "NO_API"],
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    _write_report(report_path, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dca-run-dir", required=True)
    parser.add_argument("--feedback-csv", required=True)
    parser.add_argument("--day", default="2026-05-02")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0")
    parser.add_argument("--run-label", default="siglow_20260502")
    parser.add_argument("--min-drop-60-pct", type=float, default=0.20)
    parser.add_argument("--min-drop-180-pct", type=float, default=0.35)
    parser.add_argument("--duplicate-minutes", type=int, default=45)
    parser.add_argument("--duplicate-lower-improve-pct", type=float, default=0.15)
    parser.add_argument("--per-page", type=int, default=9)
    args = parser.parse_args()

    payload = run_calibration(
        dca_run_dir=Path(args.dca_run_dir),
        feedback_csv=Path(args.feedback_csv),
        day=args.day,
        symbol=args.symbol,
        timeframe=args.timeframe,
        out_dir=Path(args.out_dir),
        run_label=args.run_label,
        min_drop_60_pct=args.min_drop_60_pct,
        min_drop_180_pct=args.min_drop_180_pct,
        duplicate_minutes=args.duplicate_minutes,
        duplicate_lower_improve_pct=args.duplicate_lower_improve_pct,
        per_page=args.per_page,
    )
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
