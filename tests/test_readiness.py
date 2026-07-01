from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mlbotnav.readiness import check_action_allowed, load_readiness, save_readiness, write_readiness_report


class ReadinessTests(unittest.TestCase):
    def test_default_blocks_train_action(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cfg = load_readiness(root)
            self.assertFalse(cfg["project_ready"])
            check = check_action_allowed(root, action="pipeline_train_eval")
            self.assertFalse(check["allowed"])
            self.assertIn("project_not_ready_for_pipeline_train_eval", check["reason"])

    def test_ready_state_allows_train_action(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cfg = load_readiness(root)
            cfg["project_ready"] = True
            save_readiness(root, cfg)
            check = check_action_allowed(root, action="pipeline_train_eval")
            self.assertTrue(check["allowed"])
            self.assertEqual("ok", check["reason"])

    def test_write_report_creates_json(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            p = write_readiness_report(root, check={"action": "pipeline_train_eval", "allowed": False})
            self.assertTrue(p.exists())
            self.assertEqual(".json", p.suffix)


if __name__ == "__main__":
    unittest.main()
