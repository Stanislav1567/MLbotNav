from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from mlbotnav.audit import audit_event
from mlbotnav.dataset import FEATURE_COLUMNS, build_feature_frame, load_ohlcv_range


def _psi(ref: np.ndarray, cur: np.ndarray, bins: int = 10) -> float:
    ref = ref[np.isfinite(ref)]
    cur = cur[np.isfinite(cur)]
    if len(ref) < bins or len(cur) < bins:
        return 0.0
    qs = np.linspace(0, 1, bins + 1)
    edges = np.quantile(ref, qs)
    edges = np.unique(edges)
    if len(edges) < 3:
        return 0.0
    ref_hist, _ = np.histogram(ref, bins=edges)
    cur_hist, _ = np.histogram(cur, bins=edges)
    ref_pct = np.clip(ref_hist / max(ref_hist.sum(), 1), 1e-6, 1)
    cur_pct = np.clip(cur_hist / max(cur_hist.sum(), 1), 1e-6, 1)
    return float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))


def main() -> int:
    parser = argparse.ArgumentParser(description="Feature drift monitor (PSI).")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--reference-start", required=True)
    parser.add_argument("--reference-end", required=True)
    parser.add_argument("--current-start", required=True)
    parser.add_argument("--current-end", required=True)
    parser.add_argument("--psi-alert-threshold", type=float, default=0.2)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    ref_raw = load_ohlcv_range(
        project_root,
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=args.reference_start,
        end_date=args.reference_end,
    )
    cur_raw = load_ohlcv_range(
        project_root,
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=args.current_start,
        end_date=args.current_end,
    )
    ref = build_feature_frame(ref_raw)
    cur = build_feature_frame(cur_raw)

    per_feature = {}
    max_psi = 0.0
    for c in FEATURE_COLUMNS:
        v = _psi(ref[c].to_numpy(), cur[c].to_numpy())
        per_feature[c] = v
        max_psi = max(max_psi, v)

    drift_detected = max_psi >= args.psi_alert_threshold
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = project_root / "reports" / "monitoring"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"drift_report_{args.symbol}_{args.timeframe}_{ts}.json"

    report = {
        "run_utc": ts,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "reference_range": {"start": args.reference_start, "end": args.reference_end},
        "current_range": {"start": args.current_start, "end": args.current_end},
        "psi_alert_threshold": args.psi_alert_threshold,
        "max_psi": max_psi,
        "drift_detected": drift_detected,
        "per_feature_psi": per_feature,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    alert_path = None
    if drift_detected:
        alert_path = out_dir / f"drift_alert_{args.symbol}_{args.timeframe}_{ts}.json"
        report["alert_created_at_utc"] = datetime.now(timezone.utc).isoformat()
        alert_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    audit_event(
        project_root,
        event="monitor_drift_completed",
        payload={
            "symbol": args.symbol,
            "timeframe": args.timeframe,
            "report_path": str(report_path),
            "drift_detected": drift_detected,
            "max_psi": max_psi,
        },
    )
    print(json.dumps({"report_path": str(report_path), "drift_detected": drift_detected, "alert_path": str(alert_path) if alert_path else None}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
