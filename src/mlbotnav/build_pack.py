from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from mlbotnav.audit import audit_event
from mlbotnav.security import require_role, sign_file


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _latest_file(path_glob: str, root: Path) -> Path | None:
    files = sorted(root.glob(path_glob), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def _add_if_exists(copy_map: list[tuple[str, Path]], dst_name: str, src: Path | None) -> None:
    if src is not None and src.exists():
        copy_map.append((dst_name, src))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build daily artifact pack with checksums.")
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    role = require_role(project_root, action="pack")
    if not role["allowed"]:
        raise PermissionError(f"RBAC denied for action=pack: {role['reason']}")
    session_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    pack_dir = project_root / "packs" / args.date / session_id
    pack_dir.mkdir(parents=True, exist_ok=True)

    copy_map: list[tuple[str, Path]] = []
    raw = project_root / "data" / "raw" / "bybit_ohlcv" / f"dt={args.date}" / f"tf={args.timeframe}" / f"symbol={args.symbol}" / "part-final.csv"
    _add_if_exists(copy_map, "raw_ohlcv.csv", raw)

    dq = project_root / "data" / "dq" / "ohlcv_quality_report.csv"
    _add_if_exists(copy_map, "dq_report.csv", dq)

    model = _latest_file(f"models/pipeline/champion_candidate_*_{args.symbol}_{args.timeframe}_*.joblib", project_root)
    _add_if_exists(copy_map, model.name if model else "model.joblib", model)

    pipe_report = _latest_file(f"reports/pipeline/pipeline_report_{args.symbol}_{args.timeframe}_*.json", project_root)
    _add_if_exists(copy_map, pipe_report.name if pipe_report else "pipeline_report.json", pipe_report)

    chart = _latest_file(f"reports/screenshots/candles_clean_v2_{args.symbol}_{args.timeframe}_{args.date}_*.png", project_root)
    _add_if_exists(copy_map, chart.name if chart else "candles.png", chart)

    drift_report = _latest_file(f"reports/monitoring/drift_report_{args.symbol}_{args.timeframe}_*.json", project_root)
    _add_if_exists(copy_map, drift_report.name if drift_report else "drift_report.json", drift_report)

    drift_alert = _latest_file(f"reports/monitoring/drift_alert_{args.symbol}_{args.timeframe}_*.json", project_root)
    _add_if_exists(copy_map, drift_alert.name if drift_alert else "drift_alert.json", drift_alert)

    rollback_report = _latest_file("reports/registry/rollback_guard_*.json", project_root)
    _add_if_exists(copy_map, rollback_report.name if rollback_report else "rollback_guard.json", rollback_report)

    prod_cycle_report = _latest_file(f"reports/prod_cycle/prod_cycle_{args.symbol}_{args.timeframe}_*.json", project_root)
    _add_if_exists(copy_map, prod_cycle_report.name if prod_cycle_report else "prod_cycle.json", prod_cycle_report)

    cv_root = project_root / "data" / "cv" / "artifacts"
    cv_overlay = _latest_file(f"source_id=*/dt={args.date}/tf={args.timeframe}/symbol={args.symbol}/*_overlay.png", cv_root)
    _add_if_exists(copy_map, cv_overlay.name if cv_overlay else "cv_overlay.png", cv_overlay)
    cv_original = _latest_file(f"source_id=*/dt={args.date}/tf={args.timeframe}/symbol={args.symbol}/*_original.png", cv_root)
    _add_if_exists(copy_map, cv_original.name if cv_original else "cv_original.png", cv_original)
    cv_metadata = _latest_file(f"source_id=*/dt={args.date}/tf={args.timeframe}/symbol={args.symbol}/*_metadata.json", cv_root)
    _add_if_exists(copy_map, cv_metadata.name if cv_metadata else "cv_metadata.json", cv_metadata)
    cv_decision = _latest_file(f"source_id=*/dt={args.date}/tf={args.timeframe}/symbol={args.symbol}/*_decision.json", cv_root)
    _add_if_exists(copy_map, cv_decision.name if cv_decision else "cv_decision.json", cv_decision)

    final_visual = _latest_file(f"reports/final_review/minute_final_entry_{args.symbol}_{args.timeframe}_*.png", project_root)
    _add_if_exists(copy_map, final_visual.name if final_visual else "minute_final_entry.png", final_visual)
    final_md = _latest_file(f"reports/final_review/minute_final_summary_{args.symbol}_{args.timeframe}_*.md", project_root)
    _add_if_exists(copy_map, final_md.name if final_md else "minute_final_summary.md", final_md)
    final_json = _latest_file(f"reports/final_review/minute_final_summary_{args.symbol}_{args.timeframe}_*.json", project_root)
    _add_if_exists(copy_map, final_json.name if final_json else "minute_final_summary.json", final_json)

    ta_report = _latest_file(f"reports/technical_analysis/ta_report_{args.symbol}_{args.timeframe}_*.json", project_root)
    _add_if_exists(copy_map, ta_report.name if ta_report else "ta_report.json", ta_report)
    levels_csv = project_root / "data" / "analytics" / "levels.csv"
    _add_if_exists(copy_map, "levels.csv", levels_csv)
    pattern_csv = project_root / "data" / "analytics" / "pattern_events.csv"
    _add_if_exists(copy_map, "pattern_events.csv", pattern_csv)
    signals_csv = project_root / "data" / "analytics" / "signal_events.csv"
    _add_if_exists(copy_map, "signal_events.csv", signals_csv)
    fallback_csv = project_root / "data" / "analytics" / "signal_fallback_events.csv"
    _add_if_exists(copy_map, "signal_fallback_events.csv", fallback_csv)
    levels_pq = project_root / "data" / "analytics" / "levels.parquet"
    _add_if_exists(copy_map, "levels.parquet", levels_pq)
    patterns_pq = project_root / "data" / "analytics" / "pattern_events.parquet"
    _add_if_exists(copy_map, "pattern_events.parquet", patterns_pq)
    signals_pq = project_root / "data" / "analytics" / "signal_events.parquet"
    _add_if_exists(copy_map, "signal_events.parquet", signals_pq)
    fallback_pq = project_root / "data" / "analytics" / "signal_fallback_events.parquet"
    _add_if_exists(copy_map, "signal_fallback_events.parquet", fallback_pq)
    ta_xlsx = _latest_file(f"data/analytics/technical_analysis_{args.symbol}_{args.timeframe}_*.xlsx", project_root)
    _add_if_exists(copy_map, ta_xlsx.name if ta_xlsx else "technical_analysis.xlsx", ta_xlsx)

    copied: list[Path] = []
    for dst_name, src in copy_map:
        dst = pack_dir / dst_name
        shutil.copy2(src, dst)
        copied.append(dst)

    checksums_path = pack_dir / "checksums.csv"
    with checksums_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file_name", "sha256"])
        for p in copied:
            w.writerow([p.name, _sha256(p)])

    manifest = {
        "date": args.date,
        "session_id": session_id,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": [p.name for p in copied],
        "checksums_file": checksums_path.name,
    }
    manifest_path = pack_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest_sig = sign_file(project_root, path=manifest_path, meta={"action": "pack", "session_id": session_id})

    index_path = project_root / "packs" / "index.csv"
    index_parquet_path = project_root / "packs" / "index.parquet"
    new_row = [args.date, session_id, args.symbol, args.timeframe, str(pack_dir), datetime.now(timezone.utc).isoformat()]
    if not index_path.exists():
        with index_path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "session_id", "symbol", "timeframe", "pack_dir", "created_at_utc"])
            w.writerow(new_row)
    else:
        with index_path.open("a", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(new_row)
    try:
        pd.read_csv(index_path).to_parquet(index_parquet_path, index=False)
    except Exception:
        pass
    checksums_sig = sign_file(project_root, path=checksums_path, meta={"action": "pack", "session_id": session_id})

    audit_event(
        project_root,
        event="build_pack_completed",
        payload={
            "date": args.date,
            "symbol": args.symbol,
            "timeframe": args.timeframe,
            "pack_dir": str(pack_dir),
            "files_count": len(copied),
            "index_csv": str(index_path),
            "index_parquet": str(index_parquet_path),
            "manifest_sig": str(manifest_sig),
            "checksums_sig": str(checksums_sig),
            "rbac": role,
        },
    )
    print(json.dumps({"pack_dir": str(pack_dir), "manifest_path": str(manifest_path), "files_count": len(copied)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
