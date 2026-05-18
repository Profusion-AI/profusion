"""Generate the fixture-backed M8-GTM receipt packet."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.m8_gtm.fixtures import load_workflow_fixture
from orchestrator.m8_gtm.renderers import render_receipt_html, render_receipt_markdown
from orchestrator.m8_gtm.schemas import (
    EVIDENCE_MODE,
    LOCAL_FIXTURE_LIMITATION,
    M8GTMError,
    NO_COMPLIANCE_LIMITATION,
    NO_LIVE_SEND_LIMITATION,
    WORKFLOW_NAME,
    WORKFLOW_SLUG,
)


def build_artifact_manifest(fixture: dict[str, Any], packet_dir: Path) -> dict[str, Any]:
    """Copy source artifacts into a packet and write their SHA-256 manifest."""

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
            dest_path = artifacts_dir / str(row["run_dir_name"]) / str(row["filename"])
            artifact_rows.append(
                _copy_artifact(
                    artifact_id=_artifact_id(str(row["case_id"]), str(row["artifact_key"])),
                    case_id=str(row["case_id"]),
                    artifact_type=str(row["artifact_type"]),
                    source_path=source_path,
                    dest_path=dest_path,
                    packet_dir=packet_dir,
                    description=_artifact_description(str(row["case_id"]), str(row["artifact_key"])),
                )
            )

    manifest = {
        "manifest_id": f"manifest-{generated_at.replace(':', '').replace('-', '')}-{uuid4().hex[:8]}",
        "workflow_slug": fixture["workflow_slug"],
        "evidence_mode": EVIDENCE_MODE,
        "generated_at": generated_at,
        "source_fixture_path": fixture["fixture_dir"],
        "packet_dir": str(packet_dir),
        "artifacts": artifact_rows,
        "limitations": _limitations(),
    }
    _write_json(packet_dir / "artifact_manifest.json", manifest)
    return manifest


def build_m8_observation(fixture: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    """Build the receipt-local M8 observation payload."""

    workflow = fixture["workflow"]
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
                    "input_artifact_id": _artifact_id(case_id, _key_for_filename(action["input_artifact"])),
                    "output_artifact_id": _artifact_id(case_id, _key_for_filename(action["output_artifact"])),
                    "risk_signal": action["risk_signal"],
                }
            )
        for action in raw_run.get("tool_actions", []):
            tool_actions.append(
                {
                    "case_id": case_id,
                    "action": action["action"],
                    "artifact_id": _artifact_id(case_id, _key_for_filename(action["artifact"])),
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
        "workflow_id": WORKFLOW_SLUG,
        "workflow_name": WORKFLOW_NAME,
        "evidence_mode": EVIDENCE_MODE,
        "source_system": workflow["source_system"],
        "run_id": f"{WORKFLOW_SLUG}-fixture-run",
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

    claims_supported = list(observation["supported_claims"])
    claims_not_supported = list(observation["unsupported_claims"])
    limitations = list(observation["limitations"])
    _require_claim_lists(claims_supported, claims_not_supported, limitations)

    return {
        "receipt_id": f"workflow-receipt-{_now_iso().replace(':', '').replace('-', '')}-{uuid4().hex[:8]}",
        "source_observation_id": observation["observation_id"],
        "source_manifest_id": manifest["manifest_id"],
        "workflow_name": WORKFLOW_NAME,
        "workflow_purpose": (
            "Show when AI-assisted support work crossed a human review boundary "
            "before a final response artifact was marked ready."
        ),
        "evidence_mode": EVIDENCE_MODE,
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
        manifest = build_artifact_manifest(fixture, partial_dir)
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


def _artifact_description(case_id: str, artifact_key: str) -> str:
    labels = {
        "run": "Run metadata fixture.",
        "inbound_message": "Inbound support message artifact.",
        "ai_classification": "AI classification artifact.",
        "ai_draft_reply": "AI draft reply artifact.",
        "human_review_event": "Human review boundary artifact.",
        "final_reply": "Final reply artifact marked ready in the fixture log.",
        "execution_log": "Local fixture execution log.",
    }
    return f"{case_id}: {labels.get(artifact_key, artifact_key)}"


def _key_for_filename(filename: str) -> str:
    return {
        "run.json": "run",
        "inbound_message.md": "inbound_message",
        "ai_classification.json": "ai_classification",
        "ai_draft_reply.md": "ai_draft_reply",
        "human_review_event.json": "human_review_event",
        "final_reply.md": "final_reply",
        "execution_log.json": "execution_log",
    }[filename]


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
