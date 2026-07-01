from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from mlbotnav.dataset import FEATURE_COLUMNS, FEATURE_GROUPS, build_feature_frame, load_ohlcv_range
from mlbotnav.hypothesis_registry import load_backlog_registry
from mlbotnav.technical_analysis import CANDLE_PATTERN_TYPES, FIGURE_PATTERN_TYPES


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _check(name: str, ok: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": details or {}}


def _dups(values: list[str]) -> list[str]:
    c = Counter(values)
    return sorted([k for k, v in c.items() if v > 1])


def _collect_backlog_items(cfg: dict[str, Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    backlog = cfg.get("extended_hypotheses_backlog") or {}
    if not isinstance(backlog, dict):
        return out
    for family, items in backlog.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            out.append(
                {
                    "family": str(family),
                    "name": str(item.get("name", "")).strip(),
                    "status": str(item.get("status", "")).strip(),
                }
            )
    return out


def _find_sample_partition(project_root: Path) -> dict[str, str] | None:
    base = project_root / "data" / "raw" / "bybit_ohlcv"
    if not base.exists():
        return None
    for day_dir in sorted(base.glob("dt=*")):
        if not day_dir.is_dir():
            continue
        day = day_dir.name.split("=", 1)[1]
        for tf_dir in sorted(day_dir.glob("tf=*")):
            if not tf_dir.is_dir():
                continue
            tf = tf_dir.name.split("=", 1)[1]
            for sym_dir in sorted(tf_dir.glob("symbol=*")):
                if not sym_dir.is_dir():
                    continue
                symbol = sym_dir.name.split("=", 1)[1]
                part = sym_dir / "part-final.csv"
                if part.exists():
                    return {"day": day, "timeframe": tf, "symbol": symbol}
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit configs/features_block.yaml consistency.")
    parser.add_argument("--config", default="configs/features_block.yaml")
    parser.add_argument("--out-dir", default="reports/qa_gate")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    cfg_path = Path(str(args.config))
    if not cfg_path.is_absolute():
        cfg_path = (project_root / cfg_path).resolve()
    out_dir = Path(str(args.out_dir))
    if not out_dir.is_absolute():
        out_dir = (project_root / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []
    if not cfg_path.exists():
        checks.append(_check("config_exists", False, {"path": str(cfg_path)}))
        payload = {
            "status": "FAIL",
            "generated_at_utc": _utc_iso(),
            "config_path": str(cfg_path),
            "checks": checks,
            "summary": {"total": 1, "failed": 1},
        }
        report = out_dir / f"features_block_audit_{_utc_tag()}.json"
        report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": "FAIL", "report_path": str(report)}, ensure_ascii=False))
        return 1

    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    checks.append(_check("config_exists", True, {"path": str(cfg_path)}))

    features = (((cfg.get("features") or {}).get("columns")) or [])
    hypotheses = (cfg.get("hypotheses") or {})
    signal_modes = hypotheses.get("signal_modes") or []
    execution_modes = hypotheses.get("execution_modes") or []
    order_types = hypotheses.get("order_types") or []
    candle_patterns = (((cfg.get("technical_analysis") or {}).get("candle_patterns")) or [])
    pattern_types = (((cfg.get("technical_analysis") or {}).get("pattern_types")) or [])
    cfg_groups = (((cfg.get("features") or {}).get("groups")) or {})
    ru = cfg.get("ru_labels") or {}
    ru_features = ru.get("feature_columns") or {}
    ru_candles = ru.get("technical_candle_patterns") or {}
    ru_ptypes = ru.get("technical_pattern_types") or {}
    cfg_feature_cols = [str(x) for x in features]
    ds_feature_cols = [str(x) for x in FEATURE_COLUMNS]

    checks.append(_check("features_columns_non_empty", len(features) > 0, {"count": len(features)}))
    checks.append(
        _check(
            "features_columns_match_dataset_exact_order",
            cfg_feature_cols == ds_feature_cols,
            {"cfg_count": len(cfg_feature_cols), "dataset_count": len(ds_feature_cols)},
        )
    )
    checks.append(
        _check(
            "features_columns_match_dataset_exact_set",
            set(cfg_feature_cols) == set(ds_feature_cols),
            {
                "cfg_only": sorted(set(cfg_feature_cols) - set(ds_feature_cols)),
                "dataset_only": sorted(set(ds_feature_cols) - set(cfg_feature_cols)),
            },
        )
    )
    for profile in ["trend_filters_long_style_1m", "trend_filters_short_style_1m", "trend_filters_both_style_1m"]:
        raw = hypotheses.get(profile) or []
        valid = [x for x in raw if isinstance(x, dict) and str(x.get("trend_filter", "")).strip()]
        checks.append(
            _check(
                f"hypothesis_profile_{profile}_non_empty",
                len(valid) > 0,
                {"profile": profile, "count": len(valid)},
            )
        )
    checks.append(
        _check(
            "signal_modes_supported",
            set(str(x) for x in signal_modes) == {"both", "long_only", "short_only"},
            {"found": [str(x) for x in signal_modes]},
        )
    )
    checks.append(
        _check(
            "execution_modes_supported",
            set(str(x) for x in execution_modes) == {"research", "exchange_like"},
            {"found": [str(x) for x in execution_modes]},
        )
    )
    checks.append(
        _check(
            "order_types_supported",
            set(str(x) for x in order_types) == {"market", "limit"},
            {"found": [str(x) for x in order_types]},
        )
    )

    allowed_filters = {
        "none",
        "ema_gap_sign",
        "ema_cross_20_50",
        "ema_cross_20_200",
        "ema_stack_bull",
        "channel_breakout_50",
        "adx_trend_18",
        "fib_retrace_0382_0618_trend_resume",
        "fib_extension_targets",
        "swing_hl_hh_long",
        "swing_lh_ll_short",
        "bos_continuation_confirm",
        "min_max_range_revert",
        "max_low_pullback_long",
        "hvn_lvn_density_reaction",
        "volume_profile_poc_vah_val_retest",
        "value_area_rotation_vs_breakout",
        "wedge_breakout_plus_profile_acceptance",
        "orderbook_imbalance_l1_l50",
        "spread_pressure_and_delta_absorption",
    }
    bad_filters: dict[str, list[str]] = {}
    for profile in ["trend_filters_long_style_1m", "trend_filters_short_style_1m", "trend_filters_both_style_1m"]:
        raw = hypotheses.get(profile) or []
        invalid = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            tf = str(item.get("trend_filter", "")).strip()
            if tf and tf not in allowed_filters:
                invalid.append(tf)
        if invalid:
            bad_filters[profile] = sorted(set(invalid))
    checks.append(_check("trend_filters_supported_by_runtime", len(bad_filters) == 0, {"invalid": bad_filters}))

    backlog_items = _collect_backlog_items(cfg)
    allowed_statuses = {"planned", "in_code_density_only", "active", "validated"}
    missing_name = sorted([f"{x['family']}::<empty_name>" for x in backlog_items if not x["name"]])
    missing_status = sorted([f"{x['family']}::{x['name'] or '<empty_name>'}" for x in backlog_items if not x["status"]])
    invalid_status = sorted(
        [
            f"{x['family']}::{x['name']}::{x['status']}"
            for x in backlog_items
            if x["status"] and x["status"] not in allowed_statuses
        ]
    )
    checks.append(
        _check(
            "backlog_items_have_name_and_status",
            len(missing_name) == 0 and len(missing_status) == 0,
            {
                "items_total": len(backlog_items),
                "missing_name": missing_name,
                "missing_status": missing_status,
            },
        )
    )
    checks.append(
        _check(
            "backlog_status_vocabulary_valid",
            len(invalid_status) == 0,
            {
                "allowed_statuses": sorted(allowed_statuses),
                "invalid_items": invalid_status,
            },
        )
    )
    checks.append(
        _check(
            "backlog_hypothesis_names_unique",
            len(_dups([x["name"] for x in backlog_items if x["name"]])) == 0,
            {"dups": _dups([x["name"] for x in backlog_items if x["name"]])},
        )
    )

    # P6.1: unified config->runtime mapping audit for all backlog hypotheses.
    runtime_registry = load_backlog_registry(
        project_root=project_root,
        features_config=str(cfg_path),
        run_signal_mode="both",
    )
    checks.append(
        _check(
            "backlog_runtime_registry_load_ok",
            str(runtime_registry.get("status", "")).lower() == "ok",
            {"registry_status": runtime_registry.get("status"), "config_path": runtime_registry.get("config_path")},
        )
    )
    reg_items = runtime_registry.get("items") or []
    reg_names = {str(x.get("name", "")).strip() for x in reg_items if isinstance(x, dict)}
    cfg_names = {str(x.get("name", "")).strip() for x in backlog_items if x.get("name")}
    checks.append(
        _check(
            "backlog_runtime_item_count_matches_config",
            len(reg_names) == len(cfg_names),
            {"registry_unique_count": len(reg_names), "config_unique_count": len(cfg_names)},
        )
    )
    checks.append(
        _check(
            "backlog_runtime_mapping_covers_all_config_items",
            cfg_names.issubset(reg_names),
            {"unmapped_backlog_names": sorted(cfg_names - reg_names)},
        )
    )
    checks.append(
        _check(
            "backlog_runtime_has_no_unknown_items",
            reg_names.issubset(cfg_names),
            {"unknown_registry_names": sorted(reg_names - cfg_names)},
        )
    )
    active_or_validated = [
        x
        for x in reg_items
        if isinstance(x, dict) and str(x.get("status", "")).strip().lower() in {"active", "validated"}
    ]
    missing_required = []
    missing_source = []
    source_probe = runtime_registry.get("source_probe") or {}
    source_ready_map = source_probe.get("source_ready") or {}
    for item in active_or_validated:
        name = str(item.get("name", "")).strip()
        miss = [str(v) for v in (item.get("missing_required_features") or [])]
        if miss:
            missing_required.append({"name": name, "missing_required_features": miss})
        req_src = item.get("requires_external_source")
        if req_src not in (None, "") and not bool(source_ready_map.get(str(req_src), False)):
            missing_source.append(
                {
                    "name": name,
                    "requires_external_source": req_src,
                    "source_ready": bool(source_ready_map.get(str(req_src), False)),
                }
            )
    checks.append(
        _check(
            "active_validated_backlog_required_features_available",
            len(missing_required) == 0,
            {"violations": missing_required},
        )
    )
    checks.append(
        _check(
            "active_validated_backlog_no_external_source_dependency",
            len(missing_source) == 0,
            {"violations": missing_source, "source_probe": source_probe},
        )
    )

    checks.append(_check("features_columns_unique", len(_dups([str(x) for x in features])) == 0, {"dups": _dups([str(x) for x in features])}))
    checks.append(_check("candle_patterns_unique", len(_dups([str(x) for x in candle_patterns])) == 0, {"dups": _dups([str(x) for x in candle_patterns])}))
    checks.append(_check("pattern_types_unique", len(_dups([str(x) for x in pattern_types])) == 0, {"dups": _dups([str(x) for x in pattern_types])}))
    checks.append(
        _check(
            "candle_patterns_match_runtime_catalog",
            set(str(x) for x in candle_patterns) == set(CANDLE_PATTERN_TYPES),
            {
                "cfg_only": sorted(set(str(x) for x in candle_patterns) - set(CANDLE_PATTERN_TYPES)),
                "runtime_only": sorted(set(CANDLE_PATTERN_TYPES) - set(str(x) for x in candle_patterns)),
            },
        )
    )
    checks.append(
        _check(
            "pattern_types_match_runtime_catalog",
            set(str(x) for x in pattern_types) == set(FIGURE_PATTERN_TYPES),
            {
                "cfg_only": sorted(set(str(x) for x in pattern_types) - set(FIGURE_PATTERN_TYPES)),
                "runtime_only": sorted(set(FIGURE_PATTERN_TYPES) - set(str(x) for x in pattern_types)),
            },
        )
    )
    cfg_group_ok = True
    group_details: dict[str, Any] = {"missing_groups": [], "mismatch_groups": []}
    for g_name, ds_cols in FEATURE_GROUPS.items():
        cfg_cols = [str(x) for x in (cfg_groups.get(g_name) or [])]
        if not cfg_cols:
            cfg_group_ok = False
            group_details["missing_groups"].append(g_name)
            continue
        if cfg_cols != [str(x) for x in ds_cols]:
            cfg_group_ok = False
            group_details["mismatch_groups"].append(g_name)
    checks.append(_check("feature_groups_match_dataset", cfg_group_ok, group_details))
    cfg_union = set()
    for v in cfg_groups.values():
        if isinstance(v, list):
            cfg_union.update(str(x) for x in v)
    checks.append(
        _check(
            "feature_groups_cover_all_features",
            set(cfg_feature_cols).issubset(cfg_union),
            {"uncovered_features": sorted(set(cfg_feature_cols) - cfg_union)},
        )
    )

    feature_keys = {str(x) for x in features}
    checks.append(
        _check(
            "ru_feature_columns_cover_all",
            feature_keys.issubset(set(str(k) for k in ru_features.keys())),
            {"features_total": len(feature_keys), "ru_total": len(ru_features)},
        )
    )
    candle_keys = {str(x) for x in candle_patterns}
    checks.append(
        _check(
            "ru_candle_patterns_cover_all",
            candle_keys.issubset(set(str(k) for k in ru_candles.keys())),
            {"patterns_total": len(candle_keys), "ru_total": len(ru_candles)},
        )
    )
    ptype_keys = {str(x) for x in pattern_types}
    checks.append(
        _check(
            "ru_pattern_types_cover_all",
            ptype_keys.issubset(set(str(k) for k in ru_ptypes.keys())),
            {"types_total": len(ptype_keys), "ru_total": len(ru_ptypes)},
        )
    )

    sample = _find_sample_partition(project_root)
    if sample:
        try:
            raw = load_ohlcv_range(
                project_root,
                symbol=str(sample["symbol"]),
                timeframe=str(sample["timeframe"]),
                start_date=str(sample["day"]),
                end_date=str(sample["day"]),
            )
            ff = build_feature_frame(raw, horizon_bars=1, include_targets=False, include_dropna=False)
            missing_runtime = [c for c in cfg_feature_cols if c not in ff.columns]
            checks.append(
                _check(
                    "runtime_feature_frame_contains_all_config_features",
                    len(missing_runtime) == 0,
                    {"sample": sample, "missing": missing_runtime},
                )
            )
        except Exception as e:
            checks.append(
                _check(
                    "runtime_feature_frame_contains_all_config_features",
                    False,
                    {"sample": sample, "error": str(e)},
                )
            )
    else:
        checks.append(
            _check(
                "runtime_feature_frame_contains_all_config_features",
                False,
                {"error": "no_sample_raw_partition_found"},
            )
        )

    failed = int(sum(1 for c in checks if not c["ok"]))
    payload = {
        "status": "PASS" if failed == 0 else "FAIL",
        "generated_at_utc": _utc_iso(),
        "config_path": str(cfg_path),
        "checks": checks,
        "summary": {"total": len(checks), "failed": failed},
    }
    report = out_dir / f"features_block_audit_{_utc_tag()}.json"
    report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "report_path": str(report), "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
