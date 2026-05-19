"""Load and validate local M8-GTM workflow fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orchestrator.m8_gtm.registry import (
    WORKFLOW_SPECS,
    WorkflowSpec,
    get_workflow_spec,
    supported_workflow_slugs,
)
from orchestrator.m8_gtm.schemas import FixtureValidationError, UnknownWorkflowError


def default_fixture_root() -> Path:
    """Return the repository-local M8 fixture root."""

    return Path(__file__).resolve().parents[3] / "examples" / "m8"


def load_workflow_fixture(
    workflow_slug: str,
    fixture_root: Path | None = None,
) -> dict[str, Any]:
    """Load and validate the requested workflow fixture."""

    if workflow_slug not in WORKFLOW_SPECS:
        raise UnknownWorkflowError(
            f"Unknown M8 demo workflow {workflow_slug!r}. Supported: {supported_workflow_slugs()}"
        )
    spec = get_workflow_spec(workflow_slug)

    root = fixture_root or default_fixture_root()
    fixture_dir = root / workflow_slug
    workflow_path = fixture_dir / "workflow.json"
    if not workflow_path.exists():
        raise FixtureValidationError(f"Missing workflow fixture: {workflow_path}")

    workflow = _read_json(workflow_path)
    runs_dir = fixture_dir / "runs"
    if not runs_dir.exists():
        raise FixtureValidationError(f"Missing runs directory: {runs_dir}")

    runs = [
        _load_run_dir(path, spec, fixture_dir)
        for path in sorted(runs_dir.iterdir())
        if path.is_dir()
    ]
    fixture = {
        "workflow_slug": workflow_slug,
        "workflow_spec": spec,
        "workflow": workflow,
        "fixture_dir": str(fixture_dir),
        "workflow_path": str(workflow_path),
        "runs": runs,
    }
    validate_workflow_fixture(fixture, spec)
    return fixture


def validate_workflow_fixture(
    fixture: dict[str, Any],
    spec: WorkflowSpec | None = None,
) -> None:
    """Validate fixture completeness and claim-safety invariants."""

    spec = spec or get_workflow_spec(str(fixture.get("workflow_slug")))
    workflow = _required_dict(fixture.get("workflow"), "workflow")
    if workflow.get("workflow_slug") != spec.slug:
        raise FixtureValidationError(f"workflow_slug must be {spec.slug!r}")
    if workflow.get("workflow_name") != spec.name:
        raise FixtureValidationError(f"workflow_name must be {spec.name!r}")
    if workflow.get("evidence_mode") != spec.evidence_mode:
        raise FixtureValidationError(f"evidence_mode must be {spec.evidence_mode!r}")

    runs = fixture.get("runs")
    if not isinstance(runs, list) or not runs:
        raise FixtureValidationError("Fixture must include at least one run")

    runs_by_case = {str(run.get("case_id")): run for run in runs}
    for case_id in spec.required_case_ids:
        if case_id not in runs_by_case:
            raise FixtureValidationError(f"Missing required case fixture: {case_id}")

    for run in runs:
        case_id = str(run.get("case_id") or "")
        artifacts = _required_dict(run.get("artifacts"), f"{case_id}.artifacts")
        for artifact_spec in spec.artifact_specs:
            if not artifact_spec.required:
                continue
            artifact_key = artifact_spec.artifact_key
            if artifact_key not in artifacts:
                raise FixtureValidationError(
                    f"{case_id} requires a {artifact_spec.filename} artifact"
                )

    for case_id, artifact_keys in spec.required_case_artifacts.items():
        run = runs_by_case[case_id]
        artifacts = _required_dict(run.get("artifacts"), f"{case_id}.artifacts")
        for artifact_key in artifact_keys:
            if artifact_key not in artifacts:
                filename = _filename_for_artifact_key(spec, artifact_key)
                raise FixtureValidationError(f"{case_id} requires a {filename} artifact")

    if spec.slug == "support-triage-human-review":
        _validate_support_triage_review(runs_by_case)
    if spec.slug == "aice-source-to-narrative-receipt":
        _validate_aice_run(runs_by_case)


def _load_run_dir(
    run_dir: Path,
    spec: WorkflowSpec,
    fixture_dir: Path,
) -> dict[str, Any]:
    raw_run = _read_json(run_dir / "run.json")
    case_id = str(raw_run.get("case_id") or "")
    if not case_id:
        raise FixtureValidationError(f"{run_dir}/run.json is missing case_id")

    artifacts: dict[str, Any] = {}
    artifact_files = []
    for artifact_spec in spec.artifact_specs:
        filename = artifact_spec.filename
        artifact_key = artifact_spec.artifact_key
        artifact_type = artifact_spec.artifact_type
        path = run_dir / filename
        if not path.exists() and spec.slug == "aice-source-to-narrative-receipt":
            path = fixture_dir / filename
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
                "flat_packet_path": spec.slug == "aice-source-to-narrative-receipt",
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


def _filename_for_artifact_key(spec: WorkflowSpec, artifact_key: str) -> str:
    for artifact_spec in spec.artifact_specs:
        if artifact_spec.artifact_key == artifact_key:
            return artifact_spec.filename
    return f"{artifact_key}.json"


def _validate_support_triage_review(runs_by_case: dict[str, dict[str, Any]]) -> None:
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


def _validate_aice_run(runs_by_case: dict[str, dict[str, Any]]) -> None:
    run = runs_by_case["live_minimum_aice"]
    artifacts = _required_dict(run.get("artifacts"), "live_minimum_aice.artifacts")

    n8n_run = _required_dict(artifacts["n8n_run_summary"], "n8n_run_summary")
    if int(n8n_run.get("node_count") or 0) < 3:
        raise FixtureValidationError("AICE n8n_run_summary requires node_count >= 3")
    nodes_executed = n8n_run.get("nodes_executed")
    if not isinstance(nodes_executed, list) or len(nodes_executed) < 3:
        raise FixtureValidationError("AICE n8n_run_summary requires at least 3 executed nodes")

    quote_candidates = _required_dict(artifacts["quote_candidates"], "quote_candidates")
    candidates = quote_candidates.get("quote_candidates", quote_candidates.get("candidates", []))
    if not isinstance(candidates, list) or not candidates:
        raise FixtureValidationError("AICE quote_candidates requires at least one candidate")
    for candidate in candidates:
        if candidate.get("audio_visual_downloaded") is not False:
            raise FixtureValidationError("AICE media candidates must not download audio/video")
        if candidate.get("storage_mode") != "metadata_only":
            raise FixtureValidationError("AICE media candidates must use metadata_only storage")
        if "local_media_path" in candidate or "transcript_full_text" in candidate:
            raise FixtureValidationError("AICE media candidates must remain reference-only")

    ambiguity_register = _required_dict(artifacts["ambiguity_register"], "ambiguity_register")
    ambiguities = ambiguity_register.get("ambiguities", ambiguity_register.get("items", []))
    if not isinstance(ambiguities, list) or not ambiguities:
        raise FixtureValidationError("AICE ambiguity_register requires at least one ambiguity")
