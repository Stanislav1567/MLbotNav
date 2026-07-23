from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import (
    PROJECT_ROOT,
    compact_day,
    ensure_parent,
    forbidden_feature_matches,
    load_manifest_feature_columns,
    normalize_day,
    normalize_ts,
    rel,
    utc_now,
    write_json,
)


STATUS = "PASS_NO_TRAINING_PHASE_STATE_REASON_READY"
SYMBOL = "SOLUSDT"
TIMEFRAME = "1m"

TARGET_COLUMNS = [
    "entry_y",
    "entry_y_class",
    "phase_y",
    "phase_y_code",
    "state_y",
    "state_y_code",
    "reason_y",
    "reason_y_code",
    "reason_y_family",
    "entry_label",
    "entry_reason_primary",
    "entry_reason_secondary",
    "market_phase_primary",
    "market_phase_secondary",
    "phase_label_status",
    "train_label_binary",
    "train_target_good",
    "train_target_bad_or_no_trade",
    "train_use_default",
    "review_status",
    "phase_segment_id",
    "phase_segment_label",
    "phase_y_source",
    "state_y_source",
    "reason_y_source",
    "targets_are_features",
]

PHASES = [
    {
        "phase_segment_id": "S01",
        "phase_y": "P1_ASIA_EARLY_STRUCTURE",
        "phase_y_code": 1,
        "phase_segment_label": "ASIA_EARLY_APPROVED_IDS",
        "state_y_default": "AUTO_SESSION_STRUCTURE",
        "start_utc": "00:00",
        "end_utc": "06:00",
        "direction_code": 0,
        "direction_label": "AUTO_SESSION",
        "teacher_logic": "USER_APPROVED_GOOD_IDS: coarse session segment until manual structure is drawn.",
    },
    {
        "phase_segment_id": "S02",
        "phase_y": "P2_MORNING_STRUCTURE",
        "phase_y_code": 2,
        "phase_segment_label": "MORNING_APPROVED_IDS",
        "state_y_default": "AUTO_SESSION_STRUCTURE",
        "start_utc": "06:00",
        "end_utc": "12:00",
        "direction_code": 0,
        "direction_label": "AUTO_SESSION",
        "teacher_logic": "USER_APPROVED_GOOD_IDS: coarse session segment until manual structure is drawn.",
    },
    {
        "phase_segment_id": "S03",
        "phase_y": "P3_MIDDAY_STRUCTURE",
        "phase_y_code": 3,
        "phase_segment_label": "MIDDAY_APPROVED_IDS",
        "state_y_default": "AUTO_SESSION_STRUCTURE",
        "start_utc": "12:00",
        "end_utc": "16:00",
        "direction_code": 0,
        "direction_label": "AUTO_SESSION",
        "teacher_logic": "USER_APPROVED_GOOD_IDS: coarse session segment until manual structure is drawn.",
    },
    {
        "phase_segment_id": "S04",
        "phase_y": "P4_NY_STRUCTURE",
        "phase_y_code": 4,
        "phase_segment_label": "NY_APPROVED_IDS",
        "state_y_default": "AUTO_SESSION_STRUCTURE",
        "start_utc": "16:00",
        "end_utc": "20:00",
        "direction_code": 0,
        "direction_label": "AUTO_SESSION",
        "teacher_logic": "USER_APPROVED_GOOD_IDS: coarse session segment until manual structure is drawn.",
    },
    {
        "phase_segment_id": "S05",
        "phase_y": "P5_LATE_STRUCTURE",
        "phase_y_code": 5,
        "phase_segment_label": "LATE_APPROVED_IDS",
        "state_y_default": "AUTO_SESSION_STRUCTURE",
        "start_utc": "20:00",
        "end_utc": "23:59",
        "direction_code": 0,
        "direction_label": "AUTO_SESSION",
        "teacher_logic": "USER_APPROVED_GOOD_IDS: coarse session segment until manual structure is drawn.",
    },
]

STATE_CODES = {
    "USER_APPROVED_GOOD_ENTRY_ZONE": 1,
    "BAD_NEAR_APPROVED_NOT_SELECTED": 2,
    "NO_TRADE_NOT_USER_SELECTED": 3,
}

REASON_CODES = {
    "GOOD_USER_APPROVED_ENTRY": 1,
    "BAD_NOT_USER_SELECTED_WORSE_THAN_APPROVED": 2,
    "NO_TRADE_NOT_USER_SELECTED": 3,
}


def _parse_good_ids(raw: list[str]) -> list[str]:
    text = ",".join(str(item) for item in raw)
    parts = [part.strip().upper() for part in re.split(r"[\s,;]+", text) if part.strip()]
    out: list[str] = []
    for item in parts:
        if re.fullmatch(r"\d+", item):
            item = f"LA{int(item):03d}"
        elif re.fullmatch(r"LA\d+", item):
            item = "LA" + str(int(item[2:])).zfill(3)
        if item not in out:
            out.append(item)
    return out


def _latest_full274_run(day: str) -> Path:
    compact = compact_day(day)
    runs_dir = PROJECT_ROOT / "STAS5_ML_CORE" / "runs"
    matches = sorted(
        runs_dir.glob(f"full274_feature_collect_{compact}*"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not matches:
        raise FileNotFoundError(f"FULL274 run not found for {day}: {runs_dir}")
    return matches[0]


def _default_paths(day: str) -> dict[str, Path]:
    compact = compact_day(day)
    base = PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5" / "market_passports" / compact
    prefix = f"STAS5_V5_MARKET_PASSPORT_{compact}"
    return {
        "base": base,
        "ledger": base / f"{prefix}_ENTRY_PHASE_STATE_REASON_LEDGER_USER_APPROVED_V2.csv",
        "ml_ready": base / f"{prefix}_ML_READY_274F_ENTRY_PHASE_STATE_REASON_TARGETS_V2.csv",
        "allowlist": base / f"{prefix}_FEATURE_ALLOWLIST_274_ENTRY_PHASE_STATE_REASON_V2.json",
        "guard": base / f"{prefix}_PHASE_STATE_REASON_GUARD_V2.json",
        "summary": base / f"{prefix}_PHASE_STATE_REASON_SUMMARY_V2.csv",
        "phase_segments": base / f"{prefix}_PHASE_SEGMENTS_USER_APPROVED_V1.csv",
        "market_structure": base / f"{prefix}_MARKET_STRUCTURE_NUMERIC_V1.csv",
        "schema": base / "TRAINING_SCHEMA_ENTRY_PHASE_STATE_REASON_RU.md",
        "readme": base / "README_RU.md",
        "open_first": base / "00_OPEN_FIRST_RU.md",
    }


def _path_from_summary(run_dir: Path, key: str) -> str:
    summary_path = run_dir / "STAS5_FULL274_FEATURE_COLLECT_SUMMARY.json"
    if not summary_path.exists():
        return ""
    payload = json.loads(summary_path.read_text(encoding="utf-8-sig"))
    value = str(payload.get(key, "") or "")
    if not value:
        return ""
    path = Path(value)
    if path.is_absolute():
        return str(path)
    return str((PROJECT_ROOT / path).resolve())


def _phase_for_time(entry_time: Any) -> dict[str, Any]:
    ts = pd.Timestamp(entry_time)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    minute = ts.hour * 60 + ts.minute
    for phase in PHASES:
        start_h, start_m = [int(item) for item in phase["start_utc"].split(":")]
        end_h, end_m = [int(item) for item in phase["end_utc"].split(":")]
        start = start_h * 60 + start_m
        end = end_h * 60 + end_m
        if start <= minute <= end:
            return phase
    return PHASES[-1]


def _phase_time(day: str, hhmm: str) -> pd.Timestamp:
    return pd.Timestamp(f"{day} {hhmm}:00", tz="UTC")


def _load_ohlcv(day: str, frame: pd.DataFrame) -> tuple[Path, pd.DataFrame | None]:
    for column in ["v2_combo_source_ohlcv", "source_ohlcv"]:
        if column in frame.columns:
            values = frame[column].dropna().astype(str)
            if not values.empty and values.iloc[0]:
                path = PROJECT_ROOT / values.iloc[0]
                if path.exists():
                    return path, pd.read_csv(path, encoding="utf-8-sig")
    path = PROJECT_ROOT / f"data/core/bybit_ohlcv/dt={day}/tf={TIMEFRAME}/symbol={SYMBOL}/part-final.csv"
    if path.exists():
        return path, pd.read_csv(path, encoding="utf-8-sig")
    return path, None


def _segment_stats(day: str, ohlcv: pd.DataFrame | None, candidates: pd.DataFrame, phase: dict[str, Any]) -> dict[str, Any]:
    start_ts = _phase_time(day, phase["start_utc"])
    end_ts = _phase_time(day, phase["end_utc"])
    if ohlcv is not None and "open_time_utc" in ohlcv.columns:
        o = ohlcv.copy()
        o["open_time_utc"] = pd.to_datetime(o["open_time_utc"], utc=True)
        seg = o[(o["open_time_utc"] >= start_ts) & (o["open_time_utc"] <= end_ts)]
        if not seg.empty:
            open_ = float(seg["open"].iloc[0])
            close = float(seg["close"].iloc[-1])
            high = float(seg["high"].max())
            low = float(seg["low"].min())
            volume = float(seg["volume"].sum()) if "volume" in seg.columns else 0.0
            base = close if close else 1.0
            return {
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
                "range_pct": (high - low) / base * 100.0,
                "move_pct": (close / open_ - 1.0) * 100.0 if open_ else 0.0,
            }
    seg_c = candidates[
        (pd.to_datetime(candidates["entry_time_utc"], utc=True) >= start_ts)
        & (pd.to_datetime(candidates["entry_time_utc"], utc=True) <= end_ts)
    ]
    if seg_c.empty:
        return {"open": 0.0, "high": 0.0, "low": 0.0, "close": 0.0, "volume": 0.0, "range_pct": 0.0, "move_pct": 0.0}
    prices = pd.to_numeric(seg_c["entry_price_5bps"], errors="coerce").dropna()
    if prices.empty:
        return {"open": 0.0, "high": 0.0, "low": 0.0, "close": 0.0, "volume": 0.0, "range_pct": 0.0, "move_pct": 0.0}
    open_ = float(prices.iloc[0])
    close = float(prices.iloc[-1])
    high = float(prices.max())
    low = float(prices.min())
    return {
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": 0.0,
        "range_pct": (high - low) / (close if close else 1.0) * 100.0,
        "move_pct": (close / open_ - 1.0) * 100.0 if open_ else 0.0,
    }


def _nearest_good_minutes(row: pd.Series, good_times: list[pd.Timestamp]) -> float:
    if not good_times:
        return 9999.0
    entry = pd.Timestamp(row["entry_time_utc"])
    if entry.tzinfo is None:
        entry = entry.tz_localize("UTC")
    diffs = [abs((entry - ts).total_seconds()) / 60.0 for ts in good_times]
    return float(min(diffs))


def _build_targets(
    *,
    day: str,
    full: pd.DataFrame,
    good_ids: list[str],
    source_screenshot: str,
    source_original_csv: str,
    source_ohlcv: str,
) -> pd.DataFrame:
    out = full.copy()
    out["candidate_id"] = out["candidate_id"].astype(str).str.upper()
    good_set = set(good_ids)
    good_times = []
    for value in out.loc[out["candidate_id"].isin(good_set), "entry_time_utc"]:
        ts = pd.Timestamp(value)
        if ts.tzinfo is None:
            ts = ts.tz_localize("UTC")
        good_times.append(ts.tz_convert("UTC"))
    phase_rows = [_phase_for_time(value) for value in out["entry_time_utc"]]
    out["phase_y"] = [row["phase_y"] for row in phase_rows]
    out["phase_y_code"] = [row["phase_y_code"] for row in phase_rows]
    out["phase_segment_id"] = [row["phase_segment_id"] for row in phase_rows]
    out["phase_segment_label"] = [row["phase_segment_label"] for row in phase_rows]
    out["market_phase_primary"] = out["phase_y"]
    out["market_phase_secondary"] = "AUTO_COARSE_SESSION_SEGMENT_FROM_USER_APPROVED_GOOD_IDS"

    is_good = out["candidate_id"].isin(good_set)
    near_good = out.apply(lambda row: _nearest_good_minutes(row, good_times), axis=1) <= 45.0
    out["entry_y"] = is_good.astype(int)
    out["entry_y_class"] = is_good.map({True: "GOOD_ENTRY", False: "BAD_ENTRY"})
    out["state_y"] = "NO_TRADE_NOT_USER_SELECTED"
    out.loc[near_good & ~is_good, "state_y"] = "BAD_NEAR_APPROVED_NOT_SELECTED"
    out.loc[is_good, "state_y"] = "USER_APPROVED_GOOD_ENTRY_ZONE"
    out["state_y_code"] = out["state_y"].map(STATE_CODES).astype(int)
    out["reason_y"] = "NO_TRADE_NOT_USER_SELECTED"
    out.loc[near_good & ~is_good, "reason_y"] = "BAD_NOT_USER_SELECTED_WORSE_THAN_APPROVED"
    out.loc[is_good, "reason_y"] = "GOOD_USER_APPROVED_ENTRY"
    out["reason_y_code"] = out["reason_y"].map(REASON_CODES).astype(int)
    out["reason_y_family"] = "NO_TRADE"
    out.loc[out["entry_y"].eq(0), "reason_y_family"] = "BAD"
    out.loc[is_good, "reason_y_family"] = "GOOD"
    out["entry_label"] = "NO_TRADE_ZONE"
    out.loc[near_good & ~is_good, "entry_label"] = "BAD_IN_GROUP"
    out.loc[is_good, "entry_label"] = "GOOD_APPROVED"
    out["entry_reason_primary"] = out["reason_y"]
    out["entry_reason_secondary"] = "USER_APPROVED_GOOD_IDS_AUTO_NEGATIVE"
    out.loc[is_good, "entry_reason_secondary"] = "USER_APPROVED_PRIMARY_ENTRY"
    out["is_good_entry"] = out["entry_y"]
    out["is_bad_entry"] = (1 - out["entry_y"]).astype(int)
    out["review_status"] = f"USER_APPROVED_{compact_day(day)}_GOOD_IDS_NO_TRAINING"
    out["phase_y_source"] = "USER_APPROVED_GOOD_IDS_AUTO_SESSION_TEACHER_NOT_FEATURE"
    out["state_y_source"] = "USER_APPROVED_GOOD_IDS_AUTO_SESSION_TEACHER_NOT_FEATURE"
    out["reason_y_source"] = "USER_APPROVED_GOOD_IDS_AUTO_SESSION_TEACHER_NOT_FEATURE"
    out["targets_are_features"] = 0
    out["phase_label_status"] = "USER_APPROVED_GOOD_IDS_AUTO_COARSE_PHASE"
    out["train_label_binary"] = out["entry_y"]
    out["train_target_good"] = out["entry_y"]
    out["train_target_bad_or_no_trade"] = (1 - out["entry_y"]).astype(int)
    out["train_use_default"] = is_good.map({True: "POSITIVE_AFTER_DATASET_APPROVAL", False: "NEGATIVE_AFTER_DATASET_APPROVAL"})
    out["source_screenshot"] = source_screenshot
    out["source_original_csv"] = source_original_csv
    out["source_ohlcv"] = source_ohlcv
    out["notes"] = "Пользователь утвердил GOOD ids для дня; остальные кандидаты считаются хуже и идут как negative/no-trade."
    return out


def _make_ledger(ml: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "day",
        "symbol",
        "timeframe",
        "candidate_id",
        "record_id",
        "entry_time_utc",
        "entry_price_5bps",
        "anchor_low_price",
        "suggested_type",
        "phase_y",
        "phase_y_code",
        "phase_segment_id",
        "phase_segment_label",
        "market_phase_primary",
        "market_phase_secondary",
        "state_y",
        "state_y_code",
        "entry_y",
        "entry_y_class",
        "reason_y",
        "reason_y_code",
        "reason_y_family",
        "entry_label",
        "entry_reason_primary",
        "entry_reason_secondary",
        "is_good_entry",
        "is_bad_entry",
        "review_status",
        "phase_y_source",
        "state_y_source",
        "reason_y_source",
        "targets_are_features",
        "phase_label_status",
        "train_use_default",
        "source_screenshot",
        "source_original_csv",
        "source_ohlcv",
        "pre_15m_phase",
        "pre_30m_phase",
        "pre_60m_phase",
        "stas4_v2_combo_short_pressure_score",
        "stas4_v2_combo_rsi14",
        "stas4_v2_combo_macd_hist",
        "stas4_v2_combo_stoch_k14",
        "stas4_v2_volume_z20",
        "notes",
    ]
    for column in ["symbol", "timeframe"]:
        if column not in ml.columns:
            ml[column] = SYMBOL if column == "symbol" else TIMEFRAME
    return ml[[column for column in columns if column in ml.columns]].copy()


def _make_phase_segments(day: str, ml: pd.DataFrame, ohlcv: pd.DataFrame | None) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for phase in PHASES:
        start = _phase_time(day, phase["start_utc"])
        end = _phase_time(day, phase["end_utc"])
        seg_ml = ml[(pd.to_datetime(ml["entry_time_utc"], utc=True) >= start) & (pd.to_datetime(ml["entry_time_utc"], utc=True) <= end)]
        stats = _segment_stats(day, ohlcv, ml, phase)
        good_ids = seg_ml.loc[seg_ml["entry_y"].eq(1), "candidate_id"].tolist()
        rows.append(
            {
                "day": day,
                "symbol": SYMBOL,
                "timeframe": TIMEFRAME,
                "phase_segment_id": phase["phase_segment_id"],
                "phase_segment_label": phase["phase_segment_label"],
                "state_y_default": phase["state_y_default"],
                "start_utc": phase["start_utc"],
                "end_utc": phase["end_utc"],
                "direction_code": phase["direction_code"],
                "direction_label": phase["direction_label"],
                "teacher_logic": phase["teacher_logic"],
                **stats,
                "candidates": int(len(seg_ml)),
                "good_approved": int(seg_ml["entry_y"].sum()),
                "bad_in_group": int(seg_ml["entry_label"].eq("BAD_IN_GROUP").sum()),
                "no_trade_zone": int(seg_ml["entry_label"].eq("NO_TRADE_ZONE").sum()),
                "approved_good_ids": ",".join(good_ids),
                "state_target_source": "user_good_ids_auto_session_teacher_not_feature",
            }
        )
    return pd.DataFrame(rows)


def _make_market_structure(day: str, phase_segments: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in phase_segments.iterrows():
        low = float(row["low"])
        high = float(row["high"])
        width = max(high - low, 0.0)
        rows.append(
            {
                "day": day,
                "symbol": SYMBOL,
                "timeframe": TIMEFRAME,
                "phase": row["phase_segment_label"],
                "phase_code": int(str(row["phase_segment_id"])[1:]),
                "start_utc": row["start_utc"],
                "end_utc": row["end_utc"],
                "direction_code": row["direction_code"],
                "direction_label": row["direction_label"],
                "manual_support_low": low,
                "manual_support_high": low + width * 0.22,
                "manual_resistance_low": high - width * 0.22,
                "manual_resistance_high": high,
                "manual_low_zone_label": "auto_segment_low_zone_from_ohlcv",
                "manual_high_zone_label": "auto_segment_high_zone_from_ohlcv",
                "approved_good_ids": row["approved_good_ids"],
                "negative_logic": "not_user_selected_is_worse_or_no_trade",
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "range_pct": row["range_pct"],
                "move_pct": row["move_pct"],
                "candidates": row["candidates"],
                "good_approved": row["good_approved"],
                "bad_in_group": row["bad_in_group"],
                "no_trade": row["no_trade_zone"],
            }
        )
    return pd.DataFrame(rows)


def _make_summary(ml: pd.DataFrame) -> pd.DataFrame:
    groups = []
    for column in ["entry_label", "phase_y", "state_y", "reason_y"]:
        counts = ml[column].value_counts(dropna=False).sort_index()
        for label, count in counts.items():
            groups.append({"metric": column, "label": str(label), "count": int(count)})
    return pd.DataFrame(groups)


def _write_schema(path: Path, day: str, good_ids: list[str], feature_count: int) -> None:
    text = f"""# STAS5 V5 Training Schema Entry/Phase/State/Reason {day}

Статус: `NO_TRAINING`.

Этот файл описывает approved-passport слой дня `{day}`.

## X

Входные признаки модели берутся только из allowlist:

```text
274 старых causal признака из FULL274
```

Позже команда-лестница добавляет live-safe `cs_*` и `fcs_*`, которые считаются только из свечей до `entry_time_utc`.

## y

Ручной список пользователя является учителем:

```text
GOOD ids: {", ".join(good_ids)}
feature_count: {feature_count}
```

`entry_y`, `phase_y`, `state_y`, `reason_y` являются target-ответами, а не прямыми live-признаками.

## Запрет

Нельзя добавлять в `X` future/postfact/hit_/TP/Stas3/exit/старые ML score/decision, а также ручные phase/state/reason targets.

Обучение этим builder'ом не запускается.
"""
    ensure_parent(path)
    path.write_text(text, encoding="utf-8")


def _write_readme(paths: dict[str, Path], day: str, good_ids: list[str], guard: dict[str, Any]) -> None:
    compact = compact_day(day)
    text = f"""# STAS5 V5 Market Passport Package {day}

Статус: `{guard["status"]}`.

Открывать первым:

```text
00_OPEN_FIRST_RU.md
```

## Что утверждено

Пользовательские GOOD-входы:

```text
{", ".join(good_ids)}
```

Остальные кандидаты дня идут как отрицательные примеры: `BAD_IN_GROUP` рядом с утвержденными входами или `NO_TRADE_ZONE` вне близкой зоны.

## Главные файлы

```text
STAS5_V5_MARKET_PASSPORT_{compact}_ML_READY_274F_ENTRY_PHASE_STATE_REASON_TARGETS_V2.csv
STAS5_V5_MARKET_PASSPORT_{compact}_ML_READY_274F_PLUS_CAUSAL_STRUCTURE_TARGETS_V1.csv
STAS5_V5_MARKET_PASSPORT_{compact}_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv
STAS5_V5_MARKET_PASSPORT_{compact}_FULL_CAUSAL_STRUCTURE_GUARD_V1.json
DAY_MARKET_PASSPORT_{compact}_FULL_CAUSAL_STRUCTURE_MAP_V1.png
```

## Правило

Ручной approved-passport слой дает target `y`. Прямые признаки `X` для модели должны идти через allowlist и causal builders.
Обучение и forward этим пакетом не запускались.
"""
    paths["readme"].write_text(text, encoding="utf-8")
    paths["open_first"].write_text(text, encoding="utf-8")


def build_approved_passport(
    *,
    day: str,
    good_ids: list[str],
    full274_run_dir: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    day = normalize_day(day)
    compact = compact_day(day)
    run_dir = full274_run_dir or _latest_full274_run(day)
    full_csv = run_dir / f"STAS5_FULL274_FEATURE_SNAPSHOT_{compact}.csv"
    manifest = run_dir / f"STAS5_FULL274_FEATURE_SNAPSHOT_{compact}.manifest.json"
    if not full_csv.exists():
        raise FileNotFoundError(f"FULL274 CSV not found: {full_csv}")
    if not manifest.exists():
        raise FileNotFoundError(f"FULL274 manifest not found: {manifest}")

    feature_columns = load_manifest_feature_columns(manifest)
    full = pd.read_csv(full_csv, encoding="utf-8-sig")
    full["day"] = full["day"].map(normalize_day)
    full["candidate_id"] = full["candidate_id"].astype(str).str.upper()
    good_ids = _parse_good_ids(good_ids)
    missing_good = sorted(set(good_ids) - set(full["candidate_id"]))
    if missing_good:
        raise ValueError(f"GOOD ids not found in FULL274 {day}: {missing_good}")
    missing_features = [column for column in feature_columns if column not in full.columns]
    if missing_features:
        raise ValueError(f"Feature columns missing from FULL274 {day}: {missing_features[:20]}")

    paths = _default_paths(day)
    if output_dir is not None:
        for key, path in list(paths.items()):
            if key != "base":
                paths[key] = output_dir / path.name
        paths["base"] = output_dir
    paths["base"].mkdir(parents=True, exist_ok=True)

    source_screenshot = _path_from_summary(run_dir, "graph_png")
    source_original_csv = str(full_csv.resolve())
    ohlcv_path, ohlcv = _load_ohlcv(day, full)
    source_ohlcv = str(ohlcv_path.resolve())
    ml = _build_targets(
        day=day,
        full=full,
        good_ids=good_ids,
        source_screenshot=source_screenshot,
        source_original_csv=source_original_csv,
        source_ohlcv=source_ohlcv,
    )
    if "symbol" not in ml.columns:
        ml["symbol"] = SYMBOL
    if "timeframe" not in ml.columns:
        ml["timeframe"] = TIMEFRAME

    metadata_columns = [column for column in ml.columns if column not in feature_columns and column not in TARGET_COLUMNS]
    ordered_columns = metadata_columns + [column for column in TARGET_COLUMNS if column in ml.columns] + feature_columns
    ml_ready = ml[ordered_columns].copy()
    ledger = _make_ledger(ml)
    phase_segments = _make_phase_segments(day, ml, ohlcv)
    market_structure = _make_market_structure(day, phase_segments)
    summary = _make_summary(ml)

    for path, frame in [
        (paths["ledger"], ledger),
        (paths["ml_ready"], ml_ready),
        (paths["phase_segments"], phase_segments),
        (paths["market_structure"], market_structure),
        (paths["summary"], summary),
    ]:
        ensure_parent(path)
        frame.to_csv(path, index=False, encoding="utf-8-sig")

    forbidden = forbidden_feature_matches(feature_columns)
    target_hits = [column for column in feature_columns if column in set(TARGET_COLUMNS)]
    allowlist = {
        "status": "PASS",
        "day": day,
        "feature_count": len(feature_columns),
        "feature_columns": feature_columns,
        "source_manifest": rel(manifest),
        "source_full274_csv": rel(full_csv),
        "forbidden_feature_columns_detected": forbidden,
        "targets_not_in_features": not target_hits,
        "rule": {
            "manual_targets_are_y_not_x": True,
            "training_started": False,
            "forward_started": False,
        },
    }
    write_json(paths["allowlist"], allowlist)

    entry_counts = {str(key): int(value) for key, value in ml["entry_y"].value_counts().sort_index().to_dict().items()}
    checks = [
        {"check": "rows_match", "status": "PASS" if len(ml_ready) == len(full) == len(ledger) else "FAIL", "details": {"full274_rows": len(full), "ml_rows": len(ml_ready), "ledger_rows": len(ledger)}},
        {"check": "feature_count_274", "status": "PASS" if len(feature_columns) == 274 else "FAIL", "details": {"feature_count": len(feature_columns)}},
        {"check": "good_ids_match", "status": "PASS" if not missing_good else "FAIL", "details": {"actual_good": sorted(ml.loc[ml["entry_y"].eq(1), "candidate_id"].tolist()), "expected_good": sorted(good_ids), "missing_good": missing_good}},
        {"check": "entry_y_counts", "status": "PASS" if entry_counts.get("1", 0) == len(good_ids) else "FAIL", "details": {"entry_y_counts": entry_counts}},
        {"check": "phase_y_5_labels", "status": "PASS" if ml["phase_y"].nunique() == 5 else "FAIL", "details": {"phase_y_counts": {str(key): int(value) for key, value in ml["phase_y"].value_counts().sort_index().to_dict().items()}}},
        {"check": "state_reason_non_empty", "status": "PASS" if int(ml["state_y"].eq("").sum() + ml["reason_y"].eq("").sum()) == 0 else "FAIL", "details": {"missing_state": int(ml["state_y"].eq("").sum()), "missing_reason": int(ml["reason_y"].eq("").sum())}},
        {"check": "forbidden_features_absent", "status": "PASS" if not forbidden else "FAIL", "details": {"forbidden_features": forbidden}},
        {"check": "targets_not_in_features", "status": "PASS" if not target_hits else "FAIL", "details": {"target_hits": target_hits}},
    ]
    status = STATUS if all(item["status"] == "PASS" for item in checks) else "FAIL_APPROVED_PASSPORT_GUARD"
    guard = {
        "status": status,
        "day": day,
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "created_utc": utc_now(),
        "rows": int(len(ml_ready)),
        "feature_count": int(len(feature_columns)),
        "entry_y_counts": entry_counts,
        "phase_y_counts": {str(key): int(value) for key, value in ml["phase_y"].value_counts().sort_index().to_dict().items()},
        "state_y_counts": {str(key): int(value) for key, value in ml["state_y"].value_counts().sort_index().to_dict().items()},
        "reason_y_counts": {str(key): int(value) for key, value in ml["reason_y"].value_counts().sort_index().to_dict().items()},
        "entry_label_counts": {str(key): int(value) for key, value in ml["entry_label"].value_counts().sort_index().to_dict().items()},
        "forbidden_feature_columns_detected": forbidden,
        "good_ids": good_ids,
        "source_full274_run": rel(run_dir),
        "outputs": {key: str(value.resolve()) for key, value in paths.items() if key != "base"},
        "checks": checks,
        "rule": {
            "teacher_may_use_full_historical_review_for_labels": True,
            "features_must_be_causal_at_entry_time": True,
            "entry_y_phase_y_state_y_reason_y_are_targets_not_features": True,
            "auto_phase_detail": "coarse_session_teacher_from_good_ids_until_manual_structure_is_drawn",
            "training_started": False,
            "forward_started": False,
        },
    }
    write_json(paths["guard"], guard)
    _write_schema(paths["schema"], day, good_ids, len(feature_columns))
    _write_readme(paths, day, good_ids, guard)
    if status != STATUS:
        raise RuntimeError(f"approved passport guard failed for {day}: {paths['guard']}")
    return guard


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", required=True)
    parser.add_argument("--good-ids", nargs="+", required=True)
    parser.add_argument("--full274-run-dir", default="")
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()

    guard = build_approved_passport(
        day=args.day,
        good_ids=args.good_ids,
        full274_run_dir=Path(args.full274_run_dir) if args.full274_run_dir else None,
        output_dir=Path(args.output_dir) if args.output_dir else None,
    )
    print(json.dumps({"status": guard["status"], "day": guard["day"], "rows": guard["rows"], "feature_count": guard["feature_count"], "entry_y_counts": guard["entry_y_counts"], "good_ids": guard["good_ids"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
