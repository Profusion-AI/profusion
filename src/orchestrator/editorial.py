"""Editorial pipeline: brief and script generation via Claude.

Keeps prompt-specific logic out of the Claude adapter. Testable in
isolation: callers can monkeypatch `orchestrator.adapters.claude.generate`
to avoid live API calls.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from orchestrator.adapters import claude
from orchestrator.models import BriefDraft, QAResult, ScriptBatch, ScriptDraft

_PROMPTS_DIR = Path(__file__).parent / "prompts"

DEFAULT_VARIANTS: list[dict[str, str]] = [
    {
        "name": "straight_explainer",
        "style_note": (
            "Plainspoken explainer. Open with the most important concrete "
            "fact. Walk the viewer through the argument in order. No "
            "rhetorical flourish."
        ),
    },
    {
        "name": "provocative_hook",
        "style_note": (
            "Lead with a counterintuitive framing that is nonetheless "
            "true. Earn the hook with evidence in the body. Avoid "
            "outrage or partisan tone."
        ),
    },
    {
        "name": "myth_vs_reality",
        "style_note": (
            "Contrast a widely held assumption with what the evidence "
            "actually shows. Name the assumption fairly before correcting it."
        ),
    },
]


class QACheckError(RuntimeError):
    """Raised when Claude output cannot be parsed or validated for QA."""


class BriefGenerationError(RuntimeError):
    """Raised when Claude output cannot be parsed or validated for a brief."""


class ScriptGenerationError(RuntimeError):
    """Raised when Claude output cannot be parsed or validated for scripts."""


def _load_prompt(relative_path: str) -> str:
    path = _PROMPTS_DIR / relative_path
    return path.read_text(encoding="utf-8")


_JSON_FENCE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.DOTALL)


def _extract_json_object(raw: str) -> Any:
    """Best-effort JSON extraction from a model response.

    Handles:
      - plain JSON
      - markdown-fenced JSON (```json ... ```)
      - trailing/leading whitespace or prose (falls back to the first {...} span)
    """
    text = raw.strip()
    fence = _JSON_FENCE.match(text)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback: grab the first balanced {...} span.
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(text[start : end + 1])


def generate_brief(
    *,
    topic: str,
    pillar: str | None = None,
    audience: str | None = None,
    sources: list[dict[str, Any]] | None = None,
) -> BriefDraft:
    """Ask Claude for a structured editorial brief and return a validated BriefDraft."""
    system = _load_prompt("planning/brief.md")

    user_payload: dict[str, Any] = {"topic": topic}
    if pillar:
        user_payload["pillar"] = pillar
    if audience:
        user_payload["audience"] = audience
    if sources:
        user_payload["sources"] = sources

    user = json.dumps(user_payload, indent=2)
    raw = claude.generate(system=system, user=user, max_tokens=3000)

    try:
        parsed = _extract_json_object(raw)
    except json.JSONDecodeError as e:
        raise BriefGenerationError(
            f"Claude did not return parseable JSON for brief: {e}\n---\n{raw[:500]}"
        ) from e

    try:
        return BriefDraft.model_validate(parsed)
    except ValidationError as e:
        raise BriefGenerationError(
            f"Brief JSON failed schema validation: {e}"
        ) from e


def generate_scripts(
    *,
    topic: str,
    brief: BriefDraft,
    variants: list[dict[str, str]] | None = None,
    duration_target_seconds: int = 60,
) -> list[ScriptDraft]:
    """Ask Claude for a batch of script variants; return validated ScriptDrafts.

    Default variants: straight_explainer, provocative_hook, myth_vs_reality.
    """
    variants = variants or DEFAULT_VARIANTS
    system = _load_prompt("scripting/script_variant.md")
    user_payload = {
        "topic": topic,
        "brief": brief.model_dump(mode="json"),
        "variants": variants,
        "duration_target_seconds": duration_target_seconds,
    }
    user = json.dumps(user_payload, indent=2)
    raw = claude.generate(system=system, user=user, max_tokens=4000)

    try:
        parsed = _extract_json_object(raw)
    except json.JSONDecodeError as e:
        raise ScriptGenerationError(
            f"Claude did not return parseable JSON for scripts: {e}\n---\n{raw[:500]}"
        ) from e

    try:
        batch = ScriptBatch.model_validate(parsed)
    except ValidationError as e:
        raise ScriptGenerationError(
            f"Script JSON failed schema validation: {e}"
        ) from e

    requested = {v["name"] for v in variants}
    returned = {v.variant_name for v in batch.variants}
    missing = requested - returned
    extra = returned - requested
    if missing:
        raise ScriptGenerationError(
            f"Claude omitted requested variants: {sorted(missing)}"
        )
    if extra:
        raise ScriptGenerationError(
            f"Claude returned unexpected variants: {sorted(extra)}"
        )

    return batch.variants


def run_qa_check(
    *,
    topic: str,
    script_text: str,
    brief_dict: dict,
) -> QAResult:
    """Run the editorial risk QA prompt against a rendered artifact; return a validated QAResult."""
    system = _load_prompt("qa/editorial_risk.md")
    user = json.dumps(
        {"topic": topic, "script": script_text, "brief": brief_dict},
        indent=2,
    )
    raw = claude.generate(system=system, user=user, max_tokens=2000)
    try:
        parsed = _extract_json_object(raw)
    except json.JSONDecodeError as e:
        raise QACheckError(
            f"Claude did not return parseable JSON for QA: {e}\n---\n{raw[:500]}"
        ) from e
    try:
        return QAResult.model_validate(parsed)
    except ValidationError as e:
        raise QACheckError(f"QA JSON failed schema validation: {e}") from e
