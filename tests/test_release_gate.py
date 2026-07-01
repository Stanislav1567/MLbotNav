from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mlbotnav.release_gate import evaluate_deployment_gate


def _mk_report(root: Path, *, gate_pass: bool = True) -> dict:
    model_dir = root / "models" / "pipeline"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "m.joblib"
    model_path.write_bytes(b"ok")
    return {
        "symbol": "SOLUSDT",
        "timeframe": "1m",
        "run_utc": "20260521T100000Z",
        "gate": {"pass": gate_pass, "reasons": [] if gate_pass else ["x"]},
        "artifacts": {"model_path": str(model_path)},
    }


class ReleaseGateTests(unittest.TestCase):
    def test_stage_gate_blocks_if_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "configs").mkdir(parents=True, exist_ok=True)
            (root / "data" / "meta").mkdir(parents=True, exist_ok=True)
            (root / "configs" / "prod_policy.yaml").write_text(
                (
                    "prod:\n"
                    "  promotion:\n"
                    "    deployment_gate:\n"
                    "      require_pipeline_gate_pass: true\n"
                    "      require_stage_ready: true\n"
                    "      required_stage_terminal: READY\n"
                    "      required_last_completed_stage: D90\n"
                    "      require_security_gate: false\n"
                    "      require_model_artifact_exists: true\n"
                    "      require_inference_sla_gate: false\n"
                ),
                encoding="utf-8",
            )
            st = {
                "current_stage": "D2",
                "last_completed_stage": "D1",
                "history": [],
            }
            (root / "data" / "meta" / "stage_runtime_state.json").write_text(json.dumps(st), encoding="utf-8")
            out = evaluate_deployment_gate(root, report=_mk_report(root), stage="promote")
            self.assertFalse(out["allowed"])
            self.assertTrue(any("stage_not_ready" in r for r in out["reasons"]))

    def test_stage_gate_allows_ready_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "configs").mkdir(parents=True, exist_ok=True)
            (root / "data" / "meta").mkdir(parents=True, exist_ok=True)
            (root / "configs" / "prod_policy.yaml").write_text(
                (
                    "prod:\n"
                    "  promotion:\n"
                    "    deployment_gate:\n"
                    "      require_pipeline_gate_pass: true\n"
                    "      require_stage_ready: true\n"
                    "      required_stage_terminal: READY\n"
                    "      required_last_completed_stage: D90\n"
                    "      require_security_gate: false\n"
                    "      require_model_artifact_exists: true\n"
                    "      require_inference_sla_gate: false\n"
                ),
                encoding="utf-8",
            )
            st = {
                "current_stage": "READY",
                "last_completed_stage": "D90",
                "history": [],
            }
            (root / "data" / "meta" / "stage_runtime_state.json").write_text(json.dumps(st), encoding="utf-8")
            out = evaluate_deployment_gate(root, report=_mk_report(root), stage="promote")
            self.assertTrue(out["allowed"])
            self.assertEqual(out["reasons"], ["ok"])

    def test_inference_sla_gate_blocks_when_report_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "configs").mkdir(parents=True, exist_ok=True)
            (root / "configs" / "prod_policy.yaml").write_text(
                (
                    "prod:\n"
                    "  promotion:\n"
                    "    deployment_gate:\n"
                    "      require_pipeline_gate_pass: true\n"
                    "      require_stage_ready: false\n"
                    "      require_security_gate: false\n"
                    "      require_model_artifact_exists: true\n"
                    "      require_inference_sla_gate: true\n"
                    "      require_inference_metrics: true\n"
                    "      max_sla_report_age_minutes: 180\n"
                ),
                encoding="utf-8",
            )
            out = evaluate_deployment_gate(root, report=_mk_report(root), stage="promote")
            self.assertFalse(out["allowed"])
            self.assertTrue(any("inference_sla_report_missing" in r for r in out["reasons"]))

    def test_inference_sla_gate_defaults_to_hard_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "configs").mkdir(parents=True, exist_ok=True)
            (root / "configs" / "prod_policy.yaml").write_text(
                (
                    "prod:\n"
                    "  promotion:\n"
                    "    deployment_gate:\n"
                    "      require_pipeline_gate_pass: true\n"
                    "      require_stage_ready: false\n"
                    "      require_security_gate: false\n"
                    "      require_model_artifact_exists: true\n"
                    "      require_inference_metrics: true\n"
                    "      max_sla_report_age_minutes: 180\n"
                ),
                encoding="utf-8",
            )
            out = evaluate_deployment_gate(root, report=_mk_report(root), stage="promote")
            self.assertFalse(out["allowed"])
            self.assertTrue(any("inference_sla_report_missing" in r for r in out["reasons"]))

    def test_inference_sla_gate_allows_with_fresh_report(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "configs").mkdir(parents=True, exist_ok=True)
            (root / "reports" / "monitoring").mkdir(parents=True, exist_ok=True)
            (root / "configs" / "prod_policy.yaml").write_text(
                (
                    "prod:\n"
                    "  kpi:\n"
                    "    min_inference_availability_pct: 99.5\n"
                    "    max_inference_p95_latency_ms: 300.0\n"
                    "  promotion:\n"
                    "    deployment_gate:\n"
                    "      require_pipeline_gate_pass: true\n"
                    "      require_stage_ready: false\n"
                    "      require_security_gate: false\n"
                    "      require_model_artifact_exists: true\n"
                    "      require_inference_sla_gate: true\n"
                    "      require_inference_metrics: true\n"
                    "      max_sla_report_age_minutes: 180\n"
                ),
                encoding="utf-8",
            )
            sla = {
                "status": "PASS",
                "alert_required": False,
                "metrics": {
                    "inference_service": {
                        "availability_pct": 99.9,
                        "latency_ms_p95": 120.0,
                    }
                },
            }
            (root / "reports" / "monitoring" / "sla_report_20260526T000000Z.json").write_text(
                json.dumps(sla),
                encoding="utf-8",
            )
            out = evaluate_deployment_gate(root, report=_mk_report(root), stage="promote")
            self.assertTrue(out["allowed"])

    def test_security_gate_defaults_to_hard_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "configs").mkdir(parents=True, exist_ok=True)
            (root / "configs" / "prod_policy.yaml").write_text(
                (
                    "prod:\n"
                    "  promotion:\n"
                    "    deployment_gate:\n"
                    "      require_pipeline_gate_pass: true\n"
                    "      require_stage_ready: false\n"
                    "      require_model_artifact_exists: true\n"
                    "      require_inference_sla_gate: false\n"
                ),
                encoding="utf-8",
            )
            out = evaluate_deployment_gate(root, report=_mk_report(root), stage="promote")
            self.assertFalse(out["allowed"])
            self.assertTrue(any("security_gate_fail:" in r for r in out["reasons"]))


if __name__ == "__main__":
    unittest.main()
