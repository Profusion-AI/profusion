# AICE Workflow Receipt Validator Design

Date: 2026-05-19
Status: Orchestrator-reviewed for PR5 implementation

## Purpose

Build the local-only validator surface missing after the AICE receipt proof.
The AICE backend path now proves this bounded sequence:

```text
n8n workspace execution -> structured runtime payload -> Profusion receipt packet
```

The active experience is the **AICE Workflow Receipt Validator**. It validates
that one completed AICE receipt packet is inspectable: required files exist,
workflow execution metadata is present, the node trail is represented, artifacts
are preserved, human review is visible, supported claims exist, unsupported
claims exist, limitations exist, paths are safe, and founder-facing language
does not overclaim.

Implementation note from the PR5 orchestrator review: the workflow replay must
be built from the recorded `n8n_execution.nodes_executed` trail, not from a
hand-coded storyboard. The terminal `Profusion Receipt Packet` frame is the only
derived node.

The **HyperFrames Explorer** remains the interactive view inside the validator.
The receipt packet remains the source of truth. The validator is not a new
evidence source and does not certify factual truth, legal clearance, copyright
clearance, fair use, compliance, platform safety, customer traction, production
readiness, or publication safety.

## Scope

Public/demo name: AICE Workflow Receipt Validator.

UI subtitle:

```text
HyperFrames Explorer for one completed Profusion receipt packet
```

The first slice loads a single AICE receipt packet from a local path and serves a
local validation replay:

```bash
uv run profusion hyperframes validate --receipt-dir <receipt_dir>
```

Keep this compatibility command:

```bash
uv run profusion hyperframes serve --receipt-dir <receipt_dir>
```

Both commands bind to `127.0.0.1`, parse the receipt packet, validate the packet
boundary, start the local validator, print the local URL, and print the first
thing Kyle should open. A `--dry-run` mode exists for tests and preflight checks.

PR5 must reject non-loopback bind hosts. Public exposure, LAN exposure, tunnels,
and production deployment remain outside this slice.

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
- Do not generate or claim an MP4 render in PR5.
- Do not add React, JSX, Vite, or a frontend framework.
- Do not use CardMint or content publishing surfaces.
- Do not use "certified," "truth verified," "legally cleared," "fair-use
  approved," "copyright safe," "compliance approved," "platform compliant,"
  "safe to publish," "no risk," "customer validated," or "production ready" as
  founder-facing proof language unless the phrase appears inside an explicit
  unsupported-claims/no-claims section.

## Product Semantics

The validator process is:

```text
run validator
  -> load receipt packet
  -> validate required evidence
  -> replay workflow visually
  -> inspect artifacts
  -> compare supported vs unsupported claims
  -> copy founder proof summary
```

The naming hierarchy is:

```text
Validator = process and founder-facing product moment.
Explorer = interactive view inside the validator.
Receipt = source of truth.
HyperFrames = future visual/render layer.
```

## Architecture

The receipt packet remains the source of truth. The validator has three small
units:

1. `src/orchestrator/hyperframes_receipts.py`
   - Pure parser, validator, and HTML renderer.
   - Reads `workflow_receipt.json`, `artifact_manifest.json`,
     `m8_observation.json`, and `artifacts/runtime_payload.json`.
   - Produces a normalized validator model with workflow metadata, AICE node
     map, derived edges, artifact summaries, receipt sections, validation
     findings, safe founder claims, and scene-ready render data.

2. `src/orchestrator/hyperframes_server.py`
   - Local FastAPI app for one receipt directory.
   - Serves `/` for the validator explorer, `/api/model` for the normalized
     model, `/receipt` for the generated `workflow_receipt.html`, safe
     `/packet/<path>` links for files inside the receipt directory, and a
     compatibility `/artifacts/<path>` route for files under `artifacts/`.

3. `src/orchestrator/cli.py`
   - Adds `profusion hyperframes validate`.
   - Keeps `profusion hyperframes serve` as an alias/compatibility command.
   - Defaults to local-only bind `127.0.0.1`.
   - Provides `--dry-run` so parser, validation status, and URL output are
     testable without blocking the test process.

## HyperFrames Fit

HyperFrames is the right downstream render layer because its current public
docs describe an HTML-native, agent-oriented workflow for previewing and
rendering compositions. The PR5 validator should therefore use plain
HTML/CSS/JS and scene-ready `data-*` attributes now, while deliberately leaving
actual preview/render commands for a later video slice.

## Normalized Model

The parser produces the existing workflow, node, edge, artifact, and receipt
section fields plus a first-class validation object:

```json
{
  "validation": {
    "validation_status": "validated_with_limitations",
    "core_files_present": true,
    "display_files_present": true,
    "runtime_payload_found": true,
    "workflow_slug_matches": true,
    "n8n_execution_id_present": true,
    "node_count_matches_trail": true,
    "minimum_node_count_met": true,
    "human_review_artifact_present": true,
    "supported_claims_present": true,
    "unsupported_claims_present": true,
    "limitations_present": true,
    "forbidden_overclaim_language_found": false,
    "artifact_hashes_checked": "partial",
    "artifact_hash_limitation": "Only manifest-listed hashes were available for validation.",
    "path_safety_passed": true,
    "validation_findings": []
  }
}
```

Use `validated_with_limitations` for the known-good AICE packet. Use
`validated_with_warnings` when the packet can still be inspected but an
optional display surface such as `workflow_receipt.html` is missing. Fail fast
for missing core JSON files. Use `validation_failed` only when a parsed packet
has a fatal boundary problem, unsafe path, forbidden founder-facing overclaim,
or missing core proof condition.

Validation findings use a small schema:

```json
{
  "severity": "pass",
  "code": "runtime_payload_found",
  "message": "Runtime payload artifact is present."
}
```

Allowed severities are `pass`, `warn`, and `fail`.

## Visual Model

The first screen should read as a validation instrument, not a generic admin
dashboard. It opens with:

```text
AICE Workflow Receipt Validator
Validated with limitations
This n8n workflow ran. Profusion preserved what happened.
```

It immediately shows four proof counters:

```text
7 nodes executed
6 receipt artifacts found
2 claim boundaries present
1 human review gate recorded
```

The core visual grammar is:

```text
Execution -> Evidence -> Receipt
```

The left side shows the recorded n8n path. The middle makes the **Human
Editorial Review Gate** visually distinct. The right side shows the receipt
packet, claim boundary, and limitations. The bottom shows the artifact ledger
with hashes and view links.

The primary validation surface contains:

- A clickable seven-node AICE workflow plus a derived terminal frame,
  `Profusion Receipt Packet`.
- A visually distinct Human Editorial Review Gate.
- Labeled data movement lanes for topic/thesis, source card, quote candidate,
  claim map, rights review, ambiguity register, human review state, runtime
  payload, and receipt packet.
- Artifact ledger with file purpose, path, hash, existence, and safe view links.
- Embedded or linked finished receipt.
- Evidence map fields from runtime payload and receipt files.
- Supported and unsupported claims in separate columns.
- Limitations visible near the claim boundary.
- Founder-safe claim panel.
- Validation findings panel with PASS, WARN, and FAIL tiers.
- Copy Founder Proof Summary button.

The artifact ledger must include every manifest-listed artifact and any required
receipt display/core files that are not already listed in the manifest.

The lineage note must be explicit:

```text
AICE workflow map derived from recorded node trail and receipt artifacts.
```

## Scene-Ready Markup

PR5 does not create a HyperFrames MP4, but the generated page must be structured
so a follow-on HyperFrames video slice can reuse the same model and markup. The
DOM must include these scene markers:

```html
<main data-prof-demo="aice-validator">
  <section data-scene="validation-header"></section>
  <section data-scene="workflow-replay"></section>
  <section data-scene="human-review-gate"></section>
  <section data-scene="claim-boundary"></section>
  <section data-scene="artifact-ledger"></section>
  <section data-scene="founder-summary"></section>
</main>
```

Do not add video timing attributes or claim render readiness in PR5. The page
only needs to be visually strong enough to screen-record and composition-ready
enough for a later HyperFrames render slice.

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

Use this verified local packet for the first manual validator check:

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

Kyle can run one local command, open one local URL, and immediately see:

- the workflow ran
- the receipt packet exists
- the human review boundary is visible
- artifacts are inspectable
- claims are separated into supported and unsupported
- limitations are explicit
- a founder-safe summary can be copied
- the visual surface is good enough to serve as the basis for the actual product
  demo video

The validator proves inspectability over a completed receipt packet. It does not
prove production n8n Cloud API reachability, public API exposure, source
credential validity, factual truth, copyright clearance, fair use, legal
compliance, platform compliance, publication safety, customer traction,
production readiness, or MP4 rendering.
