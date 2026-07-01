from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from mlbotnav.postgres_runtime import ensure_postgres_schema, is_postgres_mode, pg_register_partition


def _append_row(path: Path, headers: list[str], row: list[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(headers)
        if row:
            w.writerow(row)


def _write_optional_parquet_from_csv(csv_path: Path, parquet_path: Path) -> None:
    try:
        df = pd.read_csv(csv_path)
        df.to_parquet(parquet_path, index=False)  # requires optional pyarrow/fastparquet
    except Exception:
        return


def register_partition(
    project_root: Path,
    *,
    layer: str,
    dataset: str,
    trade_date_utc: str,
    symbol: str,
    timeframe: str,
    file_path: Path,
    rows: int,
    run_id: str,
    status: str,
) -> None:
    if is_postgres_mode(project_root):
        pg_register_partition(
            project_root,
            {
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "layer": layer,
                "dataset": dataset,
                "trade_date_utc": trade_date_utc,
                "symbol": symbol,
                "timeframe": timeframe,
                "file_path": str(file_path),
                "rows": int(rows),
                "run_id": run_id,
                "status": status,
            },
        )
        return
    meta_dir = project_root / "data" / "meta"
    csv_path = meta_dir / "storage_partitions.csv"
    parquet_path = meta_dir / "storage_partitions.parquet"
    headers = [
        "created_at_utc",
        "layer",
        "dataset",
        "trade_date_utc",
        "symbol",
        "timeframe",
        "file_path",
        "rows",
        "run_id",
        "status",
    ]
    row = [
        datetime.now(timezone.utc).isoformat(),
        layer,
        dataset,
        trade_date_utc,
        symbol,
        timeframe,
        str(file_path),
        int(rows),
        run_id,
        status,
    ]
    _append_row(csv_path, headers, row)
    _write_optional_parquet_from_csv(csv_path, parquet_path)


def bootstrap_analytics_tables(project_root: Path) -> None:
    analytics_dir = project_root / "data" / "analytics"
    analytics_dir.mkdir(parents=True, exist_ok=True)

    _append_row(
        analytics_dir / "levels.csv",
        [
            "level_id",
            "symbol",
            "timeframe",
            "detected_at_utc",
            "level_price",
            "level_type",
            "strength_score",
            "touches_count",
            "valid_from_utc",
            "valid_to_utc",
            "run_id",
        ],
        [],
    )
    _append_row(
        analytics_dir / "pattern_events.csv",
        [
            "pattern_id",
            "symbol",
            "timeframe",
            "pattern_type",
            "direction",
            "start_time_utc",
            "end_time_utc",
            "confidence_score",
            "target_price",
            "stop_price",
            "invalidation_price",
            "run_id",
        ],
        [],
    )
    _append_row(
        analytics_dir / "signal_events.csv",
        [
            "signal_id",
            "symbol",
            "timeframe",
            "signal_time_utc",
            "side",
            "entry_price",
            "stop_price",
            "take_profit_price",
            "expected_move_pct",
            "tp_reach_prob",
            "decision",
            "reason_code",
            "run_id",
        ],
        [],
    )


def ensure_storage_layout(project_root: Path) -> None:
    if is_postgres_mode(project_root):
        ensure_postgres_schema(project_root)
    (project_root / "data" / "raw").mkdir(parents=True, exist_ok=True)
    (project_root / "data" / "core").mkdir(parents=True, exist_ok=True)
    (project_root / "data" / "analytics").mkdir(parents=True, exist_ok=True)
    (project_root / "data" / "dq").mkdir(parents=True, exist_ok=True)
    (project_root / "data" / "meta").mkdir(parents=True, exist_ok=True)
    bootstrap_analytics_tables(project_root)
