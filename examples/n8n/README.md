# n8n Examples

This directory contains importable n8n workflow examples for Profusion receipt
demos. They are local-demo assets only: no secrets, credentials, live sends, or
media downloads are included.

## AICE Source-to-Narrative Receipt

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
