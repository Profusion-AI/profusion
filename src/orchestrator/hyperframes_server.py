"""Local FastAPI server for AICE HyperFrames receipt validation."""

from __future__ import annotations

from pathlib import Path, PurePosixPath
from urllib.parse import unquote

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from orchestrator.hyperframes_receipts import (
    load_aice_hyperframe_model,
    render_aice_validator_view,
)


def create_aice_hyperframes_app(
    receipt_dir: Path | str, *, local_url: str
) -> FastAPI:
    """Create a local-only validator app for one receipt packet."""

    root = Path(receipt_dir).expanduser().resolve()
    model = load_aice_hyperframe_model(root)
    viewer_html = render_aice_validator_view(model, local_url=local_url)
    app = FastAPI(title="AICE Workflow Receipt Validator")

    @app.get("/", response_class=HTMLResponse)
    def validator_view() -> HTMLResponse:
        return HTMLResponse(viewer_html)

    @app.get("/api/model")
    def validator_model() -> dict:
        return model

    @app.get("/receipt")
    def receipt_html() -> FileResponse:
        receipt_path = root / "workflow_receipt.html"
        if not receipt_path.is_file():
            raise HTTPException(status_code=404)
        return FileResponse(receipt_path, media_type="text/html")

    @app.get("/packet/{packet_path:path}")
    def packet_file(packet_path: str) -> FileResponse:
        return _file_response(_safe_route_path(root, packet_path))

    @app.get("/artifacts/{artifact_path:path}")
    def artifact_file(artifact_path: str) -> FileResponse:
        return _file_response(_safe_route_path(root / "artifacts", artifact_path))

    return app


def _safe_route_path(root: Path, route_path: str) -> Path:
    decoded = unquote(route_path)
    if not decoded or _has_control_chars(decoded):
        raise HTTPException(status_code=404)
    if "\\" in decoded:
        raise HTTPException(status_code=404)

    posix_path = PurePosixPath(decoded)
    if posix_path.is_absolute() or any(part == ".." for part in posix_path.parts):
        raise HTTPException(status_code=404)

    root_resolved = root.resolve()
    candidate = (root_resolved / Path(*posix_path.parts)).resolve()
    if root_resolved not in (candidate, *candidate.parents):
        raise HTTPException(status_code=404)
    if not candidate.is_file():
        raise HTTPException(status_code=404)
    return candidate


def _file_response(path: Path) -> FileResponse:
    return FileResponse(path)


def _has_control_chars(value: str) -> bool:
    return any(ord(char) < 32 or ord(char) == 127 for char in value)
