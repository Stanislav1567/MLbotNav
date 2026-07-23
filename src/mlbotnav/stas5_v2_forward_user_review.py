from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from mlbotnav.stas5_common import PROJECT_ROOT, STAS5_ARTIFACTS_DIR, rel, utc_now, write_json
from mlbotnav.stas5_v2_combo_feature_exporter import DEFAULT_V2_COMBO_FEATURE_PATH
from mlbotnav.visual_entry_low_anchor_suggester import _bar_width_days, _draw_candles, _load_ohlcv, _source_csv, _style_axis


STATUS = "STAS5_V2_FORWARD_USER_REVIEW_READY_NO_TRAINING_NO_TP_NO_API"
DEFAULT_FORWARD_V2_FEATURE_PATH = (
    STAS5_ARTIFACTS_DIR / "v2" / "features" / "stas5_v2_combo_features_20260515_20260520_forward_v0.csv"
)
DEFAULT_USER_REVIEW_ROOT = STAS5_ARTIFACTS_DIR / "v2" / "user_review"

BUCKET_STYLES = {
    "USER_KEEP_FORWARD_AUDIT": {"marker": "*", "color": "#00e5ff", "size": 190, "label": "user keep"},
    "BLOCKED": {"marker": "X", "color": "#ff1744", "size": 150, "label": "blocked"},
    "HIGH_RISK": {"marker": "v", "color": "#ff4d5e", "size": 118, "label": "high risk"},
    "CAUTION": {"marker": "D", "color": "#ffd43b", "size": 105, "label": "caution"},
    "LOW_RISK": {"marker": "^", "color": "#00e676", "size": 118, "label": "low risk"},
}


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


def _fmt_ts(value: Any) -> str:
    if value is None or str(value).strip() == "":
        return ""
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def risk_bucket(row: pd.Series) -> str:
    label = str(row.get("user_review_label") or "")
    if label == "USER_KEEP_FORWARD_AUDIT":
        return "USER_KEEP_FORWARD_AUDIT"
    allowed = int(_safe_float(row.get("stas5_v2_gate_long_allowed_final"), 1.0))
    risk = _safe_float(row.get("stas5_v2_risk_knife_pre_entry"))
    short = _safe_float(row.get("stas4_v2_combo_short_pressure_score"))
    if allowed == 0:
        return "BLOCKED"
    if risk >= 0.55 or short >= 0.80:
        return "HIGH_RISK"
    if risk >= 0.45 or short >= 0.60:
        return "CAUTION"
    return "LOW_RISK"


def _read_features(path: Path, day: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"V2 features not found: {path}")
    out = pd.read_csv(path, encoding="utf-8-sig")
    out = out[out["day"].astype(str) == day].copy()
    if out.empty:
        raise ValueError(f"no V2 feature rows for day {day}")
    out["entry_ts"] = pd.to_datetime(out["entry_time_utc"], utc=True)
    out["feature_ts"] = pd.to_datetime(out["feature_time_utc"], utc=True)
    if "user_review_label" not in out.columns:
        out["user_review_label"] = "PENDING_USER_REVIEW"
    out["risk_bucket"] = out.apply(risk_bucket, axis=1)
    return out.sort_values("entry_ts").reset_index(drop=True)


def build_user_review_template(rows: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "day",
        "candidate_id",
        "record_id",
        "entry_time_utc",
        "feature_time_utc",
        "entry_price_5bps",
        "user_review_label",
        "user_note",
        "risk_bucket",
        "stas5_v2_risk_knife_pre_entry",
        "stas4_v2_combo_short_pressure_score",
        "stas4_v2_combo_long_recovery_score",
        "stas5_v2_gate_long_allowed_final",
        "audit_no_trade_reason",
        "stas4_v2_structure_support_score",
        "stas4_v2_structure_conflict_score",
        "stas4_v2_density_support_score",
        "stas4_v2_density_conflict_score",
        "stas4_v2_div_bullish_recent",
        "stas4_v2_div_hidden_bullish_recent",
        "stas4_v2_combo_rsi14",
        "stas4_v2_combo_macd_hist_norm",
        "stas4_v2_combo_stoch_k14",
    ]
    out = rows.copy()
    out["user_review_label"] = "PENDING_USER_REVIEW"
    out["user_note"] = ""
    out["risk_bucket"] = out.apply(risk_bucket, axis=1)
    for column in columns:
        if column not in out.columns:
            out[column] = ""
    return out[columns]


def _plot_candidates(ax: Any, rows: pd.DataFrame, *, label_all: bool = True) -> None:
    if rows.empty:
        return
    rows = rows.copy()
    rows["risk_bucket"] = rows.apply(risk_bucket, axis=1)
    for bucket, style in BUCKET_STYLES.items():
        subset = rows[rows["risk_bucket"] == bucket]
        if subset.empty:
            continue
        ax.scatter(
            subset["entry_ts"].dt.tz_convert(None),
            pd.to_numeric(subset["entry_price_5bps"], errors="coerce"),
            marker=style["marker"],
            s=style["size"],
            color=style["color"],
            edgecolors="#071014",
            linewidths=0.65,
            alpha=0.96,
            zorder=9,
            label=f"{style['label']} ({len(subset)})",
        )
    if not label_all:
        return
    for idx, row in rows.reset_index(drop=True).iterrows():
        bucket = str(row["risk_bucket"])
        style = BUCKET_STYLES.get(bucket, BUCKET_STYLES["CAUTION"])
        entry_ts = pd.Timestamp(row["entry_ts"]).tz_convert("UTC").tz_convert(None)
        price = _safe_float(row.get("entry_price_5bps"))
        y_offset = 9 if idx % 2 == 0 else -18
        va = "bottom" if y_offset > 0 else "top"
        text = (
            f"{row['candidate_id']}\n"
            f"r{_safe_float(row.get('stas5_v2_risk_knife_pre_entry')):.2f} "
            f"s{_safe_float(row.get('stas4_v2_combo_short_pressure_score')):.1f}"
        )
        ax.annotate(
            text,
            xy=(entry_ts, price),
            xytext=(0, y_offset),
            textcoords="offset points",
            ha="center",
            va=va,
            color=style["color"],
            fontsize=7.4,
            alpha=0.96,
            arrowprops={"arrowstyle": "-", "color": style["color"], "linewidth": 0.55, "alpha": 0.65},
        )


def render_review_window(
    *,
    day_df: pd.DataFrame,
    rows: pd.DataFrame,
    day: str,
    symbol: str,
    timeframe: str,
    start_ts: pd.Timestamp,
    end_ts: pd.Timestamp,
    out_path: Path,
    title_suffix: str,
    label_all: bool = True,
) -> None:
    window_df = day_df[(day_df["open_time_utc"] >= start_ts) & (day_df["open_time_utc"] <= end_ts)].copy().reset_index(drop=True)
    window_rows = rows[(rows["entry_ts"] >= start_ts) & (rows["entry_ts"] <= end_ts)].copy()
    if window_df.empty:
        raise ValueError(f"empty OHLCV window {start_ts}..{end_ts}")

    fig, (ax_price, ax_vol, ax_risk, ax_combo) = plt.subplots(
        4,
        1,
        figsize=(24, 14),
        sharex=True,
        gridspec_kw={"height_ratios": [5.7, 1.05, 1.85, 2.25], "hspace": 0.055},
    )
    fig.patch.set_facecolor("#101418")
    for ax in [ax_price, ax_vol, ax_risk, ax_combo]:
        _style_axis(ax)

    _draw_candles(ax_price, window_df, timeframe, linewidth=0.35)
    candle_colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(window_df["open"], window_df["close"])]
    ax_vol.bar(
        window_df["open_time_utc"].dt.tz_convert(None),
        window_df["volume"],
        width=_bar_width_days(timeframe),
        color=candle_colors,
        alpha=0.72,
    )
    _plot_candidates(ax_price, window_rows, label_all=label_all)
    ax_price.set_ylabel("Price", color="#eceff1")
    ax_vol.set_ylabel("Vol", color="#eceff1")
    ax_price.set_title(
        f"STAS5 V2 user review | {symbol} {timeframe} {day} | {title_suffix} | mark 2-5 real entries, rest noise",
        color="#eceff1",
        fontsize=15,
    )
    legend = ax_price.legend(loc="upper left", facecolor="#101418", edgecolor="#455a64", labelcolor="#eceff1", fontsize=9)
    for text in legend.get_texts():
        text.set_color("#eceff1")

    if not window_rows.empty:
        x = window_rows["entry_ts"].dt.tz_convert(None)
        ax_risk.plot(
            x,
            window_rows["stas5_v2_risk_knife_pre_entry"],
            color="#ff4d5e",
            linewidth=1.25,
            marker="o",
            markersize=4.0,
            label="knife_risk",
        )
        ax_risk.plot(
            x,
            window_rows["stas4_v2_combo_short_pressure_score"],
            color="#ff9f1a",
            linewidth=1.10,
            marker="o",
            markersize=3.5,
            label="short_pressure",
        )
        ax_risk.plot(
            x,
            window_rows["stas4_v2_combo_long_recovery_score"],
            color="#00e5ff",
            linewidth=1.10,
            marker="o",
            markersize=3.5,
            label="long_recovery",
        )
        blocked = window_rows[window_rows["stas5_v2_gate_long_allowed_final"].astype(int) == 0]
        if not blocked.empty:
            ax_risk.scatter(
                blocked["entry_ts"].dt.tz_convert(None),
                [1.05] * len(blocked),
                marker="X",
                s=92,
                color="#ff1744",
                zorder=9,
                label="long_allowed=0",
            )
        ax_combo.plot(x, window_rows["stas4_v2_combo_rsi14"], color="#ffffff", linewidth=1.10, marker=".", label="RSI14")
        ax_combo.plot(
            x,
            window_rows["stas4_v2_combo_rsi_signal9"],
            color="#f3d42b",
            linewidth=1.05,
            marker=".",
            label="RSI signal",
        )
        ax_combo.plot(
            x,
            window_rows["stas4_v2_combo_stoch_k14"],
            color="#00ffc3",
            linewidth=1.00,
            marker=".",
            label="Stoch K",
        )
        ax_combo.bar(
            x,
            pd.to_numeric(window_rows["stas4_v2_combo_macd_hist_norm"], errors="coerce").clip(-8, 8) * 2.2,
            bottom=50,
            width=0.0022,
            color=np.where(window_rows["stas4_v2_combo_macd_hist_norm"] >= 0, "#00c781", "#ff4b5c"),
            alpha=0.24,
            label="MACD hist norm",
        )
    ax_risk.axhspan(0.55, 1.05, color="#5b1f34", alpha=0.22)
    ax_risk.axhline(0.55, color="#ff4d5e", linestyle="--", linewidth=0.80, alpha=0.72)
    ax_risk.axhline(0.45, color="#ffd43b", linestyle="--", linewidth=0.80, alpha=0.72)
    ax_risk.set_ylim(-0.03, 1.08)
    ax_risk.set_ylabel("Risk/Gate", color="#eceff1")
    risk_legend = ax_risk.legend(loc="upper right", facecolor="#101418", edgecolor="#455a64", labelcolor="#eceff1", fontsize=9, ncol=4)
    for text in risk_legend.get_texts():
        text.set_color("#eceff1")

    for level, color, alpha in [(80, "#ff3355", 0.75), (60, "#7d8594", 0.32), (50, "#cfd8dc", 0.35), (40, "#7d8594", 0.32), (20, "#00e676", 0.75)]:
        ax_combo.axhline(level, color=color, linestyle="--" if level in {80, 20} else "-", linewidth=0.75, alpha=alpha)
    ax_combo.set_ylim(0, 100)
    ax_combo.set_ylabel("Combo", color="#eceff1")
    combo_legend = ax_combo.legend(loc="upper right", facecolor="#101418", edgecolor="#455a64", labelcolor="#eceff1", fontsize=9, ncol=4)
    for text in combo_legend.get_texts():
        text.set_color("#eceff1")

    start_no_tz = start_ts.tz_convert(None)
    end_no_tz = end_ts.tz_convert(None)
    for ax in [ax_price, ax_vol, ax_risk, ax_combo]:
        ax.set_xlim(start_no_tz.to_pydatetime(), end_no_tz.to_pydatetime())
    ax_combo.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
    ax_combo.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate()
    fig.subplots_adjust(left=0.045, right=0.995, top=0.955, bottom=0.085, hspace=0.065)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor())
    plt.close(fig)


def _window_bounds(day: str, window_hours: int) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    start = pd.Timestamp(f"{day}T00:00:00Z")
    end = start + pd.Timedelta(days=1)
    out: list[tuple[pd.Timestamp, pd.Timestamp]] = []
    cur = start
    while cur < end:
        nxt = min(cur + pd.Timedelta(hours=window_hours), end)
        out.append((cur, nxt))
        cur = nxt
    return out


def run_user_review_render(
    *,
    day: str,
    symbol: str = "SOLUSDT",
    timeframe: str = "1m",
    features_path: Path = DEFAULT_FORWARD_V2_FEATURE_PATH,
    out_root: Path = DEFAULT_USER_REVIEW_ROOT,
    window_hours: int = 3,
    label_all: bool = True,
) -> dict[str, Any]:
    day = pd.Timestamp(day).strftime("%Y-%m-%d")
    source = _source_csv(PROJECT_ROOT, day, timeframe, symbol)
    if not source.exists():
        raise FileNotFoundError(f"OHLCV not found: {source}")
    day_df = _load_ohlcv(source)
    rows = _read_features(features_path, day)
    out_dir = out_root / day.replace("-", "")
    out_dir.mkdir(parents=True, exist_ok=True)

    template = build_user_review_template(rows)
    template_path = out_dir / f"STAS5_V2_USER_REVIEW_TEMPLATE_{day.replace('-', '')}.csv"
    template.to_csv(template_path, index=False, encoding="utf-8-sig")

    page_paths: list[Path] = []
    for page_no, (start_ts, end_ts) in enumerate(_window_bounds(day, window_hours), start=1):
        window_rows = rows[(rows["entry_ts"] >= start_ts) & (rows["entry_ts"] <= end_ts)]
        if window_rows.empty:
            continue
        suffix = f"PAGE_{page_no:02d}_{start_ts.strftime('%H%M')}_{end_ts.strftime('%H%M')}"
        out_path = out_dir / f"STAS5_V2_USER_REVIEW_{day.replace('-', '')}_{suffix}.png"
        render_review_window(
            day_df=day_df,
            rows=rows,
            day=day,
            symbol=symbol,
            timeframe=timeframe,
            start_ts=start_ts,
            end_ts=end_ts,
            out_path=out_path,
            title_suffix=suffix,
            label_all=label_all,
        )
        page_paths.append(out_path)

    full_path = out_dir / f"STAS5_V2_USER_REVIEW_{day.replace('-', '')}_FULL.png"
    render_review_window(
        day_df=day_df,
        rows=rows,
        day=day,
        symbol=symbol,
        timeframe=timeframe,
        start_ts=pd.Timestamp(f"{day}T00:00:00Z"),
        end_ts=pd.Timestamp(f"{day}T23:59:59Z"),
        out_path=full_path,
        title_suffix="FULL_DAY",
        label_all=False,
    )

    counts = rows["risk_bucket"].value_counts().to_dict()
    manifest = {
        "status": "PASS",
        "pipeline_status": STATUS,
        "created_utc": utc_now(),
        "day": day,
        "symbol": symbol,
        "timeframe": timeframe,
        "source_features": rel(features_path),
        "source_ohlcv": rel(source),
        "out_dir": rel(out_dir),
        "template_csv": rel(template_path),
        "full_png": rel(full_path),
        "page_pngs": [rel(path) for path in page_paths],
        "rows": int(len(rows)),
        "risk_bucket_counts": {str(key): int(value) for key, value in counts.items()},
        "guardrails": [
            "forward_user_review_only",
            "not_training",
            "not_threshold_tuning",
            "not_trading_permission",
            "user_review_label_template_defaults_to_pending",
        ],
    }
    manifest_path = out_dir / f"STAS5_V2_USER_REVIEW_{day.replace('-', '')}.manifest.json"
    write_json(manifest_path, manifest)
    manifest["manifest_path"] = rel(manifest_path)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Render STAS5 V2 forward user-review pages.")
    parser.add_argument("--day", default="2026-05-15")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--features-path", default=str(DEFAULT_FORWARD_V2_FEATURE_PATH))
    parser.add_argument("--out-root", default=str(DEFAULT_USER_REVIEW_ROOT))
    parser.add_argument("--window-hours", type=int, default=3)
    parser.add_argument("--no-label-all", action="store_true")
    args = parser.parse_args()
    manifest = run_user_review_render(
        day=args.day,
        symbol=args.symbol,
        timeframe=args.timeframe,
        features_path=Path(args.features_path),
        out_root=Path(args.out_root),
        window_hours=args.window_hours,
        label_all=not args.no_label_all,
    )
    print(manifest["status"], manifest["rows"], manifest["out_dir"])
    print(manifest["template_csv"])
    for path in manifest["page_pngs"]:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
