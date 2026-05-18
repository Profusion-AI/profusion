"""Load and validate local M8-GTM workflow fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orchestrator.m8_gtm.schemas import (
    EVIDENCE_MODE,
    FixtureValidationError,
    UnknownWorkflowError,
    WORKFLOW_NAME,
    WORKFLOW_SLUG,
)


RUN_ARTIFACTS: dict[str, tuple[str, str]] = {
    "run.json": ("run", "run_log"),
    "inbound_message.md": ("inbound_message", "inbound_message"),
    "ai_classification.json": ("ai_classification", "ai_classification"),
    "ai_draft_reply.md": ("ai_draft_reply", "ai_draft"),
    "human_review_event.json": ("human_review_event", "human_review"),
    "final_reply.md": ("final_reply", "final_reply"),
    "execution_log.json": ("execution_log", "execution_log"),
}

REQUIRED_RUN_FILES = (
    "run.json",
    "inbound_message.md",
    "ai_classification.json",
    "ai_draft_reply.md",
    "final_reply.md",
    "execution_log.json",
)


def default_fixture_root() -> Path:
    """Return the repository-local M8 fixture root."""

    return Path(__file__).resolve().parents[3] / "examples" / "m8"


def load_workflow_fixture(
    workflow_slug: str,
    fixture_root: Path | None = None,
) -> dict[str, Any]:
    """Load and validate the requested workflow fixture."""

    if workflow_slug != WORKFLOW_SLUG:
        raise UnknownWorkflowError(
            f"Unknown M8 demo workflow {workflow_slug!r}. Supported: {WORKFLOW_SLUG}"
        )

    root = fixture_root or default_fixture_root()
    fixture_dir = root / workflow_slug
    workflow_path = fixture_dir / "workflow.json"
    if not workflow_path.exists():
        raise FixtureValidationError(f"Missing workflow fixture: {workflow_path}")

    workflow = _read_json(workflow_path)
    runs_dir = fixture_dir / "runs"
    if not runs_dir.exists():
        raise FixtureValidationError(f"Missing runs directory: {runs_dir}")

    runs = [_load_run_dir(path) for path in sorted(runs_dir.iterdir()) if path.is_dir()]
    fixture = {
        "workflow_slug": workflow_slug,
        "workflow": workflow,
        "fixture_dir": str(fixture_dir),
        "workflow_path": str(workflow_path),
        "runs": runs,
    }
    validate_workflow_fixture(fixture)
    return fixture


def validate_workflow_fixture(fixture: dict[str, Any]) -> None:
    """Validate fixture completeness and claim-safety invariants."""

    workflow = _required_dict(fixture.get("workflow"), "workflow")
    if workflow.get("workflow_slug") != WORKFLOW_SLUG:
        raise FixtureValidationError(f"workflow_slug must be {WORKFLOW_SLUG!r}")
    if workflow.get("workflow_name") != WORKFLOW_NAME:
        raise FixtureValidationError(f"workflow_name must be {WORKFLOW_NAME!r}")
    if workflow.get("evidence_mode") != EVIDENCE_MODE:
        raise FixtureValidationError(f"evidence_mode must be {EVIDENCE_MODE!r}")

    runs = fixture.get("runs")
    if not isinstance(runs, list) or not runs:
        raise FixtureValidationError("Fixture must include at least one run")

    runs_by_case = {str(run.get("case_id")): run for run in runs}
    for case_id in ("routine_invoice", "sensitive_billing_complaint"):
        if case_id not in runs_by_case:
            raise FixtureValidationError(f"Missing required case fixture: {case_id}")

    for run in runs:
        case_id = str(run.get("case_id") or "")
        artifacts = _required_dict(run.get("artifacts"), f"{case_id}.artifacts")
        for filename in REQUIRED_RUN_FILES:
            artifact_key = RUN_ARTIFACTS[filename][0]
            if artifact_key not in artifacts:
                raise FixtureValidationError(
                    f"{case_id} requires a {filename} artifact"
                )

    sensitive = runs_by_case["sensitive_billing_complaint"]
    sensitive_artifacts = _required_dict(
        sensitive.get("artifacts"),
        "sensitive_billing_complaint.artifacts",
    )
    if "human_review_event" not in sensitive_artifacts:
        raise FixtureValidationError(
            "sensitive_billing_complaint requires a human_review_event.json artifact"
        )
    review = _required_dict(
        sensitive_artifacts["human_review_event"],
        "sensitive_billing_complaint.human_review_event",
    )
    if review.get("case_id") != "sensitive_billing_complaint":
        raise FixtureValidationError(
            "sensitive_billing_complaint human_review_event.json has wrong case_id"
        )
    if not review.get("reviewed_artifact_ids") or not review.get("resulting_artifact_id"):
        raise FixtureValidationError(
            "sensitive_billing_complaint human review must include reviewed and resulting artifacts"
        )


def _load_run_dir(run_dir: Path) -> dict[str, Any]:
    raw_run = _read_json(run_dir / "run.json")
    case_id = str(raw_run.get("case_id") or "")
    if not case_id:
        raise FixtureValidationError(f"{run_dir}/run.json is missing case_id")

    artifacts: dict[str, Any] = {}
    artifact_files = []
    for filename, (artifact_key, artifact_type) in RUN_ARTIFACTS.items():
        path = run_dir / filename
        if not path.exists():
            continue
        artifacts[artifact_key] = (
            _read_json(path) if path.suffix == ".json" else path.read_text(encoding="utf-8")
        )
        artifact_files.append(
            {
                "artifact_key": artifact_key,
                "artifact_type": artifact_type,
                "filename": filename,
                "source_path": str(path),
                "case_id": case_id,
                "run_dir_name": run_dir.name,
            }
        )

    return {
        "run_id": str(raw_run.get("run_id") or run_dir.name),
        "case_id": case_id,
        "case_dir": str(run_dir),
        "run": raw_run,
        "artifacts": artifacts,
        "artifact_files": artifact_files,
    }


def _read_json(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise FixtureValidationError(f"Cannot read fixture JSON: {path}") from exc
    except ValueError as exc:
        raise FixtureValidationError(f"Invalid fixture JSON: {path}") from exc
    if not isinstance(loaded, dict):
        raise FixtureValidationError(f"Fixture JSON must be an object: {path}")
    return loaded


def _required_dict(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FixtureValidationError(f"{label} must be an object")
    return value
