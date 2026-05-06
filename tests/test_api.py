"""FastAPI operator dashboard route tests."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import orchestrator.config as config
from orchestrator.api import create_app
from orchestrator.db import (
    init_db,
    insert_content_item,
    update_item_status,
)
from orchestrator.diagnostics import write_diagnostic
from tests.test_publish import _seed_approved_item


@pytest.fixture()
def client(monkeypatch, tmp_path):
    db_path = tmp_path / "content.db"
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    init_db(db_path)
    monkeypatch.setattr(config, "DB_PATH", db_path)
    monkeypatch.setattr(config, "LOGS_DIR", logs_dir)
    monkeypatch.setattr(config, "POST_BRIDGE_API_KEY", "test-key")
    monkeypatch.setattr(config, "RENDERS_DIR", tmp_path / "renders")
    monkeypatch.setattr(config, "RECEIPTS_DIR", tmp_path / "receipts")
    app = create_app(dev=True)
    return TestClient(app), db_path, logs_dir, tmp_path


# ---------------------------------------------------------------------------
# Queue
# ---------------------------------------------------------------------------

def test_get_queue_empty_shape(client):
    tc, *_ = client
    resp = tc.get("/api/queue")
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "summary" in body
    assert "filters" in body
    assert body["items"] == []


def test_get_queue_with_item_returns_normalized_timestamp(client):
    tc, db_path, *_ = client
    insert_content_item(db_path, topic="ts check")
    resp = tc.get("/api/queue")
    assert resp.status_code == 200
    item = resp.json()["items"][0]
    assert item["created_at"].endswith("Z"), "timestamp must be ISO UTC with Z suffix"


def test_get_queue_status_filter(client):
    tc, db_path, *_ = client
    idea_id = insert_content_item(db_path, topic="idea item")
    planned_id = insert_content_item(db_path, topic="planned item")
    update_item_status(db_path, planned_id, "planned")

    resp = tc.get("/api/queue?status=idea")
    assert resp.status_code == 200
    ids = [i["id"] for i in resp.json()["items"]]
    assert idea_id in ids
    assert planned_id not in ids


# ---------------------------------------------------------------------------
# Item detail
# ---------------------------------------------------------------------------

def test_get_item_not_found_returns_404(client):
    tc, *_ = client
    resp = tc.get("/api/items/nonexistent-id")
    assert resp.status_code == 404


def test_get_item_returns_inspect_payload_shape(client):
    tc, db_path, *_ = client
    item_id = insert_content_item(db_path, topic="detail test")
    resp = tc.get(f"/api/items/{item_id}")
    assert resp.status_code == 200
    body = resp.json()
    for key in ("item", "lifecycle_state", "blockage", "retry", "next_safe_command", "artifacts", "recent_logs"):
        assert key in body, f"missing key {key!r}"
    assert body["item"]["id"] == item_id
    assert body["lifecycle_state"] == "idea"


def test_get_item_jobs_not_found(client):
    tc, *_ = client
    resp = tc.get("/api/items/bad-id/jobs")
    assert resp.status_code == 404


def test_get_item_jobs_returns_lists(client):
    tc, db_path, logs_dir, tmp_path = client
    item_id, _variant_id, _mp4 = _seed_approved_item(db_path, tmp_path)
    resp = tc.get(f"/api/items/{item_id}/jobs")
    assert resp.status_code == 200
    body = resp.json()
    assert "render_jobs" in body
    assert "publish_jobs" in body


def test_get_item_renders_not_found(client):
    tc, *_ = client
    assert tc.get("/api/items/bad/renders").status_code == 404


def test_get_item_renders_shape(client):
    tc, db_path, logs_dir, tmp_path = client
    item_id, *_ = _seed_approved_item(db_path, tmp_path)
    resp = tc.get(f"/api/items/{item_id}/renders")
    assert resp.status_code == 200
    body = resp.json()
    assert "latest_render_job" in body
    assert "artifacts" in body


def test_get_item_approvals_not_found(client):
    tc, *_ = client
    assert tc.get("/api/items/bad/approvals").status_code == 404


def test_get_item_approvals_returns_effective_decision(client):
    tc, db_path, logs_dir, tmp_path = client
    item_id, *_ = _seed_approved_item(db_path, tmp_path)
    resp = tc.get(f"/api/items/{item_id}/approvals")
    assert resp.status_code == 200
    body = resp.json()
    assert "effective_decision" in body
    assert body["effective_decision"] == "approved"


def test_get_item_receipts_returns_current_lifecycle_status(client):
    tc, db_path, logs_dir, tmp_path = client
    from orchestrator.receipts.generator import (
        generate_content_video_receipt,
        transition_receipt,
    )

    item_id, *_ = _seed_approved_item(db_path, tmp_path)
    generated = generate_content_video_receipt(
        db_path=db_path,
        logs_dir=logs_dir,
        receipts_dir=tmp_path / "receipts",
        item_id=item_id,
    )
    transition_receipt(
        receipts_dir=tmp_path / "receipts",
        receipt_id=generated.receipt_id,
        to_status="reviewed",
    )

    resp = tc.get(f"/api/items/{item_id}/receipts")

    assert resp.status_code == 200
    body = resp.json()
    assert body["item_id"] == item_id
    assert body["receipt_count"] == 1
    assert body["receipts"][0]["receipt_id"] == generated.receipt_id
    assert body["receipts"][0]["receipt_status"] == "reviewed"
    assert body["receipts"][0]["status_history"][-1]["to_status"] == "reviewed"
    assert body["receipts"][0]["receipt_type"] == "content_video_receipt"
    assert body["receipts"][0]["evidence_json"].endswith("evidence.json")


# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------

def test_get_logs_returns_list_shape(client):
    tc, *_ = client
    resp = tc.get("/api/logs")
    assert resp.status_code == 200
    assert "logs" in resp.json()
    assert isinstance(resp.json()["logs"], list)


def test_get_logs_with_diagnostic_entry(client):
    tc, db_path, logs_dir, tmp_path = client
    item_id = insert_content_item(db_path, topic="log test")
    write_diagnostic(logs_dir, stage="render", item_id=item_id, job_id="j1",
                     attempt=1, error="boom", error_code="TEST_ERR", context={})
    resp = tc.get("/api/logs")
    assert resp.status_code == 200
    assert len(resp.json()["logs"]) >= 1


def test_get_logs_item_id_filter(client):
    tc, db_path, logs_dir, tmp_path = client
    item_a = insert_content_item(db_path, topic="item A")
    item_b = insert_content_item(db_path, topic="item B")
    write_diagnostic(logs_dir, stage="render", item_id=item_a, job_id="ja",
                     attempt=1, error="e", error_code="E", context={})
    write_diagnostic(logs_dir, stage="render", item_id=item_b, job_id="jb",
                     attempt=1, error="e", error_code="E", context={})
    resp = tc.get(f"/api/logs?item_id={item_a}")
    assert resp.status_code == 200
    logs = resp.json()["logs"]
    # item_id filter uses filename match or JSON content — job_id "ja" vs "jb" is in the name
    assert len(logs) > 0
    assert not any("jb" in entry["name"] for entry in logs), "item_b logs must be excluded"
    assert all("ja" in entry["name"] for entry in logs), "only item_a logs expected"


# ---------------------------------------------------------------------------
# Retry mutations
# ---------------------------------------------------------------------------

def test_post_retry_qa_unknown_item_404(client):
    tc, *_ = client
    resp = tc.post("/api/items/bad-id/retry/qa")
    assert resp.status_code == 404


def test_post_retry_qa_non_qa_failed_returns_409(client):
    tc, db_path, *_ = client
    item_id = insert_content_item(db_path, topic="not qa_failed")
    resp = tc.post(f"/api/items/{item_id}/retry/qa")
    assert resp.status_code == 409
    assert "qa_failed" in resp.json()["detail"]


def test_post_retry_render_nonexistent_job_409(client):
    tc, *_ = client
    resp = tc.post("/api/jobs/render/nonexistent-job-id/retry")
    assert resp.status_code == 409
    assert "not found" in resp.json()["detail"]


def test_post_retry_publish_nonexistent_job_409(client):
    tc, *_ = client
    resp = tc.post("/api/jobs/publish/nonexistent-job-id/retry")
    assert resp.status_code == 409
    assert "not found" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# Status validation
# ---------------------------------------------------------------------------

def test_get_queue_invalid_status_returns_422(client):
    tc, *_ = client
    resp = tc.get("/api/queue?status=bogus")
    assert resp.status_code == 422
    assert "bogus" in resp.json()["detail"]


def test_get_queue_valid_status_does_not_error(client):
    tc, db_path, *_ = client
    insert_content_item(db_path, topic="idea item")
    for status in ("idea", "planned", "published"):
        resp = tc.get(f"/api/queue?status={status}")
        assert resp.status_code == 200, f"status={status!r} should be valid"


# ---------------------------------------------------------------------------
# SPA fallback (prod mode)
# ---------------------------------------------------------------------------

def test_spa_fallback_serves_index_for_deep_links(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "assets").mkdir()
    (dist / "index.html").write_text("<html><body>spa</body></html>")
    app = create_app(dev=False, dist_path=dist)
    tc = TestClient(app)
    for path in ["/", "/queue", "/items/some-id", "/logs"]:
        resp = tc.get(path)
        assert resp.status_code == 200, f"{path!r} returned {resp.status_code}"
        assert "spa" in resp.text, f"{path!r} did not return index.html"


def test_spa_fallback_api_routes_still_work(tmp_path, monkeypatch):
    import orchestrator.config as config
    db_path = tmp_path / "content.db"
    from orchestrator.db import init_db
    init_db(db_path)
    monkeypatch.setattr(config, "DB_PATH", db_path)
    monkeypatch.setattr(config, "LOGS_DIR", tmp_path / "logs")
    (tmp_path / "logs").mkdir()

    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "assets").mkdir()
    (dist / "index.html").write_text("<html>spa</html>")

    app = create_app(dev=False, dist_path=dist)
    tc = TestClient(app)
    resp = tc.get("/api/queue")
    assert resp.status_code == 200
    assert "items" in resp.json()


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

def test_cors_header_present_in_dev_mode(client):
    tc, *_ = client
    resp = tc.get("/api/queue", headers={"Origin": "http://localhost:5173"})
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"
