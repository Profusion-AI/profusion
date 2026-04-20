"""MoneyPrinterV2 adapter — PostBridge publishing.

Publish path: upload video to PostBridge media API, then create a post.
Auth: Bearer token via POST_BRIDGE_API_KEY env var.
API docs: https://api.post-bridge.com/reference

V2 vendor reference: vendor/MoneyPrinterV2/src/classes/PostBridge.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import httpx


class V2PublishError(RuntimeError):
    """Raised when publishing via PostBridge fails."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass
class PublishProfile:
    platform: str       # PostBridge platform slug, e.g. "youtube_shorts", "tiktok"
    account_id: int     # PostBridge social account ID
    api_key: str        # PostBridge Bearer token
    title: str = ""
    description: str = ""


@dataclass
class PublishResult:
    platform: str
    external_post_id: str
    published_url: Optional[str]
    post_response: dict = field(default_factory=dict)


_POST_BRIDGE_BASE = "https://api.post-bridge.com/v1"
_UPLOAD_TIMEOUT = 600
_DEFAULT_TIMEOUT = 60


def publish(
    video_path: str | Path,
    profile: PublishProfile,
    *,
    client: httpx.Client | None = None,
) -> PublishResult:
    """Upload video to PostBridge and create a post.

    Accepts an optional httpx.Client for dependency injection in tests.
    Raises V2PublishError on any failure.
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise V2PublishError(f"Video file not found: {video_path}")
    if video_path.stat().st_size == 0:
        raise V2PublishError(f"Video file is empty: {video_path}")

    auth_headers = {
        "Authorization": f"Bearer {profile.api_key}",
        "Content-Type": "application/json",
    }

    own_client = client is None
    if own_client:
        client = httpx.Client(timeout=_DEFAULT_TIMEOUT)

    try:
        media_id, upload_url = _create_upload_url(client, auth_headers, video_path)
        _upload_file(client, upload_url, video_path)
        caption = (profile.title or profile.description or video_path.stem).strip()
        result = _create_post(client, auth_headers, profile, media_id, caption)

        post_id = str(result.get("id", ""))
        published_url = result.get("url") or result.get("post_url")

        return PublishResult(
            platform=profile.platform,
            external_post_id=post_id,
            published_url=published_url,
            post_response=result,
        )
    except V2PublishError:
        raise
    except httpx.HTTPStatusError as exc:
        raise V2PublishError(
            f"PostBridge HTTP {exc.response.status_code}: {exc.response.text[:200]}",
            status_code=exc.response.status_code,
        ) from exc
    except httpx.RequestError as exc:
        raise V2PublishError(f"PostBridge request failed: {exc}") from exc
    finally:
        if own_client:
            client.close()


def _create_upload_url(
    client: httpx.Client, headers: dict, video_path: Path
) -> tuple[str, str]:
    response = client.post(
        f"{_POST_BRIDGE_BASE}/media/create-upload-url",
        headers=headers,
        json={
            "name": video_path.name,
            "mime_type": "video/mp4",
            "size_bytes": video_path.stat().st_size,
        },
        timeout=_DEFAULT_TIMEOUT,
    )
    if response.status_code not in (200, 201):
        raise V2PublishError(
            f"PostBridge create-upload-url returned HTTP {response.status_code}: {response.text[:200]}",
            status_code=response.status_code,
        )
    body = response.json()
    media_id = body.get("media_id")
    upload_url = body.get("upload_url")
    if not media_id or not upload_url:
        raise V2PublishError(
            f"PostBridge did not return media_id/upload_url. Response: {body}"
        )
    return media_id, upload_url


def _upload_file(client: httpx.Client, upload_url: str, video_path: Path) -> None:
    with open(video_path, "rb") as f:
        response = client.put(
            upload_url,
            content=f.read(),
            headers={"Content-Type": "video/mp4"},
            timeout=_UPLOAD_TIMEOUT,
        )
    if response.status_code not in (200, 201):
        raise V2PublishError(
            f"PostBridge upload PUT returned HTTP {response.status_code}: {response.text[:200]}",
            status_code=response.status_code,
        )


def _create_post(
    client: httpx.Client,
    headers: dict,
    profile: PublishProfile,
    media_id: str,
    caption: str,
) -> dict:
    payload: dict = {
        "caption": caption,
        "social_accounts": [profile.account_id],
        "media": [media_id],
        "processing_enabled": True,
    }
    if profile.platform == "tiktok" and profile.title:
        payload["platform_configurations"] = {"tiktok": {"title": profile.title}}

    response = client.post(
        f"{_POST_BRIDGE_BASE}/posts",
        headers=headers,
        json=payload,
        timeout=_DEFAULT_TIMEOUT,
    )
    if response.status_code not in (200, 201):
        raise V2PublishError(
            f"PostBridge create_post returned HTTP {response.status_code}: {response.text[:200]}",
            status_code=response.status_code,
        )
    return response.json()
