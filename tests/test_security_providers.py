from __future__ import annotations

import base64
import os
import tempfile
import unittest
from pathlib import Path

from mlbotnav.security import resolve_secret


class SecurityProvidersTests(unittest.TestCase):
    def _mk_project(self) -> Path:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        (root / "configs").mkdir(parents=True, exist_ok=True)
        return root

    def test_env_provider_reads_plain_env_secret(self) -> None:
        root = self._mk_project()
        (root / "configs" / "security_governance.yaml").write_text(
            "security:\n  provider:\n    required: env\n",
            encoding="utf-8",
        )
        os.environ["BYBIT_API_KEY"] = "abc123"
        try:
            out = resolve_secret(root, name="BYBIT_API_KEY")
            self.assertTrue(out["found"])
            self.assertEqual(out["value"], "abc123")
        finally:
            os.environ.pop("BYBIT_API_KEY", None)

    def test_kms_provider_offline_b64_fallback(self) -> None:
        root = self._mk_project()
        (root / "configs" / "security_governance.yaml").write_text(
            "security:\n  provider:\n    required: kms\n    allow_fallback: true\n",
            encoding="utf-8",
        )
        os.environ["KMS_KEY_ID"] = "kms-key-test"
        os.environ["BYBIT_API_SECRET_ENC_B64"] = base64.b64encode(b"secret-xyz").decode("utf-8")
        try:
            out = resolve_secret(root, name="BYBIT_API_SECRET")
            self.assertTrue(out["found"])
            self.assertEqual(out["value"], "secret-xyz")
        finally:
            os.environ.pop("KMS_KEY_ID", None)
            os.environ.pop("BYBIT_API_SECRET_ENC_B64", None)

    def test_kms_provider_offline_fallback_disabled(self) -> None:
        root = self._mk_project()
        (root / "configs" / "security_governance.yaml").write_text(
            "security:\n  provider:\n    required: kms\n    allow_fallback: false\n",
            encoding="utf-8",
        )
        os.environ["KMS_KEY_ID"] = "kms-key-test"
        os.environ["BYBIT_API_SECRET_ENC_B64"] = base64.b64encode(b"secret-xyz").decode("utf-8")
        try:
            out = resolve_secret(root, name="BYBIT_API_SECRET")
            self.assertFalse(out["found"])
            self.assertEqual(out["reason"], "kms_offline_fallback_disabled")
        finally:
            os.environ.pop("KMS_KEY_ID", None)
            os.environ.pop("BYBIT_API_SECRET_ENC_B64", None)


if __name__ == "__main__":
    unittest.main()
