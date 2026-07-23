from __future__ import annotations

import pandas as pd

from mlbotnav.stas5_v5_forward_visual_review import STATUS_PASS, render_forward_visual_review


def test_forward_visual_review_creates_enter_arrow_pngs(tmp_path) -> None:
    day = "2026-02-28"
    run_dir = tmp_path / "forward_run"
    predictions_path = run_dir / "STAS5_V5_FORWARD_PREDICTIONS_20260228_20260228_V1.csv"
    predictions_path.parent.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "day": day,
                "candidate_id": "LA001",
                "record_id": "R1",
                "entry_time_utc": "2026-02-28T00:10:00Z",
                "entry_price_5bps": 100.2,
                "ENTRY_ML_LIVE_SCORE": 0.99,
                "ENTRY_ML_LIVE_DECISION": "ENTER",
            },
            {
                "day": day,
                "candidate_id": "LA002",
                "record_id": "R2",
                "entry_time_utc": "2026-02-28T00:20:00Z",
                "entry_price_5bps": 100.4,
                "ENTRY_ML_LIVE_SCORE": 0.50,
                "ENTRY_ML_LIVE_DECISION": "WATCH",
            },
        ]
    ).to_csv(predictions_path, index=False, encoding="utf-8-sig")

    def make_candles(start: pd.Timestamp, count: int) -> list[dict[str, object]]:
        candles = []
        for idx in range(count):
            ts = start + pd.Timedelta(minutes=idx)
            open_px = 100.0 + idx * 0.01
            close_px = open_px + (0.03 if idx % 2 == 0 else -0.02)
            candles.append(
                {
                    "open_time_utc": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "close_time_utc": (ts + pd.Timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "open": open_px,
                    "high": max(open_px, close_px) + 0.05,
                    "low": min(open_px, close_px) - 0.05,
                    "close": close_px,
                    "volume": 1000 + idx,
                }
            )
        return candles

    ohlcv_path = tmp_path / "data" / "core" / "bybit_ohlcv" / f"dt={day}" / "tf=1m" / "symbol=SOLUSDT" / "part-final.csv"
    ohlcv_path.parent.mkdir(parents=True)
    pd.DataFrame(make_candles(pd.Timestamp("2026-02-28T00:00:00Z"), 80)).to_csv(ohlcv_path, index=False)

    context_path = run_dir / "ohlcv_contexts" / "STAS5_V5C_OHLCV_CONTEXT_20260227_20260228_FROM_20260227_1200.csv"
    context_path.parent.mkdir(parents=True)
    context_candles = make_candles(pd.Timestamp("2026-02-27T22:00:00Z"), 200)
    for idx, row in enumerate(context_candles):
        open_px = 100.0 + idx * 0.01
        close_px = open_px + (0.03 if idx % 2 == 0 else -0.02)
        row["open"] = open_px
        row["high"] = max(open_px, close_px) + 0.05
        row["low"] = min(open_px, close_px) - 0.05
        row["close"] = close_px
    pd.DataFrame(context_candles).to_csv(context_path, index=False)

    manifest = render_forward_visual_review(
        forward_run_dir=run_dir,
        predictions_path=predictions_path,
        start_day=day,
        end_day=day,
        data_root=tmp_path,
    )

    assert manifest["status"] == STATUS_PASS
    assert manifest["png_count"] == 2
    day_output = manifest["day_outputs"][0]
    assert day_output["strength_strip_context_status"] == "CONTINUOUS_CONTEXT_OHLCV"
    assert day_output["strength_strip_context_rows"] == 200
    assert day_output["strength_strip_hour_rows"] > 0
    assert day_output["strength_strip_gap_rows_filtered"] >= 0
    assert day_output["strength_strip_gap_rows_rendered"] == 0
    assert day_output["strength_strip_tail_covered_to_data_end"] is True
    assert day_output["strength_strip_available_end_utc"]
    assert day_output["strength_strip_last_wave_end_utc"]
    assert day_output["strength_strip_label_pct_basis"] == "cumulative_from_true_wave_start"
    assert day_output["strength_strip_cumulative_pct_rows"] == day_output["strength_strip_macro_wave_rows"]
    assert set(day_output["strength_strip_macro_wave_directions"]).issubset({"LONG", "SHORT"})
    assert "strength_strip_is_visual_review_only_not_model_feature" in manifest["guardrails"]
    assert "strength_strip_active_wave_extends_to_available_candle_end" in manifest["guardrails"]
    overview = run_dir / "visual_review" / "20260228" / "STAS5_V5_FORWARD_VISUAL_REVIEW_20260228_ENTER_ARROWS.png"
    closeups = run_dir / "visual_review" / "20260228" / "STAS5_V5_FORWARD_ENTER_CLOSEUPS_20260228.png"
    assert overview.exists()
    assert closeups.exists()
