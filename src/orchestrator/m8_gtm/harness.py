"""Generate the fixture-backed M8-GTM receipt packet."""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.m8_gtm.fixtures import load_workflow_fixture
from orchestrator.m8_gtm.registry import (
    AICE_SLUG,
    SUPPORT_TRIAGE_SLUG,
    WorkflowSpec,
    get_workflow_spec,
)
from orchestrator.m8_gtm.renderers import render_receipt_html, render_receipt_markdown
from orchestrator.m8_gtm.runtime_payloads import (
    WORKSPACE_RUNTIME_EVIDENCE_MODE,
    validate_aice_runtime_payload,
)
from orchestrator.m8_gtm.schemas import (
    LOCAL_FIXTURE_LIMITATION,
    M8GTMError,
    NO_COMPLIANCE_LIMITATION,
    NO_LIVE_SEND_LIMITATION,
)


def build_artifact_manifest(fixture: dict[str, Any], packet_dir: Path) -> dict[str, Any]:
    """Copy source artifacts into a packet and write their SHA-256 manifest."""

    spec: WorkflowSpec = fixture["workflow_spec"]
    packet_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir = packet_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    generated_at = _now_iso()
    artifact_rows: list[dict[str, Any]] = []

    workflow_path = Path(str(fixture["workflow_path"]))
    workflow_dest = artifacts_dir / "workflow.json"
    artifact_rows.append(
        _copy_artifact(
            artifact_id="workflow.workflow_json",
            case_id="workflow",
            artifact_type="workflow_json",
            source_path=workflow_path,
            dest_path=workflow_dest,
            packet_dir=packet_dir,
            description="Static n8n-style workflow fixture snapshot.",
        )
    )

    for run in fixture["runs"]:
        for row in run["artifact_files"]:
            source_path = Path(str(row["source_path"]))
            if row.get("flat_packet_path"):
                dest_path = artifacts_dir / str(row["filename"])
            else:
                dest_path = artifacts_dir / str(row["run_dir_name"]) / str(row["filename"])
            artifact_rows.append(
                _copy_artifact(
                    artifact_id=_artifact_id(str(row["case_id"]), str(row["artifact_key"])),
                    case_id=str(row["case_id"]),
                    artifact_type=str(row["artifact_type"]),
                    source_path=source_path,
                    dest_path=dest_path,
                    packet_dir=packet_dir,
                    description=_artifact_description(
                        str(row["case_id"]),
                        str(row["artifact_key"]),
                        spec,
                    ),
                )
            )

    manifest = {
        "manifest_id": f"manifest-{generated_at.replace(':', '').replace('-', '')}-{uuid4().hex[:8]}",
        "workflow_slug": fixture["workflow_slug"],
        "evidence_mode": spec.evidence_mode,
        "generated_at": generated_at,
        "source_fixture_path": fixture["fixture_dir"],
        "packet_dir": str(packet_dir),
        "artifacts": artifact_rows,
        "limitations": _manifest_limitations(spec),
    }
    _write_json(packet_dir / "artifact_manifest.json", manifest)
    return manifest


def build_m8_observation(fixture: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    """Build the receipt-local M8 observation payload."""

    if fixture["workflow_slug"] == AICE_SLUG:
        return _build_aice_observation(fixture, manifest)
    if fixture["workflow_slug"] != SUPPORT_TRIAGE_SLUG:
        raise M8GTMError(f"Unsupported observation workflow: {fixture['workflow_slug']}")

    workflow = fixture["workflow"]
    spec: WorkflowSpec = fixture["workflow_spec"]
    runs = fixture["runs"]
    observed_at = _now_iso()
    ai_actions = []
    tool_actions = []
    human_reviews = []
    outcomes = {}
    failure_state = {"status": "none", "details": "No failure or retry occurred in the fixture runs."}

    for run in runs:
        case_id = str(run["case_id"])
        raw_run = run["run"]
        outcomes[case_id] = raw_run["outcome"]
        for action in raw_run.get("ai_actions", []):
            ai_actions.append(
                {
                    "case_id": case_id,
                    "action": action["action"],
                    "input_artifact_id": _artifact_id(
                        case_id,
                        _key_for_filename(action["input_artifact"], spec),
                    ),
                    "output_artifact_id": _artifact_id(
                        case_id,
                        _key_for_filename(action["output_artifact"], spec),
                    ),
                    "risk_signal": action["risk_signal"],
                }
            )
        for action in raw_run.get("tool_actions", []):
            tool_actions.append(
                {
                    "case_id": case_id,
                    "action": action["action"],
                    "artifact_id": _artifact_id(
                        case_id,
                        _key_for_filename(action["artifact"], spec),
                    ),
                    "description": action["description"],
                }
            )
        review = run["artifacts"].get("human_review_event")
        if isinstance(review, dict):
            human_reviews.append(
                {
                    "case_id": review["case_id"],
                    "reviewer": review["reviewer"],
                    "decision": review["decision"],
                    "reviewed_artifact_ids": review["reviewed_artifact_ids"],
                    "resulting_artifact_id": review["resulting_artifact_id"],
                    "review_summary": review.get("review_summary"),
                    "reviewed_at": review.get("reviewed_at"),
                }
            )
        raw_failure = raw_run.get("failure_or_retry_state")
        if isinstance(raw_failure, dict) and raw_failure.get("status") != "none":
            failure_state = raw_failure

    supported_claims = [
        "Human review occurred before the sensitive billing complaint final response was marked ready to send.",
        "The routine invoice request proceeded without a human review boundary in the local fixture.",
        "The generated packet captured workflow, inbound, AI classification, AI draft, human review, final reply, and execution log artifacts.",
    ]
    unsupported_claims = [
        "The receipt does not prove that the customer's billing claim was factually correct.",
        "The receipt does not prove live n8n, Gmail, Slack, Google Sheets, HubSpot, or n8n API execution.",
        "The receipt does not prove that any customer message was sent.",
    ]
    limitations = _limitations()
    _require_claim_lists(supported_claims, unsupported_claims, limitations)

    return {
        "observation_id": f"m8-gtm-observation-{observed_at.replace(':', '').replace('-', '')}-{uuid4().hex[:8]}",
        "source_manifest_id": manifest["manifest_id"],
        "workflow_id": spec.slug,
        "workflow_name": spec.name,
        "evidence_mode": spec.evidence_mode,
        "source_system": workflow["source_system"],
        "run_id": f"{spec.slug}-fixture-run",
        "case_ids": [str(run["case_id"]) for run in runs],
        "observed_at": observed_at,
        "workflow_boundary": workflow["workflow_boundary"],
        "trigger_summary": workflow["trigger_summary"],
        "ai_actions_observed": ai_actions,
        "tool_actions_observed": tool_actions,
        "human_review_events": human_reviews,
        "artifacts_captured": [
            {"artifact_id": row["artifact_id"]} for row in manifest["artifacts"]
        ],
        "outcome": outcomes,
        "failure_or_retry_state": failure_state,
        "supported_claims": supported_claims,
        "unsupported_claims": unsupported_claims,
        "limitations": limitations,
        "next_recommended_review": (
            "Review the generated receipt packet with Kyle before using it in a demo, "
            "design-partner conversation, or P1 HyperFrames video."
        ),
    }


def build_workflow_receipt(
    observation: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """Build the buyer-readable workflow receipt JSON payload."""

    if observation["workflow_id"] == AICE_SLUG:
        return _build_aice_workflow_receipt(observation, manifest)

    claims_supported = list(observation["supported_claims"])
    claims_not_supported = list(observation["unsupported_claims"])
    limitations = list(observation["limitations"])
    _require_claim_lists(claims_supported, claims_not_supported, limitations)

    return {
        "receipt_id": f"workflow-receipt-{_now_iso().replace(':', '').replace('-', '')}-{uuid4().hex[:8]}",
        "source_observation_id": observation["observation_id"],
        "source_manifest_id": manifest["manifest_id"],
        "workflow_name": observation["workflow_name"],
        "workflow_purpose": (
            "Show when AI-assisted support work crossed a human review boundary "
            "before a final response artifact was marked ready."
        ),
        "evidence_mode": observation["evidence_mode"],
        "evidence_boundary": observation["workflow_boundary"],
        "what_happened": [
            "A routine invoice request was classified, drafted, and marked ready in the local fixture.",
            "A sensitive billing complaint was classified as sensitive and routed through human review.",
            "The human reviewer edited the sensitive-case draft before the final reply artifact was marked ready.",
        ],
        "where_ai_acted": [
            f"{row['case_id']}: {row['action']} produced {row['output_artifact_id']}"
            for row in observation["ai_actions_observed"]
        ],
        "where_human_review_entered": [
            (
                f"{row['case_id']}: {row['reviewer']} {row['decision']} "
                f"{', '.join(row['reviewed_artifact_ids'])} before {row['resulting_artifact_id']}."
            )
            for row in observation["human_review_events"]
        ],
        "artifacts_reviewed": [
            {
                "artifact_id": row["artifact_id"],
                "label": row["description"],
                "packet_path": row["packet_path"],
            }
            for row in manifest["artifacts"]
        ],
        "final_action": observation["outcome"],
        "QA_or_review_status": (
            "Sensitive case reviewed by a human in the fixture; routine case did not require review."
        ),
        "claims_supported": claims_supported,
        "claims_not_supported": claims_not_supported,
        "limitations": limitations,
        "next_recommended_review": observation["next_recommended_review"],
        "generated_at": _now_iso(),
    }


def _build_aice_observation(fixture: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    workflow = fixture["workflow"]
    spec: WorkflowSpec = fixture["workflow_spec"]
    run = fixture["runs"][0]
    raw_run = run["run"]
    artifacts = run["artifacts"]
    observed_at = _now_iso()

    n8n_run = artifacts["n8n_run_summary"]
    topic_brief = artifacts["topic_brief"]
    source_cards = artifacts["source_cards"]
    quote_candidates = artifacts["quote_candidates"]
    claim_map = artifacts["claim_map"]
    attention_map = artifacts["attention_intelligence_map"]
    rights_review = artifacts["rights_review"]
    ambiguity_register = artifacts["ambiguity_register"]
    human_review = artifacts["human_editorial_review"]
    narrative_brief = artifacts["narrative_brief"]
    visual_plan = artifacts["visual_plan"]

    quotes = quote_candidates.get("quote_candidates", quote_candidates.get("candidates", []))
    ambiguities = ambiguity_register.get("ambiguities", ambiguity_register.get("items", []))

    ai_actions = [
        {
            "case_id": run["case_id"],
            "action": action["action"],
            "input_artifact_id": _artifact_id(
                str(run["case_id"]),
                _key_for_filename(action["input_artifact"], spec),
            ),
            "output_artifact_id": _artifact_id(
                str(run["case_id"]),
                _key_for_filename(action["output_artifact"], spec),
            ),
            "risk_signal": action["risk_signal"],
        }
        for action in raw_run.get("ai_actions", [])
    ]
    human_reviews = [
        {
            "case_id": run["case_id"],
            "reviewer": human_review["reviewer"],
            "decision": human_review["decision"],
            "reviewed_artifact_ids": human_review.get("reviewed_artifacts", []),
            "resulting_artifact_id": "narrative_brief",
            "review_summary": human_review.get("approval_summary"),
            "reviewed_at": human_review.get("reviewed_at"),
        }
    ]

    if spec.evidence_mode == WORKSPACE_RUNTIME_EVIDENCE_MODE:
        supported_claims = [
            (
                "The n8n workspace workflow executed and returned a workspace "
                "runtime payload used for Profusion receipt generation."
            ),
            f"At least three n8n workspace nodes participated in the run; the recorded node count is {n8n_run['node_count']}.",
            "A topic/thesis artifact was captured from the workspace runtime payload.",
            "At least one runtime source card was captured.",
            "At least one runtime claim candidate was mapped to a source card.",
            "At least one quote or segment candidate was captured as metadata/reference only.",
            "At least one Attention Intelligence dimension was mapped.",
            "At least one rights, risk, or ambiguity item was recorded.",
            "A human editorial review artifact exists for the narrative decision.",
            "A receipt packet was generated from runtime payload artifacts with hashes.",
            "The receipt includes supported claims, unsupported claims, and limitations.",
        ]
        limitations = _aice_runtime_limitations(n8n_run.get("limitations", []))
    else:
        supported_claims = [
            "The n8n workflow executed in the recorded P0.1.1 live-minimum path.",
            f"At least three n8n nodes participated in the run; the recorded node count is {n8n_run['node_count']}.",
            "A topic/thesis artifact was captured for the AICE workflow.",
            "At least one source card was captured.",
            "At least one claim candidate was mapped to a source card.",
            "At least one quote or segment candidate was captured as metadata/reference only.",
            "At least one Attention Intelligence dimension was mapped.",
            "At least one rights, risk, or ambiguity item was recorded.",
            "A human editorial review artifact exists for the narrative decision.",
            "A receipt packet was generated with artifact hashes.",
            "The receipt includes supported claims, unsupported claims, and limitations.",
        ]
        limitations = _aice_limitations()
    unsupported_claims = _aice_unsupported_claims()
    _require_claim_lists(supported_claims, unsupported_claims, limitations)

    return {
        "observation_id": f"m8-gtm-aice-observation-{observed_at.replace(':', '').replace('-', '')}-{uuid4().hex[:8]}",
        "source_manifest_id": manifest["manifest_id"],
        "workflow_id": spec.slug,
        "workflow_name": spec.name,
        "trust_domain": workflow["trust_domain"],
        "evidence_mode": spec.evidence_mode,
        "source_system": workflow["source_system"],
        "run_id": raw_run["run_id"],
        "case_ids": [str(run["case_id"])],
        "observed_at": observed_at,
        "workflow_boundary": workflow["workflow_boundary"],
        "trigger_summary": workflow["trigger_summary"],
        "topic_brief": topic_brief,
        "source_cards": source_cards.get("sources", []),
        "quote_candidates": quotes,
        "claim_map": claim_map.get("claims", []),
        "attention_intelligence_map": attention_map.get("mapped_dimensions", []),
        "rights_review": rights_review,
        "ambiguity_register": ambiguities,
        "human_review_events": human_reviews,
        "narrative_brief": narrative_brief,
        "visual_plan": visual_plan,
        "n8n_execution": {
            "workspace_workflow_id": n8n_run.get("workspace_workflow_id"),
            "workspace_url": n8n_run.get("workspace_url"),
            "execution_id": n8n_run["execution_id"],
            "execution_url": n8n_run.get("execution_url"),
            "status": n8n_run["status"],
            "execution_mode": n8n_run["execution_mode"],
            "run_timestamp": n8n_run["run_timestamp"],
            "input_topic": n8n_run["input_topic"],
            "node_count": n8n_run["node_count"],
            "nodes_executed": n8n_run["nodes_executed"],
            "generated_artifacts": n8n_run["generated_artifacts"],
            "receipt_packet_path": n8n_run["receipt_packet_path"],
            "output_receipt_path": n8n_run["output_receipt_path"],
            "limitations": n8n_run.get("limitations", []),
        },
        "ai_actions_observed": ai_actions,
        "artifacts_captured": [
            {"artifact_id": row["artifact_id"]} for row in manifest["artifacts"]
        ],
        "outcome": raw_run["outcome"],
        "failure_or_retry_state": raw_run.get(
            "failure_or_retry_state",
            {"status": "none", "details": "No failure or retry occurred."},
        ),
        "supported_claims": supported_claims,
        "unsupported_claims": unsupported_claims,
        "limitations": limitations,
        "next_recommended_review": (
            "Run Kyle's editorial review against live source metadata before any "
            "external AICE demo, script draft, generated media plan, or publication step."
        ),
    }


def _build_aice_workflow_receipt(
    observation: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    claims_supported = list(observation["supported_claims"])
    claims_not_supported = list(observation["unsupported_claims"])
    limitations = list(observation["limitations"])
    _require_claim_lists(claims_supported, claims_not_supported, limitations)

    topic = observation["topic_brief"]
    narrative = observation["narrative_brief"]
    visual_plan = observation["visual_plan"]
    n8n_execution = observation["n8n_execution"]
    ambiguities = observation["ambiguity_register"]

    return {
        "receipt_id": f"workflow-receipt-{_now_iso().replace(':', '').replace('-', '')}-{uuid4().hex[:8]}",
        "source_observation_id": observation["observation_id"],
        "source_manifest_id": manifest["manifest_id"],
        "workflow_name": observation["workflow_name"],
        "workflow_purpose": (
            "Show how AI-assisted source-to-narrative work was captured, bounded, "
            "reviewed, and converted into a reviewer-readable receipt before publication decisions."
        ),
        "trust_domain": observation["trust_domain"],
        "evidence_mode": observation["evidence_mode"],
        "evidence_boundary": observation["workflow_boundary"],
        "topic_episode_thesis": (
            f"{topic['title']}: {topic['editorial_question']}"
        ),
        "what_happened": [
            "A topic/thesis artifact entered the AICE source-to-narrative workflow.",
            "n8n passed the topic through source metadata, claim extraction, rights/ambiguity classification, and receipt-generation nodes.",
            "Quote and segment candidates remained metadata/reference only.",
            "Unsupported claims were held out of the narrative brief.",
            "Human editorial review marked the brief for internal demo use only.",
        ],
        "where_ai_acted": [
            f"{row['case_id']}: {row['action']} produced {row['output_artifact_id']} with risk signal {row['risk_signal']}."
            for row in observation["ai_actions_observed"]
        ],
        "where_n8n_acted": [
            f"{index + 1}. {node}"
            for index, node in enumerate(n8n_execution["nodes_executed"])
        ],
        "where_human_review_entered": [
            (
                f"{row['case_id']}: {row['reviewer']} recorded {row['decision']} "
                f"after reviewing {', '.join(row['reviewed_artifact_ids'])}."
            )
            for row in observation["human_review_events"]
        ],
        "source_cards": observation["source_cards"],
        "quote_candidates": observation["quote_candidates"],
        "claims_and_quote_candidates": {
            "claims": observation["claim_map"],
            "quote_candidates": observation["quote_candidates"],
        },
        "rights_use_ambiguity_classification": {
            "rights_review": observation["rights_review"],
            "ambiguities": ambiguities,
        },
        "attention_intelligence_mapping": observation["attention_intelligence_map"],
        "narrative_decisions": narrative.get("brief", []),
        "generated_synthetic_media_plan": visual_plan,
        "artifacts_reviewed": [
            {
                "artifact_id": row["artifact_id"],
                "label": row["description"],
                "packet_path": row["packet_path"],
            }
            for row in manifest["artifacts"]
        ],
        "final_action": {
            "outcome": observation["outcome"],
            "publication_state": narrative["allowed_use"],
            "n8n_status": n8n_execution["status"],
        },
        "claims_supported": claims_supported,
        "claims_not_supported": claims_not_supported,
        "ambiguities_preserved": ambiguities,
        "limitations": limitations,
        "next_recommended_review": observation["next_recommended_review"],
        "generated_at": _now_iso(),
    }


def generate_demo_packet(
    workflow_slug: str,
    output_root: Path | None = None,
    fixture_root: Path | None = None,
) -> dict[str, Any]:
    """Generate the complete P0 receipt packet atomically."""

    if output_root is None:
        from orchestrator import config

        output_root = config.RECEIPTS_DIR / "m8-gtm"

    fixture = load_workflow_fixture(workflow_slug, fixture_root=fixture_root)
    receipt_id = f"receipt-{_now_iso().replace(':', '').replace('-', '')}-{uuid4().hex[:8]}"
    slug_root = output_root / workflow_slug
    final_dir = slug_root / receipt_id
    partial_dir = slug_root / f"{receipt_id}.partial"
    if partial_dir.exists() or final_dir.exists():
        raise M8GTMError(f"Receipt packet already exists: {final_dir}")

    try:
        if workflow_slug == AICE_SLUG:
            _stamp_aice_n8n_receipt_paths(fixture, final_dir)
        manifest = build_artifact_manifest(fixture, partial_dir)
        if workflow_slug == AICE_SLUG:
            _rewrite_aice_n8n_summary_artifact(fixture, manifest, partial_dir)
        manifest["packet_dir"] = str(final_dir)
        _write_json(partial_dir / "artifact_manifest.json", manifest)

        observation = build_m8_observation(fixture, manifest)
        receipt = build_workflow_receipt(observation, manifest)
        receipt["receipt_id"] = receipt_id

        _write_json(partial_dir / "m8_observation.json", observation)
        _write_json(partial_dir / "workflow_receipt.json", receipt)
        (partial_dir / "workflow_receipt.md").write_text(
            render_receipt_markdown(receipt),
            encoding="utf-8",
        )
        (partial_dir / "workflow_receipt.html").write_text(
            render_receipt_html(receipt),
            encoding="utf-8",
        )
        _assert_required_packet_files(partial_dir)
        partial_dir.rename(final_dir)
    except Exception:
        if partial_dir.exists():
            shutil.rmtree(partial_dir)
        raise

    return {
        "receipt_id": receipt_id,
        "packet_dir": final_dir,
        "artifact_manifest": final_dir / "artifact_manifest.json",
        "m8_observation": final_dir / "m8_observation.json",
        "workflow_receipt_json": final_dir / "workflow_receipt.json",
        "workflow_receipt_md": final_dir / "workflow_receipt.md",
        "workflow_receipt_html": final_dir / "workflow_receipt.html",
        "manifest": manifest,
        "observation": observation,
        "receipt": receipt,
    }


def generate_packet_from_runtime_payload(
    workflow_slug: str,
    payload: dict[str, Any],
    output_root: Path | None = None,
) -> dict[str, Any]:
    """Generate a complete AICE packet from n8n runtime payload data."""

    if workflow_slug != AICE_SLUG:
        raise M8GTMError("runtime payload generation is currently supported only for AICE")
    if output_root is None:
        from orchestrator import config

        output_root = config.RECEIPTS_DIR / "m8-gtm"

    normalized = validate_aice_runtime_payload(payload)
    receipt_id = f"receipt-{_now_iso().replace(':', '').replace('-', '')}-{uuid4().hex[:8]}"
    slug_root = output_root / workflow_slug
    final_dir = slug_root / receipt_id
    partial_dir = slug_root / f"{receipt_id}.partial"
    if partial_dir.exists() or final_dir.exists():
        raise M8GTMError(f"Receipt packet already exists: {final_dir}")

    fixture = _aice_runtime_payload_to_fixture(normalized, final_dir)
    try:
        manifest = _build_runtime_artifact_manifest(fixture, normalized, partial_dir)
        manifest["packet_dir"] = str(final_dir)
        _write_json(partial_dir / "artifact_manifest.json", manifest)

        observation = build_m8_observation(fixture, manifest)
        receipt = build_workflow_receipt(observation, manifest)
        receipt["receipt_id"] = receipt_id

        _write_json(partial_dir / "m8_observation.json", observation)
        _write_json(partial_dir / "workflow_receipt.json", receipt)
        (partial_dir / "workflow_receipt.md").write_text(
            render_receipt_markdown(receipt),
            encoding="utf-8",
        )
        (partial_dir / "workflow_receipt.html").write_text(
            render_receipt_html(receipt),
            encoding="utf-8",
        )
        _assert_required_packet_files(partial_dir)
        partial_dir.rename(final_dir)
    except Exception:
        if partial_dir.exists():
            shutil.rmtree(partial_dir)
        raise

    return {
        "receipt_id": receipt_id,
        "packet_dir": final_dir,
        "artifact_manifest": final_dir / "artifact_manifest.json",
        "m8_observation": final_dir / "m8_observation.json",
        "workflow_receipt_json": final_dir / "workflow_receipt.json",
        "workflow_receipt_md": final_dir / "workflow_receipt.md",
        "workflow_receipt_html": final_dir / "workflow_receipt.html",
        "manifest": manifest,
        "observation": observation,
        "receipt": receipt,
    }


def _aice_runtime_payload_to_fixture(
    payload: dict[str, Any],
    final_dir: Path,
) -> dict[str, Any]:
    spec = replace(
        get_workflow_spec(AICE_SLUG),
        evidence_mode=WORKSPACE_RUNTIME_EVIDENCE_MODE,
    )
    topic = payload["topic_brief"]
    run_id = f"{AICE_SLUG}-workspace-runtime-{payload['n8n_execution_id']}"
    artifacts = {
        "topic_brief": topic,
        "source_cards": payload["source_cards"],
        "quote_candidates": payload["quote_candidates"],
        "claim_map": payload["claim_map"],
        "attention_intelligence_map": payload["attention_intelligence_map"],
        "rights_review": payload["rights_review"],
        "ambiguity_register": payload["ambiguity_register"],
        "human_editorial_review": payload["human_editorial_review"],
        "narrative_brief": payload["narrative_brief"],
        "visual_plan": payload["visual_plan"],
        "execution_log": _runtime_execution_log(payload),
        "n8n_run_summary": _runtime_n8n_summary(payload, final_dir),
    }
    run = {
        "run_id": run_id,
        "case_id": "workspace_runtime_aice",
        "case_dir": "runtime_payload",
        "run": {
            "run_id": run_id,
            "case_id": "workspace_runtime_aice",
            "workflow_slug": AICE_SLUG,
            "evidence_mode": WORKSPACE_RUNTIME_EVIDENCE_MODE,
            "outcome": {
                "status": "receipt_generated_from_runtime_payload",
                "publication_state": payload["narrative_brief"]["allowed_use"],
            },
            "ai_actions": [
                {
                    "action": "n8n built runtime source cards",
                    "input_artifact": "topic_brief.json",
                    "output_artifact": "source_cards.json",
                    "risk_signal": "source_context_required",
                },
                {
                    "action": "n8n mapped runtime claims and quote candidates",
                    "input_artifact": "source_cards.json",
                    "output_artifact": "claim_map.json",
                    "risk_signal": "unsupported_claims_must_remain_visible",
                },
                {
                    "action": "n8n prepared runtime narrative brief",
                    "input_artifact": "claim_map.json",
                    "output_artifact": "narrative_brief.json",
                    "risk_signal": "human_editorial_review_required",
                },
            ],
            "failure_or_retry_state": {
                "status": "none",
                "details": "No failure or retry occurred in the runtime payload proof.",
            },
        },
        "artifacts": artifacts,
        "artifact_files": [],
    }
    return {
        "workflow_slug": AICE_SLUG,
        "workflow_spec": spec,
        "workflow": {
            "workflow_slug": AICE_SLUG,
            "workflow_name": spec.name,
            "trust_domain": "ai_assisted_investigative_content",
            "source_system": "n8n",
            "evidence_mode": WORKSPACE_RUNTIME_EVIDENCE_MODE,
            "workflow_boundary": (
                "Profusion documents an n8n workspace runtime AICE workflow: "
                "topic brief, metadata-only source cards, quote candidates, "
                "claim mapping, rights review, ambiguity register, human "
                "editorial review, and receipt generation from the payload "
                "that moved through the workspace execution."
            ),
            "trigger_summary": (
                f"n8n workspace workflow {payload['n8n_workspace_workflow_id']} "
                f"execution {payload['n8n_execution_id']} passed runtime AICE "
                "data into Profusion receipt generation."
            ),
        },
        "fixture_dir": "runtime_payload",
        "workflow_path": "runtime_payload",
        "runs": [run],
    }


def _runtime_execution_log(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_timestamp": payload["executed_at"],
        "workflow_slug": AICE_SLUG,
        "execution_mode": WORKSPACE_RUNTIME_EVIDENCE_MODE,
        "workspace_workflow_id": payload["n8n_workspace_workflow_id"],
        "execution_id": payload["n8n_execution_id"],
        "nodes_executed": payload["nodes_executed"],
        "limitations": payload["limitations"],
    }


def _runtime_n8n_summary(payload: dict[str, Any], final_dir: Path) -> dict[str, Any]:
    return {
        "workflow_slug": AICE_SLUG,
        "workspace_workflow_id": payload["n8n_workspace_workflow_id"],
        "workspace_url": payload.get("n8n_workspace_url"),
        "execution_id": payload["n8n_execution_id"],
        "execution_url": payload.get("n8n_execution_url"),
        "status": payload.get("status", "success"),
        "execution_mode": WORKSPACE_RUNTIME_EVIDENCE_MODE,
        "run_timestamp": payload["executed_at"],
        "input_topic": payload["topic_brief"].get("title"),
        "node_count": payload["node_count"],
        "nodes_executed": payload["nodes_executed"],
        "generated_artifacts": [
            "topic_brief.json",
            "source_cards.json",
            "quote_candidates.json",
            "claim_map.json",
            "rights_review.json",
            "ambiguity_register.json",
            "human_editorial_review.json",
            "narrative_brief.json",
            "visual_plan.json",
            "workflow_receipt.html",
        ],
        "receipt_packet_path": str(final_dir),
        "output_receipt_path": str(final_dir / "workflow_receipt.html"),
        "limitations": payload["limitations"],
    }


def _build_runtime_artifact_manifest(
    fixture: dict[str, Any],
    payload: dict[str, Any],
    packet_dir: Path,
) -> dict[str, Any]:
    spec: WorkflowSpec = fixture["workflow_spec"]
    packet_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir = packet_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    generated_at = _now_iso()
    run = fixture["runs"][0]
    artifact_rows = [
        _write_runtime_artifact(
            artifact_id="runtime.runtime_payload",
            case_id="workspace_runtime_aice",
            artifact_type="runtime_payload",
            payload=payload,
            dest_path=artifacts_dir / "runtime_payload.json",
            packet_dir=packet_dir,
            description="Original validated n8n runtime payload.",
        )
    ]
    artifact_specs_by_key = {
        artifact_spec.artifact_key: artifact_spec for artifact_spec in spec.artifact_specs
    }
    for artifact_key, artifact_payload in run["artifacts"].items():
        artifact_spec = artifact_specs_by_key.get(artifact_key)
        filename = artifact_spec.filename if artifact_spec else f"{artifact_key}.json"
        artifact_rows.append(
            _write_runtime_artifact(
                artifact_id=_artifact_id("workspace_runtime_aice", artifact_key),
                case_id="workspace_runtime_aice",
                artifact_type=(
                    artifact_spec.artifact_type if artifact_spec else artifact_key
                ),
                payload=artifact_payload,
                dest_path=artifacts_dir / filename,
                packet_dir=packet_dir,
                description=_artifact_description(
                    "workspace_runtime_aice",
                    artifact_key,
                    spec,
                ),
            )
        )

    manifest = {
        "manifest_id": f"manifest-{generated_at.replace(':', '').replace('-', '')}-{uuid4().hex[:8]}",
        "workflow_slug": AICE_SLUG,
        "evidence_mode": WORKSPACE_RUNTIME_EVIDENCE_MODE,
        "generated_at": generated_at,
        "source_fixture_path": None,
        "source_runtime_payload": "artifacts/runtime_payload.json",
        "packet_dir": str(packet_dir),
        "artifacts": artifact_rows,
        "limitations": _aice_runtime_limitations(payload.get("limitations", [])),
    }
    _write_json(packet_dir / "artifact_manifest.json", manifest)
    return manifest


def _write_runtime_artifact(
    *,
    artifact_id: str,
    case_id: str,
    artifact_type: str,
    payload: dict[str, Any],
    dest_path: Path,
    packet_dir: Path,
    description: str,
) -> dict[str, Any]:
    _write_json(dest_path, payload)
    return {
        "artifact_id": artifact_id,
        "case_id": case_id,
        "artifact_type": artifact_type,
        "source_path": "runtime_payload",
        "packet_path": str(dest_path.relative_to(packet_dir)),
        "sha256": _sha256(dest_path),
        "description": description,
        "redaction_state": "none",
    }


def _stamp_aice_n8n_receipt_paths(fixture: dict[str, Any], final_dir: Path) -> None:
    """Record the generated packet path in the in-memory AICE n8n summary."""

    run = fixture["runs"][0]
    n8n_run_summary = run["artifacts"].get("n8n_run_summary")
    if not isinstance(n8n_run_summary, dict):
        return
    n8n_run_summary["receipt_packet_path"] = str(final_dir)
    n8n_run_summary["output_receipt_path"] = str(final_dir / "workflow_receipt.html")


def _rewrite_aice_n8n_summary_artifact(
    fixture: dict[str, Any],
    manifest: dict[str, Any],
    packet_dir: Path,
) -> None:
    """Persist generated receipt paths and refresh the manifest hash."""

    run = fixture["runs"][0]
    n8n_run_summary = run["artifacts"].get("n8n_run_summary")
    if not isinstance(n8n_run_summary, dict):
        return

    for row in manifest["artifacts"]:
        if row["artifact_type"] != "n8n_run_summary":
            continue
        dest_path = packet_dir / str(row["packet_path"])
        _write_json(dest_path, n8n_run_summary)
        row["sha256"] = _sha256(dest_path)
        return


def _copy_artifact(
    *,
    artifact_id: str,
    case_id: str,
    artifact_type: str,
    source_path: Path,
    dest_path: Path,
    packet_dir: Path,
    description: str,
) -> dict[str, Any]:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, dest_path)
    return {
        "artifact_id": artifact_id,
        "case_id": case_id,
        "artifact_type": artifact_type,
        "source_path": str(source_path),
        "packet_path": str(dest_path.relative_to(packet_dir)),
        "sha256": _sha256(dest_path),
        "description": description,
        "redaction_state": "none",
    }


def _artifact_id(case_id: str, artifact_key: str) -> str:
    return f"{case_id}.{artifact_key}"


def _artifact_description(case_id: str, artifact_key: str, spec: WorkflowSpec) -> str:
    support_labels = {
        "run": "Run metadata fixture.",
        "inbound_message": "Inbound support message artifact.",
        "ai_classification": "AI classification artifact.",
        "ai_draft_reply": "AI draft reply artifact.",
        "human_review_event": "Human review boundary artifact.",
        "final_reply": "Final reply artifact marked ready in the fixture log.",
        "execution_log": "Local fixture execution log.",
    }
    aice_labels = {
        "run": "AICE run metadata fixture.",
        "topic_brief": "AICE topic and thesis artifact.",
        "source_cards": "Candidate source-card artifact.",
        "quote_candidates": "Metadata-only quote and segment candidate artifact.",
        "claim_map": "Claim-to-source mapping artifact.",
        "attention_intelligence_map": "Attention Intelligence dimension mapping artifact.",
        "rights_review": "Rights and use classification artifact.",
        "ambiguity_register": "Explicit ambiguity register artifact.",
        "human_editorial_review": "Human editorial review boundary artifact.",
        "narrative_brief": "Narrative brief generated from approved or contextualized claims.",
        "visual_plan": "Generated and synthetic media planning artifact.",
        "execution_log": "Local AICE execution log artifact.",
        "n8n_run_summary": "Live n8n run summary artifact.",
    }
    labels = aice_labels if spec.slug == AICE_SLUG else support_labels
    return f"{case_id}: {labels.get(artifact_key, artifact_key)}"


def _key_for_filename(filename: str, spec: WorkflowSpec) -> str:
    return spec.artifact_specs_by_filename[filename].artifact_key


def _aice_unsupported_claims() -> list[str]:
    return [
        "This receipt does not certify factual truth.",
        "This receipt does not certify copyright clearance.",
        "This receipt does not certify fair use.",
        "This receipt does not prove that third-party video/audio may be downloaded, edited, republished, or monetized.",
        "This receipt does not prove platform-policy compliance.",
        "This receipt does not certify journalistic neutrality.",
        "This receipt does not imply PBS/Frontline affiliation or endorsement.",
        "This receipt does not mean the final content is safe to publish.",
        "This receipt does not replace human editorial or legal review.",
        "This receipt only shows what was captured, classified, reviewed, limited, and generated inside the recorded workflow boundary.",
    ]


def _aice_limitations() -> list[str]:
    return [
        "The n8n path is a P0.1.1 live-minimum workflow and may use controlled fallback source metadata when external credentials are unavailable.",
        "Media candidates remain metadata/reference-only; no third-party audio/video is downloaded, packaged, edited, republished, or monetized.",
        "The packet records source cards, claim mappings, rights/risk classification, ambiguity states, human editorial review, and generated receipt artifacts.",
        "The receipt is not a publication, legal, compliance, rights-clearance, journalistic-neutrality, or platform-policy approval mechanism.",
    ]


def _aice_runtime_limitations(payload_limitations: list[str]) -> list[str]:
    limitations = [
        "Workspace proof uses controlled runtime metadata generated inside n8n.",
        "Media candidates remain metadata/reference-only; no third-party audio/video is downloaded, packaged, edited, republished, or monetized.",
        "The packet records source cards, claim mappings, rights/risk classification, ambiguity states, human editorial review, and generated receipt artifacts from the runtime payload.",
        "The receipt is not a publication, legal, compliance, rights-clearance, journalistic-neutrality, or platform-policy approval mechanism.",
    ]
    for item in payload_limitations:
        if item not in limitations:
            limitations.append(item)
    return limitations


def _manifest_limitations(spec: WorkflowSpec) -> list[str]:
    if spec.slug == AICE_SLUG:
        return _aice_limitations()
    return _limitations()


def _limitations() -> list[str]:
    return [
        LOCAL_FIXTURE_LIMITATION,
        NO_LIVE_SEND_LIMITATION,
        NO_COMPLIANCE_LIMITATION,
    ]


def _require_claim_lists(
    supported_claims: list[str],
    unsupported_claims: list[str],
    limitations: list[str],
) -> None:
    if not supported_claims:
        raise M8GTMError("supported claims must be non-empty")
    if not unsupported_claims:
        raise M8GTMError("unsupported claims must be non-empty")
    if not limitations:
        raise M8GTMError("limitations must be non-empty")


def _assert_required_packet_files(packet_dir: Path) -> None:
    required = {
        "artifact_manifest.json",
        "m8_observation.json",
        "workflow_receipt.json",
        "workflow_receipt.md",
        "workflow_receipt.html",
    }
    missing = [name for name in sorted(required) if not (packet_dir / name).exists()]
    if missing:
        raise M8GTMError(f"Receipt packet is missing required files: {', '.join(missing)}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
