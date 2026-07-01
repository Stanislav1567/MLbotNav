from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml
from mlbotnav.data_window_readiness import evaluate_data_window_readiness, write_data_window_readiness_report


DEFAULT_GATE = {
    "locked_timeframe": "1m",
    "require_user_confirmation_for_30d": True,
    "allow_30d_window": False,
    "minute_study_completed": False,
    "confirmation_note": "",
    "confirmed_at_utc": None,
    "require_data_window_readiness": True,
    "data_window_readiness_min_days": 30,
    "data_window_readiness_layer": "raw",
    "data_window_readiness_require_full_coverage": True,
}


def _gate_path(project_root: Path) -> Path:
    return project_root / "configs" / "workflow_gate.yaml"


def load_workflow_gate(project_root: Path) -> dict:
    p = _gate_path(project_root)
    if not p.exists():
        return dict(DEFAULT_GATE)
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    merged = dict(DEFAULT_GATE)
    merged.update(data if isinstance(data, dict) else {})
    return merged


def save_workflow_gate(project_root: Path, gate: dict) -> Path:
    p = _gate_path(project_root)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        yaml.safe_dump(gate, f, allow_unicode=True, sort_keys=False)
    return p


def _inclusive_days(start_date: str | None, end_date: str | None) -> int | None:
    if not start_date or not end_date:
        return None
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    return (end - start).days + 1


def enforce_training_scope(
    *,
    project_root: Path,
    symbol: str | None = None,
    timeframe: str,
    start_date: str | None,
    end_date: str | None,
    action_name: str,
) -> None:
    gate = load_workflow_gate(project_root)
    locked_tf = str(gate.get("locked_timeframe", "1m"))
    if locked_tf and timeframe != locked_tf:
        raise RuntimeError(
            f"Workflow gate blocked for {action_name}: timeframe='{timeframe}' is not allowed, use '{locked_tf}'."
        )

    days = _inclusive_days(start_date, end_date)
    require_confirm = bool(gate.get("require_user_confirmation_for_30d", True))
    allow_30d = bool(gate.get("allow_30d_window", False))
    if require_confirm and (not allow_30d) and days is not None and days >= 30:
        raise RuntimeError(
            "Workflow gate blocked: 30-day minute runs are disabled until user confirmation. "
            "After explicit approval run: "
            "python -m mlbotnav.workflow_gate --allow-30d true --mark-minute-study-complete true "
            "--confirmation-note \"user confirmed minute result\""
        )

    require_data_window_readiness = bool(gate.get("require_data_window_readiness", True))
    data_window_min_days = int(gate.get("data_window_readiness_min_days", 30))
    if (
        require_data_window_readiness
        and symbol
        and start_date
        and end_date
        and days is not None
        and days >= data_window_min_days
    ):
        payload = evaluate_data_window_readiness(
            project_root,
            symbol=str(symbol),
            timeframe=str(timeframe),
            start_date=str(start_date),
            end_date=str(end_date),
            layer=str(gate.get("data_window_readiness_layer", "raw")),
            require_full_coverage=bool(gate.get("data_window_readiness_require_full_coverage", True)),
        )
        report_path = write_data_window_readiness_report(
            project_root,
            payload=payload,
            action_name=str(action_name),
        )
        if str(payload.get("status")) != "PASS":
            missing_days = payload.get("missing_days", [])
            sample = ", ".join([str(x) for x in missing_days[:5]])
            raise RuntimeError(
                "Workflow gate blocked: data_window_readiness_failed "
                f"(missing_days={len(missing_days)}, sample=[{sample}], report={report_path})"
            )


def _parse_bool(text: str) -> bool:
    t = (text or "").strip().lower()
    if t in {"1", "true", "yes", "y", "on"}:
        return True
    if t in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"Unsupported bool value: {text}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage workflow gate for minute-first process.")
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--allow-30d", default=None, help="true/false")
    parser.add_argument("--mark-minute-study-complete", default=None, help="true/false")
    parser.add_argument("--confirmation-note", default=None)
    parser.add_argument("--locked-timeframe", default=None)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    gate = load_workflow_gate(project_root)

    changed = False
    if args.allow_30d is not None:
        gate["allow_30d_window"] = _parse_bool(args.allow_30d)
        changed = True
    if args.mark_minute_study_complete is not None:
        gate["minute_study_completed"] = _parse_bool(args.mark_minute_study_complete)
        changed = True
    if args.confirmation_note is not None:
        gate["confirmation_note"] = args.confirmation_note
        changed = True
    if args.locked_timeframe is not None:
        gate["locked_timeframe"] = args.locked_timeframe
        changed = True

    if changed:
        if bool(gate.get("allow_30d_window", False)):
            gate["confirmed_at_utc"] = datetime.now(timezone.utc).isoformat()
        save_workflow_gate(project_root, gate)

    if args.show or True:
        print(json.dumps(gate, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
