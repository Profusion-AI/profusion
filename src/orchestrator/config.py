"""Configuration loader.

Safe to import without a live ANTHROPIC_API_KEY. Individual adapters
raise MissingAPIKeyError at call time, not import time.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from repo root (two levels up from this file: src/orchestrator/config.py)
_env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(_env_path, override=False)


def get(key: str, default: str | None = None) -> str | None:
    return os.environ.get(key, default)


def require(key: str) -> str:
    val = os.environ.get(key)
    if not val:
        raise MissingConfigError(key)
    return val


class MissingConfigError(Exception):
    def __init__(self, key: str) -> None:
        super().__init__(
            f"Required config key {key!r} is not set. "
            f"Copy .env.example to .env and fill in the value."
        )
        self.key = key


ANTHROPIC_API_KEY: str | None = get("ANTHROPIC_API_KEY")
FIRECRAWL_URL: str = get("FIRECRAWL_URL", "http://localhost:3002") or "http://localhost:3002"
PIPELINE_ENV: str = get("PIPELINE_ENV", "development") or "development"
LOG_LEVEL: str = get("LOG_LEVEL", "INFO") or "INFO"
CLAUDE_MODEL: str = get("CLAUDE_MODEL", "claude-sonnet-4-6") or "claude-sonnet-4-6"

DB_PATH: Path = Path(get("DB_PATH", "data/content.db") or "data/content.db")
RENDERS_DIR: Path = Path(get("RENDERS_DIR", "data/renders") or "data/renders")
LOGS_DIR: Path = Path(get("LOGS_DIR", "data/logs") or "data/logs")
TURBO_URL: str = get("TURBO_URL", "http://localhost:8080") or "http://localhost:8080"
POST_BRIDGE_API_KEY: str = get("POST_BRIDGE_API_KEY", "") or ""
