from __future__ import annotations

from pathlib import Path

import yaml

from mlbotnav.backtest import _normalize_trend_filter
from mlbotnav.dataset import FEATURE_COLUMNS, FEATURE_GROUPS
from mlbotnav.technical_analysis import CANDLE_PATTERN_TYPES, FIGURE_PATTERN_TYPES


def _load_features_cfg() -> dict:
    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "configs" / "features_block.yaml"
    return yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}


def test_feature_columns_exact_parity_with_runtime() -> None:
    cfg = _load_features_cfg()
    cfg_cols = [str(x) for x in (((cfg.get("features") or {}).get("columns")) or [])]
    assert cfg_cols == list(FEATURE_COLUMNS)


def test_feature_groups_exact_parity_with_runtime() -> None:
    cfg = _load_features_cfg()
    cfg_groups = (((cfg.get("features") or {}).get("groups")) or {})
    assert set(str(k) for k in cfg_groups.keys()) == set(FEATURE_GROUPS.keys())
    for name, cols in FEATURE_GROUPS.items():
        assert [str(x) for x in (cfg_groups.get(name) or [])] == [str(x) for x in cols]


def test_trend_filters_from_registry_are_supported_by_runtime() -> None:
    cfg = _load_features_cfg()
    hypotheses = cfg.get("hypotheses") or {}
    filters: set[str] = set()
    for profile_name, items in hypotheses.items():
        if not str(profile_name).startswith("trend_filters_") or not isinstance(items, list):
            continue
        for row in items:
            if not isinstance(row, dict):
                continue
            tf = str(row.get("trend_filter", "")).strip()
            if tf:
                filters.add(tf)

    backlog = cfg.get("extended_hypotheses_backlog") or {}
    if isinstance(backlog, dict):
        for _, items in backlog.items():
            if not isinstance(items, list):
                continue
            for row in items:
                if not isinstance(row, dict):
                    continue
                if str(row.get("status", "")).strip().lower() != "active":
                    continue
                name = str(row.get("name", "")).strip()
                if name:
                    filters.add(name)

    for tf in sorted(filters):
        assert _normalize_trend_filter(tf) == tf


def test_pattern_catalog_exact_parity_with_runtime() -> None:
    cfg = _load_features_cfg()
    ta = cfg.get("technical_analysis") or {}
    cfg_candles = [str(x) for x in (ta.get("candle_patterns") or [])]
    cfg_patterns = [str(x) for x in (ta.get("pattern_types") or [])]
    assert set(cfg_candles) == set(CANDLE_PATTERN_TYPES)
    assert set(cfg_patterns) == set(FIGURE_PATTERN_TYPES)
