"""State machine unit tests."""

import pytest

from orchestrator.state import ContentStatus, InvalidTransitionError, transition


def test_valid_forward_transitions():
    assert transition(ContentStatus.IDEA, ContentStatus.PLANNED) == ContentStatus.PLANNED
    assert transition(ContentStatus.PLANNED, ContentStatus.SCRIPTED) == ContentStatus.SCRIPTED
    assert transition(ContentStatus.SCRIPTED, ContentStatus.RENDERED) == ContentStatus.RENDERED
    assert transition(ContentStatus.RENDERED, ContentStatus.QA_PASSED) == ContentStatus.QA_PASSED
    assert transition(ContentStatus.RENDERED, ContentStatus.QA_FAILED) == ContentStatus.QA_FAILED
    assert transition(ContentStatus.QA_PASSED, ContentStatus.AWAITING_APPROVAL) == ContentStatus.AWAITING_APPROVAL
    assert transition(ContentStatus.AWAITING_APPROVAL, ContentStatus.APPROVED) == ContentStatus.APPROVED
    assert transition(ContentStatus.APPROVED, ContentStatus.SCHEDULED) == ContentStatus.SCHEDULED
    assert transition(ContentStatus.SCHEDULED, ContentStatus.PUBLISHED) == ContentStatus.PUBLISHED
    assert transition(ContentStatus.PUBLISHED, ContentStatus.MEASURED) == ContentStatus.MEASURED
    assert transition(ContentStatus.MEASURED, ContentStatus.ARCHIVED) == ContentStatus.ARCHIVED


def test_qa_failed_retry_path():
    """qa_failed → rendered is the valid re-render path."""
    assert transition(ContentStatus.QA_FAILED, ContentStatus.RENDERED) == ContentStatus.RENDERED


def test_archived_is_terminal():
    for status in ContentStatus:
        if status == ContentStatus.ARCHIVED:
            continue
        with pytest.raises(InvalidTransitionError):
            transition(ContentStatus.ARCHIVED, status)


def test_invalid_direct_jumps():
    invalid_pairs = [
        (ContentStatus.IDEA, ContentStatus.PUBLISHED),
        (ContentStatus.IDEA, ContentStatus.APPROVED),
        (ContentStatus.SCRIPTED, ContentStatus.PUBLISHED),
        (ContentStatus.RENDERED, ContentStatus.APPROVED),
        (ContentStatus.QA_PASSED, ContentStatus.PUBLISHED),
        (ContentStatus.PLANNED, ContentStatus.RENDERED),
    ]
    for current, new in invalid_pairs:
        with pytest.raises(InvalidTransitionError):
            transition(current, new)


def test_all_items_can_archive():
    """Every non-terminal state can transition to archived."""
    for status in ContentStatus:
        if status == ContentStatus.ARCHIVED:
            continue
        result = transition(status, ContentStatus.ARCHIVED)
        assert result == ContentStatus.ARCHIVED


def test_invalid_transition_error_message():
    with pytest.raises(InvalidTransitionError) as exc_info:
        transition(ContentStatus.IDEA, ContentStatus.PUBLISHED)
    assert "idea" in str(exc_info.value)
    assert "published" in str(exc_info.value)
