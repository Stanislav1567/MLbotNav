from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from mlbotnav.stas5_common import (
    STAS5_ARTIFACTS_DIR,
    TRAIN_END_DAY,
    TRAIN_START_DAY,
    iter_days,
    rel,
    run_stamp,
    utc_now,
    write_json,
)
from mlbotnav.stas5_v2_feature_snapshot_builder import DEFAULT_V2_FEATURE_SNAPSHOT_PATH
from mlbotnav.stas5_v2_feature_visual_approval import DEFAULT_STAS2_TRAIN_RUN_DIR, run as render_train_day


STATUS = "STAS5_V2_TRAIN_VISUAL_BATCH_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3"
DEFAULT_TRAIN_VISUAL_RUNS_ROOT = STAS5_ARTIFACTS_DIR / "v2" / "visual_approval" / "runs"
DEFAULT_TRAIN_VISUAL_LATEST_POINTER = STAS5_ARTIFACTS_DIR / "v2" / "visual_approval" / "STAS5_V2_LATEST_TRAIN_VISUAL_RUN.json"


def run_train_visual_batch(
    *,
    start_day: str = TRAIN_START_DAY,
    end_day: str = TRAIN_END_DAY,
    run_id: str | None = None,
    out_root: Path = DEFAULT_TRAIN_VISUAL_RUNS_ROOT,
    snapshot_path: Path = DEFAULT_V2_FEATURE_SNAPSHOT_PATH,
    stas2_run_dir: Path = DEFAULT_STAS2_TRAIN_RUN_DIR,
) -> dict[str, Any]:
    run_id = run_id or f"stas5_v2_train_visual_{run_stamp()}"
    run_root = out_root / run_id
    day_outputs: list[dict[str, Any]] = []
    total_rows = 0
    total_keep = 0
    total_cut = 0
    total_yellow = 0
    total_conflict = 0

    for day in iter_days(start_day, end_day):
        payload = render_train_day(day=day, snapshot_path=snapshot_path, stas2_run_dir=stas2_run_dir, out_root=run_root)
        labels = payload.get("label_counts", {})
        total_rows += int(payload.get("rows", 0))
        total_keep += int(labels.get("KEEP_DRAFT", 0)) + int(labels.get("KEEP_APPROVED", 0))
        total_cut += int(labels.get("CUT_DRAFT", 0)) + int(labels.get("CUT_APPROVED", 0))
        total_yellow += int(payload.get("yellow_x_count", 0))
        total_conflict += int(payload.get("yellow_x_conflict_count", 0))
        day_outputs.append(
            {
                "day": day,
                "status": payload["status"],
                "rows": int(payload["rows"]),
                "label_counts": labels,
                "png": payload["artifacts"]["png"],
                "manifest": payload["artifacts"]["manifest"],
            }
        )

    manifest_path = run_root / "STAS5_V2_TRAIN_VISUAL_BATCH_MANIFEST.json"
    manifest = {
        "status": STATUS,
        "created_utc": utc_now(),
        "run_id": run_id,
        "run_dir": rel(run_root),
        "date_range": {"start_day": start_day, "end_day": end_day},
        "snapshot_path": rel(snapshot_path),
        "stas2_run_dir": rel(stas2_run_dir),
        "days": len(day_outputs),
        "rows": total_rows,
        "keep_rows": total_keep,
        "cut_rows": total_cut,
        "yellow_x_rows": total_yellow,
        "yellow_x_conflict_rows": total_conflict,
        "day_outputs": day_outputs,
        "guardrails": [
            "train_visual_batch_only",
            "uses_same_v2_feature_snapshot_as_ml_training",
            "no_model_training",
            "no_threshold_tuning",
            "no_tp_stas3_exit",
            "yellow_x_strategy_layers_are_audit_only",
        ],
    }
    write_json(manifest_path, manifest)
    write_json(
        DEFAULT_TRAIN_VISUAL_LATEST_POINTER,
        {
            "status": "LATEST_TRAIN_VISUAL_RUN_POINTER",
            "created_utc": utc_now(),
            "run_id": run_id,
            "run_dir": rel(run_root),
            "manifest_path": rel(manifest_path),
        },
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Render STAS5 V2 train visual approval PNGs for all train days.")
    parser.add_argument("--start-day", default=TRAIN_START_DAY)
    parser.add_argument("--end-day", default=TRAIN_END_DAY)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--out-root", type=Path, default=DEFAULT_TRAIN_VISUAL_RUNS_ROOT)
    parser.add_argument("--snapshot-path", type=Path, default=DEFAULT_V2_FEATURE_SNAPSHOT_PATH)
    parser.add_argument("--stas2-run-dir", type=Path, default=DEFAULT_STAS2_TRAIN_RUN_DIR)
    args = parser.parse_args()
    manifest = run_train_visual_batch(
        start_day=args.start_day,
        end_day=args.end_day,
        run_id=args.run_id or None,
        out_root=args.out_root,
        snapshot_path=args.snapshot_path,
        stas2_run_dir=args.stas2_run_dir,
    )
    print(
        {
            "status": manifest["status"],
            "run_id": manifest["run_id"],
            "run_dir": manifest["run_dir"],
            "days": manifest["days"],
            "rows": manifest["rows"],
            "keep_rows": manifest["keep_rows"],
            "cut_rows": manifest["cut_rows"],
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
