from __future__ import annotations

import pandas as pd

from mlbotnav.stas5_v5_continuous_ml import _thresholds_for_entry_decision_policy, build_continuous_ohlcv_context


def _write_ohlcv(root, day: str, start: str, minutes: int) -> None:
    path = root / "data" / "core" / "bybit_ohlcv" / f"dt={day}" / "tf=1m" / "symbol=SOLUSDT" / "part-final.csv"
    path.parent.mkdir(parents=True)
    rows = []
    ts0 = pd.Timestamp(start, tz="UTC")
    for idx in range(minutes):
        ts = ts0 + pd.Timedelta(minutes=idx)
        rows.append(
            {
                "open_time_utc": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "open": 100 + idx,
                "high": 101 + idx,
                "low": 99 + idx,
                "close": 100.5 + idx,
                "volume": 1000 + idx,
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8-sig")


def test_continuous_ohlcv_context_crosses_midnight(tmp_path) -> None:
    _write_ohlcv(tmp_path, "2026-02-27", "2026-02-27T23:58:00Z", 2)
    _write_ohlcv(tmp_path, "2026-02-28", "2026-02-28T00:00:00Z", 3)

    manifest = build_continuous_ohlcv_context(
        start_day="2026-02-27",
        end_day="2026-02-28",
        output_dir=tmp_path / "contexts",
        project_root=tmp_path,
    )

    context = pd.read_csv(tmp_path / manifest["outputs"]["context_csv"], encoding="utf-8-sig")
    assert manifest["status"].startswith("PASS")
    assert manifest["rows"] == 5
    assert context["open_time_utc"].iloc[0].startswith("2026-02-27")
    assert context["open_time_utc"].iloc[-1].startswith("2026-02-28")


def test_normal_entry_decision_policy_uses_train_oof_quantiles(tmp_path) -> None:
    oof_path = tmp_path / "train_oof.csv"
    pd.DataFrame({"ENTRY_BASELINE_OOF_SCORE": [idx / 100 for idx in range(101)]}).to_csv(
        oof_path,
        index=False,
        encoding="utf-8-sig",
    )
    thresholds = _thresholds_for_entry_decision_policy(
        train_manifest={"artifacts": {"train_oof_predictions": "train_oof.csv"}},
        selected_model_key="entry_baseline",
        selected_package={"thresholds": {"entry_enter_threshold": 0.99, "entry_watch_threshold": 0.84}},
        entry_decision_policy="normal",
        project_root=tmp_path,
    )

    assert thresholds["active_decision_policy"] == "train_oof_quantile_normal_no_forward_tuning"
    assert thresholds["source_score_column"] == "ENTRY_BASELINE_OOF_SCORE"
    assert thresholds["enter_quantile"] == 0.9
    assert thresholds["watch_quantile"] == 0.6
    assert thresholds["entry_enter_threshold"] == 0.9
    assert thresholds["entry_watch_threshold"] == 0.6
    assert thresholds["entry_watch_threshold"] < thresholds["entry_enter_threshold"]


def test_wide_review_entry_decision_policy_is_wider_than_normal(tmp_path) -> None:
    oof_path = tmp_path / "train_oof.csv"
    pd.DataFrame({"ENTRY_BASELINE_OOF_SCORE": [idx / 100 for idx in range(101)]}).to_csv(
        oof_path,
        index=False,
        encoding="utf-8-sig",
    )
    thresholds = _thresholds_for_entry_decision_policy(
        train_manifest={"artifacts": {"train_oof_predictions": "train_oof.csv"}},
        selected_model_key="entry_baseline",
        selected_package={"thresholds": {"entry_enter_threshold": 0.99, "entry_watch_threshold": 0.84}},
        entry_decision_policy="wide_review",
        project_root=tmp_path,
    )

    assert thresholds["active_decision_policy"] == "train_oof_quantile_wide_review_no_forward_tuning"
    assert thresholds["enter_quantile"] == 0.8
    assert thresholds["watch_quantile"] == 0.5
    assert thresholds["entry_enter_threshold"] == 0.8
    assert thresholds["entry_watch_threshold"] == 0.5
