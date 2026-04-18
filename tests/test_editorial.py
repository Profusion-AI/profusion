"""editorial module unit tests — JSON extraction and validation."""

import json

import pytest

from orchestrator import editorial
from orchestrator.models import BriefDraft


def test_extract_plain_json():
    obj = editorial._extract_json_object('{"a": 1}')
    assert obj == {"a": 1}


def test_extract_fenced_json():
    obj = editorial._extract_json_object('```json\n{"a": 2}\n```')
    assert obj == {"a": 2}


def test_extract_fenced_bare():
    obj = editorial._extract_json_object('```\n{"a": 3}\n```')
    assert obj == {"a": 3}


def test_extract_json_with_trailing_prose():
    raw = 'Here is the brief:\n{"a": 4}\n\nLet me know if you want changes.'
    obj = editorial._extract_json_object(raw)
    assert obj == {"a": 4}


def test_extract_json_raises_on_garbage():
    with pytest.raises(json.JSONDecodeError):
        editorial._extract_json_object("not json at all")


def test_generate_brief_validates_output(monkeypatch):
    from orchestrator.adapters import claude

    payload = {"thesis": "A terse thesis."}

    monkeypatch.setattr(claude, "generate", lambda **_: json.dumps(payload))
    brief = editorial.generate_brief(topic="x")
    assert isinstance(brief, BriefDraft)
    assert brief.thesis == "A terse thesis."
    assert brief.risk_flags == []


def test_generate_brief_raises_on_missing_required(monkeypatch):
    from orchestrator.adapters import claude

    monkeypatch.setattr(claude, "generate", lambda **_: json.dumps({"angle": "only an angle"}))
    with pytest.raises(editorial.BriefGenerationError):
        editorial.generate_brief(topic="x")


def test_generate_scripts_requires_all_variants(monkeypatch):
    from orchestrator.adapters import claude

    payload = {
        "variants": [
            {
                "variant_name": "straight_explainer",
                "script_text": "ok",
                "duration_target_seconds": 60,
            }
        ]
    }
    monkeypatch.setattr(claude, "generate", lambda **_: json.dumps(payload))
    brief = BriefDraft(thesis="x")
    with pytest.raises(editorial.ScriptGenerationError):
        editorial.generate_scripts(topic="t", brief=brief)


def test_generate_scripts_rejects_extra_variants(monkeypatch):
    from orchestrator.adapters import claude

    payload = {
        "variants": [
            {"variant_name": "straight_explainer", "script_text": "ok", "duration_target_seconds": 60},
            {"variant_name": "provocative_hook", "script_text": "ok", "duration_target_seconds": 60},
            {"variant_name": "myth_vs_reality", "script_text": "ok", "duration_target_seconds": 60},
            {"variant_name": "extra_uninvited", "script_text": "ok", "duration_target_seconds": 60},
        ]
    }
    monkeypatch.setattr(claude, "generate", lambda **_: json.dumps(payload))
    brief = BriefDraft(thesis="x")
    with pytest.raises(editorial.ScriptGenerationError):
        editorial.generate_scripts(topic="t", brief=brief)
