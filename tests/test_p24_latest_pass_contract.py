from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _touch_mtime(path: Path, ts: float) -> None:
    os.utime(path, (ts, ts))


class P24LatestPassContractTests(unittest.TestCase):
    def _prepare_workspace(self) -> tuple[Path, Path]:
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        self.addCleanup(td.cleanup)

        src_script = Path(__file__).resolve().parents[1] / "run_p24_latest_pass_report.ps1"
        dst_script = root / "run_p24_latest_pass_report.ps1"
        dst_script.write_text(src_script.read_text(encoding="utf-8"), encoding="utf-8")
        src_pkg = root / "src" / "mlbotnav"
        src_pkg.mkdir(parents=True, exist_ok=True)
        (src_pkg / "__init__.py").write_text(
            (Path(__file__).resolve().parents[1] / "src" / "mlbotnav" / "__init__.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        (src_pkg / "p24_latest_pass_contract.py").write_text(
            (Path(__file__).resolve().parents[1] / "src" / "mlbotnav" / "p24_latest_pass_contract.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )

        qa = root / "reports" / "qa_gate"
        final_review = root / "reports" / "final_review"
        qa.mkdir(parents=True, exist_ok=True)
        final_review.mkdir(parents=True, exist_ok=True)

        now = 1760000000.0
        fresh = now
        old = now - 3600.0

        p23 = qa / "p23_operator_unified_20260526T150424Z.json"
        _write_json(
            p23,
            {
                "status": "PASS",
                "mode": "table_chain",
            },
        )
        _touch_mtime(p23, fresh)

        for name in [
            "table_convergence_5plus_20260526T150434Z.json",
            "features_block_audit_20260526T150505Z.json",
            "orderbook_source_audit_20260526T150448Z.json",
            "tz_gate_20260526T150449Z.json",
            "p72_freeze_ready_20260526T150505Z.json",
        ]:
            p = qa / name
            _write_json(p, {"status": "PASS"})
            _touch_mtime(p, fresh)

        stress = final_review / "stress_backtest_contour_SOLUSDT_1m_2026-05-20_short_only_20260526T144231Z.json"
        _write_json(stress, {"status": "PASS"})
        _touch_mtime(stress, old)

        return root, p23

    def _run_p24(self, root: Path, *extra_args: str) -> dict:
        script = root / "run_p24_latest_pass_report.ps1"
        cmd = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            *extra_args,
        ]
        p = subprocess.run(cmd, cwd=root, capture_output=True, text=True, check=False)
        self.assertEqual(p.returncode, 0, msg=f"stdout={p.stdout}\nstderr={p.stderr}")
        line = (p.stdout or "").strip().splitlines()[-1]
        m_status = re.search(r'"status":"([^"]+)"', line)
        m_report = re.search(r'"report_path":"([^"]+)"', line)
        self.assertIsNotNone(m_status, msg=f"cannot parse status from: {line}")
        self.assertIsNotNone(m_report, msg=f"cannot parse report_path from: {line}")
        report_path = Path(str(m_report.group(1)))
        return json.loads(report_path.read_text(encoding="utf-8-sig"))

    def test_epoch_lock_uses_baseline_latest_for_stress(self) -> None:
        root, p23 = self._prepare_workspace()
        report = self._run_p24(root, "-SourceP23ReportPath", str(p23))
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["epoch_lock_enabled"])
        self.assertIn(
            "reports/final_review/stress_backtest_contour_*.json",
            report.get("epoch_lock_baseline_allowed_patterns", []),
        )

        items = report.get("items", [])
        stress_item = next(x for x in items if x.get("pattern") == "reports/final_review/stress_backtest_contour_*.json")
        self.assertEqual(stress_item.get("status"), "PASS")
        self.assertEqual(stress_item.get("resolution_mode"), "baseline_latest")
        self.assertTrue(bool(stress_item.get("epoch_lock_bypass")))

    def test_epoch_lock_fails_without_matching_baseline_allowlist(self) -> None:
        root, p23 = self._prepare_workspace()
        report = self._run_p24(
            root,
            "-SourceP23ReportPath",
            str(p23),
            "-EpochLockBaselineAllowedPatterns",
            "reports/final_review/non_matching_pattern_*.json",
        )
        self.assertEqual(report["status"], "FAIL")
        items = report.get("items", [])
        stress_item = next(x for x in items if x.get("pattern") == "reports/final_review/stress_backtest_contour_*.json")
        self.assertEqual(stress_item.get("status"), "missing_epoch_locked")
        self.assertEqual(stress_item.get("resolution_mode"), "epoch_locked")
        self.assertFalse(bool(stress_item.get("epoch_lock_bypass")))


if __name__ == "__main__":
    unittest.main()
