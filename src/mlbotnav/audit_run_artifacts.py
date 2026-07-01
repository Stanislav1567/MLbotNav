from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _check(name: str, ok: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": details or {}}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="P4 audit: verify per-run artifact structure")
    parser.add_argument("--run-dir", required=True, help="Path to reports/runs/<run_id>")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    run_dir = Path(args.run_dir)
    if not run_dir.is_absolute():
        run_dir = (project_root / run_dir).resolve()
    if not run_dir.exists():
        raise FileNotFoundError(f"run-dir not found: {run_dir}")

    checks: list[dict[str, Any]] = []
    required_dirs = ["state", "data", "pipeline", "oos", "trade_simulation", "top_strategy"]
    for d in required_dirs:
        p = run_dir / d
        checks.append(_check(f"dir_{d}_exists", p.exists() and p.is_dir(), {"path": str(p)}))

    required_files = [
        run_dir / "state" / "run_manifest.json",
        run_dir / "state" / "status.json",
        run_dir / "state" / "p4_pack_manifest.json",
        run_dir / "index.json",
        run_dir / "data" / "candles_canonical.csv",
        run_dir / "data" / "feature_frame.csv",
        run_dir / "data" / "feature_frame_full.csv",
        run_dir / "oos" / "oos_report.json",
        run_dir / "oos" / "oos_backtest_trades.csv",
        run_dir / "pipeline" / "train_pipeline_report.json",
        run_dir / "trade_simulation" / "trade_simulation_summary.json",
        run_dir / "trade_simulation" / "trade_simulation.png",
        run_dir / "top_strategy" / "top_strategy_card.json",
    ]
    missing = [str(p) for p in required_files if not p.exists()]
    checks.append(_check("required_files_exist", len(missing) == 0, {"missing": missing}))

    index_path = run_dir / "index.json"
    if index_path.exists():
        try:
            idx = _load_json(index_path)
            count = int((idx.get("files_count") or 0))
            checks.append(_check("index_has_files", count > 0, {"files_count": count}))
        except Exception as exc:
            checks.append(_check("index_parseable", False, {"error": str(exc)}))

    status_path = run_dir / "state" / "status.json"
    if status_path.exists():
        try:
            st = _load_json(status_path)
            checks.append(_check("status_p4_ready", bool(st.get("p4_pack_ready", False)), {"active_step": st.get("active_step")}))
        except Exception as exc:
            checks.append(_check("status_parseable", False, {"error": str(exc)}))

    failed = int(sum(1 for c in checks if not c["ok"]))
    payload = {
        "status": "PASS" if failed == 0 else "FAIL",
        "generated_at_utc": _utc_now_iso(),
        "run_dir": str(run_dir),
        "checks": checks,
        "summary": {"total": len(checks), "failed": failed},
    }
    out_path = run_dir / "state" / "p4_audit_report.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "report_path": str(out_path), "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
