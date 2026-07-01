from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from mlbotnav.adaptive_auto_train import _run_preflight_window_once
from mlbotnav.daily_long_short_cycle import (
    _build_cycle_payload,
    _build_adaptive_cmd,
    _extract_failure_details,
    _extract_interruption_details,
    _resolve_cycle_outcome,
    _run,
    _run_core_table_window_readiness,
)


def _mk_day_file(root: Path, *, day: str, tf: str = "1m", symbol: str = "SOLUSDT", layer: str = "core") -> None:
    p = (
        root
        / "data"
        / layer
        / "bybit_ohlcv"
        / f"dt={day}"
        / f"tf={tf}"
        / f"symbol={symbol}"
        / "part-final.csv"
    )
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("open_time_utc,close_time_utc,open,high,low,close,volume\n", encoding="utf-8")


class CyclePreflightIntegrationTests(unittest.TestCase):
    def test_daily_resolve_cycle_outcome_prefers_interrupted(self) -> None:
        status, code = _resolve_cycle_outcome(
            failed=True,
            steps=[{"returncode": 1}, {"returncode": 130, "parsed_json": {"status": "INTERRUPTED"}}],
        )
        self.assertEqual(status, "INTERRUPTED")
        self.assertEqual(code, 130)

    def test_daily_resolve_cycle_outcome_fail_without_interrupt(self) -> None:
        status, code = _resolve_cycle_outcome(failed=True, steps=[{"returncode": 1}])
        self.assertEqual(status, "FAIL")
        self.assertEqual(code, 1)

    def test_daily_resolve_cycle_outcome_interrupt_from_parsed_status(self) -> None:
        status, code = _resolve_cycle_outcome(
            failed=True,
            steps=[{"returncode": 1, "parsed_json": {"status": "INTERRUPTED"}}],
        )
        self.assertEqual(status, "INTERRUPTED")
        self.assertEqual(code, 130)

    def test_daily_extract_interruption_details(self) -> None:
        details = _extract_interruption_details(
            [
                {"task": "adaptive_auto_train_long_only", "returncode": 130},
                {"task": "table_convergence_5plus_long_only", "returncode": 1},
            ]
        )
        self.assertIsNotNone(details)
        self.assertEqual(details["interrupted_task"], "adaptive_auto_train_long_only")
        self.assertEqual(details["interrupted_reason"], "keyboard_interrupt")

    def test_daily_extract_interruption_details_prefers_first_match(self) -> None:
        details = _extract_interruption_details(
            [
                {"task": "first_task", "returncode": 130},
                {"task": "second_task", "returncode": 130, "parsed_json": {"status": "INTERRUPTED", "reason": "other"}},
            ]
        )
        self.assertEqual(details["interrupted_task"], "first_task")

    def test_daily_build_cycle_payload_includes_interruption_fields(self) -> None:
        payload = _build_cycle_payload(
            status="INTERRUPTED",
            generated_at_utc="2026-05-26T18:51:44Z",
            params={"symbol": "SOLUSDT"},
            steps=[{"task": "adaptive_auto_train_long_only", "returncode": 130}],
        )
        self.assertEqual(payload["status"], "INTERRUPTED")
        self.assertEqual(payload["interrupted_task"], "adaptive_auto_train_long_only")
        self.assertEqual(payload["interrupted_reason"], "keyboard_interrupt")

    def test_daily_extract_failure_details(self) -> None:
        details = _extract_failure_details(
            [
                {"task": "ok_step", "returncode": 0},
                {"task": "failing_step", "returncode": 2, "parsed_json": {"error": "summary_path_missing"}},
            ]
        )
        self.assertIsNotNone(details)
        self.assertEqual(details["failed_task"], "failing_step")
        self.assertEqual(details["failed_reason"], "summary_path_missing")

    def test_daily_build_cycle_payload_includes_failure_fields(self) -> None:
        payload = _build_cycle_payload(
            status="FAIL",
            generated_at_utc="2026-05-26T18:51:44Z",
            params={"symbol": "SOLUSDT"},
            steps=[{"task": "failing_step", "returncode": 2, "parsed_json": {"reason": "preflight_failed"}}],
        )
        self.assertEqual(payload["status"], "FAIL")
        self.assertEqual(payload["failed_task"], "failing_step")
        self.assertEqual(payload["failed_reason"], "preflight_failed")

    def test_daily_run_handles_keyboard_interrupt(self) -> None:
        with patch("mlbotnav.daily_long_short_cycle.subprocess.run", side_effect=KeyboardInterrupt):
            out = _run(Path("."), ["python", "-V"])
        self.assertEqual(out["returncode"], 130)
        self.assertEqual((out.get("parsed_json") or {}).get("status"), "INTERRUPTED")

    def test_core_table_window_readiness_pass(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _mk_day_file(root, day="2026-05-20")
            args = SimpleNamespace(symbol="SOLUSDT", timeframe="1m", test_day="2026-05-20", test_end_day="2026-05-20")
            out = _run_core_table_window_readiness(root, args)
            self.assertEqual(out["returncode"], 0)
            self.assertEqual((out.get("parsed_json") or {}).get("status"), "PASS")

    def test_core_table_window_readiness_fail(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            args = SimpleNamespace(symbol="SOLUSDT", timeframe="1m", test_day="2026-05-20", test_end_day="2026-05-20")
            out = _run_core_table_window_readiness(root, args)
            self.assertEqual(out["returncode"], 1)
            self.assertEqual((out.get("parsed_json") or {}).get("status"), "FAIL")

    def test_adaptive_preflight_invokes_raw_layer(self) -> None:
        fake = SimpleNamespace(returncode=0, stdout='{"status":"PASS","report_path":"x","failed":0}\n', stderr="")
        with patch("mlbotnav.adaptive_auto_train.subprocess.run", return_value=fake) as run_mock:
            out = _run_preflight_window_once(
                Path("."),
                symbol="SOLUSDT",
                timeframe="1m",
                train_start="2026-05-19",
                train_end="2026-05-19",
                test_day="2026-05-20",
                test_end_day="2026-05-20",
                min_train_rows=100,
                n_folds=2,
                horizons_grid="1,2,3",
                layer="raw",
            )
            self.assertEqual(out["returncode"], 0)
            cmd = run_mock.call_args.kwargs["args"] if "args" in run_mock.call_args.kwargs else run_mock.call_args.args[0]
            self.assertIn("--layer", cmd)
            layer_idx = cmd.index("--layer")
            self.assertEqual(cmd[layer_idx + 1], "raw")

    def test_daily_cycle_passes_min_tp_reach_prob_to_adaptive(self) -> None:
        args = SimpleNamespace(
            symbol="SOLUSDT",
            timeframe="1m",
            train_start="2026-05-19",
            train_end="2026-05-19",
            test_day="2026-05-20",
            test_end_day="2026-05-20",
            repeats=1,
            goal_net_return_pct=0.0,
            min_train_rows=500,
            n_folds=1,
            fee_bps=10.0,
            slippage_bps=5.0,
            stop_loss_pct=0.002,
            take_profit_pct=0.012,
            tp_min_factor=0.5,
            min_tp_reach_prob=0.73,
            cooldown_bars=20,
            horizons_grid="12",
            p_long_grid="0.55",
            p_short_grid="0.58,0.55",
            p_short_grid_long_mode="0.45",
            p_long_grid_short_mode="0.55",
            min_expected_move_grid="0.0003,0.0005",
            notional_usd=10.0,
            leverage=1.0,
            execution_mode="exchange_like",
            order_type="market",
            cpu_max_pct=85.0,
            max_threads=8,
            search_workers=8,
            speed_profile="turbo",
            search_engine="grid",
            optuna_stage="auto",
            preflight_policy="configs/preflight_policy.yaml",
            disable_hypothesis_profile=True,
            disable_backlog_active_append=True,
        )
        cmd = _build_adaptive_cmd(args, mode="short_only")
        self.assertIn("--min-tp-reach-prob", cmd)
        idx = cmd.index("--min-tp-reach-prob")
        self.assertEqual(cmd[idx + 1], "0.73")

    def test_daily_cycle_passes_min_tp_reach_prob_to_adaptive_long_only(self) -> None:
        args = SimpleNamespace(
            symbol="SOLUSDT",
            timeframe="1m",
            train_start="2026-05-19",
            train_end="2026-05-19",
            test_day="2026-05-20",
            test_end_day="2026-05-20",
            repeats=1,
            goal_net_return_pct=0.0,
            min_train_rows=500,
            n_folds=1,
            fee_bps=10.0,
            slippage_bps=5.0,
            stop_loss_pct=0.002,
            take_profit_pct=0.012,
            tp_min_factor=0.5,
            min_tp_reach_prob=0.66,
            cooldown_bars=20,
            horizons_grid="12",
            p_long_grid="0.55,0.58",
            p_short_grid="0.45,0.42",
            p_short_grid_long_mode="0.45",
            p_long_grid_short_mode="0.55",
            min_expected_move_grid="0.0003,0.0005",
            notional_usd=10.0,
            leverage=1.0,
            execution_mode="exchange_like",
            order_type="market",
            cpu_max_pct=85.0,
            max_threads=8,
            search_workers=8,
            speed_profile="turbo",
            search_engine="grid",
            optuna_stage="auto",
            preflight_policy="configs/preflight_policy.yaml",
            disable_hypothesis_profile=True,
            disable_backlog_active_append=True,
        )
        cmd = _build_adaptive_cmd(args, mode="long_only")
        self.assertIn("--min-tp-reach-prob", cmd)
        idx = cmd.index("--min-tp-reach-prob")
        self.assertEqual(cmd[idx + 1], "0.66")

    def test_daily_cycle_optuna_flags_are_forwarded(self) -> None:
        args = SimpleNamespace(
            symbol="SOLUSDT",
            timeframe="1m",
            train_start="2026-05-19",
            train_end="2026-05-19",
            test_day="2026-05-20",
            test_end_day="2026-05-20",
            repeats=1,
            goal_net_return_pct=0.0,
            min_train_rows=500,
            n_folds=1,
            fee_bps=10.0,
            slippage_bps=5.0,
            stop_loss_pct=0.002,
            take_profit_pct=0.012,
            tp_min_factor=0.5,
            min_tp_reach_prob=0.58,
            cooldown_bars=20,
            horizons_grid="12",
            p_long_grid="0.55,0.58",
            p_short_grid="0.45,0.42",
            p_short_grid_long_mode="0.45",
            p_long_grid_short_mode="0.55",
            min_expected_move_grid="0.0003,0.0005",
            notional_usd=10.0,
            leverage=1.0,
            execution_mode="exchange_like",
            order_type="market",
            cpu_max_pct=85.0,
            max_threads=8,
            search_workers=8,
            speed_profile="turbo",
            search_engine="optuna",
            optuna_stage="B",
            optuna_n_trials_override=24,
            optuna_timeout_sec_override=900,
            preflight_policy="configs/preflight_policy.yaml",
            disable_hypothesis_profile=True,
            disable_backlog_active_append=True,
        )
        cmd = _build_adaptive_cmd(args, mode="long_only")
        self.assertIn("--search-engine", cmd)
        i_engine = cmd.index("--search-engine")
        self.assertEqual(cmd[i_engine + 1], "optuna")
        self.assertIn("--optuna-stage", cmd)
        i_stage = cmd.index("--optuna-stage")
        self.assertEqual(cmd[i_stage + 1], "B")
        self.assertIn("--optuna-n-trials-override", cmd)
        self.assertEqual(cmd[cmd.index("--optuna-n-trials-override") + 1], "24")
        self.assertIn("--optuna-timeout-sec-override", cmd)
        self.assertEqual(cmd[cmd.index("--optuna-timeout-sec-override") + 1], "900")

    def test_daily_cycle_mode_grid_switches_use_mode_specific_fallbacks(self) -> None:
        args = SimpleNamespace(
            symbol="SOLUSDT",
            timeframe="1m",
            train_start="2026-05-19",
            train_end="2026-05-19",
            test_day="2026-05-20",
            test_end_day="2026-05-20",
            repeats=1,
            goal_net_return_pct=0.0,
            min_train_rows=500,
            n_folds=1,
            fee_bps=10.0,
            slippage_bps=5.0,
            stop_loss_pct=0.002,
            take_profit_pct=0.012,
            tp_min_factor=0.5,
            min_tp_reach_prob=0.58,
            cooldown_bars=20,
            horizons_grid="12",
            p_long_grid="0.61,0.62",
            p_short_grid="0.39,0.38",
            p_short_grid_long_mode="0.41",
            p_long_grid_short_mode="0.59",
            min_expected_move_grid="0.0003,0.0005",
            notional_usd=10.0,
            leverage=1.0,
            execution_mode="exchange_like",
            order_type="market",
            cpu_max_pct=85.0,
            max_threads=8,
            search_workers=8,
            speed_profile="turbo",
            search_engine="grid",
            optuna_stage="auto",
            preflight_policy="configs/preflight_policy.yaml",
            disable_hypothesis_profile=True,
            disable_backlog_active_append=True,
        )
        short_cmd = _build_adaptive_cmd(args, mode="short_only")
        self.assertIn("--p-long-grid", short_cmd)
        i_short = short_cmd.index("--p-long-grid")
        self.assertEqual(short_cmd[i_short + 1], "0.59")
        long_cmd = _build_adaptive_cmd(args, mode="long_only")
        self.assertIn("--p-short-grid", long_cmd)
        i_long = long_cmd.index("--p-short-grid")
        self.assertEqual(long_cmd[i_long + 1], "0.41")

    def test_daily_cycle_grid_mode_does_not_forward_optuna_overrides(self) -> None:
        args = SimpleNamespace(
            symbol="SOLUSDT",
            timeframe="1m",
            train_start="2026-05-19",
            train_end="2026-05-19",
            test_day="2026-05-20",
            test_end_day="2026-05-20",
            repeats=1,
            goal_net_return_pct=0.0,
            min_train_rows=500,
            n_folds=1,
            fee_bps=10.0,
            slippage_bps=5.0,
            stop_loss_pct=0.002,
            take_profit_pct=0.012,
            tp_min_factor=0.5,
            min_tp_reach_prob=0.58,
            cooldown_bars=20,
            horizons_grid="12",
            p_long_grid="0.61,0.62",
            p_short_grid="0.39,0.38",
            p_short_grid_long_mode="0.41",
            p_long_grid_short_mode="0.59",
            min_expected_move_grid="0.0003,0.0005",
            notional_usd=10.0,
            leverage=1.0,
            execution_mode="exchange_like",
            order_type="market",
            cpu_max_pct=85.0,
            max_threads=8,
            search_workers=8,
            speed_profile="turbo",
            search_engine="grid",
            optuna_stage="B",
            optuna_n_trials_override=55,
            optuna_timeout_sec_override=777,
            preflight_policy="configs/preflight_policy.yaml",
            disable_hypothesis_profile=True,
            disable_backlog_active_append=True,
        )
        cmd = _build_adaptive_cmd(args, mode="long_only")
        self.assertNotIn("--optuna-n-trials-override", cmd)
        self.assertNotIn("--optuna-timeout-sec-override", cmd)


if __name__ == "__main__":
    unittest.main()
