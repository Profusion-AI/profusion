# Receipt Review Checklist

Date: 2026-05-06

Use this checklist before moving a receipt from `draft` to `reviewed` or `approved_for_packet`.

## Readability

- The receipt is understandable without explaining the cockpit, SQLite, FastAPI, CLI commands, or milestone history.
- The workflow summary is plain English.
- Artifact pointers are readable enough for a prospect or reviewer.
- The business value is clear.

## Evidence Boundary

- The receipt states what is inside the evidence boundary.
- The receipt states what is outside the evidence boundary.
- AI touchpoints are identified.
- Human review role is identified.
- QA or review checkpoint status is identified.

## Claim Safety

- The receipt does not imply certification.
- The receipt does not imply guaranteed compliance.
- The receipt does not imply verified truth.
- The receipt does not imply identity or liveness verification.
- The receipt does not imply universal synthetic-media detection.
- The receipt does not imply code correctness.
- The receipt does not imply production coding-agent, PR, diff, CI, or MCP capture unless that integration exists.
- The receipt does not imply hiring recommendation, ranking, selection, or rejection.

## Status Separation

- Content approval is not treated as receipt approval.
- Receipt approval is not treated as customer delivery.
- A `draft` receipt is not represented as externally approved.

## Decision

Choose one:

- Keep as `draft`.
- Move to `reviewed`.
- Move to `approved_for_packet`.
- Move to `delivered` only after the packet has actually been sent or shown.

Reviewer:

Date:

Notes:
