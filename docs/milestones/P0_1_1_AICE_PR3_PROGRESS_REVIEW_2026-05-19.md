# P0.1.1 AICE PR3 Progress Review

Date: 2026-05-19
Status: Review note for PR #3 before merge.
PR: https://github.com/Profusion-AI/profusion/pull/3
Branch: `codex/p0-1-1-aice-live-receipt`
Implementation commit reviewed: `e98089f feat: add AICE live receipt workflow`

## Executive Summary

PR #3 implements the first live-local AICE receipt proof for Profusion:

```text
local n8n workflow -> Profusion M8 receipt harness -> AICE workflow receipt packet
```

The important progress is real: AICE now has a registry-backed receipt path,
fixture/data-contract artifacts, an importable n8n workflow, AICE-specific
receipt sections, no-claims language, ambiguity preservation, HTML escaping
tests, and a generated receipt packet with hashed artifacts.

The important correction is also real: PR #3 is not an n8n MCP/cloud proof. It
uses local n8n CLI execution with controlled fallback metadata. The n8n MCP is
configured and callable in the Codex environment, but this PR did not create,
update, or execute the AICE workflow through that MCP-backed n8n workspace.

Verdict:

```text
GREEN for local n8n-to-Profusion receipt proof.
YELLOW for the full P0.1.1 "live n8n MCP/cloud" interpretation.
```

PR #3 is safe to review as the local proof layer. It should not be messaged as
the final MCP/cloud n8n proof until a follow-up commit or PR creates/tests the
workflow through `n8n_mcp`.

## What PR #3 Adds

Core harness changes:

```text
src/orchestrator/m8_gtm/registry.py
src/orchestrator/m8_gtm/fixtures.py
src/orchestrator/m8_gtm/harness.py
src/orchestrator/m8_gtm/renderers.py
src/orchestrator/m8_gtm/schemas.py
src/orchestrator/cli.py
```

New AICE tests:

```text
tests/test_m8_aice_receipt_harness.py
```

New AICE fixture and data-contract files:

```text
examples/m8/aice-source-to-narrative-receipt/
  README.md
  workflow.json
  source_policy.json
  topic_brief.json
  runs/run_001_live_minimum_aice/
    run.json
    source_cards.json
    quote_candidates.json
    claim_map.json
    attention_intelligence_map.json
    rights_review.json
    ambiguity_register.json
    human_editorial_review.json
    narrative_brief.json
    visual_plan.json
    execution_log.json
    n8n_run_summary.json
```

New n8n local workflow assets:

```text
examples/n8n/README.md
examples/n8n/aice-source-to-narrative-receipt.workflow.json
```

New durable AICE primer:

```text
docs/AICE-understanding.md
```

## Current PR State

At review time:

```text
PR #3: open
Mergeability: mergeable
Base: main
Head: codex/p0-1-1-aice-live-receipt
GitHub backend CI: passed
```

The branch was pushed to GitHub and is tracking:

```text
origin/codex/p0-1-1-aice-live-receipt
```

## What Was Proven

PR #3 proves that Profusion can generate an AICE receipt packet through the
existing M8-GTM receipt harness using a new workflow slug:

```text
aice-source-to-narrative-receipt
```

The generated receipt uses:

```text
workflow_name: AICE Source-to-Narrative Workflow Receipt
trust_domain: ai_assisted_investigative_content
evidence_mode: fixture_backed_live_n8n_demo
```

The local n8n workflow proof executed 7 nodes:

```text
Manual Trigger
Build Topic Brief
Source Metadata/Search Adapter Fallback
Claim + Quote Candidate Extraction
Rights/Ambiguity Classification
Generate Receipt Packet via Code Command
Return Receipt Summary
```

Fresh live-local n8n proof packet:

```text
/tmp/profusion-aice-p0-1/aice-source-to-narrative-receipt/receipt-20260519T111329Z-d2c41c8b/
```

Fresh direct AICE CLI packet:

```text
/tmp/profusion-aice-p0-1-pr/aice-source-to-narrative-receipt/receipt-20260519T111228Z-cad8b60b/
```

Fresh support-triage baseline packet:

```text
/tmp/profusion-support-baseline-pr/support-triage-human-review/receipt-20260519T111225Z-c190611f/
```

## What Was Not Proven

PR #3 does not prove:

```text
- n8n MCP workflow creation.
- n8n MCP workflow update.
- n8n MCP workflow execution.
- Cloud n8n execution of the AICE workflow.
- Credentialed YouTube/API metadata discovery.
- Third-party media download, import, storage, editing, republishing, or monetization.
- External publishing.
- Factual truth certification.
- Copyright clearance.
- Fair-use certification.
- Platform-policy compliance.
- Journalistic neutrality.
- PBS/Frontline affiliation or endorsement.
- Final content publication safety.
```

The n8n MCP was verified as callable after the PR was created. A search for
AICE workflows through the MCP returned no existing AICE workflow at that time.
That means the MCP lane remains open work.

## Supported Claims In The Receipt

The AICE receipt makes bounded positive claims:

```text
- The n8n workflow executed in the recorded P0.1.1 live-minimum path.
- At least three n8n nodes participated; the recorded node count is 7.
- A topic/thesis artifact was captured.
- At least one source card was captured.
- At least one claim candidate was mapped to a source card.
- At least one quote or segment candidate was captured as metadata/reference only.
- At least one Attention Intelligence dimension was mapped.
- At least one rights, risk, or ambiguity item was recorded.
- A human editorial review artifact exists for the narrative decision.
- A receipt packet was generated with artifact hashes.
- The receipt includes supported claims, unsupported claims, and limitations.
```

These claims are intentionally narrow. They describe captured process evidence,
not publication clearance or source truth.

## Unsupported Claims And No-Claims Boundary

The receipt explicitly states that it does not prove:

```text
- factual truth
- copyright clearance
- fair use
- permission to download, edit, republish, or monetize third-party audio/video
- platform-policy compliance
- journalistic neutrality
- PBS/Frontline affiliation or endorsement
- final content safety to publish
- replacement of human editorial or legal review
```

This no-claims section is part of the product, not a weakness. AICE preserves
bounded uncertainty as an inspectable artifact.

## Ambiguities Preserved

The AICE receipt preserves multiple review states:

```text
- rights/context review required
- claim-strength uncertainty unresolved
- synthetic media disclosure review required
- platform/copyright/fair-use ambiguity requiring human review
```

These are recorded as explicit ambiguity states rather than hidden as notes.

## Verification Run

Fresh verification before opening PR #3:

```bash
uv run profusion m8 demo support-triage-human-review --output-dir /tmp/profusion-support-baseline-pr
uv run profusion m8 demo aice-source-to-narrative-receipt --output-dir /tmp/profusion-aice-p0-1-pr
uv run pytest tests/test_m8_gtm_receipt_harness.py tests/test_m8_aice_receipt_harness.py -q
uv run pytest -q
uv run profusion smoke --offline
git diff --check
```

Results:

```text
support-triage demo: passed
AICE demo: passed
targeted M8/AICE tests: 14 passed
full test suite: 207 passed
offline smoke: passed
git diff --check: passed
GitHub backend CI: passed
```

n8n local proof:

```bash
N8N_USER_FOLDER=/tmp/profusion-n8n-user-pr \
N8N_DIAGNOSTICS_ENABLED=false \
N8N_VERSION_NOTIFICATIONS_ENABLED=false \
npx --yes n8n import:workflow \
  --input examples/n8n/aice-source-to-narrative-receipt.workflow.json

N8N_USER_FOLDER=/tmp/profusion-n8n-user-pr \
N8N_DIAGNOSTICS_ENABLED=false \
N8N_VERSION_NOTIFICATIONS_ENABLED=false \
NODE_FUNCTION_ALLOW_BUILTIN=child_process \
npx --yes n8n execute --id=aiceSourceNarrativeP011 --rawOutput
```

Result:

```text
n8n import: passed
n8n execute: passed
nodes executed: 7
receipt generated: /tmp/profusion-aice-p0-1/aice-source-to-narrative-receipt/receipt-20260519T111329Z-d2c41c8b/
```

## Important Implementation Detail

Local n8n `2.20.x` did not expose the Execute Command node in the CLI path used
during this sprint. The workflow therefore uses a Code node with:

```text
NODE_FUNCTION_ALLOW_BUILTIN=child_process
```

That Code node invokes:

```bash
uv run profusion m8 demo aice-source-to-narrative-receipt --output-dir /tmp/profusion-aice-p0-1
```

This is acceptable for the local proof, but it is not the final cloud/MCP
orchestration posture. A cloud n8n workflow should call a controlled webhook or
service endpoint rather than shelling into a local repo.

## Subagents Used

Subagents used during the sprint:

```text
Volta: harness/registry inspection
Tesla: n8n workflow JSON and README draft
Kuhn: AICE fixture/data-contract draft
Herschel: receipt/no-claims QA
Hooke: final sidecar review
```

Hooke identified two valid review issues before final verification:

```text
1. The receipt claimed live n8n execution while some fixture artifacts still
   said "no live execution proof."
2. AICE artifact manifests inherited support-triage limitations.
```

Both were fixed before the branch was pushed:

```text
- Fixture language now distinguishes local live-minimum n8n proof from
  credentialed YouTube/API or cloud n8n proof.
- AICE manifests now use AICE-specific limitations.
- Tests cover those boundaries.
```

## Strategic Context

This PR sits inside the post-split Profusion boundary:

```text
Profusion = B2B workflow trust and evidence receipts.
Attention Media Lab = separated education/content engine.
```

AICE is allowed to return as a Profusion workflow only because the P0.1.1 slice
is a governance/receipt proof, not a revival of the old content engine inside
the Profusion repo.

Current versioning posture:

```text
P0: existing support-triage-human-review receipt baseline.
P0.1.1: AICE Source-to-Narrative Workflow Receipt, local live n8n proof.
P0.1.2 or follow-up: n8n MCP/cloud workflow creation and execution proof.
P0.2: Cardmint receipt remains deferred as a solo-operator inventory demo.
P1: receipt-derived media/video only after receipt proof is accepted.
```

## Review Recommendation

Review PR #3 as:

```text
local live n8n-to-Profusion AICE receipt proof
```

Do not review or merge it as:

```text
n8n MCP/cloud execution proof
```

Recommended merge posture:

```text
Merge PR #3 if the immediate goal is to land the AICE receipt harness,
fixtures, local n8n workflow export, and durable AICE primer.

Hold PR #3 or add a follow-up commit if the merge gate is specifically
"MCP-backed n8n workflow created and executed in the remote n8n workspace."
```

## Next Work

Recommended next tasks:

```text
1. Use `n8n_mcp` to create or update an AICE workflow in the MCP-backed n8n
   workspace.
2. Decide whether the MCP workflow should call a local tunnel/webhook, a
   temporary local bridge, or remain MCP-tested with pinned/fallback data.
3. Generate a second receipt or review artifact that distinguishes:
   local n8n CLI proof vs MCP/cloud n8n proof.
4. Update PR #3 or open a follow-up PR depending on whether Kyle wants the MCP
   proof in the same branch.
5. Keep YouTube/media handling metadata-only until a rights/permission path is
   explicitly designed and approved.
```

## Bottom Line

PR #3 is meaningful progress. It turns AICE from a memo into a working local
receipt path:

```text
topic/thesis -> source/claim/quote artifacts -> risk/ambiguity review ->
human editorial review -> Profusion receipt packet
```

The remaining gap is precise:

```text
PR #3 proves local n8n execution.
It does not yet prove n8n MCP/cloud execution.
```

