from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from mlbotnav.stas5_common import (
    DEFAULT_STAS2_TRAIN_RUN_DIR,
    PROJECT_ROOT,
    STAS5_ARTIFACTS_DIR,
    compact_day,
    rel,
    utc_now,
    write_json,
)
from mlbotnav.stas5_v2_feature_snapshot_builder import DEFAULT_V2_FEATURE_SNAPSHOT_PATH
from mlbotnav.visual_entry_low_anchor_suggester import _bar_width_days, _draw_candles, _load_ohlcv, _source_csv, _style_axis
from mlbotnav.visual_entry_stas2_market_phase_review import (
    _render_macro_wave_strip,
    _render_rank_strip,
    _set_day_time_axis,
    _shade_sessions,
)
from mlbotnav.visual_entry_stas4_family_overlay import _family_marks, _render_combo_spectrum


STATUS = "STAS5_V2_FEATURE_VISUAL_APPROVAL_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3"
SYMBOL = "SOLUSDT"
TIMEFRAME = "1m"
DEFAULT_VISUAL_APPROVAL_ROOT = STAS5_ARTIFACTS_DIR / "v2" / "visual_approval"
REFERENCE_STAS4_ROOT = (
    PROJECT_ROOT
    / "STAS4_FEATURE_HYPOTHESIS_REVIEW"
    / "density_structure_20260501_20260514_combo_spectrum"
)

KEEP_COLOR = "#00e676"
CUT_COLOR = "#ffff00"
YELLOW_X_COLOR = "#ffff00"
CONFLICT_COLOR = "#00e5ff"

STRATEGY_AUDIT_FAMILIES: tuple[dict[str, str], ...] = (
    {
        "family": "density_profile+structure_ta",
        "label": "density+structure",
        "role": "main yellow-X audit",
        "old_color": "#ffe14d",
        "new_color": "#37a2ff",
    },
    {
        "family": "pattern+structure_ta",
        "label": "pattern+structure",
        "role": "second opinion",
        "old_color": "#ff9f1a",
        "new_color": "#37a2ff",
    },
    {
        "family": "structure_ta+volume_flow",
        "label": "structure+volume",
        "role": "hard risk flag",
        "old_color": "#ff5252",
        "new_color": "#37a2ff",
    },
    {
        "family": "structure_ta+trend_momentum",
        "label": "structure+trend",
        "role": "aggressive risk flag",
        "old_color": "#d500f9",
        "new_color": "#37a2ff",
    },
)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        out = float(value)
        if not math.isfinite(out):
            return default
        return out
    except Exception:
        return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def approval_bucket(row: pd.Series) -> str:
    label = str(row.get("human_label") or "").upper()
    yellow = _to_int(row.get("yellow_x"))
    conflict = _to_int(row.get("yellow_x_conflict"))
    if "KEEP" in label and yellow and conflict:
        return "CONFLICT"
    if "KEEP" in label:
        return "KEEP"
    if yellow:
        return "YELLOW_X"
    return "CUT"


def risk_bucket(row: pd.Series) -> str:
    allowed = _to_int(row.get("stas5_v2_gate_long_allowed_final"), 1)
    risk = _safe_float(row.get("stas5_v2_risk_knife_pre_entry"))
    short = _safe_float(row.get("stas4_v2_combo_short_pressure_score"))
    if allowed == 0:
        return "BLOCKED"
    if risk >= 0.55 or short >= 0.80:
        return "HIGH_RISK"
    if risk >= 0.45 or short >= 0.60:
        return "CAUTION"
    return "LOW_RISK"


def _keep_mask(rows: pd.DataFrame) -> pd.Series:
    return rows["human_label"].astype(str).str.contains("KEEP", case=False, na=False)


def _yellow_mask(rows: pd.DataFrame) -> pd.Series:
    return pd.to_numeric(rows["yellow_x"], errors="coerce").fillna(0).astype(int) == 1


def _conflict_mask(rows: pd.DataFrame) -> pd.Series:
    return _keep_mask(rows) & (pd.to_numeric(rows["yellow_x_conflict"], errors="coerce").fillna(0).astype(int) == 1)


def visual_marker_counts(rows: pd.DataFrame) -> dict[str, int]:
    keep = _keep_mask(rows)
    yellow = _yellow_mask(rows)
    conflict = _conflict_mask(rows)
    return {
        "human_keep_green_markers": int(keep.sum()),
        "human_cut_red_markers": int((~keep).sum()),
        "yellow_x_cut_overlay_markers": int((yellow & ~keep).sum()),
        "keep_yellow_conflict_cyan_overlay_markers": int(conflict.sum()),
    }


def strategy_audit_counts(strategy_audit: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in strategy_audit:
        out[str(item["family"])] = {
            "label": str(item["label"]),
            "role": str(item["role"]),
            "old_removed": len(item.get("old_removed", [])),
            "new_candidates": len(item.get("new_candidates", [])),
        }
    return out


def _strategy_mark_key(item: dict[str, Any]) -> str:
    return str(item.get("record_id") or item.get("candidate_id") or item.get("entry_time_utc") or "")


def _strategy_merge_reasons(prefix: str, item: dict[str, Any]) -> list[str]:
    return [f"{prefix}: {reason}" for reason in item.get("reasons", [])]


def _fmt_strategy_ts(value: Any) -> str:
    return pd.Timestamp(value).tz_convert("UTC").isoformat().replace("+00:00", "Z")


def _base_strategy_families() -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for cfg in STRATEGY_AUDIT_FAMILIES:
        for item in str(cfg["family"]).split("+"):
            family = item.strip()
            if family and family not in seen:
                seen.add(family)
                out.append(family)
    return out


def _combo_from_cached_payloads(
    family_payloads: dict[str, tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    combo_family: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    families = [part.strip() for part in combo_family.split("+") if part.strip()]
    if len(families) < 2:
        return family_payloads[combo_family]

    old_maps = {
        family: {_strategy_mark_key(item): item for item in family_payloads[family][0] if _strategy_mark_key(item)}
        for family in families
    }
    common_old_keys = set.intersection(*(set(items.keys()) for items in old_maps.values())) if old_maps else set()
    old_removed: list[dict[str, Any]] = []
    for key in sorted(common_old_keys):
        first = old_maps[families[0]][key]
        reasons: list[str] = []
        for family in families:
            reasons.extend(_strategy_merge_reasons(family, old_maps[family][key]))
        old_removed.append({**first, "source": "+".join(families), "reasons": reasons})

    new_lists = {family: family_payloads[family][1] for family in families}
    base_family = families[0]
    raw_new: list[dict[str, Any]] = []
    for base_item in new_lists[base_family]:
        base_ts = pd.Timestamp(base_item["entry_time_utc"]).tz_convert("UTC")
        matched = {base_family: base_item}
        ok = True
        for family in families[1:]:
            candidates = []
            for other in new_lists[family]:
                other_ts = pd.Timestamp(other["entry_time_utc"]).tz_convert("UTC")
                diff_min = abs((other_ts - base_ts).total_seconds()) / 60.0
                if diff_min <= 5.0:
                    candidates.append((diff_min, other))
            if not candidates:
                ok = False
                break
            matched[family] = sorted(candidates, key=lambda x: x[0])[0][1]
        if not ok:
            continue
        entry_ts = max(pd.Timestamp(item["entry_time_utc"]).tz_convert("UTC") for item in matched.values())
        signal_ts = entry_ts - pd.Timedelta(minutes=1)
        reasons = []
        score = 0.0
        for family, item in matched.items():
            reasons.extend(_strategy_merge_reasons(family, item))
            score += _safe_float(item.get("score"), 0.0)
        raw_new.append(
            {
                "kind": "new_candidate",
                "candidate_id": f"STAS4_COMBO_{'_'.join(f[:2].upper() for f in families)}_{signal_ts.strftime('%H%M')}",
                "signal_time_utc": _fmt_strategy_ts(signal_ts),
                "entry_time_utc": _fmt_strategy_ts(entry_ts),
                "entry_open_price": _safe_float(matched[base_family].get("entry_open_price")),
                "source": "+".join(families),
                "score": round(float(score), 4),
                "reasons": reasons,
            }
        )

    selected_new: list[dict[str, Any]] = []
    last_time: pd.Timestamp | None = None
    for item in sorted(raw_new, key=lambda x: (-float(x["score"]), x["entry_time_utc"])):
        ts = pd.Timestamp(item["entry_time_utc"]).tz_convert("UTC")
        if last_time is not None and abs((ts - last_time).total_seconds()) < 10 * 60:
            continue
        selected_new.append(item)
        last_time = ts
    return old_removed, sorted(selected_new, key=lambda x: x["entry_time_utc"])


def _read_snapshot(path: Path, day: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"V2 snapshot not found: {path}")
    rows = pd.read_csv(path, encoding="utf-8-sig")
    rows = rows[rows["day"].astype(str) == day].copy()
    if rows.empty:
        raise ValueError(f"no V2 snapshot rows for day {day}")
    rows["entry_ts"] = pd.to_datetime(rows["entry_time_utc"], utc=True)
    rows["entry_price_plot"] = pd.to_numeric(rows["entry_price_5bps"], errors="coerce")
    rows["approval_bucket"] = rows.apply(approval_bucket, axis=1)
    rows["risk_bucket"] = rows.apply(risk_bucket, axis=1)
    return rows.sort_values("entry_ts").reset_index(drop=True)


def _read_rows(path: Path, day: str, day_column: str = "day_utc") -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"source table not found: {path}")
    rows = pd.read_csv(path, encoding="utf-8-sig")
    rows = rows[rows[day_column].astype(str) == day].copy()
    return rows.to_dict(orient="records")


def _reference_artifacts(day: str) -> dict[str, str]:
    day_dir = REFERENCE_STAS4_ROOT / compact_day(day)
    out: dict[str, str] = {}
    if not day_dir.exists():
        return out
    for path in sorted(day_dir.glob(f"*{compact_day(day)}*")):
        suffix = path.suffix.lower().lstrip(".")
        if suffix in {"png", "json", "csv", "md"}:
            out[f"stas4_reference_{suffix}"] = rel(path)
    return out


def _compute_strategy_audit(day_df: pd.DataFrame, stas2_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    family_payloads = {family: _family_marks(day_df, stas2_rows, family) for family in _base_strategy_families()}
    out: list[dict[str, Any]] = []
    for cfg in STRATEGY_AUDIT_FAMILIES:
        old_removed, new_candidates = _combo_from_cached_payloads(family_payloads, cfg["family"])
        out.append(
            {
                **cfg,
                "old_removed": old_removed,
                "new_candidates": new_candidates,
            }
        )
    return out


def _plot_price_markers(ax: Any, rows: pd.DataFrame) -> None:
    if rows.empty:
        return
    keep_mask = _keep_mask(rows)
    yellow_mask = _yellow_mask(rows)
    conflict_mask = _conflict_mask(rows)
    cut_rows = rows[~keep_mask]
    keep_rows = rows[keep_mask]
    yellow_cut_rows = rows[yellow_mask & ~keep_mask]
    conflict_rows = rows[conflict_mask]

    if not cut_rows.empty:
        ax.scatter(
            cut_rows["entry_ts"].dt.tz_convert(None),
            cut_rows["entry_price_plot"],
            marker="x",
            s=52,
            color=CUT_COLOR,
            linewidths=0.85,
            alpha=0.98,
            zorder=9,
            label=f"human CUT ({len(cut_rows)})",
        )
    if not keep_rows.empty:
        ax.scatter(
            keep_rows["entry_ts"].dt.tz_convert(None),
            keep_rows["entry_price_plot"],
            marker="^",
            s=122,
            color=KEEP_COLOR,
            edgecolors="#071014",
            linewidths=0.85,
            alpha=0.98,
            zorder=10,
            label=f"human KEEP ({len(keep_rows)})",
        )
    if not yellow_cut_rows.empty:
        ax.scatter(
            yellow_cut_rows["entry_ts"].dt.tz_convert(None),
            yellow_cut_rows["entry_price_plot"],
            marker="X",
            s=88,
            color=YELLOW_X_COLOR,
            edgecolors="#071014",
            linewidths=0.65,
            alpha=0.90,
            zorder=11,
            label=f"yellow X audit on CUT ({len(yellow_cut_rows)})",
        )
    if not conflict_rows.empty:
        ax.scatter(
            conflict_rows["entry_ts"].dt.tz_convert(None),
            conflict_rows["entry_price_plot"],
            marker="+",
            s=230,
            color=CONFLICT_COLOR,
            linewidths=2.0,
            alpha=0.98,
            zorder=12,
            label=f"KEEP + yellow conflict overlay ({len(conflict_rows)})",
        )

    y_min = _safe_float(ax.get_ylim()[0])
    y_max = _safe_float(ax.get_ylim()[1])
    y_span = max(y_max - y_min, 1e-9)
    for idx, row in rows.reset_index(drop=True).iterrows():
        entry_ts = pd.Timestamp(row["entry_ts"]).tz_convert("UTC").tz_convert(None)
        price = _safe_float(row.get("entry_price_plot"))
        is_keep = "KEEP" in str(row.get("human_label") or "").upper()
        is_yellow_cut = (not is_keep) and _to_int(row.get("yellow_x")) == 1
        label = str(row.get("candidate_id") or "")
        if is_keep:
            label = f"{label} KEEP"
            fontsize = 6.9
            alpha = 0.98
            offset_y = 10 if idx % 2 == 0 else -16
            label_color = KEEP_COLOR
        elif is_yellow_cut:
            label = f"{label} X"
            fontsize = 5.9
            alpha = 0.82
            offset_y = 7 if idx % 2 == 0 else -12
            label_color = YELLOW_X_COLOR
        else:
            fontsize = 4.7
            alpha = 0.98
            offset_y = 5 if idx % 2 == 0 else -9
            label_color = CUT_COLOR
        ax.annotate(
            label,
            xy=(entry_ts, price),
            xytext=(0, offset_y),
            textcoords="offset points",
            ha="center",
            va="bottom" if offset_y > 0 else "top",
            color=label_color,
            fontsize=fontsize,
            alpha=alpha,
            zorder=11,
        )

    for _, row in keep_rows.iterrows():
        entry_ts = pd.Timestamp(row["entry_ts"]).tz_convert("UTC").tz_convert(None)
        ax.axvline(entry_ts, color=KEEP_COLOR, alpha=0.16, linewidth=0.9, zorder=3)

    ax.set_ylim(y_min - y_span * 0.015, y_max + y_span * 0.035)


def _plot_structure_density(ax: Any, rows: pd.DataFrame) -> None:
    _style_axis(ax)
    _shade_sessions(ax, rows["day"].iloc[0])
    x = rows["entry_ts"].dt.tz_convert(None)
    ax.plot(x, rows["stas4_v2_density_support_score"], color="#00e676", linewidth=1.05, marker="o", markersize=3.5, label="density support")
    ax.plot(x, rows["stas4_v2_density_conflict_score"], color="#ff7043", linewidth=1.05, marker="o", markersize=3.5, label="density conflict")
    ax.plot(x, rows["stas4_v2_structure_support_score"], color="#4fc3f7", linewidth=1.05, marker="o", markersize=3.5, label="structure support")
    ax.plot(x, rows["stas4_v2_structure_conflict_score"], color="#ff4081", linewidth=1.05, marker="o", markersize=3.5, label="structure conflict")
    lower = rows[pd.to_numeric(rows.get("stas4_v2_structure_lower_range_flag", 0), errors="coerce").fillna(0).astype(int) == 1]
    high = rows[pd.to_numeric(rows.get("stas4_v2_structure_high_range_flag", 0), errors="coerce").fillna(0).astype(int) == 1]
    if not lower.empty:
        ax.scatter(lower["entry_ts"].dt.tz_convert(None), [5.55] * len(lower), marker="^", s=55, color="#00e5ff", label="lower range")
    if not high.empty:
        ax.scatter(high["entry_ts"].dt.tz_convert(None), [5.05] * len(high), marker="v", s=55, color="#ff5252", label="high range")
    ax.set_ylim(-0.3, 6.0)
    ax.set_ylabel("Dens/Struct", color="#eceff1")
    ax.legend(loc="upper left", ncol=6, fontsize=7, facecolor="#101418", edgecolor="#455a64", labelcolor="#eceff1")


def _event_times(items: list[dict[str, Any]]) -> list[Any]:
    out: list[Any] = []
    for item in items:
        raw = item.get("entry_time_utc") or item.get("signal_time_utc")
        if not raw:
            continue
        try:
            out.append(pd.Timestamp(raw).tz_convert("UTC").tz_convert(None))
        except Exception:
            continue
    return out


def _plot_strategy_audit_strip(ax: Any, strategy_audit: list[dict[str, Any]], day: str) -> None:
    _style_axis(ax)
    _shade_sessions(ax, day)
    start = pd.Timestamp(day)
    end = start + pd.Timedelta(days=1)
    lane_count = len(strategy_audit)
    for idx, item in enumerate(strategy_audit):
        y = lane_count - 1 - idx
        old_removed = item.get("old_removed", [])
        new_candidates = item.get("new_candidates", [])
        old_times = _event_times(old_removed)
        new_times = _event_times(new_candidates)
        ax.axhspan(y - 0.38, y + 0.38, color="#151b22" if idx % 2 == 0 else "#101820", alpha=0.72, zorder=0)
        ax.hlines(y, start.to_pydatetime(), end.to_pydatetime(), color="#455a64", linewidth=0.55, alpha=0.55, zorder=1)
        if old_times:
            ax.scatter(
                old_times,
                [y] * len(old_times),
                marker="X",
                s=42,
                color=str(item["old_color"]),
                edgecolors="#071014",
                linewidths=0.45,
                alpha=0.88,
                zorder=5,
            )
        if new_times:
            ax.scatter(
                new_times,
                [y] * len(new_times),
                marker="^",
                s=36,
                color=str(item["new_color"]),
                edgecolors="#071014",
                linewidths=0.40,
                alpha=0.82,
                zorder=6,
            )

    y_positions = [lane_count - 1 - idx for idx in range(lane_count)]
    y_labels = [
        f"{item['label']}  X{len(item.get('old_removed', []))}/UP{len(item.get('new_candidates', []))}"
        for item in strategy_audit
    ]
    ax.set_yticks(y_positions)
    ax.set_yticklabels(y_labels, color="#eceff1", fontsize=7)
    ax.set_ylim(-0.55, lane_count - 0.45)
    ax.set_ylabel("STAS4\nAudit", color="#eceff1")
    ax.text(
        0.995,
        0.90,
        "audit-only: X=strategy risk/cut vote, UP=new candidate",
        transform=ax.transAxes,
        ha="right",
        va="top",
        color="#cfd8dc",
        fontsize=7.2,
        alpha=0.90,
    )


def _plot_risk_gate(ax: Any, rows: pd.DataFrame) -> None:
    _style_axis(ax)
    _shade_sessions(ax, rows["day"].iloc[0])
    x = rows["entry_ts"].dt.tz_convert(None)
    ax.plot(x, rows["stas5_v2_risk_knife_pre_entry"], color="#ff4d5e", linewidth=1.10, marker="o", markersize=3.4, label="knife_risk")
    ax.plot(x, rows["stas4_v2_combo_short_pressure_score"], color="#ff9f1a", linewidth=1.05, marker="o", markersize=3.2, label="short_pressure")
    ax.plot(x, rows["stas4_v2_combo_long_recovery_score"], color="#00e5ff", linewidth=1.05, marker="o", markersize=3.2, label="long_recovery")
    ax.axhline(0.45, color="#ffd43b", linewidth=0.8, linestyle="--", alpha=0.70)
    ax.axhline(0.55, color="#ff5252", linewidth=0.8, linestyle="--", alpha=0.70)
    blocked = rows[pd.to_numeric(rows["stas5_v2_gate_long_allowed_final"], errors="coerce").fillna(1).astype(int) == 0]
    if not blocked.empty:
        ax.scatter(blocked["entry_ts"].dt.tz_convert(None), [1.05] * len(blocked), marker="X", s=85, color="#ff1744", zorder=9, label="long_allowed=0")
    for bucket, color in [("LOW_RISK", "#00e676"), ("CAUTION", "#ffd43b"), ("HIGH_RISK", "#ff5252"), ("BLOCKED", "#ff1744")]:
        subset = rows[rows["risk_bucket"] == bucket]
        if subset.empty:
            continue
        ax.scatter(subset["entry_ts"].dt.tz_convert(None), [-0.06] * len(subset), marker="s", s=22, color=color, alpha=0.9, label=f"{bucket} ({len(subset)})")
    ax.set_ylim(-0.12, 1.13)
    ax.set_ylabel("Risk/Gate", color="#eceff1")
    ax.legend(loc="upper left", ncol=7, fontsize=7, facecolor="#101418", edgecolor="#455a64", labelcolor="#eceff1")


def _plot_v2_combo_snapshot(ax: Any, rows: pd.DataFrame) -> None:
    _style_axis(ax)
    _shade_sessions(ax, rows["day"].iloc[0])
    x = rows["entry_ts"].dt.tz_convert(None)
    ax.axhspan(80, 100, color="#5b1f34", alpha=0.24, zorder=0)
    ax.axhspan(0, 20, color="#143b2e", alpha=0.24, zorder=0)
    for level, color in [(80, "#ff3355"), (50, "#cfd8dc"), (20, "#00e676")]:
        ax.axhline(level, color=color, linestyle="--" if level in {80, 20} else "-", linewidth=0.75, alpha=0.65)
    ax.plot(x, rows["stas4_v2_combo_rsi14"], color="#ffffff", linewidth=1.08, marker=".", markersize=3.0, label="RSI14 @ candidate")
    ax.plot(x, rows["stas4_v2_combo_rsi_signal9"], color="#f3d42b", linewidth=0.95, marker=".", markersize=2.8, label="RSI signal")
    ax.plot(x, rows["stas4_v2_combo_stoch_k14"], color="#00d9c0", linewidth=0.95, marker=".", markersize=2.8, label="Stoch K")
    macd = pd.to_numeric(rows["stas4_v2_combo_macd_hist_norm"], errors="coerce").fillna(0).clip(-8, 8)
    colors = ["#00c781" if value >= 0 else "#ff4b5c" for value in macd]
    ax.bar(x, macd * 2.2, bottom=50, width=_bar_width_days(TIMEFRAME) * 6.0, color=colors, alpha=0.26, label="MACD hist norm")
    bullish = rows[(pd.to_numeric(rows.get("stas4_v2_div_bullish_recent", 0), errors="coerce").fillna(0) > 0) | (pd.to_numeric(rows.get("stas4_v2_div_hidden_bullish_recent", 0), errors="coerce").fillna(0) > 0)]
    bearish = rows[(pd.to_numeric(rows.get("stas4_v2_div_bearish_recent", 0), errors="coerce").fillna(0) > 0) | (pd.to_numeric(rows.get("stas4_v2_div_hidden_bearish_recent", 0), errors="coerce").fillna(0) > 0)]
    if not bullish.empty:
        ax.scatter(bullish["entry_ts"].dt.tz_convert(None), [13] * len(bullish), marker="^", s=48, color="#00ffc3", label="bull div recent")
    if not bearish.empty:
        ax.scatter(bearish["entry_ts"].dt.tz_convert(None), [88] * len(bearish), marker="v", s=48, color="#ff3333", label="bear div recent")
    ax.set_ylim(0, 100)
    ax.set_ylabel("V2 Combo", color="#eceff1")
    ax.legend(loc="upper left", ncol=7, fontsize=7, facecolor="#101418", edgecolor="#455a64", labelcolor="#eceff1")


def _plot_volume(ax: Any, day_df: pd.DataFrame, day: str) -> None:
    _style_axis(ax)
    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(day_df["open"], day_df["close"])]
    ax.bar(day_df["open_time_utc"].dt.tz_convert(None), day_df["volume"], width=_bar_width_days(TIMEFRAME), color=colors, alpha=0.70)
    _shade_sessions(ax, day)
    ax.set_ylabel("Volume", color="#eceff1")


def render_visual_approval(
    *,
    day_df: pd.DataFrame,
    rows: pd.DataFrame,
    hour_rows: list[dict[str, Any]],
    macro_wave_rows: list[dict[str, Any]],
    strategy_audit: list[dict[str, Any]],
    day: str,
    out_path: Path,
) -> None:
    fig, axes = plt.subplots(
        11,
        1,
        figsize=(32, 29.4),
        sharex=True,
        gridspec_kw={
            "height_ratios": [7.0, 0.46, 0.46, 0.46, 0.46, 1.55, 2.2, 2.0, 2.35, 3.05, 1.55],
            "hspace": 0.055,
        },
    )
    (
        ax_price,
        ax_bg_phase,
        ax_long_wave,
        ax_short_wave,
        ax_macro_wave,
        ax_strategy_audit,
        ax_density_structure,
        ax_risk_gate,
        ax_v2_combo,
        ax_combo_spectrum,
        ax_volume,
    ) = axes
    fig.patch.set_facecolor("#101418")

    _style_axis(ax_price)
    _draw_candles(ax_price, day_df, TIMEFRAME, linewidth=0.30)
    _shade_sessions(ax_price, day, label_top=True)
    _plot_price_markers(ax_price, rows)
    ax_price.set_ylabel("Price", color="#eceff1")
    ax_price.set_title(
        (
            f"STAS5 V2 feature visual approval | {SYMBOL} {TIMEFRAME} {day} | "
            "train labels + V2 causal features | NO TRAINING / NO TP / NO API"
        ),
        color="#eceff1",
        fontsize=14,
    )
    legend = ax_price.legend(loc="upper left", fontsize=8, facecolor="#101418", edgecolor="#455a64", labelcolor="#eceff1")
    for text in legend.get_texts():
        text.set_color("#eceff1")

    _render_rank_strip(ax_bg_phase, hour_rows, day, rank_field="hour_background_phase_rank", label="Fon", color_kind="phase", pct_field="hour_background_phase_metric_pct")
    _render_rank_strip(ax_long_wave, hour_rows, day, rank_field="hour_long_wave_rank", label="LONG", color_kind="long", pct_field="hour_long_wave_up_from_low_pct")
    _render_rank_strip(ax_short_wave, hour_rows, day, rank_field="hour_short_wave_rank", label="SHORT", color_kind="short", pct_field="hour_short_wave_down_from_high_pct")
    _render_macro_wave_strip(ax_macro_wave, macro_wave_rows, day)
    _plot_strategy_audit_strip(ax_strategy_audit, strategy_audit, day)
    _plot_structure_density(ax_density_structure, rows)
    _plot_risk_gate(ax_risk_gate, rows)
    _plot_v2_combo_snapshot(ax_v2_combo, rows)
    _render_combo_spectrum(ax_combo_spectrum, day_df, day)
    _plot_volume(ax_volume, day_df, day)

    start = pd.Timestamp(day)
    end = start + pd.Timedelta(days=1)
    for ax in axes:
        ax.set_xlim(start.to_pydatetime(), end.to_pydatetime())
    _set_day_time_axis(ax_volume, day)
    fig.text(
        0.012,
        0.012,
        (
            "Rows: all candidate LA entries from V2 snapshot. Green=human KEEP, red=CUT, yellow=yellow-X audit, "
            "cyan=KEEP+yellow conflict. STAS4 strategy strip is audit-only. Lower panels are pre-entry feature diagnostics, not model decisions."
        ),
        color="#cfd8dc",
        fontsize=8,
        ha="left",
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor())
    plt.close(fig)


def run(
    *,
    day: str = "2026-05-04",
    root: Path = PROJECT_ROOT,
    snapshot_path: Path = DEFAULT_V2_FEATURE_SNAPSHOT_PATH,
    stas2_run_dir: Path = DEFAULT_STAS2_TRAIN_RUN_DIR,
    out_root: Path = DEFAULT_VISUAL_APPROVAL_ROOT,
) -> dict[str, Any]:
    day = pd.Timestamp(day).strftime("%Y-%m-%d")
    day_df = _load_ohlcv(_source_csv(root, day, TIMEFRAME, SYMBOL))
    rows = _read_snapshot(snapshot_path, day)
    hour_rows = _read_rows(stas2_run_dir / "STAS2_HOURLY_PHASES.csv", day)
    macro_wave_rows = _read_rows(stas2_run_dir / "STAS2_MACRO_WAVES.csv", day)
    stas2_rows = _read_rows(stas2_run_dir / "STAS2_RECORDS.csv", day)
    strategy_audit = _compute_strategy_audit(day_df, stas2_rows)

    out_dir = out_root / compact_day(day)
    png_path = out_dir / f"STAS5_V2_FEATURE_VISUAL_APPROVAL_{compact_day(day)}.png"
    manifest_path = out_dir / f"STAS5_V2_FEATURE_VISUAL_APPROVAL_{compact_day(day)}.manifest.json"
    render_visual_approval(
        day_df=day_df,
        rows=rows,
        hour_rows=hour_rows,
        macro_wave_rows=macro_wave_rows,
        strategy_audit=strategy_audit,
        day=day,
        out_path=png_path,
    )

    label_counts = rows["human_label"].astype(str).value_counts().to_dict()
    approval_counts = rows["approval_bucket"].astype(str).value_counts().to_dict()
    risk_counts = rows["risk_bucket"].astype(str).value_counts().to_dict()
    marker_counts = visual_marker_counts(rows)
    payload = {
        "status": STATUS,
        "created_utc": utc_now(),
        "day": day,
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "rows": int(len(rows)),
        "label_counts": label_counts,
        "approval_bucket_counts": approval_counts,
        "visual_marker_counts": marker_counts,
        "strategy_audit_counts": strategy_audit_counts(strategy_audit),
        "risk_bucket_counts": risk_counts,
        "keep_ids": rows[rows["human_label"].astype(str).str.contains("KEEP", case=False, na=False)]["candidate_id"].tolist(),
        "yellow_x_count": int(pd.to_numeric(rows["yellow_x"], errors="coerce").fillna(0).sum()),
        "yellow_x_conflict_count": int(pd.to_numeric(rows["yellow_x_conflict"], errors="coerce").fillna(0).sum()),
        "artifacts": {"png": rel(png_path), "manifest": rel(manifest_path), **_reference_artifacts(day)},
        "sources": {
            "snapshot": rel(snapshot_path),
            "stas2_run_dir": rel(stas2_run_dir),
            "stas2_records": rel(stas2_run_dir / "STAS2_RECORDS.csv"),
            "ohlcv": rel(_source_csv(root, day, TIMEFRAME, SYMBOL)),
        },
        "guardrails": [
            "visual approval only",
            "STAS4 strategy layers are audit-only and not final ML/trading decisions",
            "all human KEEP entries are drawn as green markers",
            "KEEP + yellow_x_conflict entries add cyan overlay, not a replacement for green KEEP",
            "no model training",
            "no threshold tuning",
            "no TP/Stas3/exit fields",
            "yellow_x remains audit-only",
        ],
    }
    write_json(manifest_path, payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render STAS5 V2 feature visual approval graph for one train day.")
    parser.add_argument("--day", default="2026-05-04")
    parser.add_argument("--snapshot-path", type=Path, default=DEFAULT_V2_FEATURE_SNAPSHOT_PATH)
    parser.add_argument("--stas2-run-dir", type=Path, default=DEFAULT_STAS2_TRAIN_RUN_DIR)
    parser.add_argument("--out-root", type=Path, default=DEFAULT_VISUAL_APPROVAL_ROOT)
    args = parser.parse_args(argv)
    payload = run(day=args.day, snapshot_path=args.snapshot_path, stas2_run_dir=args.stas2_run_dir, out_root=args.out_root)
    print(payload["status"])
    print(payload["artifacts"]["png"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
