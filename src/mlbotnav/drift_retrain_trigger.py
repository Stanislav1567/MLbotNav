from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from mlbotnav.audit import audit_event


def _latest_alert(project_root: Path, *, symbol: str, timeframe: str) -> Path | None:
    root = project_root / "reports" / "monitoring"
    files = sorted(root.glob(f"drift_alert_{symbol}_{timeframe}_*.json"), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _parse_iso(text: str) -> datetime | None:
    try:
        return datetime.fromisoformat(text)
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Create retrain trigger from latest drift alert and validate SLA.")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--max-alert-age-sec", type=int, default=120)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    now = datetime.now(timezone.utc)
    alert_path = _latest_alert(project_root, symbol=args.symbol, timeframe=args.timeframe)
    if alert_path is None:
        out = {
            "run_utc": now.strftime("%Y%m%dT%H%M%SZ"),
            "symbol": args.symbol,
            "timeframe": args.timeframe,
            "triggered": False,
            "reason": "no_drift_alert_found",
            "alert_to_trigger_sec": None,
            "sla_breach": False,
        }
        print(json.dumps(out, ensure_ascii=False))
        return 0

    alert = _read_json(alert_path)
    if not bool(alert.get("drift_detected", False)):
        out = {
            "run_utc": now.strftime("%Y%m%dT%H%M%SZ"),
            "symbol": args.symbol,
            "timeframe": args.timeframe,
            "triggered": False,
            "reason": "alert_without_drift_detected",
            "alert_path": str(alert_path),
            "alert_to_trigger_sec": None,
            "sla_breach": False,
        }
        print(json.dumps(out, ensure_ascii=False))
        return 0

    created_at = _parse_iso(str(alert.get("alert_created_at_utc", ""))) or datetime.fromtimestamp(alert_path.stat().st_mtime, tz=timezone.utc)
    delta_sec = max(0.0, (now - created_at).total_seconds())
    stale = delta_sec > float(args.max_alert_age_sec)
    sla_breach = delta_sec > 120.0

    report = {
        "run_utc": now.strftime("%Y%m%dT%H%M%SZ"),
        "created_at_utc": now.isoformat(),
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "triggered": not stale,
        "reason": "drift_retrain_triggered" if not stale else "stale_alert",
        "alert_path": str(alert_path),
        "alert_created_at_utc": created_at.isoformat(),
        "alert_to_trigger_sec": round(delta_sec, 3),
        "sla_breach": bool(sla_breach),
        "trigger_type": "event_retrain_request",
    }
    out_dir = project_root / "reports" / "monitoring"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"retrain_trigger_{args.symbol}_{args.timeframe}_{report['run_utc']}.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    audit_event(
        project_root,
        event="drift_retrain_trigger_evaluated",
        payload={
            "symbol": args.symbol,
            "timeframe": args.timeframe,
            "triggered": report["triggered"],
            "reason": report["reason"],
            "alert_to_trigger_sec": report["alert_to_trigger_sec"],
            "sla_breach": report["sla_breach"],
            "report_path": str(out_path),
        },
    )
    print(json.dumps({"report_path": str(out_path), "triggered": report["triggered"], "sla_breach": report["sla_breach"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
