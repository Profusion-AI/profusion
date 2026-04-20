"""Turbo adapter normalization unit tests — no HTTP mocking required."""

import pytest

from orchestrator.adapters.turbo import (
    TurboUnavailableError,
    _extract_terms,
    _parse_render_response,
    _parse_task_response,
)


# ---------------------------------------------------------------------------
# _parse_render_response
# ---------------------------------------------------------------------------

def test_parse_render_response_extracts_task_id():
    body = {"data": {"task_id": "abc-123"}}
    assert _parse_render_response(body) == "abc-123"


def test_parse_render_response_rejects_empty_task_id():
    with pytest.raises(TurboUnavailableError):
        _parse_render_response({"data": {"task_id": ""}})


def test_parse_render_response_rejects_missing_task_id():
    with pytest.raises(TurboUnavailableError):
        _parse_render_response({"data": {}})


def test_parse_render_response_rejects_missing_data():
    with pytest.raises(TurboUnavailableError):
        _parse_render_response({"message": "ok"})


# ---------------------------------------------------------------------------
# _parse_task_response
# ---------------------------------------------------------------------------

def test_parse_task_response_completed_with_video():
    body = {"data": {"state": 1, "progress": 100, "videos": ["http://host/final.mp4"]}}
    r = _parse_task_response(body)
    assert r.status == "completed"
    assert r.output_url == "http://host/final.mp4"
    assert r.progress == 100


def test_parse_task_response_completed_no_video():
    body = {"data": {"state": 1, "progress": 100, "videos": []}}
    r = _parse_task_response(body)
    assert r.status == "completed"
    assert r.output_url is None


def test_parse_task_response_failed():
    body = {"data": {"state": -1, "progress": 30}}
    r = _parse_task_response(body)
    assert r.status == "failed"
    assert r.output_url is None


def test_parse_task_response_processing():
    body = {"data": {"state": 4, "progress": 55}}
    r = _parse_task_response(body)
    assert r.status == "processing"
    assert r.progress == 55


def test_parse_task_response_unknown_state_treated_as_processing():
    body = {"data": {"state": 99, "progress": 0}}
    r = _parse_task_response(body)
    assert r.status == "processing"


def test_parse_task_response_rejects_missing_data():
    with pytest.raises(TurboUnavailableError):
        _parse_task_response({"message": "ok"})


def test_parse_task_response_rejects_missing_state():
    with pytest.raises(TurboUnavailableError):
        _parse_task_response({"data": {}})


# ---------------------------------------------------------------------------
# _extract_terms
# ---------------------------------------------------------------------------

def test_extract_terms_filters_stop_words():
    terms = _extract_terms("Why schools reward compliance")
    assert "why" not in terms
    assert "schools" in terms
    assert "reward" in terms
    assert "compliance" in terms


def test_extract_terms_max_five():
    terms = _extract_terms("education reform policy compliance learning outcomes metrics")
    assert len(terms) <= 5


def test_extract_terms_min_length_filter():
    terms = _extract_terms("AI disruption in legal work")
    assert all(len(t) > 2 for t in terms)


def test_extract_terms_fallback_on_empty():
    terms = _extract_terms("")
    assert terms == ["education"]


def test_extract_terms_fallback_all_stop_words():
    terms = _extract_terms("in on at to of")
    assert terms == ["education"]


# ---------------------------------------------------------------------------
# Transport exception wrapping (httpx.RequestError → TurboUnavailableError)
# ---------------------------------------------------------------------------

def test_render_wraps_timeout_as_turbo_unavailable(monkeypatch):
    import httpx
    from orchestrator.adapters import turbo

    monkeypatch.setattr(
        httpx, "post",
        lambda *a, **kw: (_ for _ in ()).throw(httpx.TimeoutException("timed out")),
    )
    with pytest.raises(turbo.TurboUnavailableError):
        turbo.render(subject="topic", script="script text")


def test_get_job_status_wraps_timeout_as_turbo_unavailable(monkeypatch):
    import httpx
    from orchestrator.adapters import turbo

    monkeypatch.setattr(
        httpx, "get",
        lambda *a, **kw: (_ for _ in ()).throw(httpx.TimeoutException("timed out")),
    )
    with pytest.raises(turbo.TurboUnavailableError):
        turbo.get_job_status("some-task-id")


def test_render_wraps_invalid_json_as_turbo_unavailable(monkeypatch):
    import httpx
    from orchestrator.adapters import turbo

    class _BadJsonResp:
        def raise_for_status(self): pass
        def json(self): raise ValueError("no JSON object could be decoded")

    monkeypatch.setattr(httpx, "post", lambda *a, **kw: _BadJsonResp())
    with pytest.raises(turbo.TurboUnavailableError, match="not valid JSON"):
        turbo.render(subject="topic", script="script text")
