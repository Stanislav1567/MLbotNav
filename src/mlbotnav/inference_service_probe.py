from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import joblib
import numpy as np

from mlbotnav.dataset import build_feature_frame, load_ohlcv_range
from mlbotnav.model_registry import load_active_model_snapshot
from mlbotnav.security import require_role
from mlbotnav.workflow_gate import enforce_training_scope


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _resolve_horizon(project_root: Path) -> int:
    champion_path = project_root / "models" / "registry" / "champion.json"
    if not champion_path.exists():
        return 1
    row = _load_json(champion_path)
    rep_path = row.get("report_path")
    if rep_path and Path(rep_path).exists():
        rep = _load_json(Path(rep_path))
        strategy = rep.get("strategy", {}) if isinstance(rep, dict) else {}
        return int(strategy.get("horizon_bars", 1))
    return 1


def _pct(vals: list[float], q: float) -> float:
    if not vals:
        return 0.0
    return float(np.percentile(np.array(vals, dtype=float), q))


def main() -> int:
    parser = argparse.ArgumentParser(description="Inference service SLA probe (availability + p95 latency).")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--start-date", default=None, help="YYYY-MM-DD")
    parser.add_argument("--end-date", default=None, help="YYYY-MM-DD")
    parser.add_argument("--attempts", type=int, default=20)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    role = require_role(project_root, action="inference")
    if not role["allowed"]:
        raise PermissionError(f"RBAC denied for action=inference_service_probe: {role['reason']}")

    active = load_active_model_snapshot(project_root)
    if not active:
        raise RuntimeError("No active model/champion found in registry.")
    model_path = Path(active["model_path"])
    if not model_path.exists():
        raise FileNotFoundError(f"Active model not found: {model_path}")

    if args.end_date is None:
        args.end_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    if args.start_date is None:
        args.start_date = (datetime.strptime(args.end_date, "%Y-%m-%d").date() - timedelta(days=2)).strftime("%Y-%m-%d")
    enforce_training_scope(
        project_root=project_root,
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=args.start_date,
        end_date=args.end_date,
        action_name="inference_service_probe",
    )

    horizon_bars = _resolve_horizon(project_root)
    raw = load_ohlcv_range(
        project_root,
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=args.start_date,
        end_date=args.end_date,
    )
    feat = build_feature_frame(raw, horizon_bars=horizon_bars, include_targets=False)
    if feat.empty:
        raise RuntimeError("No feature rows for inference probe.")

    payload = joblib.load(model_path)
    model = payload["model"]
    features = payload["features"]
    x_last = feat[features].tail(1)

    latencies_ms: list[float] = []
    failures: list[str] = []
    attempts = max(1, int(args.attempts))
    for i in range(attempts):
        t0 = time.perf_counter()
        try:
            _ = model.predict_proba(x_last)[:, 1]
            latencies_ms.append((time.perf_counter() - t0) * 1000.0)
        except Exception as e:  # noqa: BLE001
            failures.append(f"attempt_{i + 1}:{e}")

    success_count = len(latencies_ms)
    failed_count = len(failures)
    availability_pct = (float(success_count) / float(attempts)) * 100.0
    p95_ms = _pct(latencies_ms, 95.0)
    p50_ms = _pct(latencies_ms, 50.0)
    max_ms = max(latencies_ms) if latencies_ms else 0.0

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = project_root / "reports" / "inference_service"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"inference_service_probe_{args.symbol}_{args.timeframe}_{ts}.json"
    report = {
        "run_utc": ts,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "date_range": {"start": args.start_date, "end": args.end_date},
        "attempts": attempts,
        "success_count": success_count,
        "failed_count": failed_count,
        "availability_pct": round(availability_pct, 4),
        "latency_ms_p50": round(float(p50_ms), 4),
        "latency_ms_p95": round(float(p95_ms), 4),
        "latency_ms_max": round(float(max_ms), 4),
        "failure_samples": failures[:5],
        "model_path": str(model_path),
    }
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report_path": str(out_path), "availability_pct": report["availability_pct"], "latency_ms_p95": report["latency_ms_p95"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
