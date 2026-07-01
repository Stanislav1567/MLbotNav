from __future__ import annotations

from pathlib import Path

import pandas as pd

from mlbotnav.postgres_runtime import (
    is_postgres_mode,
    pg_append_context_dq_report,
    pg_append_dq_report,
    pg_append_gap_events,
    pg_append_ingest_pair_status,
    pg_append_ingest_run,
    pg_get_watermark,
    pg_upsert_watermark,
)


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _write_csv(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def _project_root_from_data_root(data_root: Path) -> Path:
    return data_root.parents[1]


def append_ingest_run(meta_root: Path, row: dict) -> None:
    project_root = _project_root_from_data_root(meta_root)
    if is_postgres_mode(project_root):
        pg_append_ingest_run(project_root, row)
        return
    path = meta_root / "ingest_run.csv"
    df = _read_csv(path)
    out = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    _write_csv(path, out)


def upsert_watermark(meta_root: Path, row: dict) -> None:
    project_root = _project_root_from_data_root(meta_root)
    if is_postgres_mode(project_root):
        pg_upsert_watermark(project_root, row)
        return
    path = meta_root / "ingest_watermark.csv"
    keys = ["exchange", "market_type", "symbol", "timeframe"]
    df = _read_csv(path)
    new = pd.DataFrame([row])
    if df.empty:
        _write_csv(path, new)
        return

    existing_key = df[keys].astype(str).agg("|".join, axis=1)
    new_key = new[keys].astype(str).agg("|".join, axis=1).iloc[0]
    mask = existing_key == new_key
    if mask.any():
        df = df.loc[~mask].copy()
    out = pd.concat([df, new], ignore_index=True)
    _write_csv(path, out)


def append_dq_report(dq_root: Path, row: dict) -> None:
    project_root = _project_root_from_data_root(dq_root)
    if is_postgres_mode(project_root):
        pg_append_dq_report(project_root, row)
        return
    path = dq_root / "ohlcv_quality_report.csv"
    df = _read_csv(path)
    out = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    _write_csv(path, out)


def append_context_dq_report(dq_root: Path, row: dict) -> None:
    project_root = _project_root_from_data_root(dq_root)
    if is_postgres_mode(project_root):
        pg_append_context_dq_report(project_root, row)
        return
    path = dq_root / "market_context_quality_report.csv"
    df = _read_csv(path)
    out = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    _write_csv(path, out)


def append_gap_events(dq_root: Path, rows: list[dict]) -> None:
    if not rows:
        return
    project_root = _project_root_from_data_root(dq_root)
    if is_postgres_mode(project_root):
        pg_append_gap_events(project_root, rows)
        return
    path = dq_root / "gap_events.csv"
    df = _read_csv(path)
    out = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
    out = out.drop_duplicates(
        subset=[
            "run_id",
            "dataset",
            "symbol",
            "timeframe",
            "trade_date_utc",
            "expected_open_time_utc",
        ]
    )
    _write_csv(path, out)


def append_ingest_pair_status(meta_root: Path, row: dict) -> None:
    project_root = _project_root_from_data_root(meta_root)
    if is_postgres_mode(project_root):
        pg_append_ingest_pair_status(project_root, row)
        return
    path = meta_root / "ingest_pair_status.csv"
    df = _read_csv(path)
    out = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    _write_csv(path, out)


def get_watermark(meta_root: Path, *, exchange: str, market_type: str, symbol: str, timeframe: str) -> str | None:
    project_root = _project_root_from_data_root(meta_root)
    if is_postgres_mode(project_root):
        return pg_get_watermark(
            project_root,
            exchange=exchange,
            market_type=market_type,
            symbol=symbol,
            timeframe=timeframe,
        )
    path = meta_root / "ingest_watermark.csv"
    df = _read_csv(path)
    if df.empty:
        return None
    mask = (
        (df["exchange"] == exchange)
        & (df["market_type"] == market_type)
        & (df["symbol"] == symbol)
        & (df["timeframe"] == timeframe)
    )
    if not mask.any():
        return None
    row = df.loc[mask].sort_values("updated_at_utc").iloc[-1]
    return str(row["last_loaded_open_time_utc"])
