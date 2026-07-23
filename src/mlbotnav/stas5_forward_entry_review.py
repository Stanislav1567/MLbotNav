from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import joblib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from mlbotnav.stas5_common import (
    DEFAULT_MODEL_MANIFEST_PATH,
    DEFAULT_MODEL_PATH,
    FORWARD_END_DAY,
    FORWARD_START_DAY,
    PROJECT_ROOT,
    STAS5_ARTIFACTS_DIR,
    STATUS_CURRENT,
    iter_days,
    rel,
    run_stamp,
    score_to_decision,
    utc_now,
    write_csv,
    write_json,
)
from mlbotnav.stas5_entry_ranker_train import _positive_proba, _prepare_feature_matrix
from mlbotnav.stas5_feature_snapshot_builder import build_feature_snapshot_from_frames
from mlbotnav.visual_entry_low_anchor_suggester import (
    _add_features,
    _bar_width_days,
    _draw_candles,
    _load_ohlcv,
    _source_csv,
    _style_axis,
    build_candidates,
)
from mlbotnav.visual_entry_stas2_market_phase_review import run_review as run_stas2_review


DEFAULT_FORWARD_DIR = STAS5_ARTIFACTS_DIR / "forward"
DEFAULT_FORWARD_SOURCE_DIR = STAS5_ARTIFACTS_DIR / "forward_source"


def _fmt_ts(value: Any) -> str:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


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


def _record_id(day: str, candidate_id: str) -> str:
    return f"STAS5F_{day.replace('-', '')}_{candidate_id}"


def generate_forward_stas1_source(
    *,
    start_day: str,
    end_day: str,
    symbol: str,
    timeframe: str,
    out_dir: Path,
    run_label: str,
    min_score: float = 2.5,
    cooldown_minutes: int = 4,
    anchor_lookback: int = 12,
    max_anchor_age: int = 3,
) -> Path:
    root = PROJECT_ROOT
    run_id = f"{run_label}_{run_stamp()}"
    run_dir = out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    missing_sources: list[str] = []
    per_day: dict[str, int] = {}
    for day in iter_days(start_day, end_day):
        source = _source_csv(root, day, timeframe, symbol)
        if not source.exists():
            missing_sources.append(rel(source))
            continue
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
        per_day[day] = len(candidates)
        for item in candidates:
            features = item.get("features_at_signal_close") or {}
            entry_open = _safe_float(item.get("entry_open_price"))
            row = {
                "run_id": run_id,
                "day_utc": day,
                "record_id": _record_id(day, str(item["candidate_id"])),
                "candidate_id": item.get("candidate_id"),
                "review_label": "FORWARD_UNLABELED",
                "outcome_status": "FORWARD_UNLABELED_NO_OUTCOME",
                "suggested_type": item.get("suggested_type"),
                "score": item.get("score"),
                "anchor_idx": item.get("anchor_idx"),
                "signal_idx": item.get("signal_idx"),
                "confirmation_idx": item.get("confirmation_idx"),
                "entry_idx": item.get("entry_idx"),
                "anchor_age_bars": item.get("anchor_age_bars"),
                "execution_delay_bars_from_anchor": item.get("execution_delay_bars_from_anchor"),
                "anchor_time_utc": item.get("anchor_time_utc"),
                "anchor_low_price": item.get("anchor_low_price"),
                "signal_time_utc": item.get("signal_time_utc"),
                "confirmation_time_utc": item.get("confirmation_time_utc"),
                "entry_time_utc": item.get("entry_time_utc"),
                "entry_open_price": entry_open,
                "entry_price_0bps": entry_open,
                "entry_price_5bps": entry_open * 1.0005,
                "entry_price_10bps": entry_open * 1.0010,
                "risk_flags": item.get("risk_flags") or [],
                "outcome_usage": "not_calculated_for_forward_source",
                "source_csv": rel(source),
            }
            for key, value in sorted(features.items()):
                row[f"feature_{key}"] = value
            rows.append(row)

    csv_path = run_dir / "GOOD_1PCT_REVIEW_POOL_RECORDS.csv"
    write_csv(csv_path, rows)
    write_json(
        run_dir / "STAS5_FORWARD_STAS1_SOURCE_MANIFEST.json",
        {
            "status": "FORWARD_UNLABELED_CANDIDATE_SOURCE_READY",
            "pipeline_status": STATUS_CURRENT,
            "created_utc": utc_now(),
            "run_id": run_id,
            "date_range": {"start_day": start_day, "end_day": end_day},
            "symbol": symbol,
            "timeframe": timeframe,
            "rows": len(rows),
            "per_day": per_day,
            "missing_sources": missing_sources,
            "csv_path": rel(csv_path),
            "guardrails": [
                "no_human_labels",
                "no_outcome_labels",
                "candidate_generation_from_local_core_ohlcv_only",
            ],
        },
    )
    return run_dir


def ensure_forward_stas2_run(
    *,
    start_day: str,
    end_day: str,
    symbol: str,
    timeframe: str,
    stas2_run_dir: Path | None,
    forward_source_dir: Path,
    stas2_render_limit: int = 1,
) -> Path:
    if stas2_run_dir is not None:
        records = stas2_run_dir / "STAS2_RECORDS.csv"
        if not records.exists():
            raise FileNotFoundError(f"STAS2_RECORDS.csv not found: {records}")
        return stas2_run_dir

    stas1_dir = generate_forward_stas1_source(
        start_day=start_day,
        end_day=end_day,
        symbol=symbol,
        timeframe=timeframe,
        out_dir=forward_source_dir / "stas1_runs",
        run_label=f"stas5_forward_stas1_{start_day.replace('-', '')}_{end_day.replace('-', '')}",
    )
    payload = run_stas2_review(
        start_day=start_day,
        end_day=end_day,
        symbol=symbol,
        timeframe=timeframe,
        out_dir=forward_source_dir / "stas2_runs",
        run_label=f"stas5_forward_stas2_{start_day.replace('-', '')}_{end_day.replace('-', '')}",
        stas1_run_dirs=[str(stas1_dir)],
        render_limit=stas2_render_limit,
    )
    return PROJECT_ROOT / payload["artifacts"]["run_dir"]


def _add_postfact_audit(day_df: pd.DataFrame, rows: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    hit_05: list[bool] = []
    hit_10: list[bool] = []
    max_up: list[float] = []
    max_dd: list[float] = []
    for _, row in out.iterrows():
        entry_ts = pd.Timestamp(row["entry_time_utc"])
        if entry_ts.tzinfo is None:
            entry_ts = entry_ts.tz_localize("UTC")
        else:
            entry_ts = entry_ts.tz_convert("UTC")
        entry_price = _safe_float(row.get("entry_price_5bps") or row.get("entry_open_price"))
        future = day_df[day_df["open_time_utc"] > entry_ts]
        if future.empty or entry_price <= 0:
            hit_05.append(False)
            hit_10.append(False)
            max_up.append(0.0)
            max_dd.append(0.0)
            continue
        up_pct = (float(future["high"].max()) / entry_price - 1.0) * 100.0
        dd_pct = (float(future["low"].min()) / entry_price - 1.0) * 100.0
        max_up.append(round(up_pct, 6))
        max_dd.append(round(dd_pct, 6))
        hit_05.append(bool(up_pct >= 0.5))
        hit_10.append(bool(up_pct >= 1.0))
    out["postfact_hit_0p5_pct"] = hit_05
    out["postfact_hit_1p0_pct"] = hit_10
    out["postfact_max_up_pct"] = max_up
    out["postfact_max_drawdown_pct"] = max_dd
    out["postfact_usage"] = "audit_only_not_feature_not_threshold_tuning"
    return out


def predict_forward_records(
    *,
    stas2_run_dir: Path,
    model_package: dict[str, Any],
    model_manifest: dict[str, Any],
) -> pd.DataFrame:
    records_path = stas2_run_dir / "STAS2_RECORDS.csv"
    stas2 = pd.read_csv(records_path, encoding="utf-8-sig")
    if (stas2["day_utc"].astype(str) <= "2026-05-14").any():
        raise ValueError("forward review received train-window rows")
    snapshot, _manifest = build_feature_snapshot_from_frames(
        stas2=stas2,
        ledger=None,
        source_stas2_run=rel(stas2_run_dir),
        feature_columns=[str(column) for column in model_package["feature_columns"]],
    )
    x = _prepare_feature_matrix(
        snapshot,
        feature_columns=[str(column) for column in model_package["feature_columns"]],
        numeric_columns=[str(column) for column in model_package.get("numeric_columns", [])],
        categorical_columns=[str(column) for column in model_package.get("categorical_columns", [])],
    )
    scores = _positive_proba(model_package["pipeline"], x)
    thresholds = model_package.get("thresholds") or model_manifest.get("thresholds") or {"enter": 0.65, "unsure": 0.45}
    snapshot["ML_KEEP_SCORE"] = scores
    snapshot["ML_DECISION"] = [
        score_to_decision(score, enter_threshold=float(thresholds["enter"]), unsure_threshold=float(thresholds["unsure"]))
        for score in scores
    ]
    snapshot["model_id"] = model_package.get("model_id") or model_manifest.get("model_id") or "STAS5_ENTRY_RANKER"
    snapshot["threshold_enter"] = float(thresholds["enter"])
    snapshot["threshold_unsure"] = float(thresholds["unsure"])
    snapshot["forward_policy"] = "blind_forward_not_training_not_threshold_tuning"
    return snapshot


def render_forward_day(
    *,
    day_df: pd.DataFrame,
    rows: pd.DataFrame,
    day: str,
    symbol: str,
    timeframe: str,
    out_path: Path,
) -> None:
    fig, (ax_price, ax_vol) = plt.subplots(
        2,
        1,
        figsize=(32, 13),
        sharex=True,
        gridspec_kw={"height_ratios": [4.9, 1.15]},
    )
    fig.patch.set_facecolor("#101418")
    _style_axis(ax_price)
    _style_axis(ax_vol)
    _draw_candles(ax_price, day_df, timeframe, linewidth=0.30)
    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(day_df["open"], day_df["close"])]
    ax_vol.bar(day_df["open_time_utc"].dt.tz_convert(None), day_df["volume"], width=_bar_width_days(timeframe), color=colors, alpha=0.70)

    marker_style = {
        "ENTER": {"marker": "^", "color": "#00e676", "size": 130, "alpha": 0.96, "linewidth": 0.7},
        "UNSURE": {"marker": "D", "color": "#ffd54f", "size": 82, "alpha": 0.90, "linewidth": 0.45},
        "SKIP": {"marker": "x", "color": "#90a4ae", "size": 62, "alpha": 0.34, "linewidth": 1.2},
    }
    if not rows.empty:
        x_all = pd.to_datetime(rows["entry_time_utc"], utc=True).dt.tz_convert(None)
        y_all = pd.to_numeric(rows["entry_open_price"], errors="coerce")
        ax_price.scatter(x_all, y_all, s=28, color="#b0bec5", alpha=0.18, zorder=5, label="all candidates")

    for decision in ["SKIP", "UNSURE", "ENTER"]:
        subset = rows[rows["ML_DECISION"] == decision].copy()
        if subset.empty:
            continue
        style = marker_style[decision]
        x = pd.to_datetime(subset["entry_time_utc"], utc=True).dt.tz_convert(None)
        y = pd.to_numeric(subset["entry_open_price"], errors="coerce")
        scatter_kwargs = {
            "marker": style["marker"],
            "s": style["size"],
            "color": style["color"],
            "linewidths": style["linewidth"],
            "alpha": style["alpha"],
            "zorder": 8 if decision == "ENTER" else 7,
            "label": f"{decision} ({len(subset)})",
        }
        if decision != "SKIP":
            scatter_kwargs["edgecolors"] = "white"
        ax_price.scatter(x, y, **scatter_kwargs)
        if decision in {"ENTER", "UNSURE"}:
            for _, row in subset.iterrows():
                entry_ts = pd.Timestamp(row["entry_time_utc"]).tz_convert("UTC").tz_convert(None)
                price = _safe_float(row.get("entry_open_price"))
                ax_price.annotate(
                    f"{row['candidate_id']} {float(row['ML_KEEP_SCORE']):.2f}",
                    xy=(entry_ts, price),
                    xytext=(6, 8 if decision == "ENTER" else -13),
                    textcoords="offset points",
                    color=style["color"],
                    fontsize=8,
                    arrowprops={"arrowstyle": "->", "color": style["color"], "linewidth": 0.85, "alpha": 0.8},
                )

    day_start = pd.Timestamp(f"{day} 00:00:00")
    day_end = day_start + pd.Timedelta(days=1)
    ax_price.set_xlim(day_start.to_pydatetime(), day_end.to_pydatetime())
    ax_price.set_title(
        f"STAS5 ML forward entries | {symbol} {timeframe} {day} | ENTER/UNSURE/SKIP | no TP/Stas3",
        color="white",
        fontsize=15,
    )
    ax_price.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    ax_vol.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 25, 2)))
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax_price.legend(loc="upper left", facecolor="#101418", edgecolor="#455a64", labelcolor="#eceff1")
    fig.autofmt_xdate()
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor())
    plt.close(fig)


def run_forward_review(
    *,
    start_day: str = FORWARD_START_DAY,
    end_day: str = FORWARD_END_DAY,
    symbol: str = "SOLUSDT",
    timeframe: str = "1m",
    model_path: Path = DEFAULT_MODEL_PATH,
    model_manifest_path: Path = DEFAULT_MODEL_MANIFEST_PATH,
    stas2_run_dir: Path | None = None,
    out_dir: Path = DEFAULT_FORWARD_DIR,
    forward_source_dir: Path = DEFAULT_FORWARD_SOURCE_DIR,
    stas2_render_limit: int = 1,
) -> dict[str, Any]:
    model_package = joblib.load(model_path)
    model_manifest = json.loads(model_manifest_path.read_text(encoding="utf-8"))
    stas2_dir = ensure_forward_stas2_run(
        start_day=start_day,
        end_day=end_day,
        symbol=symbol,
        timeframe=timeframe,
        stas2_run_dir=stas2_run_dir,
        forward_source_dir=forward_source_dir,
        stas2_render_limit=stas2_render_limit,
    )
    predictions = predict_forward_records(stas2_run_dir=stas2_dir, model_package=model_package, model_manifest=model_manifest)

    day_outputs: list[dict[str, Any]] = []
    for day in iter_days(start_day, end_day):
        day_rows = predictions[predictions["day"].astype(str) == day].copy()
        day_dir = out_dir / day.replace("-", "")
        source = _source_csv(PROJECT_ROOT, day, timeframe, symbol)
        if not source.exists():
            day_outputs.append({"day": day, "status": "MISSING_OHLCV", "rows": int(len(day_rows)), "source": rel(source)})
            continue
        day_df = _load_ohlcv(source)
        day_rows = _add_postfact_audit(day_df, day_rows)
        csv_path = day_dir / f"STAS5_FORWARD_ENTRIES_{day.replace('-', '')}.csv"
        png_path = day_dir / f"STAS5_FORWARD_ENTRY_REVIEW_{day.replace('-', '')}.png"
        day_dir.mkdir(parents=True, exist_ok=True)
        day_rows.to_csv(csv_path, index=False, encoding="utf-8-sig")
        render_forward_day(day_df=day_df, rows=day_rows, day=day, symbol=symbol, timeframe=timeframe, out_path=png_path)
        counts = Counter(day_rows["ML_DECISION"].astype(str))
        day_outputs.append(
            {
                "day": day,
                "status": "READY",
                "rows": int(len(day_rows)),
                "decision_counts": dict(counts),
                "csv": rel(csv_path),
                "png": rel(png_path),
            }
        )

    manifest = {
        "status": "FORWARD_ENTRY_REVIEW_READY",
        "pipeline_status": STATUS_CURRENT,
        "created_utc": utc_now(),
        "date_range": {"start_day": start_day, "end_day": end_day},
        "symbol": symbol,
        "timeframe": timeframe,
        "model_path": rel(model_path),
        "model_manifest_path": rel(model_manifest_path),
        "model_id": model_package.get("model_id") or model_manifest.get("model_id"),
        "stas2_run_dir": rel(stas2_dir),
        "out_dir": rel(out_dir),
        "day_outputs": day_outputs,
        "guardrails": [
            "forward_days_not_used_for_training",
            "forward_days_not_used_for_threshold_tuning",
            "png_has_no_tp_lines",
            "stas3_not_used",
            "postfact_columns_are_audit_only",
        ],
    }
    write_json(out_dir / "STAS5_FORWARD_ENTRY_REVIEW_MANIFEST.json", manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Render STAS5 blind forward ML entry review.")
    parser.add_argument("--start-day", default=FORWARD_START_DAY)
    parser.add_argument("--end-day", default=FORWARD_END_DAY)
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--model-path", default=str(DEFAULT_MODEL_PATH))
    parser.add_argument("--model-manifest-path", default=str(DEFAULT_MODEL_MANIFEST_PATH))
    parser.add_argument("--stas2-run-dir", default="")
    parser.add_argument("--out-dir", default=str(DEFAULT_FORWARD_DIR))
    parser.add_argument("--forward-source-dir", default=str(DEFAULT_FORWARD_SOURCE_DIR))
    parser.add_argument("--stas2-render-limit", type=int, default=1)
    args = parser.parse_args()

    manifest = run_forward_review(
        start_day=args.start_day,
        end_day=args.end_day,
        symbol=args.symbol,
        timeframe=args.timeframe,
        model_path=Path(args.model_path),
        model_manifest_path=Path(args.model_manifest_path),
        stas2_run_dir=Path(args.stas2_run_dir) if args.stas2_run_dir else None,
        out_dir=Path(args.out_dir),
        forward_source_dir=Path(args.forward_source_dir),
        stas2_render_limit=args.stas2_render_limit,
    )
    print({"status": manifest["status"], "stas2_run_dir": manifest["stas2_run_dir"], "day_outputs": manifest["day_outputs"]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
