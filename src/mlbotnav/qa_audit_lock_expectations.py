from __future__ import annotations

import argparse
import json

_P26_REQUIRED_TABLE_FILES = [
    "reports/table_canon_current/data/candles_canonical.xlsx",
    "reports/table_canon_current/data/feature_frame.xlsx",
    "reports/table_canon_current/data/feature_frame_full.xlsx",
    "reports/table_canon_current/data/readable_tables_ru.xlsx",
    "reports/table_canon_current/data/feature_dictionary_ru.xlsx",
    "reports/table_canon_current/audit_chain_report.json",
]

_P26_LOCK_FILES = [
    "run_p23_operator_unified.ps1",
    "run_p24_latest_pass_report.ps1",
    "run_p22_table_chain_daily.ps1",
    "docs/P24_OPERATOR_CHECKLIST_2026-05-24_RU.md",
    "docs/P25_MASTER_RUNBOOK_2026-05-24_RU.md",
    "docs/P19_DAILY_STOP_GO_RUNBOOK_2026-05-24_RU.md",
    "docs/P20_RELEASE_PACKAGE_2026-05-24_RU.md",
]


def get_p26_required_table_files() -> list[str]:
    return list(_P26_REQUIRED_TABLE_FILES)


def get_p26_lock_files() -> list[str]:
    return list(_P26_LOCK_FILES)


def get_audit_lock_payload(*, role: str) -> dict:
    role_norm = str(role or "").strip().lower()
    if role_norm != "p26":
        raise ValueError(f"Unsupported role: {role}")
    return {
        "role": "p26",
        "required_table_files": get_p26_required_table_files(),
        "lock_files": get_p26_lock_files(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Shared table/lock-file expectations for audit lock flows.")
    parser.add_argument("--role", required=True, choices=["p26"])
    args = parser.parse_args()
    out = get_audit_lock_payload(role=str(args.role))
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
