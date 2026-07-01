from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from mlbotnav.security import resolve_secret


@dataclass(frozen=True)
class Settings:
    source_env_path: Path | None
    bybit_base_url: str
    bybit_api_key: str
    bybit_api_secret: str
    bybit_category: str
    bybit_recv_window: int
    symbol: str
    timeframes: list[str]


def _resolve_source_env(project_root: Path) -> Path | None:
    # Fallback for .env files saved with UTF-8 BOM where the first key can become "\ufeffSOURCE_ENV_PATH".
    raw = os.getenv("SOURCE_ENV_PATH", "").strip() or os.getenv("\ufeffSOURCE_ENV_PATH", "").strip()
    if not raw:
        return None
    p = Path(raw)
    if not p.is_absolute():
        p = (project_root / p).resolve()
    return p


def load_settings() -> Settings:
    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env", override=False, encoding="utf-8-sig")

    source_env_path = _resolve_source_env(project_root)
    if source_env_path and source_env_path.exists():
        # Tunnel: load external Bybit credentials without mixing codebases.
        load_dotenv(source_env_path, override=False, encoding="utf-8-sig")

    timeframes_raw = os.getenv("TIMEFRAMES", "1,5,15,30,60,240,D")
    timeframes = [x.strip() for x in timeframes_raw.split(",") if x.strip()]

    return Settings(
        source_env_path=source_env_path,
        bybit_base_url=os.getenv("BYBIT_BASE_URL", "https://api.bybit.com").rstrip("/"),
        bybit_api_key=str(resolve_secret(project_root, name="BYBIT_API_KEY").get("value", "")),
        bybit_api_secret=str(resolve_secret(project_root, name="BYBIT_API_SECRET").get("value", "")),
        bybit_category=os.getenv("BYBIT_CATEGORY", "linear"),
        bybit_recv_window=int(os.getenv("BYBIT_RECV_WINDOW", "20000")),
        symbol=os.getenv("SYMBOL", "SOLUSDT"),
        timeframes=timeframes,
    )
