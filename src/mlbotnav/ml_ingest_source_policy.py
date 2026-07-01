from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FORBIDDEN_DIRECT_REPORT_ROOTS = (
    Path("reports") / "optuna",
    Path("reports") / "pipeline",
    Path("reports") / "final_review",
)
APPROVED_PACKAGE_ROOT = Path("reports") / "ml_candidates"
APPROVAL_REGISTRY_PATH = Path("configs") / "ml_approved_calibration_packages.yaml"


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _resolve_project_path(project_root: Path, raw_path: object) -> Path:
    value = str(raw_path or "").strip()
    if not value:
        return (project_root / "__missing_path__").resolve()
    path = Path(value)
    if not path.is_absolute():
        path = project_root / path
    return path.resolve()


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def classify_ml_ingest_source_path(*, project_root: Path, source_path: object) -> dict[str, Any]:
    root = project_root.resolve()
    resolved = _resolve_project_path(root, source_path)
    registry_path = (root / APPROVAL_REGISTRY_PATH).resolve()
    package_root = (root / APPROVED_PACKAGE_ROOT).resolve()

    if resolved == registry_path:
        return {
            "status": "ALLOW",
            "source_path": str(source_path),
            "resolved_path": str(resolved),
            "source_class": "approval_registry",
            "reason": "approval_registry_allowed",
        }

    if _is_relative_to(resolved, package_root):
        return {
            "status": "ALLOW",
            "source_path": str(source_path),
            "resolved_path": str(resolved),
            "source_class": "approved_candidate_package",
            "reason": "ml_candidate_package_allowed",
        }

    for forbidden in FORBIDDEN_DIRECT_REPORT_ROOTS:
        forbidden_root = (root / forbidden).resolve()
        if _is_relative_to(resolved, forbidden_root):
            return {
                "status": "DENY",
                "source_path": str(source_path),
                "resolved_path": str(resolved),
                "source_class": "forbidden_direct_report",
                "reason": f"direct_report_source_forbidden:{forbidden.as_posix()}",
            }

    return {
        "status": "DENY",
        "source_path": str(source_path),
        "resolved_path": str(resolved),
        "source_class": "unknown",
        "reason": "not_approved_registry_or_package_source",
    }


def validate_ml_ingest_source_paths(*, project_root: Path, source_paths: list[object]) -> dict[str, Any]:
    checks = [
        classify_ml_ingest_source_path(project_root=project_root, source_path=source_path)
        for source_path in source_paths
    ]
    denials = [check for check in checks if check["status"] != "ALLOW"]
    return {
        "status": "PASS" if not denials else "FAIL",
        "allowed_count": len(checks) - len(denials),
        "denied_count": len(denials),
        "checks": checks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate ML ingest source paths.")
    parser.add_argument("--source-path", action="append", default=[], help="Source path to validate. Repeatable.")
    parser.add_argument("--out-dir", default="reports/qa_gate")
    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parents[2]
    result = validate_ml_ingest_source_paths(project_root=project_root, source_paths=list(args.source_path))

    out_dir = _resolve_project_path(project_root, args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"ml_ingest_source_policy_{_utc_tag()}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": result["status"],
                "report_path": str(out_path),
                "allowed_count": result["allowed_count"],
                "denied_count": result["denied_count"],
            },
            ensure_ascii=False,
        )
    )
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
