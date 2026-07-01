from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

from mlbotnav.audit import audit_event


def _load_policy(project_root: Path) -> dict:
    p = project_root / "configs" / "prod_policy.yaml"
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _registry_dir(project_root: Path) -> Path:
    d = project_root / "models" / "registry"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _load_history_rows(project_root: Path) -> list[dict]:
    p = _registry_dir(project_root) / "champion_history.jsonl"
    if not p.exists():
        return []
    rows: list[dict] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def _rollback_to_previous_champion(project_root: Path) -> tuple[bool, str, dict | None]:
    reg = _registry_dir(project_root)
    champion_path = reg / "champion.json"
    active_path = reg / "active_model.json"
    rows = _load_history_rows(project_root)
    if not rows:
        return False, "no_champion_history", None
    for row in reversed(rows):
        if row.get("event") != "promote":
            continue
        prev = row.get("previous_champion")
        if not isinstance(prev, dict) or not prev:
            continue
        champion_path.write_text(json.dumps(prev, ensure_ascii=False, indent=2), encoding="utf-8")
        active_payload = {
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            "symbol": prev.get("symbol"),
            "timeframe": prev.get("timeframe"),
            "run_utc": prev.get("run_utc"),
            "model_path": prev.get("model_path"),
            "champion_path": str(champion_path.resolve()),
            "rollback_source_run_utc": row.get("new_champion_run_utc"),
        }
        active_path.write_text(json.dumps(active_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return True, "rollback_applied", prev
    return False, "no_previous_champion_snapshot", None


def main() -> int:
    parser = argparse.ArgumentParser(description="Rollback guard based on latest pipeline report and prod policy.")
    parser.add_argument("--pipeline-report", required=True, help="Path to pipeline_report_*.json")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    policy = _load_policy(project_root).get("prod", {})
    rollback = policy.get("rollback", {})

    with Path(args.pipeline_report).open("r", encoding="utf-8") as f:
        rep = json.load(f)

    backtest = rep.get("backtest") or {}
    drawdown = abs(float(backtest.get("max_drawdown_pct", 0.0)))
    no_trade = float(backtest.get("no_trade_ratio", 1.0))
    no_trade_days = float(backtest.get("no_trade_ratio_days", no_trade))
    gate_pass = bool((rep.get("gate") or {}).get("pass", False))

    breaches = []
    if drawdown > float(rollback.get("max_allowed_drawdown_breach_pct", 25.0)):
        breaches.append(f"drawdown_breach:{drawdown:.3f}")
    max_no_trade_days = float(policy.get("kpi", {}).get("max_no_trade_ratio_days", policy.get("kpi", {}).get("max_no_trade_ratio", 0.80)))
    if no_trade_days > max_no_trade_days:
        breaches.append(f"no_trade_days_breach:{no_trade_days:.3f}")
    if not gate_pass:
        breaches.append("gate_not_pass")

    action = {
        "run_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "pipeline_report": str(Path(args.pipeline_report).resolve()),
        "rollback_required": len(breaches) > 0,
        "breaches": breaches,
        "rollback_sla_minutes": rollback.get("expected_rollback_sla_minutes", 5),
        "recommended_action": "keep_champion_and_block_promote" if breaches else "continue",
    }

    rollback_exec = {
        "enabled": bool(rollback.get("enabled", True)),
        "executed": False,
        "status": "not_required",
        "reason": None,
        "restored_champion_run_utc": None,
    }
    if action["rollback_required"] and rollback_exec["enabled"]:
        ok, status, restored = _rollback_to_previous_champion(project_root)
        rollback_exec["executed"] = ok
        rollback_exec["status"] = status
        rollback_exec["reason"] = "policy_breach"
        rollback_exec["restored_champion_run_utc"] = (restored or {}).get("run_utc")
    action["rollback_execution"] = rollback_exec

    out_dir = project_root / "reports" / "registry"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"rollback_guard_{action['run_utc']}.json"
    out_path.write_text(json.dumps(action, ensure_ascii=False, indent=2), encoding="utf-8")

    audit_event(
        project_root,
        event="rollback_guard_evaluated",
        payload={
            "report": str(out_path),
            "rollback_required": action["rollback_required"],
            "breaches": breaches,
            "rollback_execution": rollback_exec,
        },
    )
    print(
        json.dumps(
            {
                "rollback_required": action["rollback_required"],
                "report_path": str(out_path),
                "breaches": breaches,
                "rollback_execution": rollback_exec,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
