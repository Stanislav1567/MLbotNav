from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from mlbotnav.dataset import FEATURE_COLUMNS
from mlbotnav.external_sources import detect_external_sources


_ALLOWED_BACKLOG_STATUSES = {"planned", "in_code_density_only", "active", "validated"}


def _resolve_cfg(project_root: Path, features_config: str) -> Path:
    p = Path(str(features_config or "").strip() or "configs/features_block.yaml")
    if p.is_absolute():
        return p
    return (project_root / p).resolve()


def _mode_matches(item_mode: str, run_mode: str) -> bool:
    im = str(item_mode or "both").strip().lower()
    rm = str(run_mode or "both").strip().lower()
    if im == "both":
        return True
    return im == rm


def _spec_for_name(name: str) -> dict[str, Any]:
    n = str(name).strip().lower()
    specs: dict[str, dict[str, Any]] = {
        "fib_retrace_0382_0618_trend_resume": {
            "signal_mode": "both",
            "required_features": ["fib_0382_distance", "fib_0618_distance", "ema_gap"],
            "params_grid": {"retrace_levels": [0.382, 0.5, 0.618, 0.786]},
        },
        "fib_extension_targets": {
            "signal_mode": "both",
            "required_features": ["fib_0382_distance", "fib_0618_distance", "rr_context_estimate"],
            "params_grid": {"extension_levels": [1.272, 1.618, 2.618]},
        },
        "swing_hl_hh_long": {
            "signal_mode": "long_only",
            "required_features": ["swing_high_break_flag", "swing_low_break_flag", "ema_slope_5"],
            "params_grid": {"min_swing_window": [8, 10, 12]},
        },
        "swing_lh_ll_short": {
            "signal_mode": "short_only",
            "required_features": ["swing_high_break_flag", "swing_low_break_flag", "ema_slope_5"],
            "params_grid": {"min_swing_window": [8, 10, 12]},
        },
        "bos_continuation_confirm": {
            "signal_mode": "both",
            "required_features": ["bos_up_flag", "bos_down_flag", "retest_flag"],
            "params_grid": {"confirm_bars": [1, 2, 3]},
        },
        "min_max_range_revert": {
            "signal_mode": "both",
            "required_features": ["position_in_range", "support_distance", "resistance_distance"],
            "params_grid": {"range_tail_quantile": [0.05, 0.1, 0.15]},
        },
        "max_low_pullback_long": {
            "signal_mode": "long_only",
            "required_features": ["support_distance", "retest_flag", "trend_channel_pos"],
            "params_grid": {"pullback_depth": [0.1, 0.2, 0.3]},
        },
        "hvn_lvn_density_reaction": {
            "signal_mode": "both",
            "required_features": [
                "density_vpoc_distance_60",
                "density_cluster_share_60",
                "density_cluster_ratio_60_240",
            ],
            "params_grid": {"vpoc_distance_threshold": [0.001, 0.002, 0.003]},
        },
        "volume_profile_poc_vah_val_retest": {
            "signal_mode": "both",
            "required_features": ["density_vpoc_distance_60", "density_vpoc_share_60", "retest_flag"],
            "params_grid": {"retest_tolerance": [0.001, 0.002]},
        },
        "value_area_rotation_vs_breakout": {
            "signal_mode": "both",
            "required_features": ["position_in_range", "breakout_flag", "density_bin_share_60"],
            "params_grid": {"value_area_shift_window": [20, 40, 60]},
        },
        "wedge_breakout_plus_profile_acceptance": {
            "signal_mode": "both",
            "required_features": ["trend_channel_pos", "breakout_flag", "density_vpoc_share_60"],
            "params_grid": {"acceptance_bars": [1, 2, 3]},
        },
        "orderbook_imbalance_l1_l50": {
            "signal_mode": "both",
            "required_features": [],
            "params_grid": {"requires_orderbook_levels": "L1-L50"},
            "requires_external_source": "orderbook_l1_l50",
        },
        "spread_pressure_and_delta_absorption": {
            "signal_mode": "both",
            "required_features": [],
            "params_grid": {"requires_microstructure": ["spread", "delta_absorption"]},
            "requires_external_source": "microstructure_spread_delta",
        },
    }
    return specs.get(n, {"signal_mode": "both", "required_features": [], "params_grid": {}})


def load_backlog_registry(
    *,
    project_root: Path,
    features_config: str,
    run_signal_mode: str,
) -> dict[str, Any]:
    cfg_path = _resolve_cfg(project_root, features_config)
    if not cfg_path.exists():
        return {
            "status": "missing_config",
            "config_path": str(cfg_path),
            "items_total": 0,
            "active_items_total": 0,
            "items": [],
            "active_items": [],
        }
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    backlog = cfg.get("extended_hypotheses_backlog") or {}
    if not isinstance(backlog, dict):
        return {
            "status": "no_backlog_block",
            "config_path": str(cfg_path),
            "items_total": 0,
            "active_items_total": 0,
            "items": [],
            "active_items": [],
        }

    feat_set = set(str(x) for x in FEATURE_COLUMNS)
    source_probe = detect_external_sources(project_root)
    source_ready_map = source_probe.get("source_ready") or {}
    run_mode = str(run_signal_mode or "both").strip().lower()
    items: list[dict[str, Any]] = []
    active_items: list[dict[str, Any]] = []

    for family, raw_items in backlog.items():
        if not isinstance(raw_items, list):
            continue
        for raw in raw_items:
            if not isinstance(raw, dict):
                continue
            name = str(raw.get("name", "")).strip()
            status = str(raw.get("status", "")).strip().lower()
            spec = _spec_for_name(name)
            required_features = [str(x) for x in spec.get("required_features", [])]
            missing_features = sorted([x for x in required_features if x not in feat_set])
            spec_mode = str(spec.get("signal_mode", "both")).strip().lower()
            mode_match = _mode_matches(spec_mode, run_mode)
            status_valid = status in _ALLOWED_BACKLOG_STATUSES
            requires_external_source = str(spec.get("requires_external_source", "")).strip()
            source_ready = True
            if requires_external_source:
                source_ready = bool(source_ready_map.get(requires_external_source, False))

            enabled = bool(
                status in {"active", "validated"}
                and mode_match
                and len(missing_features) == 0
                and source_ready
            )
            reasons: list[str] = []
            if not status_valid:
                reasons.append("invalid_status")
            if status not in {"active", "validated"}:
                reasons.append("inactive_status")
            if not mode_match:
                reasons.append("signal_mode_mismatch")
            if missing_features:
                reasons.append("missing_required_features")
            if not source_ready:
                reasons.append("missing_external_source")

            rec = {
                "family": str(family),
                "name": name,
                "status": status or "missing_status",
                "status_valid": status_valid,
                "signal_mode": spec_mode,
                "mode_match_for_run": mode_match,
                "required_features": required_features,
                "missing_required_features": missing_features,
                "params_grid": spec.get("params_grid", {}),
                "requires_external_source": requires_external_source or None,
                "enabled_for_run": enabled,
                "disabled_reasons": reasons,
            }
            items.append(rec)
            if enabled:
                active_items.append(rec)

    return {
        "status": "ok",
        "config_path": str(cfg_path),
        "run_signal_mode": run_mode,
        "source_probe": source_probe,
        "items_total": len(items),
        "active_items_total": len(active_items),
        "items": items,
        "active_items": active_items,
    }
