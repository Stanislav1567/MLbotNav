from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import PROJECT_ROOT, STAS5_ARTIFACTS_DIR, compact_day, rel, run_stamp, utc_now, write_json
from mlbotnav.stas5_forward_entry_review import ensure_forward_stas2_run
from mlbotnav.stas5_v2_combo_feature_exporter import SYMBOL, TIMEFRAME, build_combo_features
from mlbotnav.stas5_v2_forward_entry_review import run_v2_forward_review
from mlbotnav.stas5_v3_entry_ranker_train import DEFAULT_V3_MODEL_DIR, DEFAULT_V3_MODEL_MANIFEST_PATH
from mlbotnav.stas5_v3_training_dataset_builder import DEFAULT_V3_TRAIN_DATASET_MANIFEST_PATH


STATUS = "STAS5_V3_FORWARD_ENTRY_REVIEW_READY_BLIND_21_25_NO_TP_NO_API_NO_STAS3"
DEFAULT_V3_FORWARD_ROOT = STAS5_ARTIFACTS_DIR / "v3" / "forward"
DEFAULT_V3_FORWARD_RUNS_DIR = DEFAULT_V3_FORWARD_ROOT / "runs"
DEFAULT_V3_FORWARD_SOURCE_DIR = STAS5_ARTIFACTS_DIR / "v3" / "forward_source"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_v3_model_manifest() -> Path:
    pointer = DEFAULT_V3_MODEL_DIR / "STAS5_V3_LATEST_MODEL_RUN.json"
    if pointer.exists():
        payload = _load_json(pointer)
        manifest_path = Path(payload.get("manifest_path", ""))
        if not manifest_path.is_absolute():
            manifest_path = PROJECT_ROOT / manifest_path
        if manifest_path.exists():
            return manifest_path
    manifests = sorted(
        DEFAULT_V3_MODEL_DIR.glob("runs/*/stas5_v3_entry_ranker_20260501_20260520_v0.manifest.json"),
        key=lambda item: item.stat().st_mtime,
    )
    if manifests:
        return manifests[-1]
    if DEFAULT_V3_MODEL_MANIFEST_PATH.exists():
        return DEFAULT_V3_MODEL_MANIFEST_PATH
    raise FileNotFoundError("no STAS5 V3 model manifest found")


def _model_path_from_manifest(manifest_path: Path) -> Path:
    payload = _load_json(manifest_path)
    model_path = Path(payload.get("model_path", ""))
    if not model_path.is_absolute():
        model_path = PROJECT_ROOT / model_path
    if not model_path.exists():
        raise FileNotFoundError(f"model file from manifest not found: {model_path}")
    return model_path


def _write_v3_prediction_csv(source_csv: Path, target_csv: Path) -> None:
    df = pd.read_csv(source_csv, encoding="utf-8-sig").copy()
    extra: dict[str, Any] = {"output_namespace": "STAS5_V3"}
    if "ML_KEEP_SCORE_V2" in df.columns:
        extra["ML_KEEP_SCORE_V3"] = df["ML_KEEP_SCORE_V2"].to_numpy()
        if "ML_KEEP_SCORE" in df.columns:
            df["ML_KEEP_SCORE"] = df["ML_KEEP_SCORE_V2"].to_numpy()
    if "ML_DECISION_V2" in df.columns:
        extra["ML_DECISION_V3"] = df["ML_DECISION_V2"].to_numpy()
        if "ML_DECISION" in df.columns:
            df["ML_DECISION"] = df["ML_DECISION_V2"].to_numpy()
    df = pd.concat([df, pd.DataFrame(extra, index=df.index)], axis=1)
    target_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(target_csv, index=False, encoding="utf-8-sig")


def run_v3_forward_review(
    *,
    start_day: str = "2026-05-21",
    end_day: str = "2026-05-25",
    symbol: str = SYMBOL,
    timeframe: str = TIMEFRAME,
    model_manifest_path: Path | None = None,
    model_path: Path | None = None,
    train_dataset_manifest_path: Path = DEFAULT_V3_TRAIN_DATASET_MANIFEST_PATH,
    stas2_run_dir: Path | None = None,
    out_dir: Path = DEFAULT_V3_FORWARD_ROOT,
    forward_source_dir: Path = DEFAULT_V3_FORWARD_SOURCE_DIR,
    stas2_render_limit: int = 1,
    strict: bool = True,
) -> dict[str, Any]:
    if model_manifest_path is None:
        model_manifest_path = _latest_v3_model_manifest()
    if model_path is None:
        model_path = _model_path_from_manifest(model_manifest_path)
    if not train_dataset_manifest_path.exists():
        raise FileNotFoundError(f"V3 train dataset manifest not found: {train_dataset_manifest_path}")

    stas2_dir = ensure_forward_stas2_run(
        start_day=start_day,
        end_day=end_day,
        symbol=symbol,
        timeframe=timeframe,
        stas2_run_dir=stas2_run_dir,
        forward_source_dir=forward_source_dir,
        stas2_render_limit=stas2_render_limit,
    )
    combo_csv = out_dir / f"STAS5_V3_COMBO_FEATURES_{compact_day(start_day)}_{compact_day(end_day)}.csv"
    combo_manifest = combo_csv.with_suffix(".manifest.json")
    _combo, combo_report = build_combo_features(
        stas2_run_dir=stas2_dir,
        start_day=start_day,
        end_day=end_day,
        output_csv=combo_csv,
        manifest_path=combo_manifest,
        strict=strict,
    )
    if strict and combo_report["status"] != "PASS":
        raise ValueError(f"V3 forward combo export failed: {combo_report.get('checks')}")

    v2_render_manifest = run_v2_forward_review(
        start_day=start_day,
        end_day=end_day,
        symbol=symbol,
        timeframe=timeframe,
        model_path=model_path,
        model_manifest_path=model_manifest_path,
        train_snapshot_manifest_path=train_dataset_manifest_path,
        v2_combo_path=combo_csv,
        stas2_run_dir=stas2_dir,
        out_dir=out_dir,
        update_latest_pointer=False,
    )
    v3_day_outputs: list[dict[str, Any]] = []
    for item in v2_render_manifest.get("day_outputs", []):
        updated = dict(item)
        if item.get("status") == "READY":
            day_compact = compact_day(str(item["day"]))
            day_dir = out_dir / day_compact
            source_csv = PROJECT_ROOT / str(item["csv"])
            source_png = PROJECT_ROOT / str(item["png"])
            v3_csv = day_dir / f"STAS5_V3_FORWARD_ENTRIES_{day_compact}.csv"
            v3_png = day_dir / f"STAS5_V3_FORWARD_ENTRY_REVIEW_{day_compact}.png"
            if source_csv.exists():
                _write_v3_prediction_csv(source_csv, v3_csv)
                updated["csv"] = rel(v3_csv)
            if source_png.exists():
                shutil.copy2(source_png, v3_png)
                updated["png"] = rel(v3_png)
        v3_day_outputs.append(updated)

    v3_all_predictions = out_dir / f"STAS5_V3_FORWARD_ALL_PREDICTIONS_{compact_day(start_day)}_{compact_day(end_day)}.csv"
    v2_all_predictions_rel = str(v2_render_manifest.get("all_predictions_csv") or "")
    if v2_all_predictions_rel:
        v2_all_predictions = PROJECT_ROOT / v2_all_predictions_rel
        if v2_all_predictions.exists():
            _write_v3_prediction_csv(v2_all_predictions, v3_all_predictions)

    ready_days = [item for item in v3_day_outputs if item.get("status") == "READY"]
    expected_days = len(v3_day_outputs)
    status_pass = combo_report["status"] == "PASS" and expected_days == len(ready_days) and expected_days > 0
    manifest_path = out_dir / "STAS5_V3_FORWARD_ENTRY_REVIEW_MANIFEST.json"
    manifest = {
        "status": STATUS if status_pass else "FAIL",
        "created_utc": utc_now(),
        "run_id": out_dir.name,
        "run_dir": rel(out_dir),
        "date_range": {"start_day": start_day, "end_day": end_day},
        "symbol": symbol,
        "timeframe": timeframe,
        "model_path": rel(model_path),
        "model_manifest_path": rel(model_manifest_path),
        "train_dataset_manifest_path": rel(train_dataset_manifest_path),
        "stas2_run_dir": rel(stas2_dir),
        "combo_csv": rel(combo_csv),
        "combo_manifest": rel(combo_manifest),
        "all_predictions_csv": rel(v3_all_predictions) if v3_all_predictions.exists() else "",
        "v2_renderer_manifest_path": rel(out_dir / "STAS5_V2_FORWARD_ENTRY_REVIEW_MANIFEST.json"),
        "day_outputs": v3_day_outputs,
        "decision_counts_total": v2_render_manifest.get("decision_counts_total", {}),
        "checks": {
            "combo_status": combo_report.get("status"),
            "expected_days": expected_days,
            "ready_days": len(ready_days),
            "missing_or_failed_days": [item for item in v2_render_manifest.get("day_outputs", []) if item.get("status") != "READY"],
        },
        "guardrails": [
            "blind_forward_20260521_20260525_only",
            "no_forward_threshold_tuning",
            "no_tp_stas3_exit_api",
            "combo_features_recomputed_before_prediction",
            "v2_renderer_used_only_for_png_layout",
        ],
    }
    write_json(manifest_path, manifest)
    write_json(
        DEFAULT_V3_FORWARD_ROOT / "STAS5_V3_LATEST_FORWARD_RUN.json",
        {
            "status": "LATEST_FORWARD_RUN_POINTER",
            "created_utc": utc_now(),
            "run_id": out_dir.name,
            "run_dir": rel(out_dir),
            "manifest_path": rel(manifest_path),
        },
    )
    if strict and manifest["status"] == "FAIL":
        raise ValueError(f"STAS5 V3 forward review failed checks: {manifest['checks']}")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Run STAS5 V3 blind forward review for 2026-05-21..2026-05-25.")
    parser.add_argument("--start-day", default="2026-05-21")
    parser.add_argument("--end-day", default="2026-05-25")
    parser.add_argument("--symbol", default=SYMBOL)
    parser.add_argument("--timeframe", default=TIMEFRAME)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--run-root", default=str(DEFAULT_V3_FORWARD_RUNS_DIR))
    parser.add_argument("--model-path", default="")
    parser.add_argument("--model-manifest-path", default="")
    parser.add_argument("--train-dataset-manifest-path", default=str(DEFAULT_V3_TRAIN_DATASET_MANIFEST_PATH))
    parser.add_argument("--stas2-run-dir", default="")
    parser.add_argument("--out-dir", default="")
    parser.add_argument("--forward-source-dir", default=str(DEFAULT_V3_FORWARD_SOURCE_DIR))
    parser.add_argument("--stas2-render-limit", type=int, default=1)
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()
    run_id = args.run_id or f"stas5_v3_forward_{run_stamp()}"
    out_dir = Path(args.out_dir) if args.out_dir else Path(args.run_root) / run_id
    manifest = run_v3_forward_review(
        start_day=args.start_day,
        end_day=args.end_day,
        symbol=args.symbol,
        timeframe=args.timeframe,
        model_path=Path(args.model_path) if args.model_path else None,
        model_manifest_path=Path(args.model_manifest_path) if args.model_manifest_path else None,
        train_dataset_manifest_path=Path(args.train_dataset_manifest_path),
        stas2_run_dir=Path(args.stas2_run_dir) if args.stas2_run_dir else None,
        out_dir=out_dir,
        forward_source_dir=Path(args.forward_source_dir),
        stas2_render_limit=args.stas2_render_limit,
        strict=not args.no_strict,
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
    return 0 if manifest["status"] != "FAIL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
