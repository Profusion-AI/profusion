# M8-GTM n8n Receipt Harness Runbook

Date: 2026-05-18
Status: P0 fixture-backed local demo

## Purpose

The M8-GTM receipt harness produces a buyer-readable Customer Trust Triage
Receipt from local support-triage artifacts.

The demo proves this narrow mechanism:

```text
AI-assisted workflow -> captured artifacts -> human review boundary -> M8 observation -> workflow receipt -> supported and unsupported claims
```

It does not prove live integrations, automated support, compliance status, or
production readiness.

## Quick Start

Run from the Profusion repo root:

```bash
uv run profusion m8 demo support-triage-human-review
```

Optional custom output root:

```bash
uv run profusion m8 demo support-triage-human-review --output-dir /tmp/profusion-m8-demo
```

## Generated Files

Default output root:

```text
data/receipts/m8-gtm/support-triage-human-review/<receipt_id>/
```

Required files:

```text
artifact_manifest.json
m8_observation.json
workflow_receipt.json
workflow_receipt.md
workflow_receipt.html
artifacts/
```

## What Is Real

- Local fixture files are copied into a durable receipt packet.
- SHA-256 hashes are computed for each copied artifact.
- The sensitive billing complaint must include `human_review_event.json`.
- `m8_observation.json` includes supported claims, unsupported claims, and
  limitations.
- `workflow_receipt.md` and `workflow_receipt.html` are rendered from
  `workflow_receipt.json`.
- HTML rendering escapes fixture-derived text.
- Packet writes use a `.partial` directory and rename only after required files
  are present.

## What Is Mocked

- The source workflow is an n8n-style local fixture, not a live n8n execution.
- Inbound support messages are local markdown files.
- AI classifications and drafts are fixture artifacts.
- Final reply files are marked ready in fixture logs only.
- No live customer message is sent.

## NO_CLAIMS

P0 does not prove live n8n execution.

P0 does not prove live Gmail, Slack, Google Sheets, HubSpot, or n8n
integration.

P0 does not send customer messages.

P0 does not certify compliance.

P0 does not provide legal assurance.

P0 does not prove the billing complaint is factually true.

P0 does not make support automation a product.

## Troubleshooting

Unknown workflow:

```bash
uv run profusion m8 demo not-a-real-workflow
```

Expected behavior: exits non-zero with `Unknown M8 demo workflow`.

Missing human review:

```text
sensitive_billing_complaint requires a human_review_event.json artifact
```

Fix: restore
`examples/m8/support-triage-human-review/runs/run_002_sensitive_billing_complaint/human_review_event.json`.

Incomplete packet:

Expected behavior: no completed packet directory is left behind. A failed run
may remove the `.partial` directory before exiting.

## Before Live Customer-Facing Use

- Replace fixture replay with a reviewed live-capture boundary.
- Define credential handling and secret storage.
- Confirm n8n execution-history export shape.
- Add redaction policy for customer data.
- Add reviewer identity policy.
- Add legal/compliance review for any external claims.
- Add buyer-facing review of the generated receipt language.

## Deferred Work

P1 HyperFrames demo video is downstream of P0 receipt acceptance.

P2 cockpit visibility is optional and read-only. It must not add approval
buttons, scheduling, publishing, mutation logic, or public website changes.
