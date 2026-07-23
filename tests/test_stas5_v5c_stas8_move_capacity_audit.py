from __future__ import annotations

import pandas as pd

from mlbotnav.stas5_v5c_stas8_move_capacity_audit import (
    _dense_thresholds,
    _future_window,
    _live_context_decision,
    _past_metrics,
    _soft_capacity_v2_decision,
    _teacher_metrics,
    _threshold_hit_metrics,
)


def test_dense_thresholds_contract() -> None:
    values = _dense_thresholds()
    assert values[0] == 0.4
    assert values[-1] == 10.0
    assert 1.2 in values
    assert 5.0 in values
    assert 5.1 not in values
    assert len(values) == len(set(values))


def test_teacher_threshold_hit_metrics_no_future_before_entry() -> None:
    entry_ts = pd.Timestamp("2026-03-21T10:00:00Z")
    candles = pd.DataFrame(
        {
            "open_time_utc": pd.to_datetime(
                [
                    "2026-03-21T09:59:00Z",
                    "2026-03-21T10:01:00Z",
                    "2026-03-21T10:02:00Z",
                    "2026-03-21T10:03:00Z",
                ],
                utc=True,
            ),
            "open": [100.0, 100.0, 100.4, 100.8],
            "high": [100.1, 100.5, 101.0, 101.3],
            "low": [99.9, 99.7, 100.0, 100.5],
            "close": [100.0, 100.4, 100.8, 101.2],
            "volume": [1.0, 1.0, 1.0, 1.0],
        }
    )
    window = _future_window(candles, entry_ts, 5)
    assert window["open_time_utc"].min() > entry_ts
    metrics = _threshold_hit_metrics(window, entry_ts, 100.0, 1.2)
    assert metrics["hit_y"] == 1
    assert metrics["time_to_min"] == 3.0
    assert metrics["mae_before_pct"] == 0.3


def test_live_context_blocks_dead_move_and_allows_rebound() -> None:
    base_row = pd.Series(
        {
            "cs_range_60m_pct": 0.3,
            "cs_range_120m_pct": 0.5,
            "cs_return_60m_pct": -0.1,
            "cs_return_120m_pct": -0.2,
            "bb20_dead_move_score": 0.9,
        }
    )
    dead = _live_context_decision(base_row, {})
    assert dead["STAS8_LIVE_ACTION"] == "WAIT_NO_MOVE"

    rebound_row = pd.Series(
        {
            "cs_range_60m_pct": 1.2,
            "cs_range_120m_pct": 1.8,
            "cs_return_60m_pct": 0.2,
            "cs_return_120m_pct": 0.5,
            "cs_bounce_from_recent_low_pct": 0.8,
            "fcs_grounding_confirmed_score": 0.7,
            "fcs_retest_after_knife_score": 0.7,
            "bb20_rebound_from_low_score": 0.7,
        }
    )
    past = {"stas8_past_120m_wave_turns": 3, "stas8_past_60m_up_leg_after_low_pct": 0.7, "stas8_past_60m_down_leg_after_high_pct": 0.5}
    rebound = _live_context_decision(rebound_row, past)
    assert rebound["STAS8_LIVE_ACTION"] == "ALLOW_ENTRY_SEARCH"
    assert rebound["STAS8_LIVE_REBOUND_PROTECTED"] == 1


def test_soft_capacity_v2_blocks_down_only_and_protects_rebound() -> None:
    down_only = {
        "ENTRY_ML_LIVE_DECISION_BEFORE_STAS8": "ENTER",
        "STAS8_LIVE_ACTION": "BLOCK_DOWN_CHANNEL",
        "STAS8_LIVE_REASON_TAGS": "DOWN_CHANNEL|SHORT_PRESSURE|WEAK_BOUNCE_IN_SHORT",
        "STAS8_LIVE_MOVE_SCORE": 0.20,
        "STAS8_LIVE_RISK_SCORE": 0.88,
        "STAS8_LIVE_EDGE_SCORE": 0.10,
        "STAS8_LIVE_RANGE_60M_PCT": 0.50,
        "STAS8_LIVE_RANGE_120M_PCT": 0.90,
        "STAS8_LIVE_RANGE_240M_PCT": 1.20,
        "STAS8_LIVE_RET_60M_PCT": -0.80,
        "STAS8_LIVE_RET_120M_PCT": -1.20,
        "STAS8_LIVE_RET_240M_PCT": -1.70,
        "STAS8_LIVE_WAVE_TURNS_120M": 1,
        "STAS8_LIVE_BOUNCE_FROM_LOW_PCT": 0.18,
        "STAS8_LIVE_UP_LEG_AFTER_LOW_PCT": 0.12,
        "STAS8_LIVE_DOWN_LEG_AFTER_HIGH_PCT": 1.15,
        "STAS8_LIVE_REBOUND_PROTECTED": 0,
        "STAS8_LIVE_NO_MOVE_FLAG": 0,
        "STAS8_LIVE_DOWN_CHANNEL_FLAG": 1,
        "STAS8_LIVE_HIGH_VOL_DANGER_FLAG": 0,
    }
    blocked = _soft_capacity_v2_decision(down_only, "balanced")
    assert blocked["LIVE_DECISION"] == "SKIP"
    assert blocked["MARKER_LABEL"] == "RISK BAD"
    assert blocked["HARD_BLOCK_FLAG"] == 1

    rebound = dict(down_only)
    rebound.update(
        {
            "STAS8_LIVE_ACTION": "ALLOW_ENTRY_SEARCH",
            "STAS8_LIVE_REASON_TAGS": "MOVE_RANGE_SEEN|REBOUND_FROM_LOW|RETEST_OR_BASE|REBOUND_PROTECTED",
            "STAS8_LIVE_MOVE_SCORE": 0.62,
            "STAS8_LIVE_RISK_SCORE": 0.52,
            "STAS8_LIVE_EDGE_SCORE": 0.58,
            "STAS8_LIVE_RANGE_60M_PCT": 1.20,
            "STAS8_LIVE_RANGE_120M_PCT": 1.75,
            "STAS8_LIVE_RET_60M_PCT": 0.25,
            "STAS8_LIVE_RET_120M_PCT": -0.20,
            "STAS8_LIVE_WAVE_TURNS_120M": 3,
            "STAS8_LIVE_BOUNCE_FROM_LOW_PCT": 0.70,
            "STAS8_LIVE_UP_LEG_AFTER_LOW_PCT": 0.65,
            "STAS8_LIVE_REBOUND_PROTECTED": 1,
            "STAS8_LIVE_DOWN_CHANNEL_FLAG": 0,
        }
    )
    protected = _soft_capacity_v2_decision(rebound, "balanced")
    assert protected["LIVE_DECISION"] == "ENTER"
    assert protected["MARKER_LABEL"] == "GOOD"
    assert protected["PROTECT_FLAG"] == 1

    watch_rebound = dict(rebound)
    watch_rebound["ENTRY_ML_LIVE_DECISION_BEFORE_STAS8"] = "WATCH"
    watch_protected = _soft_capacity_v2_decision(watch_rebound, "balanced")
    assert watch_protected["LIVE_DECISION"] == "WATCH"
    assert watch_protected["MARKER_LABEL"] == "NONE"


def test_soft_capacity_v2_never_promotes_skip_to_enter() -> None:
    row = {
        "ENTRY_ML_LIVE_DECISION_BEFORE_STAS8": "SKIP",
        "STAS8_LIVE_ACTION": "ALLOW_ENTRY_SEARCH",
        "STAS8_LIVE_REASON_TAGS": "MOVE_RANGE_SEEN|REBOUND_FROM_LOW|RETEST_OR_BASE|REBOUND_PROTECTED",
        "STAS8_LIVE_MOVE_SCORE": 0.80,
        "STAS8_LIVE_RISK_SCORE": 0.20,
        "STAS8_LIVE_EDGE_SCORE": 0.72,
        "STAS8_LIVE_RANGE_60M_PCT": 1.30,
        "STAS8_LIVE_RANGE_120M_PCT": 2.10,
        "STAS8_LIVE_RANGE_240M_PCT": 2.60,
        "STAS8_LIVE_RET_60M_PCT": 0.20,
        "STAS8_LIVE_RET_120M_PCT": 0.40,
        "STAS8_LIVE_RET_240M_PCT": 0.80,
        "STAS8_LIVE_WAVE_TURNS_120M": 4,
        "STAS8_LIVE_BOUNCE_FROM_LOW_PCT": 0.80,
        "STAS8_LIVE_UP_LEG_AFTER_LOW_PCT": 0.80,
        "STAS8_LIVE_DOWN_LEG_AFTER_HIGH_PCT": 0.50,
        "STAS8_LIVE_REBOUND_PROTECTED": 1,
        "STAS8_LIVE_NO_MOVE_FLAG": 0,
        "STAS8_LIVE_DOWN_CHANNEL_FLAG": 0,
        "STAS8_LIVE_HIGH_VOL_DANGER_FLAG": 0,
        "hit_1p2_y": 1,
        "mae_before_1p2_pct": 0.30,
        "time_to_1p2_min": 40.0,
    }
    decision = _soft_capacity_v2_decision(row, "wide")
    assert decision["LIVE_DECISION"] == "SKIP"
    assert decision["REVIEW_DECISION"] == "RECALL_WATCH"
    assert decision["MARKER_LABEL"] == "NONE"
    assert decision["RECALL_WATCH_AUDIT_Y"] == 1


def test_teacher_metrics_sets_key_hit_columns() -> None:
    entry_ts = pd.Timestamp("2026-03-21T10:00:00Z")
    row = pd.Series(
        {
            "day": "2026-03-21",
            "candidate_id": "LA001",
            "record_id": "r1",
            "entry_time_utc": "2026-03-21T10:00:00Z",
            "entry_ts": entry_ts,
            "entry_price_5bps": 100.0,
        }
    )
    candles = pd.DataFrame(
        {
            "open_time_utc": pd.date_range("2026-03-21T10:01:00Z", periods=5, freq="min"),
            "open": [100.0, 100.2, 100.8, 101.2, 101.4],
            "high": [100.3, 100.9, 101.1, 101.25, 101.6],
            "low": [99.9, 100.0, 100.4, 100.9, 101.0],
            "close": [100.2, 100.8, 101.0, 101.2, 101.5],
            "volume": [1.0, 1.0, 1.0, 1.0, 1.0],
        }
    )
    teacher, grid = _teacher_metrics(row, candles, [1.1, 1.2, 1.5])
    assert teacher["hit_1p1_y"] == 1
    assert teacher["hit_1p2_y"] == 1
    assert teacher["hit_1p5_y"] == 1
    assert len(grid) == 3
