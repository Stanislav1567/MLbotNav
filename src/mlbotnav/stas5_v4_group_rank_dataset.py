from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import (
    JOIN_KEYS,
    PROJECT_ROOT,
    STAS5_ARTIFACTS_DIR,
    compact_day,
    forbidden_feature_matches,
    is_cut_label,
    is_keep_label,
    normalize_day,
    normalize_ts,
    read_csv,
    rel,
    utc_now,
    write_json,
)
from mlbotnav.stas5_feature_snapshot_builder import classify_feature_columns
from mlbotnav.stas5_v2_feature_snapshot_builder import DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH


STATUS = "STAS5_V4_GROUP_RANK_TRAIN_DATASET_READY_20260501_20260525"
SYMBOL = "SOLUSDT"
TIMEFRAME = "1m"

DEFAULT_V4_ROOT = STAS5_ARTIFACTS_DIR / "v4"
DEFAULT_V4_FEATURE_DIR = DEFAULT_V4_ROOT / "features"
DEFAULT_V4_GROUP_LEDGER_PATH = DEFAULT_V4_ROOT / "group_rank_ledger" / "STAS5_V4_GROUP_RANK_LEDGER.csv"
DEFAULT_OLD_SNAPSHOT_PATH = STAS5_ARTIFACTS_DIR / "v2" / "features" / "stas5_v2_feature_snapshot_20260501_20260514_v0.csv"
DEFAULT_OLD_SNAPSHOT_MANIFEST_PATH = DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH
DEFAULT_FORWARD_15_20_PATH = (
    STAS5_ARTIFACTS_DIR
    / "v2"
    / "forward"
    / "runs"
    / "stas5_v2_full274_20260713_203703"
    / "STAS5_V2_FORWARD_ALL_PREDICTIONS_20260515_20260520.csv"
)
DEFAULT_FORWARD_21_25_PATH = (
    STAS5_ARTIFACTS_DIR
    / "v3"
    / "forward"
    / "runs"
    / "stas5_v3_wrapper_smoke2_20260714"
    / "STAS5_V3_FORWARD_ALL_PREDICTIONS_20260521_20260525.csv"
)
DEFAULT_V4_DATASET_PATH = DEFAULT_V4_FEATURE_DIR / "STAS5_V4_GROUP_RANK_TRAIN_DATASET_20260501_20260525.csv"
DEFAULT_V4_DATASET_MANIFEST_PATH = (
    DEFAULT_V4_FEATURE_DIR / "STAS5_V4_GROUP_RANK_TRAIN_DATASET_20260501_20260525.manifest.json"
)

V4_GROUP_MODEL_FEATURE_COLUMNS = [
    "v4_group_size",
    "v4_group_duration_min",
    "v4_group_price_range_pct",
    "v4_candidate_rank_by_price_in_group",
    "v4_is_lowest_in_group",
    "v4_distance_to_group_low_pct",
    "v4_minutes_from_group_start",
    "v4_minutes_to_group_low_abs",
    "v4_is_before_group_low",
    "v4_is_after_group_low",
    "v4_prior_candidate_better_low",
    "v4_post_candidate_lower_low_exists",
    "v4_same_basin_duplicate_count",
]

V4_GROUP_AUDIT_COLUMNS = [
    "v4_distance_to_best_low_pct_label_audit",
    "v4_minutes_to_best_low_label_audit",
]

LEDGER_COLUMNS = [
    "symbol",
    "timeframe",
    "group_id",
    "rank_label",
    "is_group_winner",
    "primary_reason_code",
    "secondary_reason_codes",
    "label_status",
    "source_review_file",
    "notes",
]

EXTRA_FORBIDDEN_FEATURE_PATTERNS = [
    r"ML_KEEP_SCORE",
    r"ML_DECISION",
    r"postfact",
    r"current_ml",
    r"train_fit_ml",
    r"oof_ml",
    r"V3_DECISION",
    r"V3_KEEP",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["day"] = out["day"].map(normalize_day)
    out["candidate_id"] = out["candidate_id"].astype(str)
    out["record_id"] = out["record_id"].astype(str)
    for column in ["entry_time_utc", "anchor_time_utc"]:
        if column in out.columns:
            out[column] = out[column].map(normalize_ts)
    return out


def _extra_forbidden_feature_matches(columns: list[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for column in columns:
        hits = [pattern for pattern in EXTRA_FORBIDDEN_FEATURE_PATTERNS if re.search(pattern, column, flags=re.IGNORECASE)]
        if hits:
            out[column] = hits
    return out


def _status_is_true(value: Any) -> bool:
    text = str(value).strip().lower()
    return text in {"1", "1.0", "true", "yes", "y"}


def _price(df: pd.DataFrame) -> pd.Series:
    return pd.to_numeric(df.get("entry_price_5bps", df.get("entry_open_price")), errors="coerce")


def _entry_ts(df: pd.DataFrame) -> pd.Series:
    return pd.to_datetime(df["entry_time_utc"], utc=True, errors="coerce")


def _assign_legacy_groups(old_snapshot: pd.DataFrame, *, max_gap_min: int = 60) -> pd.DataFrame:
    out = _normalize_keys(old_snapshot)
    out["symbol"] = SYMBOL
    out["timeframe"] = TIMEFRAME
    out["v4_train_source"] = "legacy_train_20260501_20260514"
    out["source_review_file"] = "STAS5_V2_FEATURE_SNAPSHOT_LEGACY_20260501_20260514"
    out["secondary_reason_codes"] = ""
    out["notes"] = "legacy 01..14 converted to V4 pseudo-groups from KEEP/CUT labels"
    out["label_status"] = out.get("label_status", "DRAFT")

    group_ids: list[str] = []
    for day, day_rows in out.sort_values(["day", "entry_time_utc", "record_id"]).groupby("day", sort=True):
        last_ts: pd.Timestamp | None = None
        group_idx = 0
        for idx, row in day_rows.iterrows():
            ts = pd.Timestamp(row["entry_time_utc"])
            if ts.tzinfo is None:
                ts = ts.tz_localize("UTC")
            if last_ts is None or (ts - last_ts).total_seconds() / 60.0 > max_gap_min:
                group_idx += 1
            group_ids.append((idx, f"V4LEG_{compact_day(str(day))}_{group_idx:03d}"))
            last_ts = ts
    group_map = dict(group_ids)
    out["group_id"] = out.index.map(group_map)

    out["rank_label"] = "BAD_IN_GROUP"
    out["is_group_winner"] = 0
    out["primary_reason_code"] = "BAD_LEGACY_CUT_IN_GROUP"

    for group_id, group in out.groupby("group_id", sort=False):
        keep_mask = group["human_label"].map(is_keep_label)
        if not bool(keep_mask.any()):
            out.loc[group.index, "rank_label"] = "NO_TRADE_GROUP"
            out.loc[group.index, "primary_reason_code"] = "BAD_LEGACY_NO_TRADE_GROUP"
            continue
        keep_rows = group[keep_mask].copy()
        keep_rows["_entry_price"] = _price(keep_rows)
        winner_idx = keep_rows.sort_values(["_entry_price", "entry_time_utc", "record_id"]).index[0]
        out.loc[group.index, "rank_label"] = "BAD_IN_GROUP"
        out.loc[group.index, "primary_reason_code"] = "BAD_LEGACY_CUT_IN_GROUP"
        out.loc[keep_rows.index, "rank_label"] = "GOOD_ALT"
        out.loc[keep_rows.index, "primary_reason_code"] = "GOOD_LEGACY_KEEP_ALT"
        out.loc[winner_idx, "rank_label"] = "BEST_GOOD"
        out.loc[winner_idx, "is_group_winner"] = 1
        out.loc[winner_idx, "primary_reason_code"] = "GOOD_LEGACY_KEEP_LOWEST_IN_GROUP"
    return out


def _merge_v4_review_ledger(ledger: pd.DataFrame, forward_rows: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    ledger = _normalize_keys(ledger)
    forward_rows = _normalize_keys(forward_rows)
    merged = ledger.merge(forward_rows, on=JOIN_KEYS, how="left", suffixes=("_ledger", ""), indicator=True)
    missing = merged[merged["_merge"] != "both"].copy()
    merged = merged.drop(columns=["_merge"])

    for column in ["entry_time_utc", "entry_price_5bps"]:
        ledger_column = f"{column}_ledger"
        if ledger_column in merged.columns:
            if column not in merged.columns:
                merged[column] = merged[ledger_column]
            else:
                use_ledger = merged[ledger_column].astype(str).str.strip() != ""
                merged.loc[use_ledger, column] = merged.loc[use_ledger, ledger_column]
    merged["v4_train_source"] = "review_forward_20260515_20260525_user_corrected"
    checks = {
        "ledger_rows": int(len(ledger)),
        "forward_rows": int(len(forward_rows)),
        "joined_rows": int(len(merged)),
        "missing_after_forward_join": int(len(missing)),
        "missing_after_forward_join_by_day": missing["day"].value_counts().sort_index().to_dict() if len(missing) else {},
        "ledger_duplicate_keys": int(ledger.duplicated(JOIN_KEYS).sum()),
        "forward_duplicate_keys": int(forward_rows.duplicated(JOIN_KEYS).sum()),
    }
    return merged, checks


def _add_group_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["entry_time_utc"] = out["entry_time_utc"].map(normalize_ts)
    out["entry_price_5bps"] = pd.to_numeric(out["entry_price_5bps"], errors="coerce")
    out["is_group_winner"] = out.get("is_group_winner", 0).map(lambda value: 1 if _status_is_true(value) else 0)

    parts: list[pd.DataFrame] = []
    for group_id, group in out.groupby("group_id", sort=False, dropna=False):
        group = group.copy()
        prices = _price(group)
        times = _entry_ts(group)
        group_size = int(len(group))
        low_price = float(prices.min()) if prices.notna().any() else float("nan")
        high_price = float(prices.max()) if prices.notna().any() else float("nan")
        low_idx = prices.sort_values(kind="mergesort").index[0] if prices.notna().any() else group.index[0]
        low_ts = times.loc[low_idx]
        start_ts = times.min()
        end_ts = times.max()
        duration_min = (end_ts - start_ts).total_seconds() / 60.0 if pd.notna(start_ts) and pd.notna(end_ts) else 0.0
        price_range_pct = ((high_price / low_price) - 1.0) * 100.0 if low_price and pd.notna(low_price) else 0.0
        rank_by_price = prices.rank(method="first", ascending=True)

        winner_rows = group[group["is_group_winner"].astype(int) == 1]
        best_price = float(_price(winner_rows).min()) if len(winner_rows) else float("nan")
        best_ts = _entry_ts(winner_rows).iloc[0] if len(winner_rows) else pd.NaT

        group["v4_group_size"] = group_size
        group["v4_group_duration_min"] = round(float(duration_min), 6)
        group["v4_group_price_range_pct"] = round(float(price_range_pct), 6)
        group["v4_candidate_rank_by_price_in_group"] = rank_by_price.astype(float)
        group["v4_is_lowest_in_group"] = (rank_by_price == 1).astype(int)
        group["v4_distance_to_group_low_pct"] = ((prices / low_price) - 1.0) * 100.0 if low_price else 0.0
        group["v4_minutes_from_group_start"] = (times - start_ts).dt.total_seconds() / 60.0
        group["v4_minutes_to_group_low_abs"] = (times - low_ts).dt.total_seconds().abs() / 60.0
        group["v4_is_before_group_low"] = (times < low_ts).astype(int)
        group["v4_is_after_group_low"] = (times > low_ts).astype(int)
        group["v4_prior_candidate_better_low"] = (prices.cummin().shift(1) < prices).fillna(False).astype(int)
        group["v4_post_candidate_lower_low_exists"] = (
            prices.iloc[::-1].cummin().iloc[::-1].shift(-1) < prices
        ).fillna(False).astype(int)
        group["v4_same_basin_duplicate_count"] = int((prices <= low_price * 1.0015).sum()) if low_price else 0
        group["v4_distance_to_best_low_pct_label_audit"] = ((prices / best_price) - 1.0) * 100.0 if best_price else pd.NA
        group["v4_minutes_to_best_low_label_audit"] = (
            (times - best_ts).dt.total_seconds() / 60.0 if pd.notna(best_ts) else pd.NA
        )
        parts.append(group)

    out = pd.concat(parts, ignore_index=False).sort_values(["day", "entry_time_utc", "record_id"]).reset_index(drop=True)
    for column in V4_GROUP_MODEL_FEATURE_COLUMNS + V4_GROUP_AUDIT_COLUMNS:
        if column in out:
            out[column] = pd.to_numeric(out[column], errors="coerce")
    return out


def _rank_label_target(label: Any) -> int:
    return 1 if str(label).strip().upper() == "BEST_GOOD" else 0


def _day_counts(df: pd.DataFrame) -> dict[str, int]:
    return {str(k): int(v) for k, v in df["day"].astype(str).value_counts().sort_index().items()}


def _winner_lists(df: pd.DataFrame) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    winners = df[df["is_group_winner"].astype(int) == 1]
    for day, rows in winners.sort_values(["day", "entry_time_utc", "candidate_id"]).groupby("day", sort=True):
        out[str(day)] = rows["candidate_id"].astype(str).tolist()
    return out


def _build_manifest(
    *,
    dataset: pd.DataFrame,
    feature_columns: list[str],
    numeric_columns: list[str],
    categorical_columns: list[str],
    old_manifest: dict[str, Any],
    review_join_checks: dict[str, Any],
    output_csv: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    forbidden = forbidden_feature_matches(feature_columns)
    forbidden.update(_extra_forbidden_feature_matches(feature_columns))

    groups = dataset.groupby("group_id", dropna=False)
    winner_counts = groups["is_group_winner"].apply(lambda s: int(pd.to_numeric(s, errors="coerce").fillna(0).sum()))
    labels_by_group = groups["rank_label"].apply(lambda s: set(s.astype(str)))
    no_trade_groups = [group for group, labels in labels_by_group.items() if labels == {"NO_TRADE_GROUP"}]
    trade_groups = [group for group in labels_by_group.index if group not in set(no_trade_groups)]
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
    required_group_missing = [column for column in V4_GROUP_MODEL_FEATURE_COLUMNS if column not in feature_columns]
    missing_features = [column for column in feature_columns if column not in dataset.columns]
    duplicate_keys = int(dataset.duplicated(JOIN_KEYS).sum())
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
        and not required_group_missing
        and not missing_features
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
        "v4_group_feature_columns": V4_GROUP_MODEL_FEATURE_COLUMNS,
        "v4_group_audit_columns_not_model_features": V4_GROUP_AUDIT_COLUMNS,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "output_csv": rel(output_csv),
        "manifest_path": rel(manifest_path),
        "review_join_checks": review_join_checks,
        "checks": {
            "duplicate_keys": duplicate_keys,
            "forbidden_feature_columns": forbidden,
            "trade_groups_without_exactly_one_winner": trade_groups_without_one_winner,
            "no_trade_groups_with_winner": no_trade_groups_with_winner,
            "good_without_group_id_rows": int(len(good_without_group)),
            "bad_without_reason_rows": int(len(bad_without_reason)),
            "missing_required_group_features": required_group_missing,
            "missing_feature_columns": missing_features,
            "old_manifest_status": old_manifest.get("status"),
        },
        "guardrails": [
            "15_25_user_corrected_group_ledger_join_must_match_738_of_738",
            "old_ml_keep_score_and_decision_are_forbidden_features",
            "postfact_future_tp_stas3_exit_columns_are_forbidden_features",
            "group_features_required_before_training",
            "BEST_GOOD_is_the_only_positive_training_target",
            "GOOD_ALT_stays_context_but_not_group_winner",
            "distance_to_best_low_and_minutes_to_best_low_are_audit_only_not_model_features",
        ],
    }


def build_v4_group_rank_dataset(
    *,
    old_snapshot_path: Path = DEFAULT_OLD_SNAPSHOT_PATH,
    old_snapshot_manifest_path: Path = DEFAULT_OLD_SNAPSHOT_MANIFEST_PATH,
    group_ledger_path: Path = DEFAULT_V4_GROUP_LEDGER_PATH,
    forward_15_20_path: Path = DEFAULT_FORWARD_15_20_PATH,
    forward_21_25_path: Path = DEFAULT_FORWARD_21_25_PATH,
    output_csv: Path = DEFAULT_V4_DATASET_PATH,
    manifest_path: Path = DEFAULT_V4_DATASET_MANIFEST_PATH,
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
    forward_nonempty = [frame for frame in forward_parts if not frame.empty]
    forward_rows = (
        pd.concat(forward_nonempty, ignore_index=True)
        if forward_nonempty
        else forward_parts[0].copy()
    )
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
    dataset = _add_group_features(dataset)
    dataset["target_v4_winner"] = dataset["rank_label"].map(_rank_label_target).astype(int)

    feature_columns = list(dict.fromkeys(v2_feature_columns + V4_GROUP_MODEL_FEATURE_COLUMNS))
    numeric_columns, categorical_columns, _boolean_columns = classify_feature_columns(dataset, feature_columns)
    manifest = _build_manifest(
        dataset=dataset,
        feature_columns=feature_columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        old_manifest=old_manifest,
        review_join_checks=review_join_checks,
        output_csv=output_csv,
        manifest_path=manifest_path,
    )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(output_csv, index=False, encoding="utf-8-sig")
    write_json(manifest_path, manifest)
    if strict and manifest["status"] != "PASS":
        raise ValueError(f"STAS5 V4 group-rank dataset failed checks: {manifest['checks']}")
    return dataset, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build STAS5 V4 group-rank training dataset.")
    parser.add_argument("--old-snapshot-path", default=str(DEFAULT_OLD_SNAPSHOT_PATH))
    parser.add_argument("--old-snapshot-manifest-path", default=str(DEFAULT_OLD_SNAPSHOT_MANIFEST_PATH))
    parser.add_argument("--group-ledger-path", default=str(DEFAULT_V4_GROUP_LEDGER_PATH))
    parser.add_argument("--forward-15-20-path", default=str(DEFAULT_FORWARD_15_20_PATH))
    parser.add_argument("--forward-21-25-path", default=str(DEFAULT_FORWARD_21_25_PATH))
    parser.add_argument("--output-csv", default=str(DEFAULT_V4_DATASET_PATH))
    parser.add_argument("--manifest-path", default=str(DEFAULT_V4_DATASET_MANIFEST_PATH))
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()
    _dataset, manifest = build_v4_group_rank_dataset(
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
            "review_join_checks": manifest["review_join_checks"],
            "output_csv": manifest["output_csv"],
        }
    )
    return 0 if manifest["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
