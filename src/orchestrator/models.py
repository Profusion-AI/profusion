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
# Source Document (M1)
# ---------------------------------------------------------------------------

class SourceDocument(BaseModel):
    id: str = Field(default_factory=_new_id)
    content_item_id: str
    url: str | None = None
    title: str | None = None
    markdown: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_now)


# ---------------------------------------------------------------------------
# Brief primitives (M1) — structured Claude output
# ---------------------------------------------------------------------------

RiskCategory = Literal[
    "reputational",
    "legal",
    "factual",
    "editorial_tone",
    "audience_sensitivity",
    "partisan_framing",
]


class ClaimToVerify(BaseModel):
    claim: str
    why_it_matters: str | None = None
    suggested_source_type: str | None = None


class RiskFlag(BaseModel):
    category: RiskCategory
    description: str
    mitigation: str | None = None


class SourceRef(BaseModel):
    title: str | None = None
    url: str | None = None
    note: str | None = None


class BriefDraft(BaseModel):
    """Validated structured output from the brief-generation prompt."""

    thesis: str
    angle: str | None = None
    hook_options: list[str] = Field(default_factory=list)
    cta: str | None = None
    claims_to_verify: list[ClaimToVerify] = Field(default_factory=list)
    risk_flags: list[RiskFlag] = Field(default_factory=list)
    brand_notes: str | None = None
    source_refs: list[SourceRef] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Content Brief (persisted)
# ---------------------------------------------------------------------------

class ContentBrief(BaseModel):
    id: str = Field(default_factory=_new_id)
    content_item_id: str
    thesis: str
    angle: str | None = None
    hook_options: list[str] = Field(default_factory=list)
    cta: str | None = None
    claims_to_verify: list[ClaimToVerify] = Field(default_factory=list)
    brand_notes: str | None = None
    risk_flags: list[RiskFlag] = Field(default_factory=list)
    source_refs: list[SourceRef] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)


# ---------------------------------------------------------------------------
# Script Variant
# ---------------------------------------------------------------------------

class ScriptDraft(BaseModel):
    """Validated structured output for a single script variant from Claude."""

    variant_name: str
    script_text: str
    duration_target_seconds: int = Field(default=60, ge=10, le=180)


class ScriptBatch(BaseModel):
    """A batch of script variants returned from one prompt call."""

    variants: list[ScriptDraft]


class QAResult(BaseModel):
    """Validated structured output from the editorial risk QA prompt."""

    risk_flags: list[RiskFlag] = Field(default_factory=list)
    claims_to_verify: list[ClaimToVerify] = Field(default_factory=list)
    overall_go_no_go: Literal["go", "hold"]


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
    retry_of_job_id: str | None = None
    attempt_group_id: str | None = None
    error_code: str | None = None
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
    platform: str
    engine: str = "moneyprinterv2"
    status: str = "pending"
    account_id: int | None = None
    title: str | None = None
    description: str | None = None
    scheduled_for: datetime | None = None
    platform_metadata: dict[str, Any] = Field(default_factory=dict)
    published_url: str | None = None
    external_post_id: str | None = None
    published_at: datetime | None = None
    last_error: str | None = None
    retry_of_job_id: str | None = None
    attempt_group_id: str | None = None
    error_code: str | None = None
    log_path: str | None = None
    attempt_count: int = 0
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime | None = None


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
