"""Content state machine.

Canonical lifecycle (PRD §13 — 12 states, authoritative):
  idea → planned → scripted → rendered → qa_passed → awaiting_approval
                                       ↘ qa_failed → rendered (retry)
  awaiting_approval → approved → scheduled → published → measured → archived

Note: PRD §12.5 lists 11 states (omits 'measured'). §13 is canonical here.
Decision recorded in DECISIONS.md.
"""

from enum import Enum


class ContentStatus(str, Enum):
    IDEA = "idea"
    PLANNED = "planned"
    SCRIPTED = "scripted"
    RENDERED = "rendered"
    QA_FAILED = "qa_failed"
    QA_PASSED = "qa_passed"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    MEASURED = "measured"
    ARCHIVED = "archived"


class InvalidTransitionError(Exception):
    def __init__(self, current: ContentStatus, new: ContentStatus) -> None:
        super().__init__(
            f"Invalid transition: {current.value!r} → {new.value!r}"
        )
        self.current = current
        self.new = new


VALID_TRANSITIONS: dict[ContentStatus, set[ContentStatus]] = {
    ContentStatus.IDEA: {ContentStatus.PLANNED, ContentStatus.ARCHIVED},
    ContentStatus.PLANNED: {ContentStatus.SCRIPTED, ContentStatus.ARCHIVED},
    ContentStatus.SCRIPTED: {ContentStatus.RENDERED, ContentStatus.ARCHIVED},
    ContentStatus.RENDERED: {ContentStatus.QA_PASSED, ContentStatus.QA_FAILED, ContentStatus.ARCHIVED},
    ContentStatus.QA_FAILED: {ContentStatus.RENDERED, ContentStatus.ARCHIVED},  # retry path
    ContentStatus.QA_PASSED: {ContentStatus.AWAITING_APPROVAL, ContentStatus.ARCHIVED},
    ContentStatus.AWAITING_APPROVAL: {ContentStatus.APPROVED, ContentStatus.ARCHIVED},
    ContentStatus.APPROVED: {ContentStatus.SCHEDULED, ContentStatus.ARCHIVED},
    ContentStatus.SCHEDULED: {ContentStatus.PUBLISHED, ContentStatus.ARCHIVED},
    ContentStatus.PUBLISHED: {ContentStatus.MEASURED, ContentStatus.ARCHIVED},
    ContentStatus.MEASURED: {ContentStatus.ARCHIVED},
    ContentStatus.ARCHIVED: set(),  # terminal
}


def transition(current: "ContentStatus | str", new: "ContentStatus | str") -> ContentStatus:
    """Validate and apply a state transition.

    Accepts ContentStatus enum members or raw status strings.
    Raises InvalidTransitionError if the transition is not permitted.
    Raises ValueError if either status string is not a known ContentStatus value.
    """
    current = ContentStatus(current)
    new = ContentStatus(new)
    allowed = VALID_TRANSITIONS.get(current, set())
    if new not in allowed:
        raise InvalidTransitionError(current, new)
    return new
