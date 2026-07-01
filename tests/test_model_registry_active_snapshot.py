from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mlbotnav.model_registry import load_active_model_snapshot


class ActiveModelSnapshotTests(unittest.TestCase):
    def test_load_active_prefers_active_model_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            reg = root / "models" / "registry"
            reg.mkdir(parents=True, exist_ok=True)
            (reg / "champion.json").write_text(json.dumps({"model_path": "c.joblib"}), encoding="utf-8")
            (reg / "active_model.json").write_text(json.dumps({"model_path": "a.joblib"}), encoding="utf-8")
            s = load_active_model_snapshot(root)
            self.assertEqual((s or {}).get("model_path"), "a.joblib")


if __name__ == "__main__":
    unittest.main()

