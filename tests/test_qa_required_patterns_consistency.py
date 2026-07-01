from __future__ import annotations

import unittest

from mlbotnav.qa_required_patterns import (
    STRESS_PATTERN,
    get_p24_epoch_lock_baseline_allowed_patterns,
    get_p24_required_patterns,
    get_p26_required_patterns,
    get_patterns_payload,
)


class QaRequiredPatternsConsistencyTests(unittest.TestCase):
    def test_p24_p26_required_patterns_are_identical_with_stress(self) -> None:
        p24 = get_p24_required_patterns(require_stress=True)
        p26 = get_p26_required_patterns(require_stress=True)
        self.assertEqual(p24, p26)
        self.assertIn(STRESS_PATTERN, p24)

    def test_p24_p26_required_patterns_are_identical_without_stress(self) -> None:
        p24 = get_p24_required_patterns(require_stress=False)
        p26 = get_p26_required_patterns(require_stress=False)
        self.assertEqual(p24, p26)
        self.assertNotIn(STRESS_PATTERN, p24)

    def test_p24_baseline_allowlist_matches_stress_policy(self) -> None:
        allow_with_stress = get_p24_epoch_lock_baseline_allowed_patterns(require_stress=True)
        allow_without_stress = get_p24_epoch_lock_baseline_allowed_patterns(require_stress=False)
        self.assertEqual(allow_with_stress, [STRESS_PATTERN])
        self.assertEqual(allow_without_stress, [])

    def test_payload_shape(self) -> None:
        p24 = get_patterns_payload(role="p24", require_stress=True)
        p26 = get_patterns_payload(role="p26", require_stress=True)
        self.assertEqual(p24["role"], "p24")
        self.assertEqual(p26["role"], "p26")
        self.assertIn("required_patterns", p24)
        self.assertIn("required_patterns", p26)
        self.assertIn("epoch_lock_baseline_allowed_patterns", p24)
        self.assertNotIn("epoch_lock_baseline_allowed_patterns", p26)


if __name__ == "__main__":
    unittest.main()
