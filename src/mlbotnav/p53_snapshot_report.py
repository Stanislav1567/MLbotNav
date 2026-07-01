from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest(pattern: str, root: Path) -> Path | None:
    files = sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def _check(name: str, ok: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": details or {}}


def main() -> int:
    parser = argparse.ArgumentParser(description="P5.3 snapshot report for latest long/short cycles and table convergence.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    qa = root / "reports" / "qa_gate"
    data = root / "reports" / "table_canon_current"
    qa.mkdir(parents=True, exist_ok=True)

    out = qa / f"p53_snapshot_{_utc_tag()}.json"

    long_cycle = _latest("contour_cycle_long_only_*.json", qa)
    short_cycle = _latest("contour_cycle_short_only_*.json", qa)
    dual = _latest("p53_dual_acceptance_*.json", qa)
    gate = _latest("tz_gate_*.json", qa)
    chain = data / "audit_chain_report.json"

    checks: list[dict[str, Any]] = []
    checks.append(_check("long_cycle_exists", long_cycle is not None and long_cycle.exists(), {"path": str(long_cycle) if long_cycle else None}))
    checks.append(_check("short_cycle_exists", short_cycle is not None and short_cycle.exists(), {"path": str(short_cycle) if short_cycle else None}))
    checks.append(_check("dual_acceptance_exists", dual is not None and dual.exists(), {"path": str(dual) if dual else None}))
    checks.append(_check("gate_exists", gate is not None and gate.exists(), {"path": str(gate) if gate else None}))
    checks.append(_check("chain_report_exists", chain.exists(), {"path": str(chain)}))

    if not all(c["ok"] for c in checks):
        payload = {
            "status": "FAIL",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "checks": checks,
            "summary": {"total": len(checks), "failed": int(sum(1 for c in checks if not c["ok"]))},
        }
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": "FAIL", "report_path": str(out)}, ensure_ascii=False))
        return 1

    long_obj = _load_json(long_cycle)  # type: ignore[arg-type]
    short_obj = _load_json(short_cycle)  # type: ignore[arg-type]
    dual_obj = _load_json(dual)  # type: ignore[arg-type]
    gate_obj = _load_json(gate)  # type: ignore[arg-type]
    chain_obj = _load_json(chain)

    checks.append(_check("long_cycle_pass", str(long_obj.get("status", "")).upper() == "PASS"))
    checks.append(_check("short_cycle_pass", str(short_obj.get("status", "")).upper() == "PASS"))
    checks.append(_check("dual_acceptance_pass", str(dual_obj.get("status", "")).upper() == "PASS"))
    checks.append(_check("gate_pass", str(gate_obj.get("status", "")).upper() == "PASS"))
    checks.append(_check("table_chain_pass", str(chain_obj.get("status", "")).upper() == "PASS"))

    # Extract key convergence metrics for quick human review.
    metrics: dict[str, Any] = {}
    for item in chain_obj.get("checks", []):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", ""))
        details = item.get("details", {})
        if name in {
            "candles_rows_positive",
            "feature_full_rows_eq_candles",
            "feature_train_rows_positive",
            "execution_trace_rows_non_negative",
            "execution_trace_rows_match_summary",
            "signal_frame_rows_positive",
            "parity_days_failed_zero",
        }:
            metrics[name] = details

    failed = int(sum(1 for c in checks if not c["ok"]))
    payload = {
        "status": "PASS" if failed == 0 else "FAIL",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "artifacts": {
            "long_cycle": str(long_cycle),
            "short_cycle": str(short_cycle),
            "dual_acceptance": str(dual),
            "latest_gate": str(gate),
            "table_chain_report": str(chain),
        },
        "checks": checks,
        "metrics": metrics,
        "summary": {"total": len(checks), "failed": failed},
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "report_path": str(out), "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
