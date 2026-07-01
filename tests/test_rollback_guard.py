from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mlbotnav.rollback_guard import _rollback_to_previous_champion


class RollbackGuardTests(unittest.TestCase):
    def test_restore_previous_champion_from_history(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            reg = root / "models" / "registry"
            reg.mkdir(parents=True, exist_ok=True)
            current = {"symbol": "SOLUSDT", "timeframe": "1m", "run_utc": "new", "model_path": "new.joblib"}
            previous = {"symbol": "SOLUSDT", "timeframe": "1m", "run_utc": "old", "model_path": "old.joblib"}
            (reg / "champion.json").write_text(json.dumps(current), encoding="utf-8")
            history_row = {
                "event": "promote",
                "new_champion_run_utc": "new",
                "previous_champion": previous,
                "new_champion": current,
            }
            (reg / "champion_history.jsonl").write_text(json.dumps(history_row) + "\n", encoding="utf-8")
            ok, status, restored = _rollback_to_previous_champion(root)
            self.assertTrue(ok)
            self.assertEqual(status, "rollback_applied")
            self.assertEqual((restored or {}).get("run_utc"), "old")
            now_champion = json.loads((reg / "champion.json").read_text(encoding="utf-8"))
            self.assertEqual(now_champion.get("run_utc"), "old")
            self.assertTrue((reg / "active_model.json").exists())


if __name__ == "__main__":
    unittest.main()

