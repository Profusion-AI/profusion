# n8n Examples

This directory contains importable n8n workflow examples for Profusion receipt
demos. They include no secrets, credentials, live sends, or media downloads.

There are two different proof modes here:

1. Local fixture-backed demo: n8n triggers the existing Profusion fixture demo.
2. Workspace runtime-payload proof: n8n produces a runtime payload that
   Profusion can ingest through `profusion m8 generate-from-payload` or
   `POST /api/m8/aice/receipt`.

Do not treat the local fixture-backed workflow as the workspace-runtime proof.

## Local Fixture-Backed AICE Demo

Workflow file:

```text
examples/n8n/aice-source-to-narrative-receipt.workflow.json
```

Key nodes:

- `Manual Trigger`
- `Build Topic Brief`
- `Source Metadata/Search Adapter Fallback`
- `Claim + Quote Candidate Extraction`
- `Rights/Ambiguity Classification`
- `Generate Receipt Packet via Code Command`
- `Return Receipt Summary`

The workflow uses controlled fallback source metadata when HTTP or YouTube
credentials are absent. It records that limitation in the payload and keeps all
quote candidates as metadata-only. It does not download media.

The receipt-generation node runs the local Profusion CLI from the repo root.
This n8n package does not expose `n8n-nodes-base.executeCommand`, so the demo
uses a Code node with `child_process` explicitly enabled for local execution:

```bash
NODE_FUNCTION_ALLOW_BUILTIN=child_process \
uv run profusion m8 demo aice-source-to-narrative-receipt --output-dir /tmp/profusion-aice-p0-1
```

Before importing, confirm the host running n8n can access `/home/kyle/profusion`
and can run `uv`. The generated packet is written under
`/tmp/profusion-aice-p0-1`.

This workflow is intentionally local-only and fixture-backed. It calls:

```bash
uv run profusion m8 demo aice-source-to-narrative-receipt
```

That means Profusion loads committed fixture files. It does not prove that a
hosted n8n workspace passed runtime data directly into receipt generation.

## Workspace Runtime-Payload Proof

Workflow file:

```text
examples/n8n/aice-source-to-narrative-workspace-proof.workflow.json
```

Key nodes:

- `Manual Trigger`
- `Build Topic Brief`
- `Build Source Cards`
- `Extract Claim and Quote Candidates`
- `Rights and Ambiguity Classification`
- `Human Editorial Review Stub`
- `Return Runtime Payload for Profusion`

This workflow mirrors the workspace proof created in the
`AttentionIntelligence-ContentEngine` n8n project. It does not call
`child_process`, does not assume `/home/kyle/profusion`, and does not call the
fixture-backed `m8 demo` command.

The workflow returns a structured runtime payload containing the workflow ID,
execution ID, node trail, topic brief, source cards, quote candidates, claim
map, rights review, ambiguity register, human editorial review state, narrative
brief, visual plan, supported limitations, and media-use boundaries.

Use the returned payload with:

```bash
uv run profusion m8 generate-from-payload \
  aice-source-to-narrative-receipt \
  --input /path/to/aice-runtime-payload.json \
  --output-dir /tmp/profusion-aice-workspace-proof \
  --json
```

Or, when a governed reachable API URL exists, POST it to:

```text
POST /api/m8/aice/receipt
```

### API Exposure Guard

`POST /api/m8/aice/receipt` is a local proof endpoint today. Do not expose it
through a public tunnel, domain, or cloud route until the next integration pass
adds:

- `PROFUSION_AICE_RECEIPT_TOKEN`
- `Authorization: Bearer <token>`
- project or workflow allowlisting
- payload-size limits
- redaction rules for source and review data
