"""Shared constants and errors for the M8-GTM receipt harness."""

from __future__ import annotations

WORKFLOW_SLUG = "support-triage-human-review"
WORKFLOW_NAME = "Customer Trust Triage Receipt"
EVIDENCE_MODE = "fixture_backed_local_demo"

LOCAL_FIXTURE_LIMITATION = (
    "The fixture simulates an n8n-style run with local artifacts; it does not "
    "prove live Gmail, Slack, Google Sheets, HubSpot, or n8n API execution."
)
NO_LIVE_SEND_LIMITATION = "No live customer message was sent by P0."
NO_COMPLIANCE_LIMITATION = (
    "The receipt does not certify compliance or provide legal assurance."
)


class M8GTMError(ValueError):
    """Base error for M8-GTM fixture-backed demo failures."""


class UnknownWorkflowError(M8GTMError):
    """Raised when the operator asks for an unsupported M8 demo workflow."""


class FixtureValidationError(M8GTMError):
    """Raised when a local demo fixture is malformed or unsafe to receipt."""
