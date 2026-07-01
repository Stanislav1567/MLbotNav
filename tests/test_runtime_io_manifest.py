from __future__ import annotations

from mlbotnav.qa_audit_lock_expectations import get_p26_lock_files, get_p26_required_table_files
from mlbotnav.qa_required_patterns import (
    STRESS_PATTERN,
    get_p24_epoch_lock_baseline_allowed_patterns,
    get_p24_required_patterns,
    get_p26_required_patterns,
)
from mlbotnav.runtime_io_manifest import (
    MANIFEST_SCHEMA,
    MANIFEST_SCOPE,
    build_runtime_io_manifest,
    emit_manifest_payload,
)


def test_manifest_core_metadata() -> None:
    manifest = build_runtime_io_manifest(require_stress=True)
    assert manifest["schema"] == MANIFEST_SCHEMA
    assert manifest["scope"] == MANIFEST_SCOPE
    assert manifest["require_stress"] is True
    identity = manifest["identity_rule"]
    assert identity["external_runtime_fork_allowed"] is False
    assert identity["must_match_canonical_io_and_tables"] is True


def test_manifest_patterns_and_expectations_consistency() -> None:
    manifest = build_runtime_io_manifest(require_stress=True)
    required = manifest["inputs"]["required_reports"]
    assert required["p24"] == get_p24_required_patterns(require_stress=True)
    assert required["p26"] == get_p26_required_patterns(require_stress=True)
    assert manifest["inputs"]["p24_epoch_lock_baseline_allowed_patterns"] == (
        get_p24_epoch_lock_baseline_allowed_patterns(require_stress=True)
    )
    assert manifest["outputs"]["required_table_files"] == get_p26_required_table_files()
    assert manifest["outputs"]["lock_files"] == get_p26_lock_files()
    assert manifest["outputs"]["stress_pattern"] == STRESS_PATTERN


def test_manifest_without_stress() -> None:
    manifest = build_runtime_io_manifest(require_stress=False)
    required = manifest["inputs"]["required_reports"]
    assert STRESS_PATTERN not in required["p24"]
    assert STRESS_PATTERN not in required["p26"]
    assert manifest["inputs"]["p24_epoch_lock_baseline_allowed_patterns"] == []
    assert manifest["outputs"]["stress_pattern"] is None


def test_emit_payload_has_pass_status() -> None:
    payload = emit_manifest_payload(require_stress=True)
    assert payload["status"] == "PASS"
    assert "generated_at_utc" in payload
