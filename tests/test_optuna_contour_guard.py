from __future__ import annotations

import unittest

from mlbotnav.adaptive_auto_train import _build_optuna_overrides_payload, _resolve_engine_contour


class OptunaContourGuardTests(unittest.TestCase):
    def test_optuna_rejects_both_mode(self) -> None:
        with self.assertRaises(ValueError):
            _resolve_engine_contour(signal_mode="both", contour_id="auto", search_engine="optuna")

    def test_optuna_forces_contour_to_signal_mode(self) -> None:
        engine, contour, note = _resolve_engine_contour(
            signal_mode="long_only",
            contour_id="my_custom_contour",
            search_engine="optuna",
        )
        self.assertEqual(engine, "optuna")
        self.assertEqual(contour, "long_only")
        self.assertIsNotNone(note)

    def test_grid_keeps_custom_contour(self) -> None:
        engine, contour, note = _resolve_engine_contour(
            signal_mode="both",
            contour_id="my_custom_contour",
            search_engine="grid",
        )
        self.assertEqual(engine, "grid")
        self.assertEqual(contour, "my_custom_contour")
        self.assertIsNone(note)

    def test_optuna_overrides_payload_for_optuna_normalizes_non_positive(self) -> None:
        payload = _build_optuna_overrides_payload(
            search_engine="optuna",
            n_trials_override=0,
            timeout_sec_override=-5,
        )
        self.assertEqual(payload["n_trials_override"], None)
        self.assertEqual(payload["timeout_sec_override"], None)

    def test_optuna_overrides_payload_for_optuna_keeps_positive_values(self) -> None:
        payload = _build_optuna_overrides_payload(
            search_engine="optuna",
            n_trials_override=250,
            timeout_sec_override=1800,
        )
        self.assertEqual(payload["n_trials_override"], 250)
        self.assertEqual(payload["timeout_sec_override"], 1800)

    def test_optuna_overrides_payload_for_grid_is_none(self) -> None:
        payload = _build_optuna_overrides_payload(
            search_engine="grid",
            n_trials_override=200,
            timeout_sec_override=3600,
        )
        self.assertEqual(payload["n_trials_override"], None)
        self.assertEqual(payload["timeout_sec_override"], None)


if __name__ == "__main__":
    unittest.main()
