"""Local operator dashboard API.

All routes delegate to read_models, diagnostics, or retry — no business logic here.
React never queries SQLite directly; all data flows through this layer.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import orchestrator.config as config
from orchestrator import db as _db_mod
from orchestrator.diagnostics import list_logs
from orchestrator.read_models import (
    approvals_payload,
    inspect_payload,
    jobs_payload,
    renders_payload,
    status_payload,
)
from orchestrator.retry import RetryError, retry_publish_job, retry_qa_stage, retry_render_job

_DASHBOARD_DIST = Path(__file__).parent.parent.parent / "dashboard" / "dist"


def create_app(*, dev: bool = False) -> FastAPI:
    app = FastAPI(title="Profusion Operator API", version="0.1.0")

    if dev:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173"],
            allow_methods=["GET", "POST"],
            allow_headers=["*"],
        )

    _register_routes(app)

    if not dev and _DASHBOARD_DIST.is_dir():
        app.mount("/", StaticFiles(directory=str(_DASHBOARD_DIST), html=True), name="static")

    return app


def _db() -> Path:
    return config.DB_PATH


def _logs() -> Path:
    return config.LOGS_DIR


def _require_item(item_id: str) -> dict:
    item = _db_mod.get_item(_db(), item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id!r} not found")
    return item


def _register_routes(app: FastAPI) -> None:
    @app.get("/api/queue")
    def get_queue(status: str | None = None) -> dict[str, Any]:
        return status_payload(_db(), status=status)

    @app.get("/api/items/{item_id}")
    def get_item(item_id: str) -> dict[str, Any]:
        item = _require_item(item_id)
        return inspect_payload(_db(), _logs(), item)

    @app.get("/api/items/{item_id}/jobs")
    def get_item_jobs(item_id: str) -> dict[str, Any]:
        _require_item(item_id)
        return jobs_payload(_db(), item_id)

    @app.get("/api/items/{item_id}/renders")
    def get_item_renders(item_id: str) -> dict[str, Any]:
        _require_item(item_id)
        return renders_payload(_db(), item_id)

    @app.get("/api/items/{item_id}/approvals")
    def get_item_approvals(item_id: str) -> dict[str, Any]:
        _require_item(item_id)
        return approvals_payload(_db(), item_id)

    @app.get("/api/logs")
    def get_logs(
        item_id: str | None = None,
        job_id: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        return {"logs": list_logs(_logs(), item_id=item_id, job_id=job_id, limit=limit)}

    @app.post("/api/items/{item_id}/retry/qa")
    def post_retry_qa(item_id: str) -> dict[str, Any]:
        _require_item(item_id)
        try:
            return retry_qa_stage(_db(), item_id=item_id)
        except RetryError as exc:
            raise HTTPException(status_code=409, detail=str(exc))

    @app.post("/api/jobs/render/{render_job_id}/retry")
    def post_retry_render(render_job_id: str) -> dict[str, Any]:
        try:
            return retry_render_job(_db(), _logs(), render_job_id=render_job_id)
        except RetryError as exc:
            raise HTTPException(status_code=409, detail=str(exc))

    @app.post("/api/jobs/publish/{job_id}/retry")
    def post_retry_publish(job_id: str) -> dict[str, Any]:
        try:
            return retry_publish_job(
                _db(), _logs(), job_id=job_id, api_key=config.POST_BRIDGE_API_KEY or ""
            )
        except RetryError as exc:
            raise HTTPException(status_code=409, detail=str(exc))


app = create_app(dev=os.getenv("PROFUSION_DEV", "0") == "1")
