from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

from mlbotnav.audit import audit_event
from mlbotnav.release_gate import evaluate_deployment_gate
from mlbotnav.security import require_role, sign_file


def _registry_dir(project_root: Path) -> Path:
    d = project_root / "models" / "registry"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _champion_history_path(project_root: Path) -> Path:
    return _registry_dir(project_root) / "champion_history.jsonl"


def _active_model_path(project_root: Path) -> Path:
    return _registry_dir(project_root) / "active_model.json"


def load_active_model_snapshot(project_root: Path) -> dict | None:
    reg = _registry_dir(project_root)
    active = reg / "active_model.json"
    champion = reg / "champion.json"
    if active.exists():
        try:
            return json.loads(active.read_text(encoding="utf-8"))
        except Exception:
            pass
    if champion.exists():
        try:
            row = json.loads(champion.read_text(encoding="utf-8"))
            return {
                "updated_at_utc": datetime.now(timezone.utc).isoformat(),
                "symbol": row.get("symbol"),
                "timeframe": row.get("timeframe"),
                "run_utc": row.get("run_utc"),
                "model_path": row.get("model_path"),
                "champion_path": str(champion.resolve()),
            }
        except Exception:
            return None
    return None


def _append_champion_history(project_root: Path, row: dict) -> Path:
    p = _champion_history_path(project_root)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return p


def _set_active_model(project_root: Path, champion_row: dict) -> Path:
    p = _active_model_path(project_root)
    payload = {
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": champion_row.get("symbol"),
        "timeframe": champion_row.get("timeframe"),
        "run_utc": champion_row.get("run_utc"),
        "model_path": champion_row.get("model_path"),
        "champion_path": str((_registry_dir(project_root) / "champion.json").resolve()),
    }
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def _load_prod_policy(project_root: Path) -> dict:
    p = project_root / "configs" / "prod_policy.yaml"
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _promotion_guard(project_root: Path, *, report: dict, champion_path: Path) -> tuple[bool, str]:
    policy = ((_load_prod_policy(project_root).get("prod", {})).get("promotion", {}) or {})
    if not bool(policy.get("require_vs_champion", True)):
        return True, "promotion_guard_disabled"
    if not champion_path.exists():
        return True, "no_existing_champion"
    champion = json.loads(champion_path.read_text(encoding="utf-8"))
    if champion.get("symbol") != report.get("symbol") or champion.get("timeframe") != report.get("timeframe"):
        return True, "champion_scope_mismatch"

    cand_bt = report.get("backtest", {}) or {}
    champ_bt = ((champion.get("metrics") or {}).get("backtest", {}) or {})
    cand_net = float(cand_bt.get("net_return_pct", 0.0))
    champ_net = float(champ_bt.get("net_return_pct", 0.0))
    cand_mdd = abs(float(cand_bt.get("max_drawdown_pct", 0.0)))
    champ_mdd = abs(float(champ_bt.get("max_drawdown_pct", 0.0)))
    cand_sharpe = float(cand_bt.get("sharpe_like", 0.0))
    champ_sharpe = float(champ_bt.get("sharpe_like", 0.0))

    min_net_delta = float(policy.get("min_net_return_improvement_pct", 0.0))
    max_mdd_degradation = float(policy.get("max_mdd_degradation_pct", 2.0))
    min_sharpe_delta = float(policy.get("min_sharpe_improvement", -0.10))
    net_delta = cand_net - champ_net
    mdd_delta = cand_mdd - champ_mdd
    sharpe_delta = cand_sharpe - champ_sharpe
    if net_delta < min_net_delta:
        return False, f"net_return_delta_low:{net_delta:.3f}<{min_net_delta:.3f}"
    if mdd_delta > max_mdd_degradation:
        return False, f"drawdown_regression_high:{mdd_delta:.3f}>{max_mdd_degradation:.3f}"
    if sharpe_delta < min_sharpe_delta:
        return False, f"sharpe_delta_low:{sharpe_delta:.3f}<{min_sharpe_delta:.3f}"
    return True, "promotion_guard_pass"


def register_candidate(project_root: Path, *, report: dict) -> Path:
    reg_dir = _registry_dir(project_root)
    out = reg_dir / "candidates.jsonl"
    row = {
        "registered_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": report.get("symbol"),
        "timeframe": report.get("timeframe"),
        "run_utc": report.get("run_utc"),
        "gate_pass": (report.get("gate") or {}).get("pass", False),
        "gate_reasons": (report.get("gate") or {}).get("reasons", []),
        "walk_forward": report.get("walk_forward", {}),
        "backtest": report.get("backtest", {}),
        "artifacts": report.get("artifacts", {}),
        "report_path": report.get("_report_path"),
    }
    with out.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    audit_event(project_root, event="registry_candidate_registered", payload={"run_utc": row["run_utc"], "gate_pass": row["gate_pass"]})
    return out


def promote_if_pass(project_root: Path, *, report: dict) -> tuple[bool, Path, str]:
    reg_dir = _registry_dir(project_root)
    champion_path = reg_dir / "champion.json"
    role = require_role(project_root, action="registry_promote")
    if not role["allowed"]:
        reason = f"rbac_denied:{role['reason']}"
        audit_event(project_root, event="registry_promote_skipped", payload={"run_utc": report.get("run_utc"), "reason": reason, "rbac": role})
        return False, champion_path, reason
    deployment_gate = evaluate_deployment_gate(project_root, report=report, stage="promote")
    if not bool(deployment_gate.get("allowed", False)):
        reason = f"deployment_gate_fail:{';'.join(deployment_gate.get('reasons', []))}"
        audit_event(
            project_root,
            event="registry_promote_skipped",
            payload={
                "run_utc": report.get("run_utc"),
                "reason": reason,
                "deployment_gate_report": deployment_gate.get("report_path"),
                "deployment_gate_reasons": deployment_gate.get("reasons", []),
            },
        )
        return False, champion_path, reason
    pg_ok, pg_reason = _promotion_guard(project_root, report=report, champion_path=champion_path)
    if not pg_ok:
        audit_event(project_root, event="registry_promote_skipped", payload={"run_utc": report.get("run_utc"), "reason": pg_reason})
        return False, champion_path, pg_reason

    prev_champion = None
    if champion_path.exists():
        try:
            prev_champion = json.loads(champion_path.read_text(encoding="utf-8"))
        except Exception:
            prev_champion = None

    row = {
        "promoted_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": report.get("symbol"),
        "timeframe": report.get("timeframe"),
        "run_utc": report.get("run_utc"),
        "report_path": report.get("_report_path"),
        "model_path": (report.get("artifacts") or {}).get("model_path"),
        "metrics": {
            "walk_forward": report.get("walk_forward"),
            "backtest": report.get("backtest"),
        },
    }
    champion_path.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
    champion_sig = sign_file(project_root, path=champion_path, meta={"action": "registry_promote", "run_utc": report.get("run_utc")})
    _set_active_model(project_root, row)
    _append_champion_history(
        project_root,
        {
            "event_utc": datetime.now(timezone.utc).isoformat(),
            "event": "promote",
            "symbol": row.get("symbol"),
            "timeframe": row.get("timeframe"),
            "new_champion_run_utc": row.get("run_utc"),
            "previous_champion": prev_champion,
            "new_champion": row,
            "reason": "gate_pass_and_promotion_guard_pass",
        },
    )
    audit_event(
        project_root,
        event="registry_promoted_champion",
        payload={
            "run_utc": report.get("run_utc"),
            "model_path": row.get("model_path"),
            "promotion_guard_reason": pg_reason,
            "had_previous_champion": prev_champion is not None,
            "champion_sig": str(champion_sig),
            "rbac": role,
            "deployment_gate_report": deployment_gate.get("report_path"),
            "security_gate_report": deployment_gate.get("security_gate_report"),
        },
    )
    return True, champion_path, "promoted"
