# AICE HyperFrames Receipt Explorer Design

Date: 2026-05-19
Status: Ready for Kyle review before implementation

## Purpose

Build the local-only visual proof surface missing after the AICE receipt proof.
The AICE backend path now proves:

```text
n8n workspace execution -> structured runtime payload -> Profusion receipt packet
```

The explorer must make that proof visible as a workflow, data movement path,
artifact compendium, and receipt view. It is a lens over one completed receipt
packet. It is not a new evidence source.

## Scope

Project name: AICE HyperFrames Receipt Explorer.

The first slice loads a single AICE receipt packet from a local path and serves a
local viewer:

```bash
uv run profusion hyperframes serve --receipt-dir <receipt_dir>
```

The command binds to `127.0.0.1`, parses the receipt packet, starts a local
viewer, prints the local URL, and prints the first thing Kyle should open. A
`--dry-run` mode exists for tests and preflight checks.

The implementation deliberately avoids a browser directory picker in the first
slice. A path-backed loader is smaller, testable, and better aligned with the
current CLI-first Profusion proof.

## Non-Goals

- Do not build a broad SaaS dashboard.
- Do not extend the M7 operator cockpit queue, approvals, retries, scheduling,
  publishing, or item-state surfaces.
- Do not deploy publicly or open a tunnel.
- Do not activate or mutate n8n workflows.
- Do not send external communications.
- Do not generate or claim an MP4 render in this first explorer slice.
- Do not add "certified," "truth verified," "compliance approved," or legal
  clearance language.
- Do not use CardMint or content publishing surfaces.

## Architecture

The receipt packet remains the source of truth. The explorer has three small
units:

1. `src/orchestrator/hyperframes_receipts.py`
   - Pure parser and HTML renderer.
   - Reads `workflow_receipt.json`, `artifact_manifest.json`,
     `m8_observation.json`, and `artifacts/runtime_payload.json`.
   - Produces a normalized Hyperframe model with workflow metadata, AICE node
     map, derived edges, artifact summaries, receipt sections, verification
     checks, and founder-safe claims.

2. `src/orchestrator/hyperframes_server.py`
   - Local FastAPI app for one receipt directory.
   - Serves `/` for the visual explorer, `/api/model` for the normalized model,
     `/receipt` for the generated `workflow_receipt.html`, and safe
     `/artifacts/<path>` links for files inside the receipt directory.

3. `src/orchestrator/cli.py`
   - Adds `profusion hyperframes serve`.
   - Defaults to local-only bind `127.0.0.1`.
   - Provides `--dry-run` so parser and URL output are testable without blocking
     the test process.

## Visual Model

The view should open with the completion header:

```text
AICE MVP Receipt Loaded
Workspace runtime receipt generated
```

It should show workflow name, evidence mode, n8n workflow ID, execution ID, node
count, receipt ID/path, and the status badge. The primary proof board contains:

- A clickable seven-node AICE workflow plus a derived terminal frame,
  `Profusion Receipt Packet`.
- Labeled data movement lanes for topic/thesis, source card, quote candidate,
  claim map, rights review, ambiguity register, human review state, runtime
  payload, and receipt packet.
- Artifact compendium with file purpose, path, hash, and view links.
- Embedded finished receipt.
- Evidence map fields from runtime payload and receipt files.
- Supported and unsupported claims in separate columns.
- Founder-safe claim panel.
- Verification panel.
- Copy Founder Proof Summary button.

The lineage note must be explicit:

```text
AICE workflow map derived from recorded node trail and receipt artifacts.
```

## Exact Safe Claim

Display this exact claim:

```text
This n8n workflow ran. Profusion preserved what happened. The receipt tells you what the evidence supports and what it does not.
```

Also display:

```text
Profusion turns one AI-assisted workflow execution into reviewable evidence: what ran, what artifacts existed, where human review entered, what claims are supported, what claims are not supported, and what limitations remain.
```

## Starting Receipt Packet

Use this verified local packet for the first manual explorer check:

```text
/tmp/profusion-aice-workspace-proof-post-merge/aice-source-to-narrative-receipt/receipt-20260519T150640Z-35fbc20a/
```

It contains:

- `artifact_manifest.json`
- `m8_observation.json`
- `workflow_receipt.json`
- `workflow_receipt.md`
- `workflow_receipt.html`
- `artifacts/runtime_payload.json`

The packet records workspace workflow ID `OGMdBpOOVXRMSzR6`, execution ID `1`,
node count `7`, and evidence mode `workspace_runtime_n8n_payload`.

## Acceptance

Kyle can run one local command, open one local URL, and see the AICE workflow,
data movement, artifacts, final receipt, supported claims, unsupported claims,
limitations, and copyable founder proof summary. The explorer proves visibility
over a completed receipt packet. It does not prove production n8n Cloud API
reachability, public API exposure, source credential validity, factual truth,
copyright clearance, fair use, legal compliance, platform compliance,
publication safety, customer traction, or MP4 rendering.
