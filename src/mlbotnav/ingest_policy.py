from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class IngestPolicy:
    retry_max: int
    retry_backoff_base_sec: float
    retry_jitter_sec: float
    late_data_reconcile_days: int


def load_ingest_policy(project_root: Path) -> IngestPolicy:
    cfg_path = project_root / "configs" / "config.yaml"
    data = {}
    if cfg_path.exists():
        with cfg_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    ingest = data.get("data_ingest", {})
    return IngestPolicy(
        retry_max=int(ingest.get("retry_max", 5)),
        retry_backoff_base_sec=float(ingest.get("retry_backoff_base_sec", 1.0)),
        retry_jitter_sec=float(ingest.get("retry_jitter_sec", 0.35)),
        late_data_reconcile_days=int(ingest.get("late_data_reconcile_days", 3)),
    )

