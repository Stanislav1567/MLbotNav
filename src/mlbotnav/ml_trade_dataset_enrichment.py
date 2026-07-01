from __future__ import annotations

import json
import hashlib
import math
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from mlbotnav.ml_trade_dataset_contract import RUN_CONTEXT_COLUMNS

PASSPORT_CONTEXT_EXPORT_COLUMNS = [
    "block_id",
    "passport_id",
    "action_id",
    "calibration_params_json",
    "entry_action_gate_columns",
]

TRADE_IDENTITY_COLUMNS = [
    "trade_id",
    "entry_signal_time_utc",
]

DURATION_LABEL_COLUMNS = [
    "bars_in_trade",
    "holding_seconds",
]

HIT_LABEL_COLUMNS = [
    "tp_hit",
    "sl_hit",
    "timeout_hit",
    "end_of_data_hit",
    "sl_ambiguous_hit",
]

MAE_MFE_COLUMNS = [
    "mae_pct",
    "mfe_pct",
]

HIT_LABELS_BY_EXIT_REASON = {
    "tp": ("true", "false", "false", "false", "false"),
    "sl": ("false", "true", "false", "false", "false"),
    "sl_ambiguous": ("false", "true", "false", "false", "true"),
    "timeout": ("false", "false", "true", "false", "false"),
    "end_of_data": ("false", "false", "false", "true", "false"),
    "manual_close": ("false", "false", "false", "false", "false"),
    "unknown": ("false", "false", "false", "false", "false"),
}


def add_run_context_columns(
    df: pd.DataFrame,
    *,
    run_id: str,
    symbol: str,
    timeframe: str,
    data_layer: str,
    train_start: str,
    train_end: str,
    test_start: str,
    test_end: str,
) -> pd.DataFrame:
    """Add Stage 2.1 run-level ML contract context to a trade table."""
    out = df.copy()
    values: dict[str, Any] = {
        "run_id": str(run_id),
        "symbol": str(symbol),
        "timeframe": str(timeframe),
        "data_layer": str(data_layer),
        "train_start": str(train_start),
        "train_end": str(train_end),
        "test_start": str(test_start),
        "test_end": str(test_end),
    }
    for col, value in values.items():
        out[col] = value

    ordered = [c for c in RUN_CONTEXT_COLUMNS if c in out.columns]
    ordered.extend([c for c in out.columns if c not in ordered])
    return out[ordered]


def _json_dumps_stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _load_passport_registry(project_root: Path, registry_rel_path: str) -> dict[str, Any]:
    path = project_root / registry_rel_path
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        return {}
    blocks = data.get("blocks")
    return blocks if isinstance(blocks, dict) else {}


def _normalize_str_list(values: Any) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        return [values]
    if isinstance(values, (list, tuple, set)):
        return [str(v) for v in values if str(v).strip()]
    return []


def _is_trade_side(value: Any) -> bool:
    try:
        return int(float(value)) != 0
    except (TypeError, ValueError):
        return False


def _timestamp_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text or text.lower() in {"nan", "nat", "none"}:
        return ""
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        return text
    return ts.isoformat()


def _parse_timestamp(value: Any) -> pd.Timestamp | None:
    text = str(value or "").strip()
    if not text or text.lower() in {"nan", "nat", "none"}:
        return None
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        return None
    return ts


def _infer_bar_seconds_from_frame(df: pd.DataFrame) -> float:
    if "open_time_utc" not in df.columns or len(df) < 2:
        return 0.0
    ts = pd.to_datetime(df["open_time_utc"], utc=True, errors="coerce").dropna().sort_values()
    if len(ts) < 2:
        return 0.0
    diffs = ts.diff().dropna().dt.total_seconds()
    if len(diffs) == 0:
        return 0.0
    return float(diffs.median())


def _parse_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def _trade_window(df: pd.DataFrame, entry_ts: pd.Timestamp | None, exit_ts: pd.Timestamp | None) -> pd.DataFrame:
    if "open_time_utc" not in df.columns or entry_ts is None or exit_ts is None:
        return df.iloc[0:0]
    open_ts = pd.to_datetime(df["open_time_utc"], utc=True, errors="coerce")
    mask = (open_ts >= entry_ts) & (open_ts <= exit_ts)
    window = df.loc[mask]
    if len(window) > 0:
        return window
    return df.iloc[0:0]


def _fallback_mae_mfe(row: pd.Series) -> tuple[float, float]:
    for col in ("gross_return_raw", "gross_return", "net_return"):
        ret = _parse_float(row.get(col))
        if ret is not None:
            return min(ret, 0.0), max(ret, 0.0)
    return 0.0, 0.0


def _calculate_mae_mfe_for_row(df: pd.DataFrame, row: pd.Series) -> tuple[float, float]:
    side = int(float(row.get("side")))
    entry_price = _parse_float(row.get("entry_price"))
    if entry_price is None or entry_price <= 0 or "high" not in df.columns or "low" not in df.columns:
        return _fallback_mae_mfe(row)

    window = _trade_window(df, _parse_timestamp(row.get("entry_time_utc")), _parse_timestamp(row.get("exit_time_utc")))
    if len(window) == 0:
        return _fallback_mae_mfe(row)

    lows = pd.to_numeric(window["low"], errors="coerce").dropna()
    highs = pd.to_numeric(window["high"], errors="coerce").dropna()
    if len(lows) == 0 or len(highs) == 0:
        return _fallback_mae_mfe(row)

    if side > 0:
        mae = min(float(lows.min()) / entry_price - 1.0, 0.0)
        mfe = max(float(highs.max()) / entry_price - 1.0, 0.0)
    else:
        mae = min(entry_price / float(highs.max()) - 1.0, 0.0)
        mfe = max(entry_price / float(lows.min()) - 1.0, 0.0)
    return float(mae), float(mfe)


def resolve_passport_context(
    *,
    project_root: Path,
    calibration_params: dict[str, Any] | None,
    entry_action_gate_columns: list[str] | None = None,
    registry_rel_path: str = "configs/calibration_action_passports.yaml",
) -> dict[str, str]:
    """Resolve passport ids from the active passport registry."""
    params = calibration_params or {}
    param_keys = {str(k) for k in params.keys()}
    gate_columns = set(_normalize_str_list(entry_action_gate_columns))
    blocks = _load_passport_registry(project_root, registry_rel_path)

    matches: list[tuple[int, str, str, str]] = []
    for block_id, block in blocks.items():
        if not isinstance(block, dict):
            continue
        passports = block.get("active_passports")
        if not isinstance(passports, dict):
            continue
        for passport_id, passport in passports.items():
            if not isinstance(passport, dict):
                continue
            action_id = str(passport.get("action_id") or "")
            runtime_columns = set(_normalize_str_list(passport.get("runtime_action_columns")))
            allowed_params = set(_normalize_str_list(passport.get("allowed_calibration_params")))
            score = 0
            if action_id and action_id in gate_columns:
                score += 100
            if gate_columns.intersection(runtime_columns):
                score += 90
            if param_keys.intersection(allowed_params):
                score += 50
            prefix = f"{passport_id}_"
            if any(k.startswith(prefix) for k in param_keys):
                score += 20
            if score > 0:
                matches.append((score, str(block_id), str(passport_id), action_id))

    if not matches:
        return {"block_id": "", "passport_id": "", "action_id": ""}

    matches.sort(key=lambda item: item[0], reverse=True)
    _, block_id, passport_id, action_id = matches[0]
    return {"block_id": block_id, "passport_id": passport_id, "action_id": action_id}


def add_passport_context_columns(
    df: pd.DataFrame,
    *,
    project_root: Path,
    calibration_params: dict[str, Any] | None,
    entry_action_gate_columns: list[str] | None = None,
    block_id: str | None = None,
    passport_id: str | None = None,
    action_id: str | None = None,
) -> pd.DataFrame:
    """Add Stage 2.2 passport ML contract context to a trade table."""
    resolved = resolve_passport_context(
        project_root=project_root,
        calibration_params=calibration_params,
        entry_action_gate_columns=entry_action_gate_columns,
    )
    final_block_id = str(block_id or resolved.get("block_id") or "")
    final_passport_id = str(passport_id or resolved.get("passport_id") or "")
    final_action_id = str(action_id or resolved.get("action_id") or "")
    gate_columns = _normalize_str_list(entry_action_gate_columns)
    if not gate_columns and final_action_id:
        gate_columns = [final_action_id]

    out = df.copy()
    values: dict[str, Any] = {
        "block_id": final_block_id,
        "passport_id": final_passport_id,
        "action_id": final_action_id,
        "calibration_params_json": _json_dumps_stable(calibration_params or {}),
        "entry_action_gate_columns": _json_dumps_stable(gate_columns),
    }
    for col, value in values.items():
        out[col] = value

    ordered: list[str] = []
    for col in RUN_CONTEXT_COLUMNS + PASSPORT_CONTEXT_EXPORT_COLUMNS:
        if col in out.columns and col not in ordered:
            ordered.append(col)
    ordered.extend([c for c in out.columns if c not in ordered])
    return out[ordered]


def add_trade_identity_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add Stage 2.3 stable trade identity columns to a trade table."""
    out = df.copy()
    if "trade_id" not in out.columns:
        out["trade_id"] = ""
    if "entry_signal_time_utc" not in out.columns:
        out["entry_signal_time_utc"] = ""

    for idx, row in out.iterrows():
        if not _is_trade_side(row.get("side")):
            out.at[idx, "trade_id"] = ""
            out.at[idx, "entry_signal_time_utc"] = ""
            continue

        signal_time = _timestamp_text(row.get("entry_signal_time_utc"))
        if not signal_time:
            signal_time = _timestamp_text(row.get("open_time_utc"))
        out.at[idx, "entry_signal_time_utc"] = signal_time

        existing_trade_id = str(row.get("trade_id") or "").strip()
        if existing_trade_id:
            continue

        run_id = str(row.get("run_id") or "").strip()
        action_id = str(row.get("action_id") or "").strip()
        entry_time = _timestamp_text(row.get("entry_time_utc"))
        side = str(int(float(row.get("side"))))
        fingerprint = "|".join([run_id, action_id, signal_time, entry_time, side, str(idx)])
        digest = hashlib.sha1(fingerprint.encode("utf-8")).hexdigest()[:16]
        out.at[idx, "trade_id"] = f"T{int(idx):06d}_{digest}"

    ordered: list[str] = []
    for col in RUN_CONTEXT_COLUMNS + PASSPORT_CONTEXT_EXPORT_COLUMNS + TRADE_IDENTITY_COLUMNS:
        if col in out.columns and col not in ordered:
            ordered.append(col)
    ordered.extend([c for c in out.columns if c not in ordered])
    return out[ordered]


def add_duration_label_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add Stage 2.4 trade duration labels to a trade table."""
    out = df.copy()
    if "bars_in_trade" not in out.columns:
        out["bars_in_trade"] = pd.Series([""] * len(out), index=out.index, dtype=object)
    else:
        out["bars_in_trade"] = out["bars_in_trade"].astype(object)
    if "holding_seconds" not in out.columns:
        out["holding_seconds"] = pd.Series([""] * len(out), index=out.index, dtype=object)
    else:
        out["holding_seconds"] = out["holding_seconds"].astype(object)

    bar_seconds = _infer_bar_seconds_from_frame(out)
    for idx, row in out.iterrows():
        if not _is_trade_side(row.get("side")):
            out.at[idx, "bars_in_trade"] = ""
            out.at[idx, "holding_seconds"] = ""
            continue

        entry_ts = _parse_timestamp(row.get("entry_time_utc"))
        exit_ts = _parse_timestamp(row.get("exit_time_utc"))
        holding_seconds = None
        if entry_ts is not None and exit_ts is not None:
            holding_seconds = max(0.0, float((exit_ts - entry_ts).total_seconds()))
        else:
            fallback_seconds = row.get("time_to_target_sec")
            try:
                if fallback_seconds is not None and not pd.isna(fallback_seconds):
                    holding_seconds = max(0.0, float(fallback_seconds))
            except (TypeError, ValueError):
                holding_seconds = None

        bars_in_trade = None
        fallback_bars = row.get("time_to_target_bars")
        try:
            if fallback_bars is not None and not pd.isna(fallback_bars) and float(fallback_bars) > 0:
                bars_in_trade = int(math.ceil(float(fallback_bars)))
        except (TypeError, ValueError):
            bars_in_trade = None
        if bars_in_trade is None and holding_seconds is not None and bar_seconds > 0:
            bars_in_trade = max(1, int(math.ceil(holding_seconds / bar_seconds)))
        if bars_in_trade is None:
            bars_in_trade = 1

        out.at[idx, "bars_in_trade"] = int(bars_in_trade)
        out.at[idx, "holding_seconds"] = float(holding_seconds) if holding_seconds is not None else ""

    ordered: list[str] = []
    for col in RUN_CONTEXT_COLUMNS + PASSPORT_CONTEXT_EXPORT_COLUMNS + TRADE_IDENTITY_COLUMNS + DURATION_LABEL_COLUMNS:
        if col in out.columns and col not in ordered:
            ordered.append(col)
    ordered.extend([c for c in out.columns if c not in ordered])
    return out[ordered]


def add_hit_label_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add Stage 2.5 hit labels derived from exit_reason."""
    out = df.copy()
    for col in HIT_LABEL_COLUMNS:
        if col not in out.columns:
            out[col] = pd.Series([""] * len(out), index=out.index, dtype=object)
        else:
            out[col] = out[col].astype(object)

    for idx, row in out.iterrows():
        if not _is_trade_side(row.get("side")):
            for col in HIT_LABEL_COLUMNS:
                out.at[idx, col] = ""
            continue

        exit_reason = str(row.get("exit_reason") or "unknown").strip().lower() or "unknown"
        labels = HIT_LABELS_BY_EXIT_REASON.get(exit_reason, HIT_LABELS_BY_EXIT_REASON["unknown"])
        for col, value in zip(HIT_LABEL_COLUMNS, labels):
            out.at[idx, col] = value

    ordered: list[str] = []
    for col in (
        RUN_CONTEXT_COLUMNS
        + PASSPORT_CONTEXT_EXPORT_COLUMNS
        + TRADE_IDENTITY_COLUMNS
        + DURATION_LABEL_COLUMNS
        + HIT_LABEL_COLUMNS
    ):
        if col in out.columns and col not in ordered:
            ordered.append(col)
    ordered.extend([c for c in out.columns if c not in ordered])
    return out[ordered]


def add_mae_mfe_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add Stage 2.6 maximum adverse/favorable excursion labels."""
    out = df.copy()
    for col in MAE_MFE_COLUMNS:
        if col not in out.columns:
            out[col] = pd.Series([""] * len(out), index=out.index, dtype=object)
        else:
            out[col] = out[col].astype(object)

    for idx, row in out.iterrows():
        if not _is_trade_side(row.get("side")):
            for col in MAE_MFE_COLUMNS:
                out.at[idx, col] = ""
            continue

        mae, mfe = _calculate_mae_mfe_for_row(out, row)
        out.at[idx, "mae_pct"] = mae
        out.at[idx, "mfe_pct"] = mfe

    ordered: list[str] = []
    for col in (
        RUN_CONTEXT_COLUMNS
        + PASSPORT_CONTEXT_EXPORT_COLUMNS
        + TRADE_IDENTITY_COLUMNS
        + DURATION_LABEL_COLUMNS
        + HIT_LABEL_COLUMNS
        + MAE_MFE_COLUMNS
    ):
        if col in out.columns and col not in ordered:
            ordered.append(col)
    ordered.extend([c for c in out.columns if c not in ordered])
    return out[ordered]
