from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path

from mlbotnav.qa_audit_lock_expectations import get_p26_lock_files, get_p26_required_table_files


class P26ReportExpectationsParityTests(unittest.TestCase):
    def test_report_matches_expected_table_and_lock_lists(self) -> None:
        root = Path(__file__).resolve().parents[1]
        script = root / "run_p26_audit_lock.ps1"
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)]
        p = subprocess.run(cmd, cwd=root, capture_output=True, text=True, check=False)
        self.assertEqual(p.returncode, 0, msg=f"stdout={p.stdout}\nstderr={p.stderr}")
        line = (p.stdout or "").strip().splitlines()[-1]
        m = re.search(r'"report_path":"([^"]+)"', line)
        self.assertIsNotNone(m, msg=f"cannot parse report_path from: {line}")
        report_path = Path(str(m.group(1)))
        report = json.loads(report_path.read_text(encoding="utf-8-sig"))

        expected_tables_abs = {str((root / rel).resolve()) for rel in get_p26_required_table_files()}
        expected_locks_abs = {str((root / rel).resolve()) for rel in get_p26_lock_files()}

        actual_tables_abs = {str(x.get("file")) for x in report.get("table_files", []) if x.get("file")}
        actual_locks_abs = {str(x.get("file")) for x in report.get("lock_hashes", []) if x.get("file")}

        self.assertEqual(actual_tables_abs, expected_tables_abs)
        self.assertEqual(actual_locks_abs, expected_locks_abs)


if __name__ == "__main__":
    unittest.main()
