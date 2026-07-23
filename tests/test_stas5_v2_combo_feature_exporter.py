from __future__ import annotations

import pandas as pd

from mlbotnav.stas5_v2_combo_feature_exporter import (
    build_combo_features_from_frames,
    select_v2_feature_columns,
    _recent_divergence_features,
)


def _ohlcv(day: str, *, periods: int = 90, base: float = 100.0) -> pd.DataFrame:
    times = pd.date_range(f"{day}T00:00:00Z", periods=periods, freq="min")
    close = [base + i * 0.015 + ((i % 9) - 4) * 0.01 for i in range(periods)]
    open_ = [value - 0.01 for value in close]
    high = [value + 0.04 for value in close]
    low = [value - 0.05 for value in close]
    volume = [1000.0 + (i % 13) * 17.0 for i in range(periods)]
    return pd.DataFrame(
        {
            "open_time_utc": times,
            "close_time_utc": times + pd.Timedelta(minutes=1),
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


def _candidate(day: str, candidate_id: str, record_id: str, minute: int) -> dict[str, object]:
    anchor = pd.Timestamp(f"{day}T00:00:00Z") + pd.Timedelta(minutes=minute)
    entry = anchor + pd.Timedelta(minutes=1)
    return {
        "day_utc": day,
        "candidate_id": candidate_id,
        "record_id": record_id,
        "anchor_time_utc": anchor.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_time_utc": entry.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_price_5bps": 100.05,
        "pre_15m_close_move_pct": -0.10,
        "pre_30m_close_move_pct": -0.20,
        "pre_60m_close_move_pct": -0.35,
        "pre_60m_phase_metric_pct": -0.30,
        "stas1_risk_flags": "",
        "effective_session_label": "EUROPE",
        "session_time_bucket_label": "EUROPE",
        "is_weekend": 0,
        "yellow_x": 1,
        "postfact_hit_1pct": 1,
        "ML_DECISION": "ENTER",
    }


def test_v2_combo_exporter_keeps_one_row_per_candidate_and_uses_anchor_candle():
    stas2 = pd.DataFrame(
        [
            _candidate("2026-05-01", "LA001", "G1P_20260501_LA001", 45),
            _candidate("2026-05-01", "LA002", "G1P_20260501_LA002", 60),
        ]
    )

    features, manifest = build_combo_features_from_frames(
        stas2=stas2,
        ohlcv_by_day={"2026-05-01": _ohlcv("2026-05-01")},
        start_day="2026-05-01",
        end_day="2026-05-01",
    )

    assert manifest["status"] == "PASS"
    assert manifest["rows"] == 2
    assert len(features) == len(stas2)
    assert features.loc[0, "feature_time_utc"] == "2026-05-01T00:45:00Z"
    assert features.loc[0, "entry_time_utc"] == "2026-05-01T00:46:00Z"
    assert features["feature_available_before_entry"].tolist() == [True, True]


def test_v2_feature_columns_include_combo_density_structure_risk_and_exclude_forbidden_sources():
    stas2 = pd.DataFrame([_candidate("2026-05-01", "LA001", "G1P_20260501_LA001", 50)])

    features, manifest = build_combo_features_from_frames(
        stas2=stas2,
        ohlcv_by_day={"2026-05-01": _ohlcv("2026-05-01")},
        start_day="2026-05-01",
        end_day="2026-05-01",
    )

    feature_columns = manifest["feature_columns"]
    assert "stas4_v2_combo_rsi14" in feature_columns
    assert "stas4_v2_combo_stoch_k_minus_d" in feature_columns
    assert "stas4_v2_density_vpoc60_dist_pct" in feature_columns
    assert "stas4_v2_structure_support_score" in feature_columns
    assert "stas4_v2_pattern_strength" in feature_columns
    assert "stas4_v2_block_density_structure_net_score" in feature_columns
    assert "stas4_v2_block_pattern_structure_net_score" in feature_columns
    assert "stas4_v2_block_structure_volume_net_score" in feature_columns
    assert "stas4_v2_block_structure_trend_net_score" in feature_columns
    assert "stas5_v2_short_wave_15m_down_from_high_pct" in feature_columns
    assert "stas5_v2_risk_knife_pre_entry" in feature_columns
    assert "yellow_x" not in feature_columns
    assert "postfact_hit_1pct" not in feature_columns
    assert "ML_DECISION" not in feature_columns
    assert "old_removed_candidate" not in feature_columns
    assert "new_candidate" not in feature_columns
    assert not manifest["checks"]["forbidden_feature_columns"]
    assert select_v2_feature_columns(list(features.columns)) == feature_columns


def test_v2_join_contract_does_not_merge_same_candidate_id_across_days():
    stas2 = pd.DataFrame(
        [
            _candidate("2026-05-01", "LA001", "G1P_20260501_LA001", 50),
            _candidate("2026-05-02", "LA001", "G1P_20260502_LA001", 50),
        ]
    )

    features, manifest = build_combo_features_from_frames(
        stas2=stas2,
        ohlcv_by_day={"2026-05-01": _ohlcv("2026-05-01"), "2026-05-02": _ohlcv("2026-05-02", base=105.0)},
        start_day="2026-05-01",
        end_day="2026-05-02",
    )

    assert manifest["status"] == "PASS"
    assert features["candidate_id"].tolist() == ["LA001", "LA001"]
    assert features["day"].tolist() == ["2026-05-01", "2026-05-02"]
    assert features["record_id"].tolist() == ["G1P_20260501_LA001", "G1P_20260502_LA001"]


def test_v2_divergence_features_ignore_unconfirmed_future_divergence():
    divergences = [
        {"kind": "bullish_divergence", "confirm_idx": 10},
        {"kind": "bearish_divergence", "confirm_idx": 25},
    ]

    at_20 = _recent_divergence_features(divergences, idx=20, lookback=60)
    at_30 = _recent_divergence_features(divergences, idx=30, lookback=60)

    assert at_20["stas4_v2_div_bullish_recent"] == 1
    assert at_20["stas4_v2_div_bearish_recent"] == 0
    assert at_20["stas4_v2_div_type_code"] == 1
    assert at_30["stas4_v2_div_bearish_recent"] == 1
    assert at_30["stas4_v2_div_type_code"] == -1
