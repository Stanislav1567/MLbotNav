from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from mlbotnav.stas5_common import (
    JOIN_KEYS,
    PROJECT_ROOT,
    STAS5_ARTIFACTS_DIR,
    forbidden_feature_matches,
    normalize_ts,
    read_csv,
    rel,
    utc_now,
    write_json,
)
from mlbotnav.stas5_feature_snapshot_builder import classify_feature_columns
from mlbotnav.stas5_v4_group_rank_dataset import (
    DEFAULT_FORWARD_15_20_PATH,
    DEFAULT_FORWARD_21_25_PATH,
    DEFAULT_OLD_SNAPSHOT_MANIFEST_PATH,
    DEFAULT_OLD_SNAPSHOT_PATH,
    DEFAULT_V4_GROUP_LEDGER_PATH,
    EXTRA_FORBIDDEN_FEATURE_PATTERNS,
    LEDGER_COLUMNS,
    V4_GROUP_AUDIT_COLUMNS,
    V4_GROUP_MODEL_FEATURE_COLUMNS,
    _assign_legacy_groups,
    _day_counts,
    _entry_ts,
    _merge_v4_review_ledger,
    _normalize_keys,
    _price,
    _rank_label_target,
    _winner_lists,
)


STATUS = "STAS5_V4L_LIVE_SAFE_TRAIN_DATASET_READY_20260501_20260525"
DEFAULT_V4L_ROOT = STAS5_ARTIFACTS_DIR / "v4l"
DEFAULT_V4L_FEATURE_DIR = DEFAULT_V4L_ROOT / "features"
DEFAULT_V4L_DATASET_PATH = DEFAULT_V4L_FEATURE_DIR / "STAS5_V4L_LIVE_SAFE_TRAIN_DATASET_20260501_20260525.csv"
DEFAULT_V4L_DATASET_MANIFEST_PATH = (
    DEFAULT_V4L_FEATURE_DIR / "STAS5_V4L_LIVE_SAFE_TRAIN_DATASET_20260501_20260525.manifest.json"
)

V4L_GROUP_FEATURE_COLUMNS = [
    "v4l_group_size_so_far",
    "v4l_group_age_min_so_far",
    "v4l_group_price_range_so_far_pct",
    "v4l_candidate_rank_by_price_so_far",
    "v4l_is_lowest_so_far",
    "v4l_distance_to_running_group_low_pct",
    "v4l_minutes_from_group_start",
    "v4l_minutes_since_running_low",
    "v4l_prior_candidate_better_low",
    "v4l_same_basin_duplicate_count_so_far",
    "v4l_running_lower_low_count",
    "v4l_running_retest_count",
    "v4l_running_bounce_from_low_pct",
    "v4l_running_drop_from_group_high_pct",
    "v4l_price_delta_to_best_so_far_pct",
]

V4L_FORBIDDEN_FEATURE_PATTERNS = [
    *EXTRA_FORBIDDEN_FEATURE_PATTERNS,
    r"^v4_group_",
    r"^v4_candidate_rank_by_price_in_group$",
    r"^v4_is_lowest_in_group$",
    r"^v4_distance_to_group_low_pct$",
    r"^v4_minutes_to_group_low",
    r"^v4_is_before_group_low$",
    r"^v4_is_after_group_low$",
    r"^v4_post_candidate_lower_low_exists$",
    r"^v4_same_basin_duplicate_count$",
    r"best_low",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def v4l_forbidden_feature_matches(columns: list[str]) -> dict[str, list[str]]:
    out = forbidden_feature_matches(columns)
    for column in columns:
        hits = [
            pattern
            for pattern in V4L_FORBIDDEN_FEATURE_PATTERNS
            if re.search(pattern, column, flags=re.IGNORECASE)
        ]
        if hits:
            out.setdefault(column, []).extend(hits)
    return out


def _safe_pct(numerator: float, denominator: float) -> float:
    if pd.isna(numerator) or pd.isna(denominator) or float(denominator) == 0.0:
        return 0.0
    return ((float(numerator) / float(denominator)) - 1.0) * 100.0


def _add_live_safe_group_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["entry_time_utc"] = out["entry_time_utc"].map(normalize_ts)
    out["entry_price_5bps"] = pd.to_numeric(out["entry_price_5bps"], errors="coerce")

    parts: list[pd.DataFrame] = []
    sort_columns = ["day", "group_id", "entry_time_utc", "record_id"]
    for _group_id, group in out.sort_values(sort_columns).groupby("group_id", sort=False, dropna=False):
        group = group.copy()
        prices = _price(group).astype(float)
        times = _entry_ts(group)
        start_ts = times.min()

        running_low = np.inf
        running_high = -np.inf
        running_low_ts = pd.NaT
        running_low_count = 0
        prefix_prices: list[float] = []
        feature_rows: dict[Any, dict[str, float | int]] = {}

        for position, idx in enumerate(group.index, start=1):
            price = float(prices.loc[idx]) if pd.notna(prices.loc[idx]) else np.nan
            ts = times.loc[idx]
            prior_low = running_low if np.isfinite(running_low) else np.nan

            if pd.notna(price):
                prefix_prices.append(price)
                if not np.isfinite(running_low) or price <= running_low:
                    running_low = price
                    running_low_ts = ts
                    running_low_count += 1
                if not np.isfinite(running_high) or price > running_high:
                    running_high = price

            running_low_value = running_low if np.isfinite(running_low) else price
            running_high_value = running_high if np.isfinite(running_high) else price
            rank_so_far = 1 + sum(1 for prefix_price in prefix_prices[:-1] if pd.notna(price) and prefix_price < price)
            group_age = (ts - start_ts).total_seconds() / 60.0 if pd.notna(ts) and pd.notna(start_ts) else 0.0
            minutes_since_low = (
                (ts - running_low_ts).total_seconds() / 60.0 if pd.notna(ts) and pd.notna(running_low_ts) else 0.0
            )
            basin_limit = running_low_value * 1.0015 if pd.notna(running_low_value) else np.nan
            same_basin_count = sum(1 for prefix_price in prefix_prices if pd.notna(basin_limit) and prefix_price <= basin_limit)
            retest_limit = running_low_value * 1.0015 if pd.notna(running_low_value) else np.nan
            retest_count = sum(1 for prefix_price in prefix_prices if pd.notna(retest_limit) and prefix_price <= retest_limit)

            feature_rows[idx] = {
                "v4l_group_size_so_far": int(position),
                "v4l_group_age_min_so_far": round(float(group_age), 6),
                "v4l_group_price_range_so_far_pct": round(_safe_pct(running_high_value, running_low_value), 6),
                "v4l_candidate_rank_by_price_so_far": int(rank_so_far),
                "v4l_is_lowest_so_far": int(pd.notna(price) and pd.notna(running_low_value) and price <= running_low_value),
                "v4l_distance_to_running_group_low_pct": round(_safe_pct(price, running_low_value), 6),
                "v4l_minutes_from_group_start": round(float(group_age), 6),
                "v4l_minutes_since_running_low": round(float(minutes_since_low), 6),
                "v4l_prior_candidate_better_low": int(pd.notna(prior_low) and pd.notna(price) and prior_low < price),
                "v4l_same_basin_duplicate_count_so_far": int(same_basin_count),
                "v4l_running_lower_low_count": int(running_low_count),
                "v4l_running_retest_count": int(retest_count),
                "v4l_running_bounce_from_low_pct": round(_safe_pct(price, running_low_value), 6),
                "v4l_running_drop_from_group_high_pct": round(_safe_pct(running_high_value, price), 6),
                "v4l_price_delta_to_best_so_far_pct": round(_safe_pct(price, running_low_value), 6),
            }

        features = pd.DataFrame.from_dict(feature_rows, orient="index")
        group = group.join(features, how="left")
        parts.append(group)

    result = pd.concat(parts, ignore_index=False).sort_values(["day", "entry_time_utc", "record_id"]).reset_index(drop=True)
    for column in V4L_GROUP_FEATURE_COLUMNS:
        result[column] = pd.to_numeric(result[column], errors="coerce").fillna(0.0)
    return result


def _prefix_invariance_check(dataset: pd.DataFrame, *, max_failures_to_keep: int = 10) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    checked = 0
    sorted_dataset = dataset.sort_values(["day", "group_id", "entry_time_utc", "record_id"]).copy()
    for _group_id, group in sorted_dataset.groupby("group_id", sort=False, dropna=False):
        for prefix_len in range(1, len(group) + 1):
            prefix = group.iloc[:prefix_len].drop(columns=V4L_GROUP_FEATURE_COLUMNS, errors="ignore")
            recomputed = _add_live_safe_group_features(prefix).iloc[-1]
            original = group.iloc[prefix_len - 1]
            checked += 1
            mismatched = []
            for column in V4L_GROUP_FEATURE_COLUMNS:
                lhs = pd.to_numeric(pd.Series([original[column]]), errors="coerce").iloc[0]
                rhs = pd.to_numeric(pd.Series([recomputed[column]]), errors="coerce").iloc[0]
                if not np.isclose(float(lhs), float(rhs), rtol=1e-9, atol=1e-9):
                    mismatched.append({"column": column, "full": float(lhs), "prefix": float(rhs)})
            if mismatched and len(failures) < max_failures_to_keep:
                failures.append(
                    {
                        "day": str(original["day"]),
                        "group_id": str(original["group_id"]),
                        "candidate_id": str(original["candidate_id"]),
                        "record_id": str(original["record_id"]),
                        "mismatched": mismatched,
                    }
                )
    return {"checked_rows": int(checked), "failure_count": int(len(failures)), "sample_failures": failures}


def _build_manifest(
    *,
    dataset: pd.DataFrame,
    feature_columns: list[str],
    numeric_columns: list[str],
    categorical_columns: list[str],
    old_manifest: dict[str, Any],
    review_join_checks: dict[str, Any],
    prefix_invariance: dict[str, Any],
    output_csv: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    forbidden = v4l_forbidden_feature_matches(feature_columns)
    groups = dataset.groupby("group_id", dropna=False)
    winner_counts = groups["is_group_winner"].apply(lambda s: int(pd.to_numeric(s, errors="coerce").fillna(0).sum()))
    labels_by_group = groups["rank_label"].apply(lambda s: set(s.astype(str)))
    no_trade_groups = [group for group, labels in labels_by_group.items() if labels == {"NO_TRADE_GROUP"}]
    no_trade_group_set = set(no_trade_groups)
    trade_groups = [group for group in labels_by_group.index if group not in no_trade_group_set]
    trade_groups_without_one_winner = {
        str(group): int(winner_counts.get(group, 0)) for group in trade_groups if int(winner_counts.get(group, 0)) != 1
    }
    no_trade_groups_with_winner = {
        str(group): int(winner_counts.get(group, 0)) for group in no_trade_groups if int(winner_counts.get(group, 0)) != 0
    }
    good_without_group = dataset[
        dataset["rank_label"].astype(str).isin(["BEST_GOOD", "GOOD_ALT"])
        & dataset["group_id"].astype(str).str.strip().eq("")
    ]
    bad_without_reason = dataset[
        dataset["rank_label"].astype(str).isin(["BAD_IN_GROUP", "NO_TRADE_GROUP"])
        & dataset["primary_reason_code"].astype(str).str.strip().eq("")
    ]
    missing_live_features = [column for column in V4L_GROUP_FEATURE_COLUMNS if column not in feature_columns]
    missing_features = [column for column in feature_columns if column not in dataset.columns]
    duplicate_keys = int(dataset.duplicated(JOIN_KEYS).sum())
    full_group_features_in_dataset = [
        column for column in V4_GROUP_MODEL_FEATURE_COLUMNS + V4_GROUP_AUDIT_COLUMNS if column in dataset.columns
    ]
    status_pass = (
        review_join_checks["missing_after_forward_join"] == 0
        and review_join_checks["ledger_duplicate_keys"] == 0
        and review_join_checks["forward_duplicate_keys"] == 0
        and duplicate_keys == 0
        and not forbidden
        and not trade_groups_without_one_winner
        and not no_trade_groups_with_winner
        and len(good_without_group) == 0
        and len(bad_without_reason) == 0
        and not missing_live_features
        and not missing_features
        and prefix_invariance.get("failure_count") == 0
        and not full_group_features_in_dataset
    )
    return {
        "status": "PASS" if status_pass else "FAIL",
        "pipeline_status": STATUS,
        "created_utc": utc_now(),
        "train_window": "2026-05-01..2026-05-25",
        "train_base_legacy_window": "2026-05-01..2026-05-14",
        "user_corrected_group_window": "2026-05-15..2026-05-25",
        "forward_eval_window_next": "2026-05-26..2026-05-30",
        "rows": int(len(dataset)),
        "source_counts": dataset["v4_train_source"].astype(str).value_counts().to_dict(),
        "day_counts": _day_counts(dataset),
        "rank_label_counts": dataset["rank_label"].astype(str).value_counts().to_dict(),
        "winner_count": int(pd.to_numeric(dataset["is_group_winner"], errors="coerce").fillna(0).sum()),
        "winner_lists_by_day": _winner_lists(dataset),
        "group_count": int(dataset["group_id"].nunique()),
        "trade_group_count": len(trade_groups),
        "no_trade_group_count": len(no_trade_groups),
        "feature_columns": feature_columns,
        "feature_count": len(feature_columns),
        "v2_context_feature_columns": old_manifest.get("feature_columns", []),
        "v2_context_feature_count": len(old_manifest.get("feature_columns", [])),
        "v4l_live_safe_group_feature_columns": V4L_GROUP_FEATURE_COLUMNS,
        "v4l_live_safe_group_feature_count": len(V4L_GROUP_FEATURE_COLUMNS),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "output_csv": rel(output_csv),
        "manifest_path": rel(manifest_path),
        "review_join_checks": review_join_checks,
        "prefix_invariance": prefix_invariance,
        "checks": {
            "duplicate_keys": duplicate_keys,
            "forbidden_feature_columns": forbidden,
            "trade_groups_without_exactly_one_winner": trade_groups_without_one_winner,
            "no_trade_groups_with_winner": no_trade_groups_with_winner,
            "good_without_group_id_rows": int(len(good_without_group)),
            "bad_without_reason_rows": int(len(bad_without_reason)),
            "missing_required_live_group_features": missing_live_features,
            "missing_feature_columns": missing_features,
            "full_group_or_audit_columns_present_in_dataset": full_group_features_in_dataset,
            "old_manifest_status": old_manifest.get("status"),
        },
        "guardrails": [
            "V4L_features_are_prefix_only_so_far_values",
            "full_group_low_full_group_rank_post_candidate_lower_low_are_forbidden_features",
            "prefix_invariance_must_pass_before_training",
            "15_25_user_corrected_group_ledger_join_must_match_738_of_738",
            "old_ml_keep_score_and_decision_are_forbidden_features",
            "postfact_future_tp_stas3_exit_columns_are_forbidden_features",
            "BEST_GOOD_is_the_only_positive_training_target",
            "GOOD_ALT_stays_context_but_not_group_winner",
        ],
    }


def build_v4l_live_safe_dataset(
    *,
    old_snapshot_path: Path = DEFAULT_OLD_SNAPSHOT_PATH,
    old_snapshot_manifest_path: Path = DEFAULT_OLD_SNAPSHOT_MANIFEST_PATH,
    group_ledger_path: Path = DEFAULT_V4_GROUP_LEDGER_PATH,
    forward_15_20_path: Path = DEFAULT_FORWARD_15_20_PATH,
    forward_21_25_path: Path = DEFAULT_FORWARD_21_25_PATH,
    output_csv: Path = DEFAULT_V4L_DATASET_PATH,
    manifest_path: Path = DEFAULT_V4L_DATASET_MANIFEST_PATH,
    strict: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    old_manifest = _load_json(old_snapshot_manifest_path)
    if strict and old_manifest.get("status") != "PASS":
        raise ValueError(f"old V2 snapshot manifest is not PASS: {old_manifest.get('status')}")

    v2_feature_columns = [str(column) for column in old_manifest["feature_columns"]]
    old_snapshot = read_csv(old_snapshot_path)
    old_rows = _assign_legacy_groups(old_snapshot)

    ledger = read_csv(group_ledger_path)
    forward_parts = [read_csv(forward_15_20_path), read_csv(forward_21_25_path)]
    forward_rows = pd.concat([frame for frame in forward_parts if not frame.empty], ignore_index=True)
    review_rows, review_join_checks = _merge_v4_review_ledger(ledger, forward_rows)

    for column in v2_feature_columns:
        if column not in old_rows.columns:
            old_rows[column] = pd.NA
        if column not in review_rows.columns:
            review_rows[column] = pd.NA

    needed_columns = list(dict.fromkeys(JOIN_KEYS + ["anchor_time_utc", "entry_time_utc", "entry_open_price", "entry_price_5bps"]))
    needed_columns += [column for column in LEDGER_COLUMNS if column in old_rows.columns or column in review_rows.columns]
    needed_columns += ["v4_train_source"]
    needed_columns += [column for column in ["human_label", "yellow_x", "yellow_x_conflict"] if column in old_rows.columns or column in review_rows.columns]
    needed_columns += v2_feature_columns
    for frame in [old_rows, review_rows]:
        for column in needed_columns:
            if column not in frame.columns:
                frame[column] = ""

    dataset = pd.concat([old_rows[needed_columns], review_rows[needed_columns]], ignore_index=True)
    dataset = _normalize_keys(dataset)
    dataset = _add_live_safe_group_features(dataset)
    dataset["target_v4_winner"] = dataset["rank_label"].map(_rank_label_target).astype(int)

    feature_columns = list(dict.fromkeys(v2_feature_columns + V4L_GROUP_FEATURE_COLUMNS))
    numeric_columns, categorical_columns, _boolean_columns = classify_feature_columns(dataset, feature_columns)
    prefix_invariance = _prefix_invariance_check(dataset)
    manifest = _build_manifest(
        dataset=dataset,
        feature_columns=feature_columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        old_manifest=old_manifest,
        review_join_checks=review_join_checks,
        prefix_invariance=prefix_invariance,
        output_csv=output_csv,
        manifest_path=manifest_path,
    )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(output_csv, index=False, encoding="utf-8-sig")
    write_json(manifest_path, manifest)
    if strict and manifest["status"] != "PASS":
        raise ValueError(f"STAS5 V4L live-safe dataset failed checks: {manifest['checks']}")
    return dataset, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build STAS5 V4L live-safe group-rank training dataset.")
    parser.add_argument("--old-snapshot-path", default=str(DEFAULT_OLD_SNAPSHOT_PATH))
    parser.add_argument("--old-snapshot-manifest-path", default=str(DEFAULT_OLD_SNAPSHOT_MANIFEST_PATH))
    parser.add_argument("--group-ledger-path", default=str(DEFAULT_V4_GROUP_LEDGER_PATH))
    parser.add_argument("--forward-15-20-path", default=str(DEFAULT_FORWARD_15_20_PATH))
    parser.add_argument("--forward-21-25-path", default=str(DEFAULT_FORWARD_21_25_PATH))
    parser.add_argument("--output-csv", default=str(DEFAULT_V4L_DATASET_PATH))
    parser.add_argument("--manifest-path", default=str(DEFAULT_V4L_DATASET_MANIFEST_PATH))
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()
    _dataset, manifest = build_v4l_live_safe_dataset(
        old_snapshot_path=Path(args.old_snapshot_path),
        old_snapshot_manifest_path=Path(args.old_snapshot_manifest_path),
        group_ledger_path=Path(args.group_ledger_path),
        forward_15_20_path=Path(args.forward_15_20_path),
        forward_21_25_path=Path(args.forward_21_25_path),
        output_csv=Path(args.output_csv),
        manifest_path=Path(args.manifest_path),
        strict=not args.no_strict,
    )
    print(
        {
            "status": manifest["status"],
            "rows": manifest["rows"],
            "winner_count": manifest["winner_count"],
            "feature_count": manifest["feature_count"],
            "live_safe_group_feature_count": manifest["v4l_live_safe_group_feature_count"],
            "prefix_invariance": manifest["prefix_invariance"],
            "output_csv": manifest["output_csv"],
        }
    )
    return 0 if manifest["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
