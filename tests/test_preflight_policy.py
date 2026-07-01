from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mlbotnav.preflight_policy import get_core_preflight_cfg, get_raw_preflight_cfg, resolve_preflight_runtime_args


class PreflightPolicyTests(unittest.TestCase):
    def test_defaults_when_policy_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            raw = get_raw_preflight_cfg(root, policy_path="configs/preflight_policy.yaml")
            core = get_core_preflight_cfg(root, policy_path="configs/preflight_policy.yaml")
            self.assertEqual(raw["layer"], "raw")
            self.assertEqual(raw["min_train_rows"], 900)
            self.assertEqual(raw["n_folds"], 2)
            self.assertEqual(raw["horizons_grid"], "1,2,3,4,6,8,12")
            self.assertEqual(core["layer"], "core")
            self.assertTrue(core["require_full_coverage"])

    def test_partial_override_merge(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cfg = root / "configs" / "preflight_policy.yaml"
            cfg.parent.mkdir(parents=True, exist_ok=True)
            cfg.write_text(
                "\n".join(
                    [
                        "preflight:",
                        "  raw:",
                        "    min_train_rows: 1200",
                        "    layer: raw",
                        "  core:",
                        "    require_full_coverage: false",
                    ]
                ),
                encoding="utf-8",
            )
            raw = get_raw_preflight_cfg(root, policy_path="configs/preflight_policy.yaml")
            core = get_core_preflight_cfg(root, policy_path="configs/preflight_policy.yaml")
            self.assertEqual(raw["min_train_rows"], 1200)
            self.assertEqual(raw["n_folds"], 2)
            self.assertEqual(raw["horizons_grid"], "1,2,3,4,6,8,12")
            self.assertFalse(core["require_full_coverage"])
            self.assertEqual(core["layer"], "core")

    def test_runtime_resolution_uses_policy_only_for_legacy_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cfg = root / "configs" / "preflight_policy.yaml"
            cfg.parent.mkdir(parents=True, exist_ok=True)
            cfg.write_text(
                "\n".join(
                    [
                        "preflight:",
                        "  raw:",
                        "    layer: raw_alt",
                        "    min_train_rows: 1500",
                        "    n_folds: 4",
                        '    horizons_grid: "2,4,8"',
                    ]
                ),
                encoding="utf-8",
            )
            resolved_default = resolve_preflight_runtime_args(
                root,
                policy_path="configs/preflight_policy.yaml",
                min_train_rows=900,
                n_folds=2,
                horizons_grid="1,2,3,4,6,8,12",
                legacy_min_train_rows=900,
                legacy_n_folds=2,
                legacy_horizons_grid="1,2,3,4,6,8,12",
            )
            self.assertEqual(resolved_default["min_train_rows"], 1500)
            self.assertEqual(resolved_default["n_folds"], 4)
            self.assertEqual(resolved_default["horizons_grid"], "2,4,8")
            self.assertEqual(resolved_default["raw_layer"], "raw_alt")

            resolved_explicit = resolve_preflight_runtime_args(
                root,
                policy_path="configs/preflight_policy.yaml",
                min_train_rows=2000,
                n_folds=5,
                horizons_grid="3,6,9",
                legacy_min_train_rows=900,
                legacy_n_folds=2,
                legacy_horizons_grid="1,2,3,4,6,8,12",
            )
            self.assertEqual(resolved_explicit["min_train_rows"], 2000)
            self.assertEqual(resolved_explicit["n_folds"], 5)
            self.assertEqual(resolved_explicit["horizons_grid"], "3,6,9")
            self.assertEqual(resolved_explicit["raw_layer"], "raw_alt")

    def test_bool_string_false_is_respected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cfg = root / "configs" / "preflight_policy.yaml"
            cfg.parent.mkdir(parents=True, exist_ok=True)
            cfg.write_text(
                "\n".join(
                    [
                        "preflight:",
                        "  core:",
                        '    require_full_coverage: "false"',
                    ]
                ),
                encoding="utf-8",
            )
            core = get_core_preflight_cfg(root, policy_path="configs/preflight_policy.yaml")
            self.assertFalse(core["require_full_coverage"])

    def test_invalid_int_values_fall_back_to_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cfg = root / "configs" / "preflight_policy.yaml"
            cfg.parent.mkdir(parents=True, exist_ok=True)
            cfg.write_text(
                "\n".join(
                    [
                        "preflight:",
                        "  raw:",
                        '    min_train_rows: "abc"',
                        '    n_folds: ""',
                    ]
                ),
                encoding="utf-8",
            )
            raw = get_raw_preflight_cfg(root, policy_path="configs/preflight_policy.yaml")
            self.assertEqual(raw["min_train_rows"], 900)
            self.assertEqual(raw["n_folds"], 2)


if __name__ == "__main__":
    unittest.main()
