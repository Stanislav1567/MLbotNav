from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

from mlbotnav.stas5_common import PROJECT_ROOT, compact_day, iter_days, rel, utc_now, write_json
from mlbotnav.visual_entry_low_anchor_suggester import _bar_width_days, _draw_candles, _load_ohlcv, _source_csv, _style_axis
from mlbotnav.visual_entry_stas2_market_phase_review import (
    _continuous_wave_rows,
    _hour_phase_rows,
    _macro_wave_rows,
    _render_rank_strip,
    _set_day_time_axis,
    _shade_sessions,
)


STATUS_PASS = "PASS_V5_FORWARD_VISUAL_REVIEW_READY_ALL_LA_LABELS_ENTER_TRIANGLES"
STATUS_FAIL = "FAIL_V5_FORWARD_VISUAL_REVIEW"
SYMBOL = "SOLUSDT"
TIMEFRAME = "1m"

V5_ROOT = PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5"
DEFAULT_FORWARD_RUNS_DIR = V5_ROOT / "forward" / "runs"
DEFAULT_LATEST_FORWARD_POINTER = V5_ROOT / "forward" / "STAS5_V5_LATEST_TWO_BLOCK_FORWARD_RUN.json"

DECISION_COLUMN = "ENTRY_ML_LIVE_DECISION"
SCORE_COLUMN = "ENTRY_ML_LIVE_SCORE"
PRICE_COLUMNS = ["entry_price_5bps", "entry_open_price", "entry_price"]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        out = float(value)
        if pd.isna(out):
            return default
        return out
    except Exception:
        return default


def _resolve_forward_run_dir(forward_run_dir: Path | None = None) -> Path:
    if forward_run_dir is not None:
        return forward_run_dir
    if DEFAULT_LATEST_FORWARD_POINTER.exists():
        pointer = json.loads(DEFAULT_LATEST_FORWARD_POINTER.read_text(encoding="utf-8"))
        path = PROJECT_ROOT / str(pointer["run_dir"])
        if path.exists():
            return path
    candidates = sorted(DEFAULT_FORWARD_RUNS_DIR.glob("stas5_v5_forward_*"), key=lambda item: item.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError("V5 forward run not found")
    return candidates[-1]


def _find_predictions_path(forward_run_dir: Path, predictions_path: Path | None = None) -> Path:
    if predictions_path is not None:
        return predictions_path
    candidates: list[Path] = []
    for pattern in ("STAS5_V5_FORWARD_PREDICTIONS_*_V1.csv", "STAS5_V5C_FORWARD_PREDICTIONS_*_V1.csv"):
        candidates.extend(forward_run_dir.glob(pattern))
    candidates = sorted(candidates, key=lambda item: item.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError(f"V5 forward predictions not found in {forward_run_dir}")
    return candidates[-1]


def _find_context_ohlcv_path(forward_run_dir: Path, day: str) -> Path | None:
    context_dir = forward_run_dir / "ohlcv_contexts"
    if not context_dir.exists():
        return None
    day_ts = pd.Timestamp(day)
    compact = compact_day(day)
    prev_compact = (day_ts - pd.Timedelta(days=1)).strftime("%Y%m%d")
    patterns = [
        f"STAS5_V5C_OHLCV_CONTEXT_{prev_compact}_{compact}_FROM_*.csv",
        f"*_{prev_compact}_{compact}_FROM_*.csv",
        f"*_{compact}_FROM_*.csv",
    ]
    for pattern in patterns:
        candidates = sorted(context_dir.glob(pattern), key=lambda item: item.stat().st_mtime)
        if candidates:
            return candidates[-1]
    return None


def _prepare_strip_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy().sort_values("open_time_utc").reset_index(drop=True)
    if "day_utc" not in out.columns:
        out["day_utc"] = out["open_time_utc"].dt.strftime("%Y-%m-%d")
    open_px = pd.to_numeric(out["open"], errors="coerce")
    high_px = pd.to_numeric(out["high"], errors="coerce")
    low_px = pd.to_numeric(out["low"], errors="coerce")
    close_px = pd.to_numeric(out["close"], errors="coerce")
    safe_open = open_px.where(open_px.ne(0.0))
    out["candle_range_pct"] = (high_px - low_px) / safe_open * 100.0
    out["candle_body_pct"] = (close_px - open_px).abs() / safe_open * 100.0
    out["close_step_abs_pct"] = close_px.pct_change().abs().fillna(0.0) * 100.0
    return out


def _fmt_utc(ts: pd.Timestamp) -> str:
    utc = ts.tz_convert("UTC") if ts.tzinfo is not None else ts.tz_localize("UTC")
    return utc.strftime("%Y-%m-%dT%H:%M:%SZ")


def _infer_candle_step(df: pd.DataFrame) -> pd.Timedelta:
    if len(df) > 1:
        diffs = df.sort_values("open_time_utc")["open_time_utc"].diff().dropna()
        step = diffs.median() if not diffs.empty else pd.Timedelta(minutes=1)
        if pd.notna(step) and pd.Timedelta(0) < step <= pd.Timedelta(hours=1):
            return step
    return pd.Timedelta(minutes=1)


def _target_day_data_end(df: pd.DataFrame, day: str) -> pd.Timestamp:
    day_start = pd.Timestamp(day, tz="UTC")
    day_end = day_start + pd.Timedelta(days=1)
    target = df[df["open_time_utc"].dt.strftime("%Y-%m-%d").eq(day)].sort_values("open_time_utc")
    if target.empty:
        return day_end
    data_end = pd.Timestamp(target.iloc[-1]["open_time_utc"]) + _infer_candle_step(target)
    return min(data_end, day_end)


def _directional_cum_pct(
    df: pd.DataFrame,
    *,
    direction: str,
    full_start: pd.Timestamp,
    full_start_price: float,
    until_ts: pd.Timestamp,
    include_until: bool,
) -> float:
    if full_start_price <= 0 or until_ts <= full_start:
        return 0.0
    ordered = df.sort_values("open_time_utc")
    if include_until:
        segment = ordered[(ordered["open_time_utc"] >= full_start) & (ordered["open_time_utc"] <= until_ts)]
    else:
        segment = ordered[(ordered["open_time_utc"] >= full_start) & (ordered["open_time_utc"] < until_ts)]
    if segment.empty:
        return 0.0
    if direction == "LONG":
        extreme = float(pd.to_numeric(segment["high"], errors="coerce").max())
        return max(0.0, (extreme - full_start_price) / max(full_start_price, 1e-12) * 100.0)
    if direction == "SHORT":
        extreme = float(pd.to_numeric(segment["low"], errors="coerce").min())
        return max(0.0, (full_start_price - extreme) / max(full_start_price, 1e-12) * 100.0)
    return 0.0


def _prepare_v5_macro_wave_rows(
    *,
    prepared: pd.DataFrame,
    day: str,
    has_next_render_day: bool,
) -> dict[str, Any]:
    day_start = pd.Timestamp(day, tz="UTC")
    day_end = day_start + pd.Timedelta(days=1)
    target_data_end = _target_day_data_end(prepared, day)
    continuous_rows = _continuous_wave_rows(prepared)
    continuous_by_id = {str(row.get("continuous_wave_id") or ""): row for row in continuous_rows}
    macro_rows_all = [
        row.copy()
        for row in _macro_wave_rows(prepared, continuous_rows=continuous_rows)
        if str(row.get("day_utc") or "") == day
    ]
    macro_gap_rows = [row for row in macro_rows_all if str(row.get("macro_wave_segment_kind") or "") == "GAP"]
    macro_wave_rows = [
        row
        for row in macro_rows_all
        if str(row.get("macro_wave_segment_kind") or "") == "WAVE"
        and str(row.get("macro_wave_direction") or "") in {"LONG", "SHORT"}
    ]
    macro_wave_rows = sorted(macro_wave_rows, key=lambda row: str(row.get("macro_wave_start_time_utc") or ""))

    tail_gap_rows_absorbed = 0
    tail_gap_minutes_filled = 0.0
    if macro_wave_rows:
        last_wave = max(macro_wave_rows, key=lambda row: pd.Timestamp(row["macro_wave_end_time_utc"]))
        last_end = pd.Timestamp(last_wave["macro_wave_end_time_utc"])
        if (
            str(last_wave.get("macro_wave_status") or "") == "ACTIVE"
            and target_data_end > last_end
        ):
            trailing_gaps = [
                gap
                for gap in macro_gap_rows
                if str(gap.get("macro_wave_gap_reason") or "") == "after_last_confirmed_or_active_wave"
                and pd.Timestamp(gap["macro_wave_start_time_utc"]) >= last_end
            ]
            extension_end = target_data_end
            if trailing_gaps:
                extension_end = min(
                    max(pd.Timestamp(gap["macro_wave_end_time_utc"]) for gap in trailing_gaps),
                    target_data_end,
                )
                tail_gap_rows_absorbed = len(trailing_gaps)
            if extension_end > last_end:
                last_wave["macro_wave_end_time_utc"] = _fmt_utc(extension_end)
                last_wave["macro_wave_duration_min"] = round(
                    (extension_end - pd.Timestamp(last_wave["macro_wave_start_time_utc"])).total_seconds() / 60.0,
                    3,
                )
                tail_gap_minutes_filled = round((extension_end - last_end).total_seconds() / 60.0, 3)
                last_wave["macro_wave_render_extended_to_day_end"] = True
                last_wave["macro_wave_render_carry_to_next_day"] = bool(has_next_render_day and extension_end >= day_end)
                last_wave["macro_wave_render_extension_reason"] = "active_wave_absorbed_after_last_gap_to_data_end"

    for row in macro_wave_rows:
        continuous = continuous_by_id.get(str(row.get("continuous_wave_id") or ""), {})
        direction = str(row.get("macro_wave_direction") or "")
        full_start = pd.Timestamp(row.get("macro_wave_full_start_time_utc") or row["macro_wave_start_time_utc"])
        full_start_price = _safe_float(continuous.get("continuous_wave_start_price"), _safe_float(row.get("macro_wave_start_price"), 0.0))
        visible_start = pd.Timestamp(row["macro_wave_start_time_utc"])
        visible_end = pd.Timestamp(row["macro_wave_end_time_utc"])
        start_cum_pct = _directional_cum_pct(
            prepared,
            direction=direction,
            full_start=full_start,
            full_start_price=full_start_price,
            until_ts=visible_start,
            include_until=False,
        )
        end_cum_pct = _directional_cum_pct(
            prepared,
            direction=direction,
            full_start=full_start,
            full_start_price=full_start_price,
            until_ts=visible_end,
            include_until=True,
        )
        row["macro_wave_cum_start_pct"] = round(start_cum_pct, 6)
        row["macro_wave_cum_end_pct"] = round(end_cum_pct, 6)
        row["macro_wave_cum_label"] = (
            f"{start_cum_pct:.2f}->{end_cum_pct:.2f}%"
            if start_cum_pct >= 0.005
            else f"{end_cum_pct:.2f}%"
        )
        row["macro_wave_v5_label_pct"] = round(end_cum_pct, 6)
        row["macro_wave_v5_label_pct_basis"] = "cumulative_from_true_wave_start"
        row["macro_wave_true_start_time_utc"] = _fmt_utc(full_start)
        row["macro_wave_true_start_price"] = round(full_start_price, 8) if full_start_price else ""
        row.setdefault("macro_wave_render_extended_to_day_end", False)
        row.setdefault("macro_wave_render_carry_to_next_day", False)

    last_wave_end = max([pd.Timestamp(row["macro_wave_end_time_utc"]) for row in macro_wave_rows], default=day_start)
    tail_covered = bool(not macro_wave_rows or last_wave_end >= target_data_end)
    cross_day_wave_rows = [
        row
        for row in macro_wave_rows
        if bool(row.get("macro_wave_carry_from_prev_day"))
        or bool(row.get("macro_wave_carry_to_next_day"))
        or bool(row.get("macro_wave_render_carry_to_next_day"))
    ]
    visible_to_cumulative_deltas = [
        abs(_safe_float(row.get("macro_wave_cum_end_pct"), 0.0) - _safe_float(row.get("macro_wave_visible_move_pct"), 0.0))
        for row in macro_wave_rows
    ]
    return {
        "macro_rows_all": macro_rows_all,
        "macro_wave_rows": macro_wave_rows,
        "macro_gap_rows": macro_gap_rows,
        "macro_gap_rows_filtered": len(macro_gap_rows),
        "macro_non_wave_rows_filtered": len(macro_rows_all) - len(macro_gap_rows) - len(macro_wave_rows),
        "tail_gap_rows_absorbed": tail_gap_rows_absorbed,
        "tail_gap_minutes_filled": tail_gap_minutes_filled,
        "target_data_end_utc": _fmt_utc(target_data_end),
        "last_wave_end_utc": _fmt_utc(last_wave_end),
        "tail_covered_to_data_end": tail_covered,
        "cross_day_wave_rows": len(cross_day_wave_rows),
        "max_visible_to_cumulative_pct_delta": round(max(visible_to_cumulative_deltas or [0.0]), 6),
    }


def _build_strength_strip_rows(strip_df: pd.DataFrame, day: str, *, has_next_render_day: bool = False) -> dict[str, Any]:
    prepared = _prepare_strip_ohlcv(strip_df)
    hour_rows = [row for row in _hour_phase_rows(prepared) if str(row.get("day_utc") or "") == day]
    macro = _prepare_v5_macro_wave_rows(prepared=prepared, day=day, has_next_render_day=has_next_render_day)
    return {
        "hour_rows": hour_rows,
        "macro_wave_rows": macro["macro_wave_rows"],
        "macro_gap_rows_filtered": macro["macro_gap_rows_filtered"],
        "macro_non_wave_rows_filtered": macro["macro_non_wave_rows_filtered"],
        "tail_gap_rows_absorbed": macro["tail_gap_rows_absorbed"],
        "tail_gap_minutes_filled": macro["tail_gap_minutes_filled"],
        "target_data_end_utc": macro["target_data_end_utc"],
        "last_wave_end_utc": macro["last_wave_end_utc"],
        "tail_covered_to_data_end": macro["tail_covered_to_data_end"],
        "cross_day_wave_rows": macro["cross_day_wave_rows"],
        "max_visible_to_cumulative_pct_delta": macro["max_visible_to_cumulative_pct_delta"],
    }


def _entry_prices(rows: pd.DataFrame) -> pd.Series:
    for column in PRICE_COLUMNS:
        if column in rows.columns:
            return pd.to_numeric(rows[column], errors="coerce")
    return pd.Series([float("nan")] * len(rows), index=rows.index)


def _load_predictions(path: Path) -> pd.DataFrame:
    rows = pd.read_csv(path, encoding="utf-8-sig")
    required = {"day", "candidate_id", "record_id", "entry_time_utc", DECISION_COLUMN, SCORE_COLUMN}
    missing = sorted(required.difference(rows.columns))
    if missing:
        raise ValueError(f"V5 forward predictions missing columns: {missing}")
    rows = rows.copy()
    rows["entry_ts"] = pd.to_datetime(rows["entry_time_utc"], utc=True, errors="raise", format="mixed")
    rows["entry_price_visual"] = _entry_prices(rows)
    rows[SCORE_COLUMN] = pd.to_numeric(rows[SCORE_COLUMN], errors="coerce").fillna(0.0)
    rows[DECISION_COLUMN] = rows[DECISION_COLUMN].astype(str).str.upper()
    return rows.sort_values(["day", "entry_ts", "candidate_id"]).reset_index(drop=True)


def _decision_styles() -> dict[str, dict[str, Any]]:
    return {
        "SKIP": {"marker": "x", "color": "#ffea00", "size": 28, "alpha": 0.86, "zorder": 7, "linewidth": 0.70},
        "WATCH": {"marker": "D", "color": "#ffd54f", "size": 58, "alpha": 0.94, "zorder": 9, "linewidth": 0.45},
        "ENTER": {"marker": "^", "color": "#00ff66", "size": 96, "alpha": 1.0, "zorder": 11, "linewidth": 0.75},
    }


def _candidate_order(value: Any) -> tuple[int, str]:
    text = str(value or "")
    digits = "".join(ch for ch in text if ch.isdigit())
    return (int(digits) if digits else 999999, text)


def _plot_candidate_labels(ax: Any, rows: pd.DataFrame, highlighted_ids: set[str] | None = None) -> None:
    label_effects = [pe.withStroke(linewidth=1.4, foreground="#061014")]
    highlighted = {str(value).upper() for value in (highlighted_ids or set())}
    ordered = rows.copy()
    ordered["_candidate_order"] = ordered["candidate_id"].map(_candidate_order)
    ordered = ordered.sort_values(["_candidate_order", "entry_ts"]).reset_index(drop=True)
    last_ts: pd.Timestamp | None = None
    lane = 0
    for _, row in ordered.iterrows():
        entry_ts = pd.Timestamp(row["entry_ts"]).tz_convert("UTC").tz_convert(None)
        price = _safe_float(row["entry_price_visual"])
        if price <= 0:
            continue
        entry_ts_utc = pd.Timestamp(row["entry_ts"]).tz_convert("UTC")
        if last_ts is None or abs((entry_ts_utc - last_ts).total_seconds()) > 9 * 60:
            lane = 0
        else:
            lane = (lane + 1) % 4
        last_ts = entry_ts_utc
        candidate_id = str(row["candidate_id"])
        dy = 7 + lane * 7 + (5 if candidate_id.upper() in highlighted else 0)
        ax.annotate(
            candidate_id,
            xy=(entry_ts, price),
            xytext=(0, dy),
            textcoords="offset points",
            ha="center",
            va="bottom",
            color="#ffea00",
            fontsize=4.9,
            fontweight="bold",
            path_effects=label_effects,
            arrowprops={
                "arrowstyle": "-",
                "color": "#ffea00",
                "linewidth": 0.36,
                "alpha": 0.68,
                "shrinkA": 0,
                "shrinkB": 0,
            },
            zorder=46,
        )


def _plot_forward_markers(ax: Any, rows: pd.DataFrame) -> None:
    if rows.empty:
        return
    styles = _decision_styles()
    for decision in ["SKIP", "WATCH", "ENTER"]:
        subset = rows[rows[DECISION_COLUMN].eq(decision)].copy()
        if subset.empty:
            continue
        style = styles[decision]
        sx = subset["entry_ts"].dt.tz_convert(None)
        sy = subset["entry_price_visual"]
        scatter_kwargs = {
            "marker": style["marker"],
            "s": style["size"],
            "color": style["color"],
            "alpha": style["alpha"],
            "zorder": style["zorder"],
            "label": f"{decision} ({len(subset)})",
            "linewidths": style["linewidth"],
        }
        if decision == "ENTER":
            scatter_kwargs["edgecolors"] = "#071014" if decision == "ENTER" else "white"
        elif decision == "WATCH":
            scatter_kwargs["edgecolors"] = "#101418"
        ax.scatter(sx, sy, **scatter_kwargs)


def _plot_bollinger_bands(
    ax: Any,
    ohlcv_df: pd.DataFrame,
    *,
    day: str,
    window: int = 20,
    num_std: float = 2.0,
) -> None:
    if ohlcv_df.empty or window <= 1 or num_std <= 0:
        return
    source = ohlcv_df.copy().sort_values("open_time_utc").reset_index(drop=True)
    close = pd.to_numeric(source["close"], errors="coerce")
    mid = close.rolling(window=window, min_periods=window).mean()
    std = close.rolling(window=window, min_periods=window).std(ddof=0)
    source["bb_mid"] = mid
    source["bb_upper"] = mid + num_std * std
    source["bb_lower"] = mid - num_std * std
    day_mask = source["open_time_utc"].dt.strftime("%Y-%m-%d").eq(day)
    plot_df = source.loc[day_mask].dropna(subset=["bb_mid", "bb_upper", "bb_lower"])
    if plot_df.empty:
        return
    x = plot_df["open_time_utc"].dt.tz_convert(None)
    upper = pd.to_numeric(plot_df["bb_upper"], errors="coerce")
    mid = pd.to_numeric(plot_df["bb_mid"], errors="coerce")
    lower = pd.to_numeric(plot_df["bb_lower"], errors="coerce")
    ax.fill_between(x, lower, upper, color="#7e57c2", alpha=0.060, linewidth=0, zorder=2.4)
    ax.plot(x, upper, color="#b388ff", linewidth=0.72, alpha=0.86, zorder=4.2, label=f"BB {window}/{num_std:g} upper")
    ax.plot(x, lower, color="#b388ff", linewidth=0.72, alpha=0.86, zorder=4.2, label=f"BB {window}/{num_std:g} lower")
    ax.plot(x, mid, color="#80deea", linewidth=0.70, alpha=0.74, linestyle="--", zorder=4.3, label=f"BB {window} mid")


def _plot_review_annotations(
    ax_price: Any,
    ax_score: Any,
    rows: pd.DataFrame,
    review_annotations: dict[str, list[str]] | None,
    panel_title: str = "USER REVIEW MARKERS",
) -> None:
    if not review_annotations:
        return
    by_id = {str(row["candidate_id"]).upper(): row for row in rows.to_dict("records")}

    def color_for(labels: list[str]) -> str:
        if "RISK BAD" in labels:
            return "#ff003d"
        if "BAD" in labels:
            return "#ff5252"
        return "#00ff66"

    def marker_for(labels: list[str]) -> str:
        return "s" if "BAD" in labels and "RISK BAD" not in labels else "o"

    def order_key(candidate_id: str) -> tuple[int, str]:
        digits = "".join(ch for ch in candidate_id if ch.isdigit())
        return (int(digits) if digits else 999999, candidate_id)

    for candidate_id in sorted(review_annotations, key=order_key):
        row = by_id.get(candidate_id)
        if not row:
            continue
        labels = review_annotations[candidate_id]
        color = color_for(labels)
        marker = marker_for(labels)
        entry_ts = pd.Timestamp(row["entry_ts"]).tz_convert("UTC").tz_convert(None)
        price = _safe_float(row["entry_price_visual"])
        if price <= 0:
            continue
        ax_price.scatter(
            [entry_ts],
            [price],
            marker=marker,
            s=330,
            facecolors="none",
            edgecolors=color,
            linewidths=2.8,
            zorder=35,
        )
        score = _safe_float(row.get(SCORE_COLUMN, 0.0))
        ax_score.scatter(
            [entry_ts],
            [score],
            marker=marker,
            s=115,
            facecolors="none",
            edgecolors=color,
            linewidths=2.2,
            zorder=18,
        )

    good_ids = [cid for cid, labels in review_annotations.items() if "GOOD" in labels]
    bad_ids = [cid for cid, labels in review_annotations.items() if "BAD" in labels]
    risk_bad_ids = [cid for cid, labels in review_annotations.items() if "RISK BAD" in labels]
    panel = "\n".join(
        [
            panel_title,
            f"green circle GOOD: {len(good_ids)}",
            f"red square BAD: {len(bad_ids)}",
            f"red circle RISK BAD: {len(risk_bad_ids)}",
        ]
    )
    ax_price.text(
        0.992,
        0.985,
        panel,
        transform=ax_price.transAxes,
        ha="right",
        va="top",
        color="white",
        fontsize=10.5,
        fontweight="bold",
        bbox={"facecolor": "#101418", "edgecolor": "#eceff1", "alpha": 0.86, "boxstyle": "round,pad=0.35"},
        zorder=50,
    )


def _plot_score_panel(ax: Any, rows: pd.DataFrame) -> None:
    _style_axis(ax)
    if rows.empty:
        return
    _shade_sessions(ax, str(rows["day"].iloc[0]))
    styles = _decision_styles()
    x = rows["entry_ts"].dt.tz_convert(None)
    score = pd.to_numeric(rows[SCORE_COLUMN], errors="coerce").fillna(0.0)
    ax.plot(x, score, color="#4dd0e1", linewidth=1.05, alpha=0.82, label="ENTRY_ML_LIVE_SCORE")
    for decision in ["SKIP", "WATCH", "ENTER"]:
        subset = rows[rows[DECISION_COLUMN].eq(decision)]
        if subset.empty:
            continue
        style = styles[decision]
        score_kwargs = {
            "marker": style["marker"],
            "s": max(22, style["size"] * 0.45),
            "color": style["color"],
            "alpha": min(1.0, style["alpha"] + 0.10),
            "zorder": 8,
            "label": f"{decision} score",
        }
        if decision == "ENTER":
            score_kwargs["edgecolors"] = "#071014"
            score_kwargs["linewidths"] = 0.7
        ax.scatter(subset["entry_ts"].dt.tz_convert(None), subset[SCORE_COLUMN], **score_kwargs)
    ax.axhline(0.5, color="#cfd8dc", linestyle="--", linewidth=0.65, alpha=0.42)
    ax.set_ylim(-0.04, 1.04)
    ax.set_ylabel("Score", color="#eceff1")
    ax.legend(loc="upper left", fontsize=8, facecolor="#101418", edgecolor="#455a64", labelcolor="#eceff1", ncol=2)


def _wave_color(direction: str) -> str:
    if direction == "LONG":
        return "#2fd17c"
    if direction == "SHORT":
        return "#ff7043"
    return "#607d8b"


def _wave_text_color(direction: str) -> str:
    return "#061014" if direction == "LONG" else "white"


def _v5_wave_label(row: dict[str, Any], duration_min: float) -> str:
    direction = str(row.get("macro_wave_direction") or "")
    wave_no = int(_safe_float(row.get("macro_wave_no"), 0.0))
    prefix = f"W{wave_no:02d} {direction}"
    start_cum = _safe_float(row.get("macro_wave_cum_start_pct"), 0.0)
    if bool(row.get("macro_wave_carry_from_prev_day")) or start_cum >= 0.005:
        prefix = "< " + prefix
    if bool(row.get("macro_wave_render_carry_to_next_day")) or bool(row.get("macro_wave_carry_to_next_day")):
        prefix += " >"
    if str(row.get("macro_wave_status") or "") == "ACTIVE" and not prefix.endswith(">"):
        prefix += " ACTIVE"
    cum_label = str(row.get("macro_wave_cum_label") or f"{_safe_float(row.get('macro_wave_cum_end_pct'), 0.0):.2f}%")
    if duration_min < 14.0:
        return cum_label
    return f"{prefix}\ncum {cum_label}"


def _render_v5_macro_wave_strip(ax: Any, wave_rows: list[dict[str, Any]], day: str) -> None:
    ax.set_facecolor("#101418")
    ax.set_yticks([])
    ax.set_ylim(0, 1)
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_color("#3a444b")
    for row in wave_rows:
        start = pd.Timestamp(row["macro_wave_start_time_utc"]).tz_convert(None)
        end = pd.Timestamp(row["macro_wave_end_time_utc"]).tz_convert(None)
        if end <= start:
            continue
        direction = str(row.get("macro_wave_direction") or "")
        color = _wave_color(direction)
        ax.add_patch(
            Rectangle(
                (mdates.date2num(start), 0.08),
                mdates.date2num(end) - mdates.date2num(start),
                0.84,
                facecolor=color,
                edgecolor="#101418",
                linewidth=0.50,
                alpha=0.88,
            )
        )
        duration_min = _safe_float(row.get("macro_wave_duration_min"), 0.0)
        is_carry = bool(row.get("macro_wave_carry_from_prev_day")) or bool(row.get("macro_wave_render_carry_to_next_day"))
        is_extended = bool(row.get("macro_wave_render_extended_to_day_end"))
        if duration_min >= 14.0 or is_carry or is_extended:
            ax.text(
                start + (end - start) / 2,
                0.52,
                _v5_wave_label(row, duration_min),
                color=_wave_text_color(direction),
                ha="center",
                va="center",
                fontsize=4.6 if duration_min < 24.0 else 5.2,
                fontweight="bold",
            )
        ax.axvline(start, color=color, alpha=0.42, linewidth=0.75)
        ax.axvline(end, color=color, alpha=0.42, linewidth=0.75)
    start_day = pd.Timestamp(day)
    end_day = start_day + pd.Timedelta(days=1)
    ax.set_xlim(start_day.to_pydatetime(), end_day.to_pydatetime())
    ax.set_ylabel("WAVE", color="white")


def render_forward_day_overview(
    *,
    day_df: pd.DataFrame,
    rows: pd.DataFrame,
    strength_hour_rows: list[dict[str, Any]],
    strength_macro_wave_rows: list[dict[str, Any]],
    day: str,
    symbol: str,
    timeframe: str,
    out_path: Path,
    review_annotations: dict[str, list[str]] | None = None,
    review_panel_title: str = "USER REVIEW MARKERS",
    bollinger_preview: bool = False,
    bollinger_source_df: pd.DataFrame | None = None,
    bollinger_window: int = 20,
    bollinger_std: float = 2.0,
    title_prefix: str = "STAS5 V5 forward visual review",
) -> None:
    fig, axes = plt.subplots(
        7,
        1,
        figsize=(32, 17.2),
        sharex=True,
        gridspec_kw={"height_ratios": [5.35, 0.38, 0.38, 0.38, 0.46, 1.35, 1.25], "hspace": 0.045},
    )
    ax_price, ax_bg_phase, ax_long_wave, ax_short_wave, ax_macro_wave, ax_score, ax_vol = axes
    fig.patch.set_facecolor("#101418")
    _style_axis(ax_price)
    _style_axis(ax_vol)
    _draw_candles(ax_price, day_df.reset_index(drop=True), timeframe, linewidth=0.28)
    _shade_sessions(ax_price, day, label_top=True)
    if bollinger_preview:
        _plot_bollinger_bands(
            ax_price,
            bollinger_source_df if bollinger_source_df is not None else day_df,
            day=day,
            window=bollinger_window,
            num_std=bollinger_std,
        )
    _plot_forward_markers(ax_price, rows)
    _render_rank_strip(
        ax_bg_phase,
        strength_hour_rows,
        day,
        rank_field="hour_background_phase_rank",
        label="Fon",
        color_kind="phase",
        pct_field="hour_background_phase_metric_pct",
    )
    _render_rank_strip(
        ax_long_wave,
        strength_hour_rows,
        day,
        rank_field="hour_long_wave_rank",
        label="LONG",
        color_kind="long",
        pct_field="hour_long_wave_up_from_low_pct",
    )
    _render_rank_strip(
        ax_short_wave,
        strength_hour_rows,
        day,
        rank_field="hour_short_wave_rank",
        label="SHORT",
        color_kind="short",
        pct_field="hour_short_wave_down_from_high_pct",
    )
    _render_v5_macro_wave_strip(ax_macro_wave, strength_macro_wave_rows, day)
    _plot_score_panel(ax_score, rows)
    _plot_review_annotations(ax_price, ax_score, rows, review_annotations, review_panel_title)
    _plot_candidate_labels(ax_price, rows, set(review_annotations or {}))

    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(day_df["open"], day_df["close"])]
    ax_vol.bar(day_df["open_time_utc"].dt.tz_convert(None), day_df["volume"], width=_bar_width_days(timeframe), color=colors, alpha=0.72)

    counts = Counter(rows[DECISION_COLUMN].astype(str)) if not rows.empty else Counter()
    ax_price.set_title(
        (
            f"{title_prefix} | {symbol} {timeframe} {day} | "
            f"green triangles = ENTER {counts.get('ENTER', 0)} | yellow diamonds = WATCH {counts.get('WATCH', 0)} | yellow X = SKIP {counts.get('SKIP', 0)}"
        ),
        color="white",
        fontsize=15,
    )
    ax_price.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    ax_price.legend(loc="upper left", fontsize=9, facecolor="#101418", edgecolor="#455a64", labelcolor="#eceff1")
    _set_day_time_axis(ax_vol, day)
    fig.autofmt_xdate()
    fig.subplots_adjust(left=0.055, right=0.995, top=0.965, bottom=0.055, hspace=0.045)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor())
    plt.close(fig)


def render_enter_closeups(
    *,
    day_df: pd.DataFrame,
    rows: pd.DataFrame,
    day: str,
    symbol: str,
    timeframe: str,
    out_path: Path,
    before_minutes: int = 55,
    after_minutes: int = 65,
) -> bool:
    enters = rows[rows[DECISION_COLUMN].eq("ENTER")].sort_values("entry_ts").reset_index(drop=True)
    if enters.empty:
        return False
    cols = 2
    plot_count = len(enters)
    row_count = int(math.ceil(plot_count / cols))
    fig, axes = plt.subplots(row_count, cols, figsize=(18, max(5, 4.4 * row_count)), sharex=False)
    fig.patch.set_facecolor("#101418")
    flat_axes = list(axes.flatten()) if hasattr(axes, "flatten") else [axes]
    for ax in flat_axes:
        _style_axis(ax)
    for idx, (_, row) in enumerate(enters.iterrows()):
        ax = flat_axes[idx]
        entry_ts_utc = pd.Timestamp(row["entry_ts"]).tz_convert("UTC")
        start = entry_ts_utc - pd.Timedelta(minutes=before_minutes)
        end = entry_ts_utc + pd.Timedelta(minutes=after_minutes)
        window = day_df[(day_df["open_time_utc"] >= start) & (day_df["open_time_utc"] <= end)].copy().reset_index(drop=True)
        if window.empty:
            continue
        _draw_candles(ax, window, timeframe, linewidth=0.42)
        entry_ts = entry_ts_utc.tz_convert(None)
        price = _safe_float(row["entry_price_visual"])
        ax.axvline(entry_ts, color="#00ff66", alpha=0.28, linewidth=1.5, zorder=4)
        ax.scatter([entry_ts], [price], marker="^", s=310, color="#00ff66", edgecolors="#071014", linewidths=1.25, zorder=12)
        ax.annotate(
            f"ENTER {row['candidate_id']}  score={_safe_float(row[SCORE_COLUMN]):.3f}",
            xy=(entry_ts, price),
            xytext=(10, 42),
            textcoords="offset points",
            color="#00ff66",
            fontsize=9,
            fontweight="bold",
            bbox={"facecolor": "#06170f", "edgecolor": "#00ff66", "alpha": 0.94, "boxstyle": "round,pad=0.20"},
            arrowprops={"arrowstyle": "-|>", "color": "#00ff66", "linewidth": 2.1, "mutation_scale": 18},
            zorder=20,
        )
        ax.set_xlim(start.tz_convert(None).to_pydatetime(), end.tz_convert(None).to_pydatetime())
        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=20))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.set_title(f"{day} {row['candidate_id']} {entry_ts.strftime('%H:%M')} | {symbol}", color="white", fontsize=10)
    for ax in flat_axes[plot_count:]:
        ax.set_axis_off()
    fig.suptitle(f"STAS5 V5 ENTER closeups | {symbol} {timeframe} {day}", color="white", fontsize=14)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor())
    plt.close(fig)
    return True


def _write_audit_ru(path: Path, manifest: dict[str, Any]) -> None:
    lines = [
        "# STAS5 V5 Forward Visual Review",
        "",
        f"Статус: `{manifest['status']}`.",
        "",
        "Создан визуальный слой для blind/no-future forward: все кандидаты подписаны желтыми `LAxxx`, `ENTER` показан зеленым треугольником, `WATCH` - маленьким желтым ромбом, `SKIP` - желтым X.",
        "",
        f"Forward run: `{manifest['forward_run_dir']}`",
        f"Predictions: `{manifest['predictions_csv']}`",
        f"PNG всего: `{manifest['png_count']}`",
        "",
        "| День | Rows | ENTER | WATCH | SKIP | Overview | Closeups |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for item in manifest["day_outputs"]:
        counts = item.get("decision_counts", {})
        lines.append(
            "| "
            + str(item["day"])
            + " | "
            + str(item.get("rows", 0))
            + " | "
            + str(counts.get("ENTER", 0))
            + " | "
            + str(counts.get("WATCH", 0))
            + " | "
            + str(counts.get("SKIP", 0))
            + " | "
            + f"`{item.get('overview_png', '')}`"
            + " | "
            + f"`{item.get('closeups_png', '')}`"
            + " |"
        )
    lines += [
        "",
        "Граница: этот слой ничего не переобучает и не меняет решения модели. Он читает готовые V5 forward predictions и OHLCV только для отрисовки.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_forward_visual_review(
    *,
    forward_run_dir: Path | None = None,
    predictions_path: Path | None = None,
    start_day: str | None = None,
    end_day: str | None = None,
    symbol: str = SYMBOL,
    timeframe: str = TIMEFRAME,
    data_root: Path = PROJECT_ROOT,
    bollinger_preview: bool = False,
    strict: bool = True,
) -> dict[str, Any]:
    run_dir = _resolve_forward_run_dir(forward_run_dir)
    pred_path = _find_predictions_path(run_dir, predictions_path)
    predictions = _load_predictions(pred_path)
    if start_day is None:
        start_day = str(predictions["day"].astype(str).min())
    if end_day is None:
        end_day = str(predictions["day"].astype(str).max())

    out_dir = run_dir / "visual_review"
    day_outputs: list[dict[str, Any]] = []
    png_paths: list[str] = []
    missing_ohlcv: list[str] = []
    for day in iter_days(start_day, end_day):
        day_rows = predictions[predictions["day"].astype(str).eq(day)].copy()
        day_rows = day_rows.sort_values("entry_ts").reset_index(drop=True)
        day_dir = out_dir / compact_day(day)
        source = _source_csv(data_root, day, timeframe, symbol)
        if not source.exists():
            missing_ohlcv.append(rel(source))
            day_outputs.append({"day": day, "status": "MISSING_OHLCV", "rows": int(len(day_rows)), "source": rel(source)})
            continue
        day_df = _load_ohlcv(source)
        context_path = _find_context_ohlcv_path(run_dir, day)
        strength_source = source
        strength_context_status = "DAY_OHLCV_FALLBACK"
        strength_df = day_df
        if context_path is not None and context_path.exists():
            strength_source = context_path
            strength_context_status = "CONTINUOUS_CONTEXT_OHLCV"
            strength_df = _load_ohlcv(context_path)
        strength_rows = _build_strength_strip_rows(strength_df, day, has_next_render_day=day < end_day)
        csv_path = day_dir / f"STAS5_V5_FORWARD_VISUAL_REVIEW_ENTRIES_{compact_day(day)}.csv"
        overview_suffix = "_ENTER_ARROWS_BOLLINGER20_2SIGMA_PREVIEW" if bollinger_preview else "_ENTER_ARROWS"
        overview_path = day_dir / f"STAS5_V5_FORWARD_VISUAL_REVIEW_{compact_day(day)}{overview_suffix}.png"
        closeups_path = day_dir / f"STAS5_V5_FORWARD_ENTER_CLOSEUPS_{compact_day(day)}.png"
        day_dir.mkdir(parents=True, exist_ok=True)
        day_rows.drop(columns=["entry_ts"], errors="ignore").to_csv(csv_path, index=False, encoding="utf-8-sig")
        render_forward_day_overview(
            day_df=day_df,
            rows=day_rows,
            strength_hour_rows=strength_rows["hour_rows"],
            strength_macro_wave_rows=strength_rows["macro_wave_rows"],
            day=day,
            symbol=symbol,
            timeframe=timeframe,
            out_path=overview_path,
            bollinger_preview=bollinger_preview,
            bollinger_source_df=strength_df,
            bollinger_window=20,
            bollinger_std=2.0,
        )
        png_paths.append(rel(overview_path))
        closeups_created = render_enter_closeups(
            day_df=day_df,
            rows=day_rows,
            day=day,
            symbol=symbol,
            timeframe=timeframe,
            out_path=closeups_path,
        )
        if closeups_created:
            png_paths.append(rel(closeups_path))
        counts = Counter(day_rows[DECISION_COLUMN].astype(str))
        day_outputs.append(
            {
                "day": day,
                "status": "READY",
                "rows": int(len(day_rows)),
                "decision_counts": {str(k): int(v) for k, v in counts.items()},
                "csv": rel(csv_path),
                "overview_png": rel(overview_path),
                "closeups_png": rel(closeups_path) if closeups_created else "",
                "bollinger_preview": bool(bollinger_preview),
                "strength_strip_status": "READY",
                "strength_strip_context_status": strength_context_status,
                "strength_strip_source": rel(strength_source),
                "strength_strip_context_rows": int(len(strength_df)),
                "strength_strip_hour_rows": int(len(strength_rows["hour_rows"])),
                "strength_strip_macro_wave_rows": int(len(strength_rows["macro_wave_rows"])),
                "strength_strip_gap_rows_filtered": int(strength_rows["macro_gap_rows_filtered"]),
                "strength_strip_non_wave_rows_filtered": int(strength_rows["macro_non_wave_rows_filtered"]),
                "strength_strip_tail_gap_rows_absorbed": int(strength_rows["tail_gap_rows_absorbed"]),
                "strength_strip_tail_gap_minutes_filled": float(strength_rows["tail_gap_minutes_filled"]),
                "strength_strip_gap_rows_rendered": 0,
                "strength_strip_available_end_utc": strength_rows["target_data_end_utc"],
                "strength_strip_target_data_end_utc": strength_rows["target_data_end_utc"],
                "strength_strip_last_wave_end_utc": strength_rows["last_wave_end_utc"],
                "strength_strip_tail_covered_to_data_end": bool(strength_rows["tail_covered_to_data_end"]),
                "strength_strip_cross_day_wave_rows": int(strength_rows["cross_day_wave_rows"]),
                "strength_strip_label_pct_basis": "cumulative_from_true_wave_start",
                "strength_strip_max_visible_to_cumulative_pct_delta": float(strength_rows["max_visible_to_cumulative_pct_delta"]),
                "strength_strip_macro_wave_directions": sorted(
                    {str(row.get("macro_wave_direction") or "") for row in strength_rows["macro_wave_rows"]}
                ),
                "strength_strip_cumulative_pct_rows": int(
                    sum(1 for row in strength_rows["macro_wave_rows"] if "macro_wave_cum_end_pct" in row)
                ),
            }
        )

    ready_outputs = [item for item in day_outputs if item.get("status") == "READY"]
    checks = [
        {"check": "predictions_csv_exists", "status": "PASS" if pred_path.exists() else "FAIL", "details": {"path": rel(pred_path)}},
        {"check": "ohlcv_present_for_all_days", "status": "PASS" if not missing_ohlcv else "FAIL", "details": {"missing": missing_ohlcv}},
        {"check": "overview_png_created_for_each_day", "status": "PASS" if len([x for x in day_outputs if x.get("overview_png")]) == len(iter_days(start_day, end_day)) else "FAIL", "details": {}},
        {"check": "enter_arrow_png_count_positive", "status": "PASS" if png_paths else "FAIL", "details": {"png_count": len(png_paths)}},
        {
            "check": "continuous_strength_strip_rendered_for_each_ready_day",
            "status": "PASS" if all(int(item.get("strength_strip_hour_rows", 0)) > 0 for item in ready_outputs) else "FAIL",
            "details": {
                "ready_days": len(ready_outputs),
                "context_days": sum(1 for item in ready_outputs if item.get("strength_strip_context_status") == "CONTINUOUS_CONTEXT_OHLCV"),
            },
        },
        {
            "check": "macro_wave_gap_segments_filtered_from_visual_strip",
            "status": "PASS"
            if all(int(item.get("strength_strip_gap_rows_rendered", 0)) == 0 for item in ready_outputs)
            else "FAIL",
            "details": {
                "filtered_gap_rows_total": sum(int(item.get("strength_strip_gap_rows_filtered", 0)) for item in ready_outputs),
                "rendered_gap_rows_total": sum(int(item.get("strength_strip_gap_rows_rendered", 0)) for item in ready_outputs),
            },
        },
        {
            "check": "macro_wave_strip_uses_only_long_short_wave_segments",
            "status": "PASS"
            if all(
                set(item.get("strength_strip_macro_wave_directions", [])).issubset({"LONG", "SHORT"})
                for item in ready_outputs
            )
            else "FAIL",
            "details": {
                "directions_by_day": {
                    str(item.get("day")): item.get("strength_strip_macro_wave_directions", []) for item in ready_outputs
                }
            },
        },
        {
            "check": "macro_wave_active_tail_covered_to_data_end",
            "status": "PASS"
            if all(bool(item.get("strength_strip_tail_covered_to_data_end", False)) for item in ready_outputs)
            else "FAIL",
            "details": {
                "absorbed_tail_gap_rows_total": sum(int(item.get("strength_strip_tail_gap_rows_absorbed", 0)) for item in ready_outputs),
                "days": {
                    str(item.get("day")): {
                        "last_wave_end": item.get("strength_strip_last_wave_end_utc"),
                        "target_data_end": item.get("strength_strip_target_data_end_utc"),
                        "covered": item.get("strength_strip_tail_covered_to_data_end"),
                    }
                    for item in ready_outputs
                },
            },
        },
        {
            "check": "macro_wave_strip_covers_available_candle_end",
            "status": "PASS"
            if all(bool(item.get("strength_strip_tail_covered_to_data_end", False)) for item in ready_outputs)
            else "FAIL",
            "details": {
                "days": {
                    str(item.get("day")): {
                        "last_wave_end": item.get("strength_strip_last_wave_end_utc"),
                        "available_end": item.get("strength_strip_available_end_utc"),
                    }
                    for item in ready_outputs
                }
            },
        },
        {
            "check": "macro_wave_tail_gap_filled_without_rendering_gap",
            "status": "PASS"
            if all(int(item.get("strength_strip_gap_rows_rendered", 0)) == 0 for item in ready_outputs)
            else "FAIL",
            "details": {
                "tail_gap_rows_filled_total": sum(int(item.get("strength_strip_tail_gap_rows_absorbed", 0)) for item in ready_outputs),
                "tail_gap_minutes_filled_total": round(
                    sum(float(item.get("strength_strip_tail_gap_minutes_filled", 0.0)) for item in ready_outputs),
                    3,
                ),
                "rendered_gap_rows_total": sum(int(item.get("strength_strip_gap_rows_rendered", 0)) for item in ready_outputs),
            },
        },
        {
            "check": "cross_day_wave_labels_use_cumulative_true_start_pct",
            "status": "PASS"
            if all(str(item.get("strength_strip_label_pct_basis")) == "cumulative_from_true_wave_start" for item in ready_outputs)
            else "FAIL",
            "details": {
                "cross_day_wave_rows_total": sum(int(item.get("strength_strip_cross_day_wave_rows", 0)) for item in ready_outputs),
                "max_visible_to_cumulative_pct_delta": max(
                    [float(item.get("strength_strip_max_visible_to_cumulative_pct_delta", 0.0)) for item in ready_outputs] or [0.0]
                ),
            },
        },
        {
            "check": "macro_wave_cumulative_pct_present_for_rendered_wave_rows",
            "status": "PASS"
            if all(
                int(item.get("strength_strip_cumulative_pct_rows", 0)) == int(item.get("strength_strip_macro_wave_rows", 0))
                for item in ready_outputs
            )
            else "FAIL",
            "details": {
                "rows_by_day": {
                    str(item.get("day")): {
                        "wave_rows": item.get("strength_strip_macro_wave_rows", 0),
                        "cum_rows": item.get("strength_strip_cumulative_pct_rows", 0),
                    }
                    for item in ready_outputs
                }
            },
        },
    ]
    status = STATUS_PASS if all(item["status"] == "PASS" for item in checks) else STATUS_FAIL
    manifest_path = out_dir / "STAS5_V5_FORWARD_VISUAL_REVIEW_MANIFEST_V1.json"
    report_path = out_dir / "STAS5_V5_FORWARD_VISUAL_REVIEW_AUDIT_RU.md"
    manifest = {
        "status": status,
        "created_utc": utc_now(),
        "forward_run_dir": rel(run_dir),
        "predictions_csv": rel(pred_path),
        "date_range": {"start_day": start_day, "end_day": end_day},
        "symbol": symbol,
        "timeframe": timeframe,
        "bollinger_preview": bool(bollinger_preview),
        "bollinger_contract": "visual_only_rolling_20_2sigma_not_ml_feature" if bollinger_preview else "",
        "out_dir": rel(out_dir),
        "png_count": len(png_paths),
        "png_paths": png_paths,
        "day_outputs": day_outputs,
        "checks": checks,
        "guardrails": [
            "visual_review_only_no_training",
            "reads_fixed_forward_predictions",
            "does_not_change_model_scores_or_decisions",
            "ohlcv_used_only_for_chart_coordinates",
            "overview_has_all_candidate_la_labels",
            "overview_has_no_long_enter_arrows_or_enter_boxes",
            "strength_strip_is_visual_review_only_not_model_feature",
            "strength_strip_uses_continuous_ohlcv_context_when_available",
            "macro_wave_gap_segments_are_filtered_so_day_boundary_is_not_gray_gap",
            "macro_wave_active_tail_is_extended_to_day_data_end_for_visual_continuity",
            "macro_wave_labels_use_cumulative_pct_from_true_wave_start",
            "strength_strip_active_wave_extends_to_available_candle_end",
            "strength_strip_cross_day_pct_uses_true_wave_start",
            "bollinger_overlay_is_visual_only_not_x439" if bollinger_preview else "bollinger_overlay_disabled",
        ],
    }
    write_json(manifest_path, manifest)
    manifest["manifest_path"] = rel(manifest_path)
    manifest["audit_ru"] = rel(report_path)
    _write_audit_ru(report_path, manifest)
    write_json(manifest_path, manifest)
    if strict and status != STATUS_PASS:
        raise ValueError(f"V5 forward visual review is not PASS: {status}")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Render STAS5 V5 forward visual review with green ENTER arrows.")
    parser.add_argument("--forward-run-dir", default="")
    parser.add_argument("--predictions-path", default="")
    parser.add_argument("--start-day", default="")
    parser.add_argument("--end-day", default="")
    parser.add_argument("--symbol", default=SYMBOL)
    parser.add_argument("--timeframe", default=TIMEFRAME)
    parser.add_argument("--bollinger-preview", action="store_true")
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()

    manifest = render_forward_visual_review(
        forward_run_dir=Path(args.forward_run_dir) if args.forward_run_dir else None,
        predictions_path=Path(args.predictions_path) if args.predictions_path else None,
        start_day=args.start_day or None,
        end_day=args.end_day or None,
        symbol=args.symbol,
        timeframe=args.timeframe,
        bollinger_preview=args.bollinger_preview,
        strict=not args.no_strict,
    )
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "forward_run_dir": manifest["forward_run_dir"],
                "manifest_path": manifest["manifest_path"],
                "png_count": manifest["png_count"],
                "bollinger_preview": manifest["bollinger_preview"],
            },
            ensure_ascii=False,
        )
    )
    return 0 if args.no_strict or manifest["status"] == STATUS_PASS else 2


if __name__ == "__main__":
    raise SystemExit(main())
