from __future__ import annotations

import argparse
import json

STRESS_PATTERN = "reports/final_review/stress_backtest_contour_*.json"

_CORE_PATTERNS = [
    "reports/qa_gate/p23_operator_unified_*.json",
    "reports/qa_gate/daily_long_short_cycle_*.json",
    "reports/qa_gate/table_convergence_5plus_*.json",
    "reports/qa_gate/features_block_audit_*.json",
    "reports/qa_gate/orderbook_source_audit_*.json",
    "reports/qa_gate/tz_gate_*.json",
    "reports/qa_gate/p72_freeze_ready_*.json",
]


def _with_optional_stress(*, require_stress: bool) -> list[str]:
    out = list(_CORE_PATTERNS)
    if require_stress:
        out.append(STRESS_PATTERN)
    return out


def get_p24_required_patterns(*, require_stress: bool = True) -> list[str]:
    return _with_optional_stress(require_stress=require_stress)


def get_p26_required_patterns(*, require_stress: bool = True) -> list[str]:
    return _with_optional_stress(require_stress=require_stress)


def get_p24_epoch_lock_baseline_allowed_patterns(*, require_stress: bool = True) -> list[str]:
    if not require_stress:
        return []
    return [STRESS_PATTERN]


def get_patterns_payload(*, role: str, require_stress: bool) -> dict:
    role_norm = str(role or "").strip().lower()
    if role_norm == "p24":
        patterns = get_p24_required_patterns(require_stress=require_stress)
        payload = {
            "role": "p24",
            "require_stress": bool(require_stress),
            "required_patterns": patterns,
            "epoch_lock_baseline_allowed_patterns": get_p24_epoch_lock_baseline_allowed_patterns(
                require_stress=require_stress
            ),
        }
        return payload
    if role_norm == "p26":
        patterns = get_p26_required_patterns(require_stress=require_stress)
        payload = {
            "role": "p26",
            "require_stress": bool(require_stress),
            "required_patterns": patterns,
        }
        return payload
    raise ValueError(f"Unsupported role: {role}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Shared required-patterns provider for P24/P26.")
    parser.add_argument("--role", required=True, choices=["p24", "p26"])
    parser.add_argument("--require-stress", default="true")
    args = parser.parse_args()
    require_stress = str(args.require_stress).strip().lower() in {"1", "true", "yes", "y", "on"}
    out = get_patterns_payload(role=str(args.role), require_stress=require_stress)
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
