from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.qa_audit_lock_expectations import get_p26_lock_files, get_p26_required_table_files
from mlbotnav.qa_required_patterns import (
    STRESS_PATTERN,
    get_p24_epoch_lock_baseline_allowed_patterns,
    get_p24_required_patterns,
    get_p26_required_patterns,
)

MANIFEST_SCHEMA = "ml_runtime_io_manifest.v1"
MANIFEST_SCOPE = "ml_runtime_noncalibration"
P23_REPORT_PATTERN = "reports/qa_gate/p23_operator_unified_*.json"
P24_REPORT_PATTERN = "reports/qa_gate/p24_latest_pass_*.json"
P26_REPORT_PATTERN = "reports/qa_gate/p26_audit_lock_*.json"


def build_runtime_io_manifest(*, require_stress: bool = True) -> dict[str, Any]:
    p24_required = get_p24_required_patterns(require_stress=require_stress)
    p26_required = get_p26_required_patterns(require_stress=require_stress)

    return {
        "schema": MANIFEST_SCHEMA,
        "scope": MANIFEST_SCOPE,
        "require_stress": bool(require_stress),
        "identity_rule": {
            "external_runtime_fork_allowed": False,
            "must_match_canonical_parameters": True,
            "must_match_canonical_features": True,
            "must_match_canonical_hypotheses": True,
            "must_match_canonical_io_and_tables": True,
        },
        "inputs": {
            "p23_report_pattern": P23_REPORT_PATTERN,
            "required_reports": {
                "p24": p24_required,
                "p26": p26_required,
            },
            "p24_epoch_lock_baseline_allowed_patterns": get_p24_epoch_lock_baseline_allowed_patterns(
                require_stress=require_stress
            ),
            "resolution_rules": {
                "table_chain_not_required_pattern": "reports/qa_gate/daily_long_short_cycle_*.json",
                "p24_epoch_lock_bypass_patterns": get_p24_epoch_lock_baseline_allowed_patterns(
                    require_stress=require_stress
                ),
            },
        },
        "outputs": {
            "p24_report_pattern": P24_REPORT_PATTERN,
            "p26_report_pattern": P26_REPORT_PATTERN,
            "required_table_files": get_p26_required_table_files(),
            "lock_files": get_p26_lock_files(),
            "stress_pattern": STRESS_PATTERN if require_stress else None,
        },
    }


def _parse_bool(text: str | bool | None) -> bool:
    if isinstance(text, bool):
        return text
    t = str(text or "").strip().lower()
    return t in {"1", "true", "yes", "y", "on"}


def emit_manifest_payload(*, require_stress: bool = True) -> dict[str, Any]:
    payload = build_runtime_io_manifest(require_stress=require_stress)
    payload["status"] = "PASS"
    payload["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="ML runtime non-calibration inputs/outputs manifest.")
    parser.add_argument("--require-stress", default="true")
    parser.add_argument("--write-json", default="")
    args = parser.parse_args()

    require_stress = _parse_bool(args.require_stress)
    out = emit_manifest_payload(require_stress=require_stress)
    text = json.dumps(out, ensure_ascii=False)
    write_json = str(args.write_json or "").strip()
    if write_json:
        path = Path(write_json).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
