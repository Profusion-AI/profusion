"""Entry point shim — the canonical CLI is the `profusion` script declared in pyproject.toml.

Run via: uv run profusion <command>
"""
from orchestrator.cli import app

if __name__ == "__main__":
    app()
