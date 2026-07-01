from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from mlbotnav.security import require_role, sign_file


class SecurityTests(unittest.TestCase):
    def test_sign_file_outputs_sig(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            p = root / "a.txt"
            p.write_text("hello", encoding="utf-8")
            sig = sign_file(root, path=p, meta={"k": "v"})
            self.assertTrue(sig.exists())
            self.assertIn("signature", sig.read_text(encoding="utf-8"))

    def test_require_role_allows_admin(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cfg = root / "configs"
            cfg.mkdir(parents=True, exist_ok=True)
            (cfg / "security_governance.yaml").write_text(
                "governance:\n  rbac:\n    action_owner_map:\n      train_eval: MLEngineer\n",
                encoding="utf-8",
            )
            os.environ["MLBOTNAV_ROLE"] = "Admin"
            res = require_role(root, action="train_eval")
            self.assertTrue(res["allowed"])


if __name__ == "__main__":
    unittest.main()

