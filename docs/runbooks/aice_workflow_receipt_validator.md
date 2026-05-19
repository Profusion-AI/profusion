# AICE Workflow Receipt Validator Runbook

Date: 2026-05-19
Status: Local-only PR5 validator

## Purpose

The AICE Workflow Receipt Validator turns one completed AICE receipt packet into
a local validation replay. It helps Kyle inspect what ran, what data moved, what
artifacts exist, where human review entered, what the receipt supports, and what
it does not prove.

The HyperFrames Explorer is the interactive view inside the validator. The
receipt packet remains the source of truth.

## Command

```bash
uv run profusion hyperframes validate \
  --receipt-dir /tmp/profusion-aice-workspace-proof-post-merge/aice-source-to-narrative-receipt/receipt-20260519T150640Z-35fbc20a
```

Open:

```text
http://127.0.0.1:8765/
```

Dry-run preflight:

```bash
uv run profusion hyperframes validate \
  --receipt-dir /tmp/profusion-aice-workspace-proof-post-merge/aice-source-to-narrative-receipt/receipt-20260519T150640Z-35fbc20a \
  --dry-run
```

Compatibility command:

```bash
uv run profusion hyperframes serve \
  --receipt-dir /tmp/profusion-aice-workspace-proof-post-merge/aice-source-to-narrative-receipt/receipt-20260519T150640Z-35fbc20a
```

## Required Receipt Files

- `artifact_manifest.json`
- `m8_observation.json`
- `workflow_receipt.json`
- `workflow_receipt.md`
- `workflow_receipt.html`
- `artifacts/runtime_payload.json`

## What To Look At First

Start with the validation header and workflow replay. Confirm:

- `AICE Workflow Receipt Validator`
- `Validated with limitations`
- evidence mode `workspace_runtime_n8n_payload`
- n8n workflow ID
- execution ID
- node count `7`
- `Human Editorial Review Gate`
- `Profusion Receipt Packet` terminal frame
- supported and unsupported claims side by side
- limitations visible near the claim boundary

## What This Validates

This validates that a completed receipt packet can be loaded locally and
inspected as a reviewable workflow evidence packet. It shows the recorded n8n
node trail, runtime payload, receipt artifacts, final HTML receipt, supported
claims, unsupported claims, limitations, and copyable founder proof summary.

## What This Does Not Validate

- public production deployment
- public Profusion API exposure
- live source credentials
- legal clearance
- fair-use approval
- factual truth certification
- platform-policy compliance
- publication safety
- customer traction
- production readiness
- MP4 rendering

## Safe Claim

```text
This n8n workflow ran. Profusion preserved what happened. The receipt tells you what the evidence supports and what it does not.
```
