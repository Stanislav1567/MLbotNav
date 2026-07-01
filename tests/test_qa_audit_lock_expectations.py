from __future__ import annotations

import unittest

from mlbotnav.qa_audit_lock_expectations import (
    get_audit_lock_payload,
    get_p26_lock_files,
    get_p26_required_table_files,
)


class QaAuditLockExpectationsTests(unittest.TestCase):
    def test_p26_lists_non_empty_and_unique(self) -> None:
        tables = get_p26_required_table_files()
        locks = get_p26_lock_files()
        self.assertGreater(len(tables), 0)
        self.assertGreater(len(locks), 0)
        self.assertEqual(len(tables), len(set(tables)))
        self.assertEqual(len(locks), len(set(locks)))

    def test_payload_shape(self) -> None:
        payload = get_audit_lock_payload(role="p26")
        self.assertEqual(payload["role"], "p26")
        self.assertEqual(payload["required_table_files"], get_p26_required_table_files())
        self.assertEqual(payload["lock_files"], get_p26_lock_files())


if __name__ == "__main__":
    unittest.main()
