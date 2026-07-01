from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

from mlbotnav.security import run_security_gate
from mlbotnav.stage_state import load_stage_state


def _load_prod_policy(project_root: Path) -> dict:
    p = project_root / "configs" / "prod_policy.yaml"
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_stage_plan(project_root: Path) -> list[str]:
    p = project_root / "configs" / "stage_plan.yaml"
    if not p.exists():
        return ["D1", "D2", "D3", "D5", "D30", "D60", "D90", "READY"]
    with p.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    sp = cfg.get("stage_plan", {}) if isinstance(cfg, dict) else {}
    stages = sp.get("stages", []) if isinstance(sp, dict) else []
    if isinstance(stages, list) and stages:
        return [str(x) for x in stages]
    return ["D1", "D2", "D3", "D5", "D30", "D60", "D90", "READY"]


def _latest_file(root: Path, pattern: str) -> Path | None:
    files = sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_deployment_gate(project_root: Path, *, report: dict, stage: str = "promote") -> dict:
    policy = ((_load_prod_policy(project_root).get("prod", {}) or {}).get("promotion", {}) or {})
    gate_cfg = policy.get("deployment_gate", {}) if isinstance(policy, dict) else {}
    if not isinstance(gate_cfg, dict):
        gate_cfg = {}

    require_gate_pass = bool(gate_cfg.get("require_pipeline_gate_pass", True))
    require_stage_ready = bool(gate_cfg.get("require_stage_ready", False))
    require_security_gate = bool(gate_cfg.get("require_security_gate", True))
    require_model_artifact_exists = bool(gate_cfg.get("require_model_artifact_exists", False))
    require_inference_sla_gate = bool(gate_cfg.get("require_inference_sla_gate", True))
    require_inference_metrics = bool(gate_cfg.get("require_inference_metrics", True))
    max_sla_report_age_minutes = int(gate_cfg.get("max_sla_report_age_minutes", 180))
    required_terminal = str(gate_cfg.get("required_stage_terminal", "READY"))
    required_last_completed = str(gate_cfg.get("required_last_completed_stage", "D90"))

    reasons: list[str] = []
    checks: dict[str, object] = {}

    if require_gate_pass:
        gp = bool((report.get("gate") or {}).get("pass", False))
        checks["pipeline_gate_pass"] = gp
        if not gp:
            reasons.append("pipeline_gate_not_passed")

    if require_model_artifact_exists:
        model_path = str((report.get("artifacts") or {}).get("model_path", "")).strip()
        model_ok = bool(model_path) and Path(model_path).exists()
        checks["model_artifact_exists"] = model_ok
        if not model_ok:
            reasons.append("model_artifact_missing")

    if require_inference_sla_gate:
        sla_path = _latest_file(project_root, "reports/monitoring/sla_report_*.json")
        checks["inference_sla_report_path"] = str(sla_path) if sla_path else None
        if sla_path is None:
            reasons.append("inference_sla_report_missing")
        else:
            try:
                sla = _read_json(sla_path)
                now = datetime.now(timezone.utc)
                age_min = max(0.0, (now - datetime.fromtimestamp(sla_path.stat().st_mtime, tz=timezone.utc)).total_seconds() / 60.0)
                checks["inference_sla_report_age_minutes"] = round(age_min, 3)
                checks["inference_sla_report_max_age_minutes"] = int(max_sla_report_age_minutes)
                if age_min > float(max_sla_report_age_minutes):
                    reasons.append(f"inference_sla_report_stale:{age_min:.1f}m>{max_sla_report_age_minutes}m")
                inf = ((sla.get("metrics") or {}).get("inference_service") or {})
                has_inf = isinstance(inf, dict) and len(inf) > 0
                checks["inference_metrics_present"] = bool(has_inf)
                if require_inference_metrics and not has_inf:
                    reasons.append("inference_sla_metrics_missing")
                if has_inf:
                    av = float(inf.get("availability_pct", 0.0))
                    p95 = float(inf.get("latency_ms_p95", 0.0))
                    kpi = ((_load_prod_policy(project_root).get("prod", {}) or {}).get("kpi", {}) or {})
                    min_av = float(kpi.get("min_inference_availability_pct", 99.5))
                    max_p95 = float(kpi.get("max_inference_p95_latency_ms", 300.0))
                    checks["inference_availability_pct"] = av
                    checks["inference_latency_ms_p95"] = p95
                    checks["inference_min_availability_pct"] = min_av
                    checks["inference_max_latency_ms_p95"] = max_p95
                    if av < min_av:
                        reasons.append(f"inference_availability_low:{av:.3f}<{min_av:.3f}")
                    if p95 > max_p95:
                        reasons.append(f"inference_p95_latency_high:{p95:.3f}>{max_p95:.3f}")
                if bool(sla.get("alert_required", False)):
                    checks["inference_sla_alert_required"] = True
                    if has_inf:
                        # keep strictness on inference-metric violations while ignoring non-inference perf breaches
                        av = float(inf.get("availability_pct", 0.0))
                        p95 = float(inf.get("latency_ms_p95", 0.0))
                        kpi = ((_load_prod_policy(project_root).get("prod", {}) or {}).get("kpi", {}) or {})
                        min_av = float(kpi.get("min_inference_availability_pct", 99.5))
                        max_p95 = float(kpi.get("max_inference_p95_latency_ms", 300.0))
                        if av < min_av or p95 > max_p95:
                            reasons.append("inference_sla_alert")
                else:
                    checks["inference_sla_alert_required"] = False
            except Exception as exc:  # noqa: BLE001
                reasons.append(f"inference_sla_report_parse_error:{exc}")

    stage_state_report = None
    if require_stage_ready:
        stages = _load_stage_plan(project_root)
        st = load_stage_state(project_root, stages=stages)
        cur = str(st.get("current_stage", ""))
        last_completed = str(st.get("last_completed_stage", ""))
        stage_ok = (cur == required_terminal) or (last_completed == required_last_completed)
        checks["stage_current"] = cur
        checks["stage_last_completed"] = last_completed
        checks["stage_required_terminal"] = required_terminal
        checks["stage_required_last_completed"] = required_last_completed
        checks["stage_ready"] = stage_ok
        stage_state_report = st
        if not stage_ok:
            reasons.append(
                f"stage_not_ready:current={cur};last_completed={last_completed};"
                f"require_current={required_terminal}|last_completed={required_last_completed}"
            )

    sg = None
    if require_security_gate:
        sg = run_security_gate(project_root, stage=stage)
        checks["security_gate_allowed"] = bool(sg.get("allowed", False))
        if not bool(sg.get("allowed", False)):
            reasons.append(f"security_gate_fail:{';'.join(sg.get('reasons', []))}")

    allowed = len(reasons) == 0
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload = {
        "run_utc": ts,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "allowed": allowed,
        "reasons": reasons if reasons else ["ok"],
        "checks": checks,
        "security_gate_report": (sg or {}).get("report_path") if sg else None,
        "stage_state_snapshot": stage_state_report,
        "policy": {
            "require_pipeline_gate_pass": require_gate_pass,
            "require_stage_ready": require_stage_ready,
            "require_security_gate": require_security_gate,
            "require_model_artifact_exists": require_model_artifact_exists,
            "require_inference_sla_gate": require_inference_sla_gate,
            "require_inference_metrics": require_inference_metrics,
            "max_sla_report_age_minutes": max_sla_report_age_minutes,
            "required_stage_terminal": required_terminal,
            "required_last_completed_stage": required_last_completed,
        },
    }
    out_dir = project_root / "reports" / "release_gate"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"deployment_gate_{stage}_{ts}.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    payload["report_path"] = str(out_path)
    return payload
