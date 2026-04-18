"""MoneyPrinterV2 adapter — stub.

Implement in Milestone 4 after vendor env and YouTube credentials are set up.

Interface:
    publish(video_path, metadata) -> PublishJob
    schedule(job_id, publish_at) -> bool
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PublishMetadata:
    title: str
    description: str
    tags: list[str] = field(default_factory=list)
    platform: str = "youtube"
    privacy: str = "private"  # always private until human approves


def publish(video_path: str, metadata: PublishMetadata) -> dict:
    """Upload an approved video via MoneyPrinterV2.

    Returns a PublishJob dict with id, status, and published_url.
    """
    raise NotImplementedError(
        "v2.publish() not yet implemented. Implement in Milestone 4. "
        "See vendor/MoneyPrinterV2 for YouTube upload flow."
    )


def schedule(job_id: str, publish_at: datetime) -> bool:
    """Schedule a publish job for a future time."""
    raise NotImplementedError(
        "v2.schedule() not yet implemented. Implement in Milestone 5."
    )
