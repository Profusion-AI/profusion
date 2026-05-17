"""Generate file-first evidence receipts from existing Profusion read models."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator import db
from orchestrator.read_models import inspect_payload

ELIGIBLE_CONTENT_STATUSES = {
    "qa_passed",
    "approved",
    "scheduled",
    "published",
    "measured",
}

RECEIPT_LIFECYCLE = (
    "draft",
    "reviewed",
    "approved_for_packet",
    "delivered",
)
NEXT_RECEIPT_STATUS = dict(zip(RECEIPT_LIFECYCLE, RECEIPT_LIFECYCLE[1:]))

MEDIA_TRUST_BOUNDARY = (
    "Profusion documents the declared workflow, generated artifacts, QA checks, "
    "review state, approval state, and evidence trail for this content workflow. "
    "It does not claim universal synthetic-media detection, identity verification, "
    "liveness verification, or proof that manipulation did not occur outside the "
    "captured workflow."
)


class ReceiptEligibilityError(ValueError):
    """Raised when a content item is not ready for a reviewer receipt."""


class ReceiptTransitionError(ValueError):
    """Raised when a receipt lifecycle transition is invalid."""


@dataclass(frozen=True)
class GeneratedReceipt:
    receipt_id: str
    trust_domain: str
    receipt_type: str
    receipt_status: str
    subject_type: str
    subject_id: str
    packet_dir: Path
    receipt_md: Path
    summary_md: Path
    limitations_md: Path
    reviewer_notes_md: Path
    evidence_json: Path
    created_at: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "trust_domain": self.trust_domain,
            "receipt_type": self.receipt_type,
            "receipt_status": self.receipt_status,
            "subject_type": self.subject_type,
            "subject_id": self.subject_id,
            "packet_dir": str(self.packet_dir),
            "receipt_md": str(self.receipt_md),
            "summary_md": str(self.summary_md),
            "limitations_md": str(self.limitations_md),
            "reviewer_notes_md": str(self.reviewer_notes_md),
            "evidence_json": str(self.evidence_json),
            "created_at": self.created_at,
            "receipt_status_updated_at": self.created_at,
            "status_history": [
                {
                    "from_status": None,
                    "to_status": self.receipt_status,
                    "transitioned_at": self.created_at,
                }
            ],
        }


def generate_content_video_receipt(
    *,
    db_path: Path,
    logs_dir: Path,
    receipts_dir: Path,
    item_id: str,
) -> GeneratedReceipt:
    """Generate a draft content video receipt packet for an eligible content item."""

    item = db.get_item(db_path, item_id)
    if item is None:
        raise ReceiptEligibilityError(f"No content item found for {item_id!r}")

    status = item["status"]
    if status not in ELIGIBLE_CONTENT_STATUSES:
        raise ReceiptEligibilityError(
            f"Content item must be qa_passed or later before a receipt can be drafted; got {status!r}"
        )

    inspected = inspect_payload(db_path, logs_dir, item)
    created_at = _now_iso()
    receipt_id = f"content-video-{item_id[:12]}-{created_at.replace(':', '').replace('-', '')}-{uuid4().hex[:8]}"
    packet_dir = receipts_dir / receipt_id
    packet_dir.mkdir(parents=True, exist_ok=False)

    generated = GeneratedReceipt(
        receipt_id=receipt_id,
        trust_domain="media_trust",
        receipt_type="content_video_receipt",
        receipt_status="draft",
        subject_type="content_item",
        subject_id=item_id,
        packet_dir=packet_dir,
        receipt_md=packet_dir / "receipt.md",
        summary_md=packet_dir / "summary.md",
        limitations_md=packet_dir / "limitations.md",
        reviewer_notes_md=packet_dir / "reviewer_notes.md",
        evidence_json=packet_dir / "evidence.json",
        created_at=created_at,
    )

    evidence = _evidence_payload(generated, inspected)
    _write_packet_files(generated, evidence)
    return generated


def receipts_payload(*, receipts_dir: Path, item_id: str) -> dict[str, Any]:
    """Return generated receipt packet summaries for a content item."""

    receipts: list[dict[str, Any]] = []
    if receipts_dir.exists():
        for evidence_path in receipts_dir.glob("*/evidence.json"):
            try:
                evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            receipt = evidence.get("receipt")
            if not isinstance(receipt, dict):
                continue
            if receipt.get("subject_id") != item_id:
                continue
            receipts.append(receipt)

    receipts.sort(key=lambda row: str(row.get("created_at") or ""), reverse=True)
    return {
        "item_id": item_id,
        "receipt_count": len(receipts),
        "receipts": receipts,
    }


def transition_receipt(
    *,
    receipts_dir: Path,
    receipt_id: str,
    to_status: str,
) -> dict[str, Any]:
    """Move a generated receipt through the approved file-first lifecycle."""

    if to_status not in RECEIPT_LIFECYCLE:
        raise ReceiptTransitionError(
            f"Unsupported receipt status {to_status!r}; "
            f"expected one of {', '.join(RECEIPT_LIFECYCLE)}"
        )
    if Path(receipt_id).name != receipt_id:
        raise ReceiptTransitionError(
            "Receipt id must be a packet directory name, not a path"
        )

    evidence_path = receipts_dir / receipt_id / "evidence.json"
    if not evidence_path.exists():
        raise ReceiptTransitionError(f"No receipt packet found for {receipt_id!r}")

    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ReceiptTransitionError(
            f"Receipt packet {receipt_id!r} has unreadable evidence.json"
        ) from exc

    receipt = evidence.get("receipt")
    if not isinstance(receipt, dict):
        raise ReceiptTransitionError(
            f"Receipt packet {receipt_id!r} is missing receipt metadata"
        )
    if receipt.get("receipt_id") != receipt_id:
        raise ReceiptTransitionError(
            f"Receipt packet {receipt_id!r} metadata id does not match"
        )

    current_status = str(receipt.get("receipt_status") or "")
    if current_status == to_status:
        return receipt

    expected_next = NEXT_RECEIPT_STATUS.get(current_status)
    if expected_next != to_status:
        raise ReceiptTransitionError(
            f"Cannot transition receipt from {current_status or 'unknown'} "
            f"to {to_status}; expected {expected_next or 'no further transition'}"
        )

    transitioned_at = _now_iso()
    receipt["receipt_status"] = to_status
    receipt["receipt_status_updated_at"] = transitioned_at
    history = receipt.get("status_history")
    if not isinstance(history, list):
        history = []
    history.append(
        {
            "from_status": current_status,
            "to_status": to_status,
            "transitioned_at": transitioned_at,
        }
    )
    receipt["status_history"] = history
    evidence["limitations"] = _limitations_for_status(to_status)

    evidence_path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    _update_packet_markdown(
        receipts_dir / receipt_id,
        current_status,
        to_status,
        transitioned_at,
    )
    return receipt


def _evidence_payload(receipt: GeneratedReceipt, inspected: dict[str, Any]) -> dict[str, Any]:
    item = inspected["item"]
    latest_approval = inspected.get("latest_approval")
    latest_render = inspected.get("latest_render_job")
    latest_publish = inspected.get("latest_publish_job")
    latest_qa = inspected.get("latest_qa")
    return {
        "receipt": receipt.to_payload(),
        "subject": {
            "type": receipt.subject_type,
            "id": receipt.subject_id,
            "topic": item.get("topic"),
            "priority": item.get("priority"),
            "source": item.get("source"),
        },
        "workflow": {
            "trust_domain": receipt.trust_domain,
            "receipt_type": receipt.receipt_type,
            "lifecycle_state": inspected.get("lifecycle_state"),
            "content_approval": {
                "decision": latest_approval.get("decision") if latest_approval else None,
                "approved_by": latest_approval.get("approved_by") if latest_approval else None,
                "timestamp": latest_approval.get("timestamp") if latest_approval else None,
            },
            "qa": {
                "present": latest_qa is not None,
                "overall_go_no_go": latest_qa.get("overall_go_no_go") if latest_qa else None,
                "risk_flags_count": len(latest_qa.get("risk_flags", [])) if latest_qa else 0,
                "claims_to_verify_count": len(latest_qa.get("claims_to_verify", [])) if latest_qa else 0,
            },
            "latest_render_job": _job_summary(latest_render),
            "latest_publish_job": _job_summary(latest_publish),
            "next_safe_command": inspected.get("next_safe_command"),
        },
        "artifacts": inspected.get("artifacts", {}),
        "evidence_sources": {
            "brief_present": inspected.get("latest_brief") is not None,
            "script_variant_count": len(inspected.get("script_variants", [])),
            "recent_log_count": len(inspected.get("recent_logs", [])),
            "render_job_count": len(inspected.get("jobs", {}).get("render_jobs", [])),
            "publish_job_count": len(inspected.get("jobs", {}).get("publish_jobs", [])),
        },
        "limitations": _limitations_for_status(receipt.receipt_status),
    }


def _job_summary(job: dict[str, Any] | None) -> dict[str, Any] | None:
    if not job:
        return None
    return {
        "id": job.get("id"),
        "platform": job.get("platform"),
        "status": job.get("status"),
        "published_url": job.get("published_url"),
        "external_post_id": job.get("external_post_id"),
        "published_at": job.get("published_at"),
        "created_at": job.get("created_at"),
        "updated_at": job.get("updated_at"),
    }


def _write_packet_files(receipt: GeneratedReceipt, evidence: dict[str, Any]) -> None:
    subject = evidence["subject"]
    workflow = evidence["workflow"]
    artifacts = evidence["artifacts"]
    summary = (
        f"# Receipt Summary\n\n"
        f"- Receipt: `{receipt.receipt_id}`\n"
        f"- Type: `{receipt.receipt_type}`\n"
        f"- Status: `{receipt.receipt_status}`\n"
        f"- Content item: `{receipt.subject_id}`\n"
        f"- Topic: {subject.get('topic') or 'unknown'}\n"
        f"- Workflow state: `{workflow.get('lifecycle_state')}`\n"
    )
    limitations = f"# Limitations\n\n{MEDIA_TRUST_BOUNDARY}\n"
    reviewer_notes = (
        "# Reviewer Notes\n\n"
        "Receipt review status: draft.\n\n"
        "Use this space for reviewer observations before marking the evidence packet "
        "reviewed, approved for packet use, or delivered.\n"
    )
    receipt_md = (
        "# Profusion Content Video Receipt\n\n"
        f"Receipt ID: `{receipt.receipt_id}`\n\n"
        "## Plain-English Summary\n\n"
        f"Profusion generated a draft reviewer evidence receipt for content item "
        f"`{receipt.subject_id}`. The item is currently `{workflow.get('lifecycle_state')}` "
        "inside the captured content workflow.\n\n"
        "## What Workflow Was Run\n\n"
        "The captured workflow is: content item -> brief -> script -> render -> QA -> "
        "approval -> schedule/publish state -> evidence packet.\n\n"
        "## What Artifacts Were Produced\n\n"
        f"- MP4: `{artifacts.get('mp4_path') or 'not recorded'}` "
        f"(exists={artifacts.get('mp4_exists')})\n"
        f"- Manifest: `{artifacts.get('manifest_path') or 'not recorded'}` "
        f"(exists={artifacts.get('manifest_exists')})\n"
        f"- QA report: `{artifacts.get('qa_report_path') or 'not recorded'}` "
        f"(exists={artifacts.get('qa_report_exists')})\n\n"
        "## QA, Review, And Approval\n\n"
        f"- QA present: `{workflow['qa']['present']}`\n"
        f"- QA result: `{workflow['qa']['overall_go_no_go'] or 'not recorded'}`\n"
        f"- Content approval decision: `{workflow['content_approval']['decision'] or 'not recorded'}`\n"
        f"- Receipt status: `{receipt.receipt_status}`\n\n"
        "## What This Proves\n\n"
        "This packet records the workflow state, artifact pointers, QA result, approval "
        "state, and evidence sources visible to Profusion at generation time.\n\n"
        "## What This Does Not Prove\n\n"
        f"{MEDIA_TRUST_BOUNDARY}\n\n"
        "## Technical Appendix\n\n"
        "- `evidence.json` contains the machine-readable evidence payload.\n"
        "- `summary.md` contains the compact reviewer summary.\n"
        "- `limitations.md` contains the boundary language.\n"
        "- `reviewer_notes.md` is reserved for packet review notes.\n"
    )

    receipt.summary_md.write_text(summary, encoding="utf-8")
    receipt.limitations_md.write_text(limitations, encoding="utf-8")
    receipt.reviewer_notes_md.write_text(reviewer_notes, encoding="utf-8")
    receipt.receipt_md.write_text(receipt_md, encoding="utf-8")
    receipt.evidence_json.write_text(
        json.dumps(evidence, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )


def _limitations_for_status(status: str) -> list[str]:
    if status == "draft":
        status_note = (
            "Receipt status is separate from content approval. "
            "A draft receipt is not approved for external packet delivery."
        )
    else:
        status_note = (
            "Receipt status is separate from content approval. "
            f"Current receipt status: {status}."
        )
    return [MEDIA_TRUST_BOUNDARY, status_note]


def _update_packet_markdown(
    packet_dir: Path,
    from_status: str,
    to_status: str,
    transitioned_at: str,
) -> None:
    _replace_line(
        packet_dir / "summary.md",
        prefix="- Status: `",
        replacement=f"- Status: `{to_status}`",
    )
    _replace_line(
        packet_dir / "receipt.md",
        prefix="- Receipt status: `",
        replacement=f"- Receipt status: `{to_status}`",
    )
    reviewer_notes = packet_dir / "reviewer_notes.md"
    with reviewer_notes.open("a", encoding="utf-8") as handle:
        handle.write(f"\n- {transitioned_at}: {from_status} -> {to_status}\n")


def _replace_line(path: Path, *, prefix: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    lines = [
        replacement if line.startswith(prefix) else line
        for line in text.splitlines()
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
