"""Validate n8n runtime payloads for AICE receipt generation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from orchestrator.m8_gtm.registry import AICE_SLUG
from orchestrator.m8_gtm.schemas import FixtureValidationError

WORKSPACE_RUNTIME_EVIDENCE_MODE = "workspace_runtime_n8n_payload"


def validate_aice_runtime_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a normalized AICE runtime payload or raise a validation error."""

    normalized = deepcopy(payload)
    if normalized.get("workflow_slug") != AICE_SLUG:
        raise FixtureValidationError(
            f"runtime payload workflow_slug must be {AICE_SLUG!r}"
        )

    required = (
        "n8n_workspace_workflow_id",
        "n8n_execution_id",
        "executed_at",
        "node_count",
        "nodes_executed",
        "topic_brief",
        "source_cards",
        "quote_candidates",
        "claim_map",
        "rights_review",
        "ambiguity_register",
        "human_editorial_review",
        "narrative_brief",
        "visual_plan",
    )
    missing = [key for key in required if key not in normalized]
    if missing:
        raise FixtureValidationError(
            "runtime payload missing required fields: " + ", ".join(missing)
        )

    node_count = int(normalized["node_count"])
    nodes_executed = normalized["nodes_executed"]
    if node_count < 3:
        raise FixtureValidationError("runtime payload requires node_count >= 3")
    if not isinstance(nodes_executed, list) or len(nodes_executed) < 3:
        raise FixtureValidationError(
            "runtime payload requires at least 3 executed nodes"
        )

    normalized["source_cards"] = _normalize_list_container(
        normalized["source_cards"], "sources", "source_cards"
    )
    normalized["quote_candidates"] = _normalize_list_container(
        normalized["quote_candidates"], "quote_candidates", "quote_candidates"
    )
    normalized["claim_map"] = _normalize_list_container(
        normalized["claim_map"], "claims", "claim_map"
    )
    normalized["attention_intelligence_map"] = _normalize_list_container(
        normalized.get("attention_intelligence_map", []),
        "mapped_dimensions",
        "attention_intelligence_map",
    )
    normalized["ambiguity_register"] = _normalize_list_container(
        normalized["ambiguity_register"], "ambiguities", "ambiguity_register"
    )
    normalized.setdefault(
        "limitations",
        [
            "No third-party media downloaded.",
            (
                "Receipt does not certify factual truth, copyright clearance, "
                "fair use, platform compliance, journalistic neutrality, or "
                "publication safety."
            ),
        ],
    )

    topic = _require_mapping(normalized["topic_brief"], "topic_brief")
    _require_text(topic, "title", "topic_brief.title")
    _require_text(topic, "editorial_question", "topic_brief.editorial_question")

    human_review = _require_mapping(
        normalized["human_editorial_review"], "human_editorial_review"
    )
    _require_text(human_review, "reviewer", "human_editorial_review.reviewer")
    _require_text(human_review, "decision", "human_editorial_review.decision")
    _require_non_empty_list(
        human_review.get("reviewed_artifacts"),
        "human_editorial_review.reviewed_artifacts",
    )

    narrative = _require_mapping(normalized["narrative_brief"], "narrative_brief")
    _require_text(narrative, "allowed_use", "narrative_brief.allowed_use")

    rights_review = _require_mapping(normalized["rights_review"], "rights_review")
    _require_text(rights_review, "status", "rights_review.status")
    rights_items = rights_review.get("items")
    if not isinstance(rights_items, list):
        raise FixtureValidationError("runtime payload rights_review.items must be a list")
    if not rights_items and not _has_no_rights_items_limitation(
        normalized["limitations"]
    ):
        raise FixtureValidationError(
            "runtime payload rights_review.items requires at least one item "
            "or an explicit no-rights-items limitation"
        )
    for item in rights_items:
        if not isinstance(item, dict):
            raise FixtureValidationError(
                "runtime payload rights_review.items entries must be objects"
            )

    quotes = normalized["quote_candidates"]["quote_candidates"]
    if not quotes:
        raise FixtureValidationError(
            "runtime payload requires at least one quote candidate"
        )
    for candidate in quotes:
        if candidate.get("audio_visual_downloaded") is not False:
            raise FixtureValidationError(
                "runtime payload media candidates must not download audio/video"
            )
        if candidate.get("storage_mode") != "metadata_only":
            raise FixtureValidationError(
                "runtime payload media candidates must use metadata_only storage"
            )
        if "local_media_path" in candidate or "transcript_full_text" in candidate:
            raise FixtureValidationError(
                "runtime payload media candidates must remain reference-only"
            )

    if not normalized["source_cards"]["sources"]:
        raise FixtureValidationError("runtime payload requires at least one source card")
    if not normalized["claim_map"]["claims"]:
        raise FixtureValidationError("runtime payload requires at least one claim")
    if not normalized["ambiguity_register"]["ambiguities"]:
        raise FixtureValidationError("runtime payload requires at least one ambiguity")

    normalized["node_count"] = node_count
    normalized["evidence_mode"] = WORKSPACE_RUNTIME_EVIDENCE_MODE
    return normalized


def _normalize_list_container(
    value: object,
    key: str,
    label: str,
) -> dict[str, list[dict[str, Any]]]:
    if isinstance(value, dict):
        items = value.get(key, value.get("items", []))
    else:
        items = value
    if not isinstance(items, list):
        raise FixtureValidationError(f"runtime payload {label} must be a list")
    for item in items:
        if not isinstance(item, dict):
            raise FixtureValidationError(f"runtime payload {label} entries must be objects")
    return {key: items}


def _require_mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FixtureValidationError(f"runtime payload {label} must be an object")
    return value


def _require_text(row: dict[str, Any], key: str, label: str) -> None:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise FixtureValidationError(f"runtime payload {label} is required")


def _require_non_empty_list(value: object, label: str) -> None:
    if not isinstance(value, list) or not value:
        raise FixtureValidationError(f"runtime payload {label} must be a non-empty list")


def _has_no_rights_items_limitation(limitations: object) -> bool:
    if not isinstance(limitations, list):
        return False
    for item in limitations:
        if not isinstance(item, str):
            continue
        normalized = item.lower().replace("_", " ")
        if (
            "no rights review items" in normalized
            or "rights review items intentionally empty" in normalized
        ):
            return True
    return False
