"""Build local AICE Workflow Receipt Validator models from receipt packets."""

from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path
from typing import Any

VALIDATOR_TITLE = "AICE Workflow Receipt Validator"
VALIDATOR_SUBTITLE = "HyperFrames Explorer for one completed Profusion receipt packet"
SAFE_FOUNDER_CLAIM = (
    "This n8n workflow ran. Profusion preserved what happened. "
    "The receipt tells you what the evidence supports and what it does not."
)
PRODUCT_SAFE_EXPLANATION = (
    "Profusion turns one AI-assisted workflow execution into reviewable evidence: "
    "what ran, what artifacts existed, where human review entered, what claims are "
    "supported, what claims are not supported, and what limitations remain."
)
LINEAGE_NOTE = "AICE workflow map derived from recorded node trail and receipt artifacts."
AICE_MINIMUM_NODE_COUNT = 7
CORE_JSON_FILES = (
    "workflow_receipt.json",
    "artifact_manifest.json",
    "m8_observation.json",
    "artifacts/runtime_payload.json",
)
DISPLAY_FILES = CORE_JSON_FILES + ("workflow_receipt.md", "workflow_receipt.html")
REQUIRED_RECEIPT_FILES = DISPLAY_FILES
FORBIDDEN_FOUNDER_TERMS = (
    "certified true",
    "truth verified",
    "legally cleared",
    "fair-use approved",
    "copyright safe",
    "compliance approved",
    "platform compliant",
    "safe to publish",
    "no risk",
    "customer validated",
    "production ready",
)


class HyperframeReceiptError(ValueError):
    """Raised when a receipt packet cannot be parsed into a validator model."""


def load_aice_hyperframe_model(receipt_dir: Path | str) -> dict[str, Any]:
    root = Path(receipt_dir).expanduser().resolve()
    if not root.is_dir():
        raise HyperframeReceiptError(f"receipt directory not found: {root}")

    missing_files = [rel for rel in REQUIRED_RECEIPT_FILES if not (root / rel).is_file()]
    missing_core = [rel for rel in CORE_JSON_FILES if not (root / rel).is_file()]
    if missing_core:
        raise HyperframeReceiptError(
            "receipt packet missing required JSON files: " + ", ".join(missing_core)
        )

    receipt = _read_json(root / "workflow_receipt.json")
    manifest = _read_json(root / "artifact_manifest.json")
    observation = _read_json(root / "m8_observation.json")
    runtime_payload = _read_json(root / "artifacts" / "runtime_payload.json")

    n8n_execution = _dict_value(observation.get("n8n_execution"))
    nodes = _build_nodes(n8n_execution)
    artifacts = _build_artifacts(root, manifest)
    supported_claims = _list_value(receipt.get("claims_supported"))
    unsupported_claims = _list_value(
        receipt.get("claims_not_supported", receipt.get("unsupported_claims"))
    )
    limitations = _list_value(receipt.get("limitations"))
    validation = _build_validation(
        root=root,
        receipt=receipt,
        manifest=manifest,
        observation=observation,
        runtime_payload=runtime_payload,
        artifacts=artifacts,
        nodes=nodes,
        missing_files=missing_files,
        supported_claims=supported_claims,
        unsupported_claims=unsupported_claims,
        limitations=limitations,
    )

    workflow_slug = (
        _string_value(manifest.get("workflow_slug"))
        or _string_value(runtime_payload.get("workflow_slug"))
        or _string_value(observation.get("workflow_id"))
    )
    workflow = {
        "name": _string_value(receipt.get("workflow_name"))
        or _string_value(observation.get("workflow_name")),
        "slug": workflow_slug,
        "evidence_mode": _string_value(receipt.get("evidence_mode"))
        or _string_value(observation.get("evidence_mode"))
        or _string_value(runtime_payload.get("evidence_mode")),
        "n8n_project": _string_value(n8n_execution.get("workspace_url")),
        "n8n_workflow_id": _string_value(n8n_execution.get("workspace_workflow_id"))
        or _string_value(runtime_payload.get("n8n_workspace_workflow_id")),
        "n8n_execution_id": _string_value(n8n_execution.get("execution_id"))
        or _string_value(runtime_payload.get("n8n_execution_id")),
        "node_count": _int_value(n8n_execution.get("node_count"))
        or len(_list_value(n8n_execution.get("nodes_executed"))),
        "status": _string_value(n8n_execution.get("status")) or "unknown",
    }
    receipt_id = _string_value(receipt.get("receipt_id")) or root.name

    return {
        "receipt_id": receipt_id,
        "receipt_path": str(root),
        "receipt": {"id": receipt_id, "path": str(root)},
        "validator_title": VALIDATOR_TITLE,
        "validator_subtitle": VALIDATOR_SUBTITLE,
        "workflow": workflow,
        "nodes": nodes,
        "edges": _build_edges(nodes),
        "data_lanes": _build_data_lanes(),
        "artifacts": artifacts,
        "receipt_sections": _build_receipt_sections(receipt),
        "supported_claims": supported_claims,
        "unsupported_claims": unsupported_claims,
        "claims": {"supported": supported_claims, "unsupported": unsupported_claims},
        "limitations": limitations,
        "founder_claim": SAFE_FOUNDER_CLAIM,
        "product_safe_explanation": PRODUCT_SAFE_EXPLANATION,
        "proof_counters": _build_proof_counters(
            root=root,
            n8n_execution=n8n_execution,
            supported_claims=supported_claims,
            unsupported_claims=unsupported_claims,
            artifacts=artifacts,
        ),
        "validation": validation,
        "verification": {
            "safe_founder_claim": SAFE_FOUNDER_CLAIM,
            "product_safe_explanation": PRODUCT_SAFE_EXPLANATION,
            "lineage_note": LINEAGE_NOTE,
            "missing_files": missing_files,
            "html_receipt_found": (root / "workflow_receipt.html").is_file(),
            "required_receipt_files": list(REQUIRED_RECEIPT_FILES),
        },
    }


def escape_text(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HyperframeReceiptError(f"invalid JSON in {path.name}: {exc}") from exc
    if not isinstance(payload, dict):
        raise HyperframeReceiptError(f"JSON file must contain an object: {path.name}")
    return payload


def _build_nodes(n8n_execution: dict[str, Any]) -> list[dict[str, Any]]:
    labels = [str(label) for label in _list_value(n8n_execution.get("nodes_executed"))]
    nodes = [
        {
            "id": _slugify(label),
            "label": label,
            "type": _node_type(label),
            "order": index + 1,
            "summary": f"Recorded n8n node: {label}",
            "inputs": [],
            "outputs": [],
            "derived": False,
        }
        for index, label in enumerate(labels)
    ]
    nodes.append(
        {
            "id": "profusion-receipt-packet",
            "label": "Profusion Receipt Packet",
            "type": "receipt_packet",
            "order": len(nodes) + 1,
            "summary": "Derived terminal node for the generated receipt packet.",
            "inputs": ["runtime_payload", "artifact_manifest"],
            "outputs": ["workflow_receipt"],
            "derived": True,
        }
    )
    return nodes


def _build_edges(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": f"{nodes[index]['id']}--{nodes[index + 1]['id']}",
            "source": nodes[index]["id"],
            "target": nodes[index + 1]["id"],
        }
        for index in range(len(nodes) - 1)
    ]


def _build_artifacts(root: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    rows = _list_value(manifest.get("artifacts"))
    artifacts: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        packet_path = _string_value(row.get("packet_path"))
        resolved = _safe_resolve(root, packet_path) if packet_path else None
        exists = bool(resolved and resolved.is_file() and _is_relative_to(resolved, root))
        seen_paths.add(packet_path)
        artifacts.append(
            {
                "artifact_id": _string_value(row.get("artifact_id")),
                "artifact_type": _string_value(row.get("artifact_type")),
                "description": _string_value(row.get("description")),
                "packet_path": packet_path,
                "sha256": _string_value(row.get("sha256")) or None,
                "exists": exists,
                "path": str(resolved) if resolved and _is_relative_to(resolved, root) else None,
                "manifest_listed": True,
            }
        )

    for rel in REQUIRED_RECEIPT_FILES:
        if rel in seen_paths:
            continue
        path = root / rel
        artifacts.append(
            {
                "artifact_id": f"receipt.{rel.replace('/', '.')}",
                "artifact_type": "receipt_packet_file",
                "description": f"Required receipt packet file: {rel}",
                "packet_path": rel,
                "sha256": _sha256(path) if path.is_file() else None,
                "exists": path.is_file(),
                "path": str(path.resolve()) if path.exists() else str(path),
                "manifest_listed": False,
            }
        )
    return artifacts


def _build_validation(
    *,
    root: Path,
    receipt: dict[str, Any],
    manifest: dict[str, Any],
    observation: dict[str, Any],
    runtime_payload: dict[str, Any],
    artifacts: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
    missing_files: list[str],
    supported_claims: list[Any],
    unsupported_claims: list[Any],
    limitations: list[Any],
) -> dict[str, Any]:
    n8n_execution = _dict_value(observation.get("n8n_execution"))
    recorded_nodes = _list_value(n8n_execution.get("nodes_executed"))
    node_count = _int_value(n8n_execution.get("node_count")) or 0
    manifest_paths_safe = _manifest_paths_are_safe(root, manifest)
    hash_status, hash_message = _check_manifest_hashes(root, manifest)
    forbidden_found = _forbidden_overclaim_language_found(receipt, observation)
    workflow_slug_matches = _workflow_slugs_match(manifest, runtime_payload, observation)

    checks: dict[str, Any] = {
        "core_files_present": all((root / rel).is_file() for rel in CORE_JSON_FILES),
        "display_files_present": all((root / rel).is_file() for rel in DISPLAY_FILES),
        "runtime_payload_found": (root / "artifacts" / "runtime_payload.json").is_file(),
        "workflow_slug_matches": workflow_slug_matches,
        "n8n_execution_id_present": bool(
            _string_value(n8n_execution.get("execution_id"))
            or _string_value(runtime_payload.get("n8n_execution_id"))
        ),
        "node_count_matches_trail": bool(node_count and node_count == len(recorded_nodes)),
        "minimum_node_count_met": len(recorded_nodes) >= AICE_MINIMUM_NODE_COUNT,
        "human_review_artifact_present": any(
            artifact["artifact_type"] == "human_editorial_review" and artifact["exists"]
            for artifact in artifacts
        ),
        "supported_claims_present": bool(supported_claims),
        "unsupported_claims_present": bool(unsupported_claims),
        "limitations_present": bool(limitations),
        "path_safety_passed": manifest_paths_safe,
        "forbidden_overclaim_language_found": forbidden_found,
        "artifact_hashes_checked": hash_status,
    }

    findings: list[dict[str, str]] = []
    _add_bool_finding(
        findings,
        "core_files_present",
        checks["core_files_present"],
        "Core receipt JSON files are present.",
        "Core receipt JSON files are missing.",
    )
    _add_bool_finding(
        findings,
        "display_files_present",
        checks["display_files_present"],
        "Display receipt files are present.",
        "Display receipt files are missing: " + ", ".join(missing_files),
        false_severity="warn",
    )
    _add_bool_finding(
        findings,
        "runtime_payload_found",
        checks["runtime_payload_found"],
        "Runtime payload artifact is present.",
        "Runtime payload artifact is missing.",
    )
    _add_bool_finding(
        findings,
        "workflow_slug_matches",
        checks["workflow_slug_matches"],
        "Workflow slug matches manifest, runtime payload, and observation.",
        "Workflow slug does not match manifest, runtime payload, and observation.",
    )
    _add_bool_finding(
        findings,
        "n8n_execution_id_present",
        checks["n8n_execution_id_present"],
        "n8n execution ID is present.",
        "n8n execution ID is missing.",
    )
    _add_bool_finding(
        findings,
        "node_count_matches_trail",
        checks["node_count_matches_trail"],
        "Recorded node count matches the execution trail.",
        "Recorded node count does not match the execution trail.",
    )
    _add_bool_finding(
        findings,
        "minimum_node_count_met",
        checks["minimum_node_count_met"],
        f"Minimum AICE workflow node count of {AICE_MINIMUM_NODE_COUNT} is met.",
        f"Minimum AICE workflow node count of {AICE_MINIMUM_NODE_COUNT} is not met.",
    )
    _add_bool_finding(
        findings,
        "human_review_artifact_present",
        checks["human_review_artifact_present"],
        "Human review artifact is present.",
        "Human review artifact is missing.",
    )
    _add_bool_finding(
        findings,
        "supported_claims_present",
        checks["supported_claims_present"],
        "Supported claims are present.",
        "Supported claims are missing.",
    )
    _add_bool_finding(
        findings,
        "unsupported_claims_present",
        checks["unsupported_claims_present"],
        "Unsupported claims are present.",
        "Unsupported claims are missing.",
    )
    _add_bool_finding(
        findings,
        "limitations_present",
        checks["limitations_present"],
        "Limitations are present.",
        "Limitations are missing.",
    )
    _add_bool_finding(
        findings,
        "path_safety_passed",
        checks["path_safety_passed"],
        "Manifest paths resolve inside the receipt packet.",
        "Manifest contains a path outside the receipt packet.",
    )
    findings.append(
        {
            "severity": "fail" if forbidden_found else "pass",
            "code": "forbidden_overclaim_language",
            "message": (
                "Forbidden founder-facing overclaim language was found."
                if forbidden_found
                else "Forbidden founder-facing overclaim language was not found."
            ),
        }
    )
    findings.append(
        {
            "severity": "fail" if hash_status is False else "pass",
            "code": "artifact_hashes_checked",
            "message": hash_message or "Manifest-listed artifact hashes match.",
        }
    )

    fail_present = any(finding["severity"] == "fail" for finding in findings)
    warn_present = any(finding["severity"] == "warn" for finding in findings)
    status = (
        "validation_failed"
        if fail_present
        else "validated_with_warnings"
        if warn_present
        else "validated_with_limitations"
    )
    validation = {
        "validation_status": status,
        "validation_findings": findings,
        "artifact_hash_limitation": hash_message if hash_status == "partial" else "",
        "node_labels_observed": [node["label"] for node in nodes],
    }
    validation.update(checks)
    return validation


def _add_bool_finding(
    findings: list[dict[str, str]],
    code: str,
    passed: bool,
    pass_message: str,
    false_message: str,
    *,
    false_severity: str = "fail",
) -> None:
    findings.append(
        {
            "severity": "pass" if passed else false_severity,
            "code": code,
            "message": pass_message if passed else false_message,
        }
    )


def _check_manifest_hashes(root: Path, manifest: dict[str, Any]) -> tuple[bool | str, str]:
    checked = 0
    for row in _list_value(manifest.get("artifacts")):
        if not isinstance(row, dict):
            continue
        packet_path = _string_value(row.get("packet_path"))
        expected_hash = _string_value(row.get("sha256"))
        if not packet_path or not expected_hash:
            continue
        path = _safe_resolve(root, packet_path)
        if path is None or not _is_relative_to(path, root):
            return False, f"Manifest artifact path is unsafe: {packet_path}"
        if not path.is_file():
            return False, f"Manifest artifact is missing: {packet_path}"
        checked += 1
        actual_hash = _sha256(path)
        if actual_hash != expected_hash:
            return False, f"Manifest hash mismatch for {packet_path}"
    if checked == 0:
        return "partial", "Only manifest-listed hashes were available for validation."
    return True, ""


def _manifest_paths_are_safe(root: Path, manifest: dict[str, Any]) -> bool:
    for row in _list_value(manifest.get("artifacts")):
        if not isinstance(row, dict):
            continue
        packet_path = _string_value(row.get("packet_path"))
        if not packet_path:
            continue
        path = _safe_resolve(root, packet_path)
        if path is None or not _is_relative_to(path, root):
            return False
    return True


def _workflow_slugs_match(
    manifest: dict[str, Any],
    runtime_payload: dict[str, Any],
    observation: dict[str, Any],
) -> bool:
    slugs = (
        _string_value(manifest.get("workflow_slug")),
        _string_value(runtime_payload.get("workflow_slug")),
        _string_value(observation.get("workflow_id")),
    )
    return all(slugs) and len(set(slugs)) == 1


def _forbidden_overclaim_language_found(
    receipt: dict[str, Any],
    observation: dict[str, Any],
) -> bool:
    fields_to_scan = [
        receipt.get("workflow_purpose"),
        receipt.get("evidence_boundary"),
        receipt.get("topic_episode_thesis"),
        receipt.get("what_happened"),
        receipt.get("where_ai_acted"),
        receipt.get("where_n8n_acted"),
        receipt.get("where_human_review_entered"),
        receipt.get("final_action"),
        receipt.get("narrative_decisions"),
        receipt.get("source_cards"),
        receipt.get("claims_and_quote_candidates"),
        receipt.get("quote_candidates"),
        receipt.get("rights_use_ambiguity_classification"),
        receipt.get("ambiguities_preserved"),
        receipt.get("attention_intelligence_mapping"),
        receipt.get("generated_synthetic_media_plan"),
        receipt.get("artifacts_reviewed"),
        receipt.get("next_recommended_review"),
        receipt.get("claims_supported"),
        observation.get("supported_claims"),
        observation.get("topic_brief"),
        observation.get("source_cards"),
        observation.get("claim_map"),
        observation.get("quote_candidates"),
        observation.get("rights_review"),
        observation.get("ambiguity_register"),
        observation.get("attention_intelligence_map"),
        observation.get("narrative_brief"),
        observation.get("visual_plan"),
        observation.get("artifacts_captured"),
        observation.get("ai_actions_observed"),
        observation.get("outcome"),
        observation.get("trigger_summary"),
        observation.get("workflow_boundary"),
    ]
    text = "\n".join(_flatten_text(value) for value in fields_to_scan).lower()
    return any(term in text for term in FORBIDDEN_FOUNDER_TERMS)


def _build_receipt_sections(receipt: dict[str, Any]) -> list[dict[str, Any]]:
    section_keys = (
        "workflow_purpose",
        "what_happened",
        "where_n8n_acted",
        "where_ai_acted",
        "where_human_review_entered",
        "final_action",
        "narrative_decisions",
        "next_recommended_review",
    )
    return [
        {"key": key, "label": key.replace("_", " ").title(), "value": receipt[key]}
        for key in section_keys
        if receipt.get(key)
    ]


def _build_data_lanes() -> list[dict[str, str]]:
    lane_names = (
        "topic/thesis",
        "source card",
        "quote candidate",
        "claim map",
        "rights review",
        "ambiguity register",
        "human review state",
        "runtime payload",
        "receipt packet",
    )
    return [{"id": _slugify(name), "label": name} for name in lane_names]


def _build_proof_counters(
    *,
    root: Path,
    n8n_execution: dict[str, Any],
    supported_claims: list[Any],
    unsupported_claims: list[Any],
    artifacts: list[dict[str, Any]],
) -> dict[str, int]:
    human_review_gates = sum(
        1
        for artifact in artifacts
        if artifact["artifact_type"] == "human_editorial_review" and artifact["exists"]
    )
    return {
        "nodes_executed": len(_list_value(n8n_execution.get("nodes_executed"))),
        "receipt_artifacts_found": sum(
            1 for rel in REQUIRED_RECEIPT_FILES if (root / rel).is_file()
        ),
        "claim_boundaries_present": int(bool(supported_claims))
        + int(bool(unsupported_claims)),
        "human_review_gates_recorded": human_review_gates,
    }


def _node_type(label: str) -> str:
    lowered = label.lower()
    if "human" in lowered or "review" in lowered:
        return "human_review"
    if "receipt" in lowered:
        return "receipt"
    if "trigger" in lowered:
        return "trigger"
    return "n8n_node"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "item"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_resolve(root: Path, packet_path: str) -> Path | None:
    if not packet_path:
        return None
    candidate = Path(packet_path)
    if candidate.is_absolute():
        return candidate.resolve()
    return (root / candidate).resolve()


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _dict_value(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_value(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _int_value(value: Any) -> int | None:
    return value if isinstance(value, int) else None


def _flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return "\n".join(_flatten_text(item) for item in value.values())
    if isinstance(value, list):
        return "\n".join(_flatten_text(item) for item in value)
    if value is None:
        return ""
    return str(value)
