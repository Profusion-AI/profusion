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
from fastapi.responses import FileResponse, Response
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
from orchestrator.receipts import receipts_payload
from orchestrator.measurements import measurement_summary_payload, measurements_payload
from orchestrator.state import ContentStatus

_DASHBOARD_DIST = Path(__file__).parent.parent.parent / "dashboard" / "dist"

_VALID_STATUSES = {s.value for s in ContentStatus}


def create_app(*, dev: bool = False, dist_path: Path | None = None) -> FastAPI:
    app = FastAPI(title="Profusion Operator API", version="0.1.0")

    if dev:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173"],
            allow_methods=["GET", "POST"],
            allow_headers=["*"],
        )

    _register_routes(app)

    _dist = dist_path if dist_path is not None else _DASHBOARD_DIST
    if not dev and _dist.is_dir():
        assets_dir = _dist / "assets"
        if assets_dir.is_dir():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

        _index = str(_dist / "index.html")

        async def _spa_fallback(full_path: str) -> Response:
            # Serve root-level static files (e.g. favicon.svg) if they exist on disk.
            # Everything else returns index.html so the React router handles the path.
            candidate = _dist / full_path
            if full_path and candidate.exists() and candidate.is_file():
                return FileResponse(str(candidate))
            return FileResponse(_index)

        app.add_api_route(
            "/{full_path:path}",
            _spa_fallback,
            methods=["GET"],
            include_in_schema=False,
        )

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
        if status is not None and status not in _VALID_STATUSES:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid status {status!r}. Valid values: {sorted(_VALID_STATUSES)}",
            )
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

    @app.get("/api/items/{item_id}/receipts")
    def get_item_receipts(item_id: str) -> dict[str, Any]:
        item = _require_item(item_id)
        return receipts_payload(receipts_dir=config.RECEIPTS_DIR, item_id=item["id"])

    @app.get("/api/items/{item_id}/measurements")
    def get_item_measurements(item_id: str) -> dict[str, Any]:
        item = _require_item(item_id)
        return measurements_payload(measurements_dir=config.MEASUREMENTS_DIR, item_id=item["id"])

    @app.get("/api/measurements/summary")
    def get_measurement_summary() -> dict[str, Any]:
        return measurement_summary_payload(
            db_path=_db(),
            measurements_dir=config.MEASUREMENTS_DIR,
        )

    @app.post("/api/m8/aice/receipt")
    def post_aice_runtime_receipt(payload: dict[str, Any]) -> dict[str, Any]:
        from orchestrator.m8_gtm.harness import generate_packet_from_runtime_payload
        from orchestrator.m8_gtm.registry import AICE_SLUG
        from orchestrator.m8_gtm.schemas import M8GTMError

        try:
            result = generate_packet_from_runtime_payload(AICE_SLUG, payload)
        except M8GTMError as exc:
            raise HTTPException(status_code=422, detail=str(exc))

        n8n_execution = result["observation"]["n8n_execution"]
        return {
            "workflow_slug": AICE_SLUG,
            "receipt_id": result["receipt_id"],
            "packet_dir": str(result["packet_dir"]),
            "workflow_receipt_html": str(result["workflow_receipt_html"]),
            "n8n_workspace_workflow_id": n8n_execution.get("workspace_workflow_id"),
            "n8n_execution_id": n8n_execution["execution_id"],
            "node_count": n8n_execution["node_count"],
            "nodes_executed": n8n_execution["nodes_executed"],
            "limitations": result["receipt"]["limitations"],
            "claims_supported": result["receipt"]["claims_supported"],
            "claims_not_supported": result["receipt"]["claims_not_supported"],
        }

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
