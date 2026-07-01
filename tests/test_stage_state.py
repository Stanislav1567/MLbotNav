from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mlbotnav.stage_state import load_stage_state, next_stage, save_stage_state


class StageStateTests(unittest.TestCase):
    def test_default_and_advance(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            stages = ["D1", "D2", "D3"]
            state = load_stage_state(root, stages=stages)
            self.assertEqual(state["current_stage"], "D1")
            state["current_stage"] = next_stage("D1", stages=stages)
            save_stage_state(root, state)
            loaded = json.loads((root / "data" / "meta" / "stage_runtime_state.json").read_text(encoding="utf-8"))
            self.assertEqual(loaded["current_stage"], "D2")


if __name__ == "__main__":
    unittest.main()

