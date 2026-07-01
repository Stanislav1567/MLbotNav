from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from mlbotnav.security import run_security_gate


class SecurityGateTests(unittest.TestCase):
    def _mk_project(self, yaml_text: str) -> Path:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        (root / "configs").mkdir(parents=True, exist_ok=True)
        (root / "configs" / "security_governance.yaml").write_text(yaml_text, encoding="utf-8")
        return root

    def test_kms_gate_requires_endpoint_when_fallback_disabled(self) -> None:
        root = self._mk_project(
            (
                "security:\n"
                "  provider:\n"
                "    required: kms\n"
                "    allow_fallback: false\n"
                "  gate:\n"
                "    active: true\n"
                "    tls_required: true\n"
                "    at_rest_encryption_required: true\n"
            )
        )
        os.environ["KMS_KEY_ID"] = "kms-key-test"
        os.environ["STORAGE_ENCRYPTION_ENABLED"] = "true"
        os.environ["STORAGE_ENCRYPTION_PROVIDER"] = "kms"
        try:
            out = run_security_gate(root, stage="test")
            self.assertFalse(out["allowed"])
            self.assertTrue(any("kms_endpoint_missing_no_fallback" in r for r in out["reasons"]))
        finally:
            os.environ.pop("KMS_KEY_ID", None)
            os.environ.pop("STORAGE_ENCRYPTION_ENABLED", None)
            os.environ.pop("STORAGE_ENCRYPTION_PROVIDER", None)

    def test_vault_gate_allows_token_file_with_https(self) -> None:
        root = self._mk_project(
            (
                "security:\n"
                "  provider:\n"
                "    required: vault\n"
                "    allow_fallback: false\n"
                "  gate:\n"
                "    active: true\n"
                "    tls_required: true\n"
                "    at_rest_encryption_required: true\n"
            )
        )
        token_file = root / "vault.token"
        token_file.write_text("token-xyz", encoding="utf-8")
        os.environ["VAULT_ADDR"] = "https://vault.local"
        os.environ["VAULT_TOKEN_FILE"] = str(token_file)
        os.environ["STORAGE_ENCRYPTION_ENABLED"] = "true"
        os.environ["STORAGE_ENCRYPTION_PROVIDER"] = "vault"
        try:
            out = run_security_gate(root, stage="test")
            self.assertTrue(out["allowed"])
            self.assertEqual(out["reasons"], ["ok"])
        finally:
            os.environ.pop("VAULT_ADDR", None)
            os.environ.pop("VAULT_TOKEN_FILE", None)
            os.environ.pop("STORAGE_ENCRYPTION_ENABLED", None)
            os.environ.pop("STORAGE_ENCRYPTION_PROVIDER", None)


if __name__ == "__main__":
    unittest.main()
