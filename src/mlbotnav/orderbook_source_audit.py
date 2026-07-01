from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from mlbotnav.external_sources import detect_external_sources
from mlbotnav.hypothesis_registry import load_backlog_registry


TARGET_HYPOTHESES = (
    "orderbook_imbalance_l1_l50",
    "spread_pressure_and_delta_absorption",
)


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _check(name: str, ok: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": details or {}}


def _get_backlog_status_map(cfg: dict[str, Any]) -> dict[str, str]:
    block = (cfg.get("extended_hypotheses_backlog") or {}).get("density_orderbook") or []
    out: dict[str, str] = {}
    if isinstance(block, list):
        for item in block:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).strip()
            status = str(item.get("status", "")).strip().lower()
            if name:
                out[name] = status
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit orderbook/microstructure source availability and planned statuses.")
    parser.add_argument("--config", default="configs/features_block.yaml")
    parser.add_argument("--out-dir", default="reports/qa_gate")
    parser.add_argument("--expect-status", choices=["planned", "active"], default="planned")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    cfg_path = (project_root / args.config).resolve() if not Path(args.config).is_absolute() else Path(args.config).resolve()
    out_dir = (project_root / args.out_dir).resolve() if not Path(args.out_dir).is_absolute() else Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []
    if not cfg_path.exists():
        payload = {
            "status": "FAIL",
            "generated_at_utc": _utc_now_iso(),
            "config_path": str(cfg_path),
            "error": "config_not_found",
            "checks": [],
        }
        out = out_dir / f"orderbook_source_audit_{_utc_tag()}.json"
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": payload["status"], "report_path": str(out), "failed": 1}, ensure_ascii=False))
        return 1

    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    status_map = _get_backlog_status_map(cfg)
    for name in TARGET_HYPOTHESES:
        checks.append(
            _check(
                f"config_status_{name}_{args.expect_status}",
                status_map.get(name, "") == args.expect_status,
                {"status": status_map.get(name), "expect_status": args.expect_status},
            )
        )

    probe = detect_external_sources(project_root)
    source_files = list(probe.get("source_files") or [])
    source_env = dict(probe.get("source_env") or {})
    source_detected = bool(probe.get("source_detected", False))
    source_ready = dict(probe.get("source_ready") or {})

    expect_planned = args.expect_status == "planned"
    checks.append(
        _check(
            "external_source_expectation",
            (not source_detected) if expect_planned else bool(source_detected),
            {"expect_status": args.expect_status, "source_detected": source_detected, "files_found_count": len(source_files), "env_flags": source_env},
        )
    )

    reg = load_backlog_registry(project_root=project_root, features_config=str(cfg_path), run_signal_mode="both")
    reg_items = {str(i.get("name")): i for i in (reg.get("items") or []) if isinstance(i, dict)}
    for name in TARGET_HYPOTHESES:
        item = reg_items.get(name, {})
        checks.append(_check(f"registry_has_{name}", bool(item), {"item": item}))
        should_be_enabled = args.expect_status == "active"
        checks.append(
            _check(
                f"registry_{name}_{'enabled' if should_be_enabled else 'disabled'}",
                bool(item.get("enabled_for_run", False)) if should_be_enabled else (not bool(item.get("enabled_for_run", False))),
                {"enabled_for_run": item.get("enabled_for_run"), "expect_status": args.expect_status},
            )
        )
        reasons = [str(x) for x in (item.get("disabled_reasons") or [])]
        if args.expect_status == "planned":
            checks.append(_check(f"registry_{name}_has_missing_external_source_reason", "missing_external_source" in reasons, {"disabled_reasons": reasons}))
        else:
            checks.append(_check(f"registry_{name}_no_missing_external_source_reason", "missing_external_source" not in reasons, {"disabled_reasons": reasons}))

    failed = int(sum(1 for c in checks if not c["ok"]))
    payload = {
        "status": "PASS" if failed == 0 else "FAIL",
        "generated_at_utc": _utc_now_iso(),
        "config_path": str(cfg_path),
        "targets": list(TARGET_HYPOTHESES),
        "source_detected": source_detected,
        "source_files": source_files[:50],
        "source_files_total": len(source_files),
        "source_env": source_env,
        "source_ready": source_ready,
        "registry_status": reg.get("status"),
        "checks": checks,
        "summary": {"total": len(checks), "failed": failed},
    }
    out = out_dir / f"orderbook_source_audit_{_utc_tag()}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "report_path": str(out), "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
