"""Workflow registry for M8-GTM receipt demos."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ArtifactSpec:
    """A required or optional artifact within a workflow run fixture."""

    filename: str
    artifact_key: str
    artifact_type: str
    required: bool = True


@dataclass(frozen=True)
class WorkflowSpec:
    """Registered M8-GTM workflow contract."""

    slug: str
    name: str
    evidence_mode: str
    artifact_specs: tuple[ArtifactSpec, ...]
    required_case_ids: tuple[str, ...]
    required_case_artifacts: dict[str, tuple[str, ...]]

    @property
    def artifact_specs_by_filename(self) -> dict[str, ArtifactSpec]:
        return {spec.filename: spec for spec in self.artifact_specs}


SUPPORT_TRIAGE_SLUG = "support-triage-human-review"
SUPPORT_TRIAGE_NAME = "Customer Trust Triage Receipt"
AICE_SLUG = "aice-source-to-narrative-receipt"
AICE_NAME = "AICE Source-to-Narrative Workflow Receipt"
LOCAL_FIXTURE_EVIDENCE_MODE = "fixture_backed_local_demo"
LIVE_N8N_EVIDENCE_MODE = "fixture_backed_live_n8n_demo"

SUPPORT_TRIAGE_SPEC = WorkflowSpec(
    slug=SUPPORT_TRIAGE_SLUG,
    name=SUPPORT_TRIAGE_NAME,
    evidence_mode=LOCAL_FIXTURE_EVIDENCE_MODE,
    required_case_ids=("routine_invoice", "sensitive_billing_complaint"),
    required_case_artifacts={
        "sensitive_billing_complaint": ("human_review_event",),
    },
    artifact_specs=(
        ArtifactSpec("run.json", "run", "run_log"),
        ArtifactSpec("inbound_message.md", "inbound_message", "inbound_message"),
        ArtifactSpec("ai_classification.json", "ai_classification", "ai_classification"),
        ArtifactSpec("ai_draft_reply.md", "ai_draft_reply", "ai_draft"),
        ArtifactSpec("human_review_event.json", "human_review_event", "human_review", required=False),
        ArtifactSpec("final_reply.md", "final_reply", "final_reply"),
        ArtifactSpec("execution_log.json", "execution_log", "execution_log"),
    ),
)

AICE_SPEC = WorkflowSpec(
    slug=AICE_SLUG,
    name=AICE_NAME,
    evidence_mode=LIVE_N8N_EVIDENCE_MODE,
    required_case_ids=("live_minimum_aice",),
    required_case_artifacts={
        "live_minimum_aice": (
            "topic_brief",
            "source_cards",
            "quote_candidates",
            "claim_map",
            "attention_intelligence_map",
            "rights_review",
            "ambiguity_register",
            "human_editorial_review",
            "narrative_brief",
            "visual_plan",
            "execution_log",
            "n8n_run_summary",
        ),
    },
    artifact_specs=(
        ArtifactSpec("run.json", "run", "run_log"),
        ArtifactSpec("topic_brief.json", "topic_brief", "topic_brief"),
        ArtifactSpec("source_policy.json", "source_policy", "source_policy", required=False),
        ArtifactSpec("source_cards.json", "source_cards", "source_cards"),
        ArtifactSpec("quote_candidates.json", "quote_candidates", "quote_candidates"),
        ArtifactSpec("claim_map.json", "claim_map", "claim_map"),
        ArtifactSpec(
            "attention_intelligence_map.json",
            "attention_intelligence_map",
            "attention_intelligence_map",
        ),
        ArtifactSpec("rights_review.json", "rights_review", "rights_review"),
        ArtifactSpec("ambiguity_register.json", "ambiguity_register", "ambiguity_register"),
        ArtifactSpec(
            "human_editorial_review.json",
            "human_editorial_review",
            "human_editorial_review",
        ),
        ArtifactSpec("narrative_brief.json", "narrative_brief", "narrative_brief"),
        ArtifactSpec("visual_plan.json", "visual_plan", "visual_plan"),
        ArtifactSpec("execution_log.json", "execution_log", "execution_log"),
        ArtifactSpec("n8n_run_summary.json", "n8n_run_summary", "n8n_run_summary"),
    ),
)

WORKFLOW_SPECS: dict[str, WorkflowSpec] = {
    SUPPORT_TRIAGE_SPEC.slug: SUPPORT_TRIAGE_SPEC,
    AICE_SPEC.slug: AICE_SPEC,
}


def get_workflow_spec(workflow_slug: str) -> WorkflowSpec:
    """Return a registered workflow spec or raise KeyError."""

    return WORKFLOW_SPECS[workflow_slug]


def supported_workflow_slugs() -> str:
    """Return supported workflow slugs for error messages."""

    return ", ".join(sorted(WORKFLOW_SPECS))
