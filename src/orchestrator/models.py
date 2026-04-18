"""Pydantic models for all pipeline entities (PRD §16)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from orchestrator.state import ContentStatus


def _new_id() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.utcnow()


# ---------------------------------------------------------------------------
# Content Item
# ---------------------------------------------------------------------------

class CreateContentItem(BaseModel):
    topic: str
    pillar: str | None = None
    audience: str | None = None
    status: ContentStatus = ContentStatus.IDEA
    priority: int = Field(default=0, ge=0)
    source: str | None = None


class ContentItem(CreateContentItem):
    id: str = Field(default_factory=_new_id)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


# ---------------------------------------------------------------------------
# Content Brief
# ---------------------------------------------------------------------------

class ContentBrief(BaseModel):
    id: str = Field(default_factory=_new_id)
    content_item_id: str
    thesis: str
    angle: str | None = None
    hook_options: list[str] = Field(default_factory=list)
    cta: str | None = None
    claims_to_verify: list[str] = Field(default_factory=list)
    brand_notes: str | None = None
    created_at: datetime = Field(default_factory=_now)


# ---------------------------------------------------------------------------
# Script Variant
# ---------------------------------------------------------------------------

class ScriptVariant(BaseModel):
    id: str = Field(default_factory=_new_id)
    content_item_id: str
    variant_name: str
    script_text: str
    duration_target_seconds: int = Field(default=60, ge=1)
    status: Literal["draft", "approved"] = "draft"
    created_at: datetime = Field(default_factory=_now)


# ---------------------------------------------------------------------------
# Render Job
# ---------------------------------------------------------------------------

class RenderJob(BaseModel):
    id: str = Field(default_factory=_new_id)
    script_variant_id: str
    engine: str = "moneyprinterturbo"
    render_profile: dict[str, Any] = Field(default_factory=dict)
    output_path: str | None = None
    status: str = "pending"
    log_path: str | None = None
    created_at: datetime = Field(default_factory=_now)


# ---------------------------------------------------------------------------
# Approval Record
# ---------------------------------------------------------------------------

class ApprovalRecord(BaseModel):
    id: str = Field(default_factory=_new_id)
    content_item_id: str
    approved_by: str
    decision: Literal["approved", "rejected", "revision_requested"]
    notes: str | None = None
    timestamp: datetime = Field(default_factory=_now)


# ---------------------------------------------------------------------------
# Publish Job
# ---------------------------------------------------------------------------

class PublishJob(BaseModel):
    id: str = Field(default_factory=_new_id)
    content_item_id: str
    platform: Literal["youtube", "tiktok", "instagram"]
    engine: str = "moneyprinterv2"
    status: str = "pending"
    published_url: str | None = None
    external_post_id: str | None = None
    published_at: datetime | None = None
    created_at: datetime = Field(default_factory=_now)


# ---------------------------------------------------------------------------
# Agent Run
# ---------------------------------------------------------------------------

class AgentRun(BaseModel):
    id: str = Field(default_factory=_new_id)
    started_at: datetime = Field(default_factory=_now)
    ended_at: datetime | None = None
    goal: str
    status: Literal["running", "completed", "failed"] = "running"
    summary: str | None = None
    error_class: str | None = None
