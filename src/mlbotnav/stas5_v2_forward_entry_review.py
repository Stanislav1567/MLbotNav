from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import joblib
import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from mlbotnav.stas5_common import (
    FORWARD_END_DAY,
    FORWARD_START_DAY,
    PROJECT_ROOT,
    STAS5_ARTIFACTS_DIR,
    compact_day,
    iter_days,
    read_csv,
    rel,
    run_stamp,
    score_to_decision,
    utc_now,
    write_json,
)
from mlbotnav.stas5_entry_ranker_train import _positive_proba, _prepare_feature_matrix
from mlbotnav.stas5_feature_snapshot_builder import build_feature_snapshot_from_frames
from mlbotnav.stas5_forward_entry_review import _add_postfact_audit
from mlbotnav.stas5_v2_combo_feature_exporter import TIMEFRAME
from mlbotnav.stas5_v2_entry_ranker_train import DEFAULT_V2_MODEL_MANIFEST_PATH, DEFAULT_V2_MODEL_PATH
from mlbotnav.stas5_v2_feature_snapshot_builder import (
    DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH,
    build_v2_feature_snapshot_from_frames,
)
from mlbotnav.stas5_v2_forward_user_review import DEFAULT_FORWARD_V2_FEATURE_PATH
from mlbotnav.stas5_v2_feature_visual_approval import (
    _plot_risk_gate,
    _plot_structure_density,
    _plot_v2_combo_snapshot,
    _read_rows,
)
from mlbotnav.visual_entry_low_anchor_suggester import _bar_width_days, _draw_candles, _load_ohlcv, _source_csv, _style_axis
from mlbotnav.visual_entry_stas2_market_phase_review import (
    _render_macro_wave_strip,
    _render_rank_strip,
    _set_day_time_axis,
    _shade_sessions,
)


STATUS = "STAS5_V2_FORWARD_ENTRY_REVIEW_READY_BLIND_NO_TP_NO_API_NO_STAS3"
SYMBOL = "SOLUSDT"
DEFAULT_V2_FORWARD_ROOT = STAS5_ARTIFACTS_DIR / "v2" / "forward"
DEFAULT_V2_FORWARD_RUNS_DIR = DEFAULT_V2_FORWARD_ROOT / "runs"
DEFAULT_FORWARD_SOURCE_STAS2_ROOT = STAS5_ARTIFACTS_DIR / "forward_source" / "stas2_runs"


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


def _resolve_stas2_run_dir(path: Path | None) -> Path:
    if path is not None:
        records = path / "STAS2_RECORDS.csv"
        if not records.exists():
            raise FileNotFoundError(f"STAS2_RECORDS.csv not found: {records}")
        return path
    candidates = sorted(
        [item for item in DEFAULT_FORWARD_SOURCE_STAS2_ROOT.glob("stas5_forward_stas2_20260515_20260520_*") if (item / "STAS2_RECORDS.csv").exists()],
        key=lambda item: item.name,
    )
    if not candidates:
        raise FileNotFoundError(f"no forward STAS2 run found under {DEFAULT_FORWARD_SOURCE_STAS2_ROOT}")
    return candidates[-1]


def _latest_model_manifest() -> Path:
    pointer = DEFAULT_V2_MODEL_PATH.parent / "STAS5_V2_LATEST_MODEL_RUN.json"
    if pointer.exists():
        payload = json.loads(pointer.read_text(encoding="utf-8"))
        manifest_path = Path(payload.get("manifest_path", ""))
        if not manifest_path.is_absolute():
            manifest_path = PROJECT_ROOT / manifest_path
        if manifest_path.exists():
            return manifest_path
    manifests = sorted(
        DEFAULT_V2_MODEL_PATH.parent.glob("runs/*/stas5_v2_entry_ranker_20260501_20260514_v0.manifest.json"),
        key=lambda item: item.stat().st_mtime,
    )
    if manifests:
        return manifests[-1]
    if DEFAULT_V2_MODEL_MANIFEST_PATH.exists():
        return DEFAULT_V2_MODEL_MANIFEST_PATH
    raise FileNotFoundError("no STAS5 V2 model manifest found")


def _model_path_from_manifest(manifest_path: Path) -> Path:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    model_path = Path(payload.get("model_path", ""))
    if not model_path.is_absolute():
        model_path = PROJECT_ROOT / model_path
    if not model_path.exists():
        raise FileNotFoundError(f"model file from manifest not found: {model_path}")
    return model_path


def build_v2_forward_snapshot(
    *,
    stas2_run_dir: Path,
    v2_combo_path: Path = DEFAULT_FORWARD_V2_FEATURE_PATH,
    train_snapshot_manifest_path: Path = DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    train_manifest = json.loads(train_snapshot_manifest_path.read_text(encoding="utf-8"))
    v1_feature_columns = [str(column) for column in train_manifest.get("v1_feature_columns", [])]
    v2_feature_columns = [str(column) for column in train_manifest.get("v2_feature_columns", [])]
    if not v1_feature_columns or not v2_feature_columns:
        raise ValueError("V2 train snapshot manifest must contain v1_feature_columns and v2_feature_columns")

    stas2 = read_csv(stas2_run_dir / "STAS2_RECORDS.csv")
    if (stas2["day_utc"].astype(str) <= "2026-05-14").any():
        raise ValueError("forward V2 snapshot received train-window rows")
    v1_snapshot, v1_manifest = build_feature_snapshot_from_frames(
        stas2=stas2,
        ledger=None,
        source_stas2_run=rel(stas2_run_dir),
        feature_columns=v1_feature_columns,
    )
    v2_combo = read_csv(v2_combo_path)
    snapshot, manifest = build_v2_feature_snapshot_from_frames(
        v1_snapshot=v1_snapshot,
        v2_combo=v2_combo,
        v1_feature_columns=v1_feature_columns,
        v2_feature_columns=v2_feature_columns,
        ledger=None,
        source_v1_snapshot=f"forward_in_memory:{rel(stas2_run_dir)}",
        source_v2_combo=rel(v2_combo_path),
    )
    manifest["status"] = "PASS" if manifest["status"] == "PASS" and v1_manifest["status"] == "PASS" else "FAIL"
    manifest["pipeline_status"] = "STAS5_V2_FORWARD_SNAPSHOT_READY_NO_TRAINING"
    manifest["source_stas2_run_dir"] = rel(stas2_run_dir)
    manifest["source_v2_combo_path"] = rel(v2_combo_path)
    manifest["train_snapshot_manifest_path"] = rel(train_snapshot_manifest_path)
    manifest["guardrails"] = list(manifest.get("guardrails", [])) + [
        "forward_snapshot_has_no_human_train_labels",
        "forward_v2_combo_join_required",
        "forward_20260515_plus_not_used_for_training",
    ]
    return snapshot, manifest


def predict_v2_forward(
    *,
    snapshot: pd.DataFrame,
    model_package: dict[str, Any],
    model_manifest: dict[str, Any],
) -> pd.DataFrame:
    feature_columns = [str(column) for column in model_package["feature_columns"]]
    x = _prepare_feature_matrix(
        snapshot,
        feature_columns=feature_columns,
        numeric_columns=[str(column) for column in model_package.get("numeric_columns", [])],
        categorical_columns=[str(column) for column in model_package.get("categorical_columns", [])],
    )
    scores = _positive_proba(model_package["pipeline"], x)
    thresholds = model_package.get("thresholds") or model_manifest.get("thresholds") or {"enter": 0.65, "unsure": 0.45}
    out = snapshot.copy()
    out["ML_KEEP_SCORE_V2"] = scores
    out["ML_DECISION_V2"] = [
        score_to_decision(score, enter_threshold=float(thresholds["enter"]), unsure_threshold=float(thresholds["unsure"]))
        for score in scores
    ]
    out["ML_KEEP_SCORE"] = out["ML_KEEP_SCORE_V2"]
    out["ML_DECISION"] = out["ML_DECISION_V2"]
    out["model_id"] = model_package.get("model_id") or model_manifest.get("model_id") or "STAS5_V2_ENTRY_RANKER"
    out["model_feature_set"] = model_package.get("model_feature_set") or model_manifest.get("model_feature_set") or "unknown"
    out["threshold_enter"] = float(thresholds["enter"])
    out["threshold_unsure"] = float(thresholds["unsure"])
    out["forward_policy"] = "blind_forward_not_training_not_threshold_tuning"
    return out


def _plot_ml_price_markers(ax: Any, rows: pd.DataFrame) -> None:
    if rows.empty:
        return
    styles = {
        "SKIP": {"marker": "x", "color": "#78909c", "size": 44, "alpha": 0.28, "label": "SKIP"},
        "UNSURE": {"marker": "D", "color": "#ffd54f", "size": 84, "alpha": 0.92, "label": "UNSURE"},
        "ENTER": {"marker": "^", "color": "#00e676", "size": 132, "alpha": 0.98, "label": "ENTER"},
    }
    rows = rows.copy()
    rows["entry_ts"] = pd.to_datetime(rows["entry_time_utc"], utc=True)
    y = pd.to_numeric(rows.get("entry_price_5bps", rows.get("entry_open_price")), errors="coerce")
    ax.scatter(rows["entry_ts"].dt.tz_convert(None), y, s=24, color="#b0bec5", alpha=0.15, zorder=5, label=f"all candidates ({len(rows)})")
    for decision in ["SKIP", "UNSURE", "ENTER"]:
        subset = rows[rows["ML_DECISION_V2"].astype(str) == decision]
        if subset.empty:
            continue
        style = styles[decision]
        yy = pd.to_numeric(subset.get("entry_price_5bps", subset.get("entry_open_price")), errors="coerce")
        kwargs = {
            "marker": style["marker"],
            "s": style["size"],
            "color": style["color"],
            "alpha": style["alpha"],
            "zorder": 8 if decision == "ENTER" else 7,
            "label": f"{style['label']} ({len(subset)})",
        }
        if decision != "SKIP":
            kwargs["edgecolors"] = "white"
            kwargs["linewidths"] = 0.65
        ax.scatter(subset["entry_ts"].dt.tz_convert(None), yy, **kwargs)
        if decision in {"ENTER", "UNSURE"}:
            for idx, row in subset.reset_index(drop=True).iterrows():
                entry_ts = pd.Timestamp(row["entry_ts"]).tz_convert("UTC").tz_convert(None)
                price = _safe_float(row.get("entry_price_5bps") or row.get("entry_open_price"))
                y_offset = 10 if idx % 2 == 0 else -16
                ax.annotate(
                    f"{row['candidate_id']} {float(row['ML_KEEP_SCORE_V2']):.2f}",
                    xy=(entry_ts, price),
                    xytext=(5, y_offset),
                    textcoords="offset points",
                    ha="left",
                    va="bottom" if y_offset > 0 else "top",
                    color=style["color"],
                    fontsize=7.5,
                    arrowprops={"arrowstyle": "->", "color": style["color"], "linewidth": 0.75, "alpha": 0.72},
                )


def _plot_ml_score_risk(ax: Any, rows: pd.DataFrame) -> None:
    _shade_sessions(ax, str(rows["day"].iloc[0]) if not rows.empty else "")
    if rows.empty:
        return
    x = pd.to_datetime(rows["entry_time_utc"], utc=True).dt.tz_convert(None)
    score_label = "V4_GROUP_RANK_SCORE" if "V4_GROUP_RANK_SCORE" in rows.columns else "ML_KEEP_SCORE_V2"
    ax.plot(x, rows["ML_KEEP_SCORE_V2"], color="#00e676", linewidth=1.25, marker="o", markersize=3.4, label=score_label)
    ax.plot(x, rows["stas5_v2_risk_knife_pre_entry"], color="#ff4d5e", linewidth=1.05, marker=".", label="knife_risk")
    ax.plot(x, rows["stas4_v2_combo_short_pressure_score"], color="#ff9f1a", linewidth=1.05, marker=".", label="short_pressure")
    ax.axhline(0.65, color="#00e676", linestyle="--", linewidth=0.8, alpha=0.75)
    ax.axhline(0.45, color="#ffd54f", linestyle="--", linewidth=0.8, alpha=0.75)
    ax.set_ylim(-0.05, 1.08)
    ax.set_ylabel("ML/Risk", color="#eceff1")
    ax.legend(loc="upper left", fontsize=8, facecolor="#101418", edgecolor="#455a64", labelcolor="#eceff1")


def _plot_block_scores(ax: Any, rows: pd.DataFrame) -> None:
    _shade_sessions(ax, str(rows["day"].iloc[0]) if not rows.empty else "")
    if rows.empty:
        return
    x = pd.to_datetime(rows["entry_time_utc"], utc=True).dt.tz_convert(None)
    columns = [
        ("stas4_v2_block_density_structure_net_score", "#00e676", "density+structure"),
        ("stas4_v2_block_pattern_structure_net_score", "#00e5ff", "pattern+structure"),
        ("stas4_v2_block_structure_volume_net_score", "#ffd54f", "structure+volume"),
        ("stas4_v2_block_structure_trend_net_score", "#ff4d5e", "structure+trend"),
    ]
    for column, color, label in columns:
        if column in rows:
            ax.plot(x, pd.to_numeric(rows[column], errors="coerce"), color=color, linewidth=1.05, marker=".", label=label)
    ax.axhline(0, color="#cfd8dc", linewidth=0.7, alpha=0.55)
    ax.set_ylabel("STAS4 blocks", color="#eceff1")
    ax.legend(loc="upper left", fontsize=8, facecolor="#101418", edgecolor="#455a64", labelcolor="#eceff1", ncol=2)


def _plot_volume(ax: Any, day_df: pd.DataFrame, day: str) -> None:
    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(day_df["open"], day_df["close"])]
    ax.bar(day_df["open_time_utc"].dt.tz_convert(None), day_df["volume"], width=_bar_width_days(TIMEFRAME), color=colors, alpha=0.70)
    _shade_sessions(ax, day)
    ax.set_ylabel("Volume", color="#eceff1")


def _risk_bucket(row: pd.Series) -> str:
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


def _prepare_render_rows(rows: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    if "entry_ts" not in out.columns and "entry_time_utc" in out.columns:
        out["entry_ts"] = pd.to_datetime(out["entry_time_utc"], utc=True)
    defaults = {
        "stas4_v2_structure_lower_range_flag": 0,
        "stas4_v2_structure_high_range_flag": 0,
        "stas4_v2_combo_long_recovery_score": 0.0,
        "stas4_v2_combo_rsi14": 50.0,
        "stas4_v2_combo_rsi_signal9": 50.0,
        "stas4_v2_combo_stoch_k14": 50.0,
        "stas4_v2_combo_macd_hist_norm": 0.0,
        "stas4_v2_div_bullish_recent": 0,
        "stas4_v2_div_hidden_bullish_recent": 0,
        "stas4_v2_div_bearish_recent": 0,
        "stas4_v2_div_hidden_bearish_recent": 0,
    }
    if "stas4_v2_combo_rsi_signal9" not in out.columns and "stas4_v2_combo_rsi_signal" in out.columns:
        out["stas4_v2_combo_rsi_signal9"] = out["stas4_v2_combo_rsi_signal"]
    for column, value in defaults.items():
        if column not in out.columns:
            out[column] = value
    if "risk_bucket" not in out.columns:
        out["risk_bucket"] = out.apply(_risk_bucket, axis=1)
    return out


def render_v2_forward_day(
    *,
    day_df: pd.DataFrame,
    rows: pd.DataFrame,
    hour_rows: list[dict[str, Any]],
    macro_wave_rows: list[dict[str, Any]],
    day: str,
    symbol: str,
    timeframe: str,
    out_path: Path,
) -> None:
    rows = _prepare_render_rows(rows)
    fig, axes = plt.subplots(
        10,
        1,
        figsize=(32, 27.5),
        sharex=True,
        gridspec_kw={"height_ratios": [7.0, 0.46, 0.46, 0.46, 0.46, 2.0, 2.0, 2.1, 2.35, 1.55], "hspace": 0.055},
    )
    (
        ax_price,
        ax_bg_phase,
        ax_long_wave,
        ax_short_wave,
        ax_macro_wave,
        ax_ml_risk,
        ax_blocks,
        ax_density_structure,
        ax_combo,
        ax_volume,
    ) = axes
    fig.patch.set_facecolor("#101418")
    for ax in axes:
        _style_axis(ax)

    _draw_candles(ax_price, day_df, timeframe, linewidth=0.30)
    _shade_sessions(ax_price, day, label_top=True)
    _plot_ml_price_markers(ax_price, rows)
    version_label = "STAS5 V2"
    if not rows.empty and "model_id" in rows.columns:
        model_ids = " ".join(rows["model_id"].astype(str).unique().tolist()).upper()
        if "STAS5_V4" in model_ids:
            version_label = "STAS5 V4"
        elif "STAS5_V3" in model_ids:
            version_label = "STAS5 V3"
    ax_price.set_ylabel("Price", color="#eceff1")
    ax_price.set_title(
        f"{version_label} ML forward entries | {symbol} {timeframe} {day} | ENTER/UNSURE/SKIP | blind forward | no TP/Stas3",
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
    _plot_ml_score_risk(ax_ml_risk, rows)
    _plot_block_scores(ax_blocks, rows)
    _plot_structure_density(ax_density_structure, rows)
    _plot_v2_combo_snapshot(ax_combo, rows)
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
            "Forward is blind review only. Postfact columns in CSV are audit-only and not model features. "
            f"Green={version_label} ENTER, yellow=UNSURE, gray=SKIP. No TP/Stas3/API/threshold tuning."
        ),
        color="#cfd8dc",
        fontsize=8,
        ha="left",
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=145, facecolor=fig.get_facecolor())
    plt.close(fig)


def run_v2_forward_review(
    *,
    start_day: str = FORWARD_START_DAY,
    end_day: str = FORWARD_END_DAY,
    symbol: str = SYMBOL,
    timeframe: str = TIMEFRAME,
    model_path: Path = DEFAULT_V2_MODEL_PATH,
    model_manifest_path: Path = DEFAULT_V2_MODEL_MANIFEST_PATH,
    train_snapshot_manifest_path: Path = DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH,
    v2_combo_path: Path = DEFAULT_FORWARD_V2_FEATURE_PATH,
    stas2_run_dir: Path | None = None,
    out_dir: Path = DEFAULT_V2_FORWARD_ROOT,
    update_latest_pointer: bool = True,
) -> dict[str, Any]:
    stas2_dir = _resolve_stas2_run_dir(stas2_run_dir)
    model_package = joblib.load(model_path)
    model_manifest = json.loads(model_manifest_path.read_text(encoding="utf-8"))
    snapshot, snapshot_manifest = build_v2_forward_snapshot(
        stas2_run_dir=stas2_dir,
        v2_combo_path=v2_combo_path,
        train_snapshot_manifest_path=train_snapshot_manifest_path,
    )
    if snapshot_manifest["status"] != "PASS":
        raise ValueError(f"V2 forward snapshot failed: {snapshot_manifest.get('checks')}")
    predictions = predict_v2_forward(snapshot=snapshot, model_package=model_package, model_manifest=model_manifest)

    out_dir.mkdir(parents=True, exist_ok=True)
    all_predictions_path = out_dir / f"STAS5_V2_FORWARD_ALL_PREDICTIONS_{compact_day(start_day)}_{compact_day(end_day)}.csv"
    predictions.to_csv(all_predictions_path, index=False, encoding="utf-8-sig")

    day_outputs: list[dict[str, Any]] = []
    for day in iter_days(start_day, end_day):
        day_rows = predictions[predictions["day"].astype(str) == day].copy()
        day_dir = out_dir / compact_day(day)
        source = _source_csv(PROJECT_ROOT, day, timeframe, symbol)
        if not source.exists():
            day_outputs.append({"day": day, "status": "MISSING_OHLCV", "rows": int(len(day_rows)), "source": rel(source)})
            continue
        day_df = _load_ohlcv(source)
        day_rows = _add_postfact_audit(day_df, day_rows)
        csv_path = day_dir / f"STAS5_V2_FORWARD_ENTRIES_{compact_day(day)}.csv"
        png_path = day_dir / f"STAS5_V2_FORWARD_ENTRY_REVIEW_{compact_day(day)}.png"
        day_dir.mkdir(parents=True, exist_ok=True)
        day_rows.to_csv(csv_path, index=False, encoding="utf-8-sig")
        hour_rows = _read_rows(stas2_dir / "STAS2_HOURLY_PHASES.csv", day)
        macro_wave_rows = _read_rows(stas2_dir / "STAS2_MACRO_WAVES.csv", day)
        render_v2_forward_day(
            day_df=day_df,
            rows=day_rows,
            hour_rows=hour_rows,
            macro_wave_rows=macro_wave_rows,
            day=day,
            symbol=symbol,
            timeframe=timeframe,
            out_path=png_path,
        )
        counts = Counter(day_rows["ML_DECISION_V2"].astype(str))
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
        "status": STATUS,
        "created_utc": utc_now(),
        "run_id": out_dir.name if out_dir.name else "",
        "run_dir": rel(out_dir),
        "date_range": {"start_day": start_day, "end_day": end_day},
        "symbol": symbol,
        "timeframe": timeframe,
        "model_path": rel(model_path),
        "model_manifest_path": rel(model_manifest_path),
        "model_id": model_package.get("model_id") or model_manifest.get("model_id"),
        "model_feature_set": model_package.get("model_feature_set") or model_manifest.get("model_feature_set"),
        "thresholds": model_package.get("thresholds") or model_manifest.get("thresholds"),
        "stas2_run_dir": rel(stas2_dir),
        "v2_combo_path": rel(v2_combo_path),
        "all_predictions_csv": rel(all_predictions_path),
        "snapshot_manifest": snapshot_manifest,
        "day_outputs": day_outputs,
        "decision_counts_total": dict(Counter(predictions["ML_DECISION_V2"].astype(str))),
        "guardrails": [
            "forward_days_not_used_for_training",
            "forward_days_not_used_for_threshold_tuning",
            "v2_forward_combo_features_joined_before_prediction",
            "png_has_no_tp_lines",
            "stas3_not_used",
            "api_not_used",
            "postfact_columns_are_audit_only",
        ],
    }
    manifest_path = out_dir / "STAS5_V2_FORWARD_ENTRY_REVIEW_MANIFEST.json"
    write_json(manifest_path, manifest)
    if update_latest_pointer:
        write_json(
            DEFAULT_V2_FORWARD_ROOT / "STAS5_V2_LATEST_FORWARD_RUN.json",
            {
                "status": "LATEST_FORWARD_RUN_POINTER",
                "created_utc": utc_now(),
                "run_id": manifest["run_id"],
                "run_dir": manifest["run_dir"],
                "manifest_path": rel(manifest_path),
            },
        )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Render STAS5 V2 blind forward ML entry review.")
    parser.add_argument("--start-day", default=FORWARD_START_DAY)
    parser.add_argument("--end-day", default=FORWARD_END_DAY)
    parser.add_argument("--symbol", default=SYMBOL)
    parser.add_argument("--timeframe", default=TIMEFRAME)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--run-root", default=str(DEFAULT_V2_FORWARD_RUNS_DIR))
    parser.add_argument("--model-path", default="")
    parser.add_argument("--model-manifest-path", default="")
    parser.add_argument("--train-snapshot-manifest-path", default=str(DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH))
    parser.add_argument("--v2-combo-path", default=str(DEFAULT_FORWARD_V2_FEATURE_PATH))
    parser.add_argument("--stas2-run-dir", default="")
    parser.add_argument("--out-dir", default="")
    args = parser.parse_args()
    model_manifest_path = Path(args.model_manifest_path) if args.model_manifest_path else _latest_model_manifest()
    model_path = Path(args.model_path) if args.model_path else _model_path_from_manifest(model_manifest_path)
    run_id = args.run_id or f"stas5_v2_forward_{run_stamp()}"
    out_dir = Path(args.out_dir) if args.out_dir else Path(args.run_root) / run_id
    manifest = run_v2_forward_review(
        start_day=args.start_day,
        end_day=args.end_day,
        symbol=args.symbol,
        timeframe=args.timeframe,
        model_path=model_path,
        model_manifest_path=model_manifest_path,
        train_snapshot_manifest_path=Path(args.train_snapshot_manifest_path),
        v2_combo_path=Path(args.v2_combo_path),
        stas2_run_dir=Path(args.stas2_run_dir) if args.stas2_run_dir else None,
        out_dir=out_dir,
    )
    print(
        {
            "status": manifest["status"],
            "run_id": manifest["run_id"],
            "run_dir": manifest["run_dir"],
            "decision_counts_total": manifest["decision_counts_total"],
            "day_outputs": manifest["day_outputs"],
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
