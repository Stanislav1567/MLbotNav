from __future__ import annotations

import unittest
from pathlib import Path

from mlbotnav.optuna_engine import (
    apply_stage_overrides,
    build_study_plan,
    enforce_storage_parallel_compat,
    load_optuna_engine_config,
    resolve_stage_profile,
    resolve_storage_url,
)


class OptunaEngineConfigTests(unittest.TestCase):
    def test_load_engine_config(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        cfg = load_optuna_engine_config(project_root)
        self.assertTrue(bool(cfg.get("enabled", False)))
        self.assertIn("sampler", cfg)
        self.assertIn("pruner", cfg)

    def test_storage_fallback_sqlite(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        cfg = load_optuna_engine_config(project_root)
        url = resolve_storage_url(project_root, cfg, env={})
        self.assertTrue(url.startswith("sqlite:///"))

    def test_study_plan_shape(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        cfg = load_optuna_engine_config(project_root)
        plan = build_study_plan(
            contour_id="long_only",
            test_day="2026-05-20",
            cfg=cfg,
            symbol="SOLUSDT",
            timeframe="1m",
            start_date="2026-05-19",
            end_date="2026-05-19",
        )
        self.assertEqual(plan["study_name"], "optuna_long_only_SOLUSDT_1m_2026-05-19_2026-05-19_2026-05-20")
        self.assertIn(plan["direction"], {"maximize", "minimize"})
        self.assertGreater(plan["n_trials"], 0)

    def test_stage_profile_exists_for_abc(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        cfg = load_optuna_engine_config(project_root)
        for stage in ("A", "B", "C"):
            profile = resolve_stage_profile(cfg=cfg, stage=stage)
            self.assertIn("n_trials", profile)
            self.assertIn("timeout_sec", profile)
            self.assertIn("workers_max", profile)

    def test_apply_stage_overrides_changes_plan(self) -> None:
        base = {"n_trials": 200, "timeout_sec": 7200, "seed": 1}
        prof = {"n_trials": 123, "timeout_sec": 456}
        out = apply_stage_overrides(study_plan=base, stage_profile=prof)
        self.assertEqual(out["n_trials"], 123)
        self.assertEqual(out["timeout_sec"], 456)
        self.assertEqual(out["seed"], 1)

    def test_storage_parallel_guard_forces_sqlite_single_worker(self) -> None:
        n_jobs, meta = enforce_storage_parallel_compat(storage_url="sqlite:///tmp/optuna.db", n_jobs=8)
        self.assertEqual(n_jobs, 1)
        self.assertTrue(bool(meta.get("forced_single_worker")))
        self.assertEqual(meta.get("reason"), "sqlite_single_worker_enforced")

    def test_storage_parallel_guard_keeps_postgres_parallel(self) -> None:
        n_jobs, meta = enforce_storage_parallel_compat(
            storage_url="postgresql://user:pass@localhost:5432/optuna",
            n_jobs=6,
        )
        self.assertEqual(n_jobs, 6)
        self.assertFalse(bool(meta.get("forced_single_worker")))


if __name__ == "__main__":
    unittest.main()
