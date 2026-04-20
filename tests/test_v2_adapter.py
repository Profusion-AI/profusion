"""MoneyPrinterV2 adapter unit tests — PostBridge HTTP calls mocked."""

from pathlib import Path
from unittest.mock import MagicMock, call

import pytest

from orchestrator.adapters.v2 import (
    PublishProfile,
    PublishResult,
    V2PublishError,
    publish,
)


def _profile() -> PublishProfile:
    return PublishProfile(
        platform="youtube_shorts",
        account_id=42,
        api_key="test-key",
        title="Test Video",
        description="A test",
    )


def _mock_client(tmp_path: Path) -> MagicMock:
    """Build a mock httpx.Client that returns success for all PostBridge calls."""
    client = MagicMock()

    upload_url_resp = MagicMock()
    upload_url_resp.status_code = 200
    upload_url_resp.json.return_value = {
        "media_id": "media-123",
        "upload_url": "https://s3.example.com/upload",
    }

    post_resp = MagicMock()
    post_resp.status_code = 201
    post_resp.json.return_value = {
        "id": "post-456",
        "url": "https://youtube.com/shorts/abc123",
    }

    client.post.side_effect = [upload_url_resp, post_resp]

    put_resp = MagicMock()
    put_resp.status_code = 200
    client.put.return_value = put_resp

    return client


def _make_mp4(tmp_path: Path, name: str = "final.mp4") -> Path:
    p = tmp_path / name
    p.write_bytes(b"FAKE_MP4_BYTES")
    return p


# ---------------------------------------------------------------------------
# Input validation (no HTTP calls needed)
# ---------------------------------------------------------------------------

def test_publish_raises_on_missing_file(tmp_path):
    with pytest.raises(V2PublishError, match="not found"):
        publish(tmp_path / "missing.mp4", _profile())


def test_publish_raises_on_empty_file(tmp_path):
    empty = tmp_path / "empty.mp4"
    empty.write_bytes(b"")
    with pytest.raises(V2PublishError, match="empty"):
        publish(empty, _profile())


# ---------------------------------------------------------------------------
# HTTP error paths
# ---------------------------------------------------------------------------

def test_publish_raises_on_create_upload_url_error(tmp_path):
    mp4 = _make_mp4(tmp_path)
    client = MagicMock()
    error_resp = MagicMock()
    error_resp.status_code = 401
    error_resp.text = "Unauthorized"
    client.post.return_value = error_resp
    with pytest.raises(V2PublishError, match="401"):
        publish(mp4, _profile(), client=client)


def test_publish_raises_if_upload_url_body_missing_fields(tmp_path):
    mp4 = _make_mp4(tmp_path)
    client = MagicMock()
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {}  # missing media_id and upload_url
    client.post.return_value = resp
    with pytest.raises(V2PublishError, match="media_id"):
        publish(mp4, _profile(), client=client)


def test_publish_raises_on_upload_put_error(tmp_path):
    mp4 = _make_mp4(tmp_path)
    client = MagicMock()

    upload_url_resp = MagicMock()
    upload_url_resp.status_code = 200
    upload_url_resp.json.return_value = {
        "media_id": "media-123",
        "upload_url": "https://s3.example.com/upload",
    }
    client.post.return_value = upload_url_resp

    put_resp = MagicMock()
    put_resp.status_code = 500
    put_resp.text = "Server error"
    client.put.return_value = put_resp

    with pytest.raises(V2PublishError, match="500"):
        publish(mp4, _profile(), client=client)


def test_publish_raises_on_create_post_error(tmp_path):
    mp4 = _make_mp4(tmp_path)
    client = MagicMock()

    upload_url_resp = MagicMock()
    upload_url_resp.status_code = 200
    upload_url_resp.json.return_value = {
        "media_id": "media-123",
        "upload_url": "https://s3.example.com/upload",
    }

    post_resp = MagicMock()
    post_resp.status_code = 422
    post_resp.text = "Unprocessable Entity"

    client.post.side_effect = [upload_url_resp, post_resp]
    client.put.return_value = MagicMock(status_code=200)

    with pytest.raises(V2PublishError, match="422"):
        publish(mp4, _profile(), client=client)


# ---------------------------------------------------------------------------
# Success path
# ---------------------------------------------------------------------------

def test_publish_success_returns_result(tmp_path):
    mp4 = _make_mp4(tmp_path)
    client = _mock_client(tmp_path)
    result = publish(mp4, _profile(), client=client)

    assert isinstance(result, PublishResult)
    assert result.platform == "youtube_shorts"
    assert result.external_post_id == "post-456"
    assert result.published_url == "https://youtube.com/shorts/abc123"


def test_publish_sends_correct_media_id_to_create_post(tmp_path):
    mp4 = _make_mp4(tmp_path)
    client = _mock_client(tmp_path)
    publish(mp4, _profile(), client=client)

    create_post_call = client.post.call_args_list[1]
    payload = create_post_call.kwargs["json"]
    assert payload["media"] == ["media-123"]
    assert payload["social_accounts"] == [42]
