"""MoneyPrinterTurbo adapter — stub.

Implement in Milestone 2 after vendor env is set up.

Interface:
    render(script, profile) -> RenderJob
    get_job_status(job_id) -> str
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RenderProfile:
    aspect_ratio: str = "9:16"
    voice: str = "en-US-GuyNeural"
    tts_engine: str = "edge-tts"
    duration_seconds: int = 60
    subtitle_style: str = "default"


def render(script: str, profile: RenderProfile | None = None) -> dict:
    """Submit a script to MoneyPrinterTurbo for video rendering.

    Returns a RenderJob dict with id, status, and log_path.
    """
    raise NotImplementedError(
        "turbo.render() not yet implemented. Implement in Milestone 2. "
        "See vendor/MoneyPrinterTurbo for API surface."
    )


def get_job_status(job_id: str) -> str:
    """Poll a render job's current status."""
    raise NotImplementedError(
        "turbo.get_job_status() not yet implemented. Implement in Milestone 2."
    )
