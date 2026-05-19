# AICE Understanding - Renewed Sprint Memory

**Document purpose:** Durable source-of-truth primer for future Profusion.AI
Restart chats, Codex sessions, Claude/OpenClaw handoffs, and agentic
implementation work involving **AICE**.

**Date:** 2026-05-19
**Owner:** Kyle Greenwell / Profusion AI
**Project:** Profusion.AI Restart
**Current sprint frame:** P0.1.1 - AICE Source-to-Narrative Workflow Receipt,
live n8n-to-receipt proof
**Primary operating rule:** AICE does not merely generate content. AICE
preserves the receipts behind the argument.

## 1. What AICE Means

**AICE** means **Attention Intelligence Content Engine**.

AICE is not simply a video generator, content automation tool, YouTube clip
finder, n8n workflow, or "AI documentary maker." It is the content-facing
expression of the broader Profusion thesis:

> AI makes outputs cheap. Profusion makes the process inspectable. Attention
> Intelligence makes the human side teachable.

AICE turns a topic, thesis, or episode idea into an inspectable
source-to-narrative workflow:

```text
episode thesis
  -> source discovery
  -> source cards
  -> claim and quote candidates
  -> Attention Intelligence mapping
  -> rights / risk / ambiguity classification
  -> human editorial review
  -> narrative brief
  -> visual plan
  -> generated workflow receipt
```

The key product object is not the final video. The key product object is the
**workflow receipt** showing what happened before the content became publishable
or draft-ready.

AICE is therefore best understood as an **evidence-to-narrative engine** and
**workflow receipt generator** for AI-assisted investigative educational media.

## 2. Philosophical Foundation: Attention Intelligence

Attention Intelligence is the human-side doctrine underneath AICE.

Money line:

> Attention Intelligence is the learned agency of deciding what deserves one's
> mind.

Core distinction:

```text
Artificial Intelligence = machine processing.
Attention Intelligence = human direction.
```

AICE must preserve this distinction at all times. Machine systems may search,
cluster, summarize, draft, render, classify, and generate. Human judgment must
still own the thesis, source choices, context, risk boundaries, publication
decisions, and final accountability.

The Attention Intelligence blueprint frames the AI era as one where answers,
drafts, explanations, and derivative outputs become abundant, while attention,
judgment, verification, purpose, and human responsibility become scarce. AICE
exists because content workflows are where that scarcity becomes visible.

AICE should strengthen at least one of the six Attention Intelligence
dimensions:

1. **Attentional sovereignty** - protect attention from capture, algorithmic
   drift, distraction, and compulsive output loops.
2. **Interpretive discernment** - evaluate sources, framing, omissions,
   incentives, synthetic slop, and weak evidence.
3. **Delegation judgment** - know what to outsource to AI, what to verify, what
   to keep human, and when automation becomes abdication.
4. **Purpose alignment** - connect attention and content choices to values,
   audience, service, craft, and long-term meaning.
5. **Temporal agency** - protect depth over time, sequence work, resist
   dopamine-driven context switching, and build durable artifacts.
6. **Relational attention** - preserve human presence, listening, civic
   responsibility, and audience trust in a mediated environment.

AICE should use these Attention Intelligence protocols directly:

```text
Attention Decision Loop:
Notice -> Name -> Choose -> Protect -> Direct -> Convert

AI Delegation Ladder:
Define objective -> classify risk -> generate options -> inspect output -> verify claims -> decide -> own outcome

Attention Audit:
What captured me? What deserved me? What did I delegate? What did I verify? What did I protect? What became action?

Slop Filter:
Source? Incentive? Evidence? Omission? Framing? Human consequence?

Depth Block:
One goal, one context, one tool boundary, one output standard, one reflection.
```

AICE must ask, before using AI:

> What would count as better judgment, not just faster output?

## 3. Strategic Foundation: Profusion As Workflow Trust Infrastructure

Profusion's company-level thesis is:

> When AI participates in consequential work, organizations need process
> evidence.

The public-facing wedge is not "AI content generation." It is:

> Profusion helps teams turn high-risk AI-assisted workflows into reviewable
> evidence packets.

A workflow receipt should show:

```text
what workflow was run
what AI tools participated
what artifacts were created
what sources were used
what claims were made
what human review occurred
what was approved, rejected, or held
what remains uncertain
what the receipt does not prove
```

AICE is the media/content governance lane of that broader thesis.

The renewed AICE sprint uses education, AI, post-labor pedagogy, U.S.
school-system critique, and Attention Intelligence content as the domain. But
the commercial abstraction is broader:

> AI made output faster. Review became the bottleneck. Profusion makes the
> review boundary visible.

AICE is one proof lane for Profusion's workflow receipt category.

## 4. Current Sprint: P0.1.1 AICE Source-to-Narrative Workflow Receipt

The current sprint is **P0.1.1**, not a vague planning exercise.

Codex's earlier conservative framing kept P0 as the existing support-triage
receipt and proposed AICE as a fixture-backed design gate. Kyle rejected the
overcautious "no live n8n" posture. The renewed sprint is:

> We are doing a bounded live minimum now.

### Mission

Implement **AICE Source-to-Narrative Workflow Receipt** as a live proof:

```text
live n8n workflow
  -> passes AICE data through at least three nodes
  -> invokes or triggers Profusion receipt generation
  -> produces an actual receipt packet
```

### Required Workflow Slug

```text
aice-source-to-narrative-receipt
```

### Required Trust Domain

```text
ai_assisted_investigative_content
```

### Required Receipt Title

```text
AICE Source-to-Narrative Workflow Receipt
```

### Current Versioning Posture

```text
P0:     Existing support-triage-human-review receipt remains baseline proof.
P0.1.1: AICE Source-to-Narrative Workflow Receipt, live n8n-to-receipt sprint.
P0.2:   Cardmint receipt, deferred as solo-operator inventory decision demo.
P1:     Receipt-derived video only after AICE receipt acceptance.
```

Cardmint remains valuable, but AICE is now the more strategic sprint because it
connects Profusion receipts, Attention Intelligence, investigative education
media, workflow trust, n8n orchestration, and future content production.

## 5. What "Live" Means In The Renewed Sprint

"Live" does **not** mean reckless. It means the system must execute an actual
workflow rather than only producing design documents.

Minimum live criteria:

```text
- n8n executes an actual workflow.
- The workflow has at least 3 nodes.
- Data passes between nodes.
- The workflow invokes or triggers the Profusion receipt-generation path.
- A receipt packet is generated by the repo.
- The receipt includes artifacts, supported claims, unsupported claims, limitations, and an AICE workflow boundary.
```

Minimum acceptable n8n workflow:

```text
1. Trigger node
   - Manual Trigger or Webhook.
   - Accepts an AICE topic/thesis payload.

2. Source / Claim Preparation node
   - Code node or HTTP Request node.
   - Produces at least one source card, one claim candidate, one quote/segment candidate, one Attention Intelligence mapping, and one rights/risk/ambiguity item.
   - If YouTube/API credentials exist, use a live metadata/search call.
   - If credentials are missing, do not block. Use a controlled live fallback payload inside the running n8n workflow and mark the limitation clearly.
   - Do not download third-party audio/video.
   - Media candidates remain metadata/reference artifacts only.

3. Receipt Generation node
   - Execute Command or HTTP Request to local Profusion.
   - Generates the AICE receipt packet.
   - Returns packet path and summary.
```

Preferred stronger workflow:

```text
Manual Trigger / Webhook
  -> Build AICE Topic Brief
  -> Source Discovery / Source Metadata
  -> Claim + Quote Candidate Extraction
  -> Rights + Ambiguity Classification
  -> Generate AICE Receipt Packet
  -> Return Receipt Summary
```

The preferred workflow feels like an actual AICE pipeline rather than a
ceremonial automation.

## 6. OODA-Driven Development Requirement

Codex should use **OODA-driven development** and act as an orchestrator for
subagents.

OODA means:

```text
Observe: Inspect current repo, current M8 harness, current n8n setup/docs, available commands, and support-triage baseline.

Orient: Identify the smallest live path from n8n trigger to receipt packet without breaking support-triage.

Decide: Select the minimum implementation that produces a live receipt now with bounded risk and no theatrical architecture.

Act: Implement, run, test, correct, and repeat until acceptance criteria pass.
```

This project is behind. Codex should not hide behind another design gate. It
should run OODA loops until a live receipt exists.

## 7. Subagent-Driven Development Requirement

Codex should use its internal subagent-driven development toolkit if available.
It should orchestrate, review, steer, merge, and verify.

Recommended subagent assignments:

```text
Subagent A - Harness / Registry
Inspect M8 support-triage harness and implement the smallest safe registry/generalization for aice-source-to-narrative-receipt. Preserve existing support-triage behavior.

Subagent B - n8n Workflow
Create/importable n8n workflow JSON with at least 3 nodes. Ensure it can run locally and call the receipt generator. Save under a path such as examples/n8n/aice-source-to-narrative-receipt.workflow.json.

Subagent C - AICE Fixtures / Data Contract
Define topic_brief, source_cards, claim_map, quote_candidates, attention_intelligence_map, rights_review, ambiguity_register, human_editorial_review, narrative_brief, visual_plan, execution_log, and n8n_run_summary artifacts.

Subagent D - Receipt / No-Claims QA
Ensure receipt includes supported claims, unsupported claims, limitations, ambiguity states, and no overclaims. Receipt must not claim copyright clearance, fair-use certification, journalistic neutrality, PBS/Frontline affiliation, final publication safety, or legal compliance.

Subagent E - Test / Smoke
Run commands, verify packet shape, verify existing support-triage baseline remains green, verify generated HTML escapes content, and verify failed runs do not leave completed packets.
```

Codex should report:

```text
- OODA cycles completed
- subagents used and what each produced
- files changed
- n8n workflow path
- receipt packet path
- commands run and results
- supported claims
- unsupported claims
- ambiguities preserved
- what remains deferred
- any risks requiring Kyle review
```

## 8. AICE Product Boundary

AICE is allowed to be ambitious. It is not allowed to launder uncertainty.

AICE is:

```text
- an evidence-to-narrative engine
- a source-to-claim workflow
- a receipt generator for AI-assisted investigative content
- a content governance layer
- an Attention Intelligence demonstration layer
- a Profusion proof lane
```

AICE is not:

```text
- a YouTube clip-ripper
- a Frontline clone
- a synthetic news anchor factory
- a legal clearance tool
- a fair-use certification engine
- an automated publisher
- a truth-certification machine
- a tool for bypassing review
- a platform-policy compliance oracle
```

The line is simple:

> AICE may discover, reference, classify, and review media candidates. AICE may
> not assume the right to download, package, republish, or monetize third-party
> audiovisual content.

AICE can record YouTube/media candidates as metadata:

```text
source URL
title
channel / publisher
published date if known
timestamp start / end
candidate quote / segment summary
intended use
rights status
review status
risk notes
```

But it must not download third-party audio/video in P0.1.1.

## 9. Investigative-Journalism Posture

AICE's content style may be **Frontline-inspired**, but it must never imitate
PBS/Frontline branding or imply affiliation.

Borrow the narrative grammar, not the costume.

Acceptable inspiration:

```text
- serious documentary structure
- cold open
- human stakes
- institutional contradiction
- archival/source texture
- expert context
- moral ambiguity
- calm but pointed narration
- closing question that lingers
```

Not acceptable:

```text
- PBS/Frontline branding imitation
- fake institutional authority
- synthetic "news anchor" cosplay
- pretending to have conducted interviews that did not occur
- overclaiming journalistic neutrality
- using clips without rights review
```

The first domain of AICE content is likely:

```text
U.S. education system
AI in schools
attention crisis
post-labor pedagogy
student agency
teacher burden
credentialing collapse
schooling as compliance vs agency formation
```

Example first prototype:

```text
Title: The Attention Crisis Schools Were Not Built to Solve
Length: 7-10 minutes
Style: investigative explainer, not fake documentary
Thesis: Schools trained compliance and answer-production; AI makes answers abundant and attention/judgment scarce.
```

## 10. AICE Long-Form Content Doctrine

AICE should not try to generate an entire long-form video directly. That is the
trap.

Medium-to-long-form output should be built around:

```text
script
argument
source trail
narration
visual system
data visuals
original commentary
selective generated sequences
receipt-backed review
```

Recommended media composition for an 8-20 minute Attention Intelligence video:

```text
70-85% human / sourced / editorial material:
- Kyle narration or presenter layer
- original script
- slides / diagrams
- source cards
- data visuals
- licensed/public-domain footage
- screen captures where permitted
- on-screen citations

15-30% generated sequences:
- visual metaphors
- chapter transitions
- abstract reenactments
- stylized scenes
- atmospheric B-roll
```

Do not produce "AI slop with citations." Produce source-grounded,
evidence-visible educational media.

Possible generator roles:

```text
Synthesia 2.0:
Presenter-led explainers, personal avatar/presenter segments, multilingual training-style modules. Avoid stock-avatar public-interest/political commentary unless policy and plan tier support it.

Kling / Omni:
Motion-heavy visual metaphors, multi-shot storyboards, controlled B-roll, cinematic sequence generation.

HappyHorse-1.0:
Backup cinematic image-to-video / text-to-video engine for short segments, especially if it proves strong in benchmarks and practical tests.

Runway / editing tools:
Finishing, repair, selective control, timeline/editorial utility.

Veo / premium models:
Hero shots only when cost and quality justify it.
```

The generator is never the evidence. The generator is a visual expression layer.

## 11. Required AICE Artifacts

The generated receipt packet should include:

```text
data/receipts/m8-gtm/aice-source-to-narrative-receipt/<receipt_id>/
  artifact_manifest.json
  m8_observation.json
  workflow_receipt.json
  workflow_receipt.md
  workflow_receipt.html
  artifacts/
    workflow.json
    topic_brief.json
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

Recommended fixture / workflow paths:

```text
examples/m8/aice-source-to-narrative-receipt/
examples/n8n/aice-source-to-narrative-receipt.workflow.json
src/orchestrator/m8_gtm/registry.py
src/orchestrator/m8_gtm/aice.py
tests/test_m8_aice_receipt_harness.py
```

## 12. Core Data Contract Sketches

### workflow.json

```json
{
  "workflow_slug": "aice-source-to-narrative-receipt",
  "workflow_name": "AICE Source-to-Narrative Workflow Receipt",
  "trust_domain": "ai_assisted_investigative_content",
  "evidence_mode": "live_n8n_plus_fixture_backed_demo",
  "workflow_boundary": "Profusion documents an AI-assisted investigative content workflow from episode thesis through source cards, quote candidates, claim mapping, Attention Intelligence mapping, risk/ambiguity review, human editorial decision, narrative brief, visual plan, and receipt generation. It does not certify factual truth, copyright clearance, fair use, journalistic neutrality, PBS/Frontline affiliation, platform compliance, legal compliance, or permission to reuse third-party video/audio.",
  "default_publication_state": "not_publishable_without_human_review"
}
```

### topic_brief.json

```json
{
  "topic_brief_id": "topic_001",
  "episode_title": "The Attention Crisis Schools Were Not Built to Solve",
  "working_thesis": "Schools optimized for compliance and answer-production, but AI makes answers cheap and raises the value of attention, judgment, verification, and agency.",
  "target_audience": "educators, parents, AI-curious founders, education reform observers",
  "attention_dimensions": [
    "attentional_sovereignty",
    "interpretive_discernment",
    "delegation_judgment"
  ],
  "publication_state": "draft_research_only"
}
```

### source_card.json

```json
{
  "source_card_id": "src_001",
  "source_type": "official_report | expert_talk | mainstream_media | youtube_video_reference | academic_source | book_excerpt | public_dataset",
  "title": "<source title>",
  "creator_or_publisher": "<publisher>",
  "url": "<source url>",
  "published_at": "<date-if-known>",
  "retrieved_at": "2026-05-19T00:00:00Z",
  "relevance_summary": "<why this source matters>",
  "claim_supports": ["claim_001"],
  "attention_dimension": "interpretive_discernment",
  "bias_or_incentive_notes": "<known incentive, editorial frame, or uncertainty>",
  "storage_mode": "metadata_only | excerpt_only | full_text_allowed | local_private_reference",
  "rights_status": "owned | licensed | public_domain | creative_commons | cite_only | fair_use_candidate | permission_required | do_not_use",
  "review_required": true
}
```

### quote_candidates.json

```json
{
  "quote_candidate_id": "quote_001",
  "source_card_id": "src_001",
  "quote_or_segment_summary": "<summary or short quote candidate>",
  "timestamp_start": "00:03:14",
  "timestamp_end": "00:03:42",
  "context_required": true,
  "candidate_use": "text_quote | paraphrase | cite_only | clip_candidate | broll_reference",
  "rights_status": "rights_review_required",
  "review_status": "human_editorial_review_required"
}
```

### claim_map.json

```json
{
  "claim_id": "claim_001",
  "claim_text": "AI makes answer-production cheaper while increasing the value of judgment, attention, and verification.",
  "claim_type": "thesis_support | factual_context | quote_support | counterargument | narrative_bridge",
  "source_card_ids": ["src_001", "src_002"],
  "evidence_strength": "strong | moderate | weak | unsupported",
  "ai_generated": true,
  "requires_human_review": true,
  "review_status": "approved_for_script_draft",
  "attention_dimension": "delegation_judgment",
  "risk_flags": ["needs_context_check", "possible_overgeneralization"]
}
```

### ambiguity_register.json

```json
{
  "ambiguity_id": "amb_001",
  "ambiguity_type": "copyright | fair_use | quote_context | factual_support | editorial_bias | synthetic_media_disclosure | platform_policy | ethical_framing",
  "artifact_id": "quote_001",
  "description": "Candidate clip may support commentary, but reuse rights are unresolved.",
  "current_status": "unresolved",
  "publication_impact": "cannot_package_clip_without_further_review",
  "safe_alternatives": [
    "cite source as reference",
    "paraphrase claim",
    "use generated abstract B-roll instead of third-party clip",
    "seek permission",
    "replace with public-domain or licensed footage"
  ],
  "human_reviewer": "Kyle",
  "review_decision": "hold_for_rights_review"
}
```

Ambiguity is not a loophole. Ambiguity is an inspectable artifact.

## 13. Required Receipt Sections

AICE receipt Markdown and HTML should include:

```text
Workflow Boundary
Topic / Episode Thesis
What Happened
Where AI Acted
Where n8n Acted
Where Human Editorial Review Entered
Source Cards Captured
Claims and Quote Candidates
Rights / Use / Ambiguity Classification
Attention Intelligence Mapping
Narrative Decisions
Generated / Synthetic Media Plan
Supported Claims
Claims Not Supported
Limitations
Next Recommended Review
```

## 14. Minimum Supported Claims

The receipt may make concrete, bounded positive claims such as:

```text
1. n8n workflow executed.
2. At least three n8n nodes participated in the run.
3. A topic/thesis artifact was captured.
4. At least one source card was captured.
5. At least one claim candidate was mapped to a source card.
6. At least one quote/segment candidate was captured as metadata/reference only.
7. At least one Attention Intelligence dimension was mapped.
8. At least one rights/risk/ambiguity item was recorded.
9. A human editorial review artifact exists, even if fixture/manual approval was used for P0.1.1.
10. A receipt packet was generated with artifact hashes.
11. The receipt includes supported claims, unsupported claims, and limitations.
```

Supported claims should be boring, concrete, and defensible. Boring is good.
Boring survives review.

## 15. Required Unsupported Claims / No-Claims Policy

AICE receipts must explicitly state what they do **not** prove.

Minimum no-claims language:

```text
1. This receipt does not certify factual truth.
2. This receipt does not certify copyright clearance.
3. This receipt does not certify fair use.
4. This receipt does not prove that third-party video/audio may be downloaded, edited, republished, or monetized.
5. This receipt does not prove platform-policy compliance.
6. This receipt does not certify journalistic neutrality.
7. This receipt does not imply PBS/Frontline affiliation or endorsement.
8. This receipt does not mean the final content is safe to publish.
9. This receipt does not replace human editorial or legal review.
10. This receipt only shows what was captured, classified, reviewed, limited, and generated inside the recorded workflow boundary.
```

Avoid phrases like:

```text
legally cleared
fair-use approved
copyright safe
journalistically verified
Frontline-style certified
PBS-like
safe to publish
platform compliant
truth-certified
no-risk clip
```

Unsupported claims are not weakness. They are the trust product.

## 16. Decision Gates

AICE must use deterministic gates wherever possible.

```text
Gate 1 - Source Support Gate
Every final script claim must map to at least one source_card_id.
If no source exists, hold or reject the claim.

Gate 2 - Evidence Strength Gate
Claims marked weak or unsupported cannot enter the narrative brief without human override.

Gate 3 - Quote Context Gate
Quote candidates require surrounding context notes before use.
If context is missing, route to quote_context_review_required.

Gate 4 - Rights / Use Gate
Third-party audio/video cannot be packaged into final assets unless rights_status is licensed, owned, public_domain, creative_commons_with_conditions_met, permission_obtained, or human-approved fair_use_candidate. For P0.1.1, default YouTube/media candidates to review_required.

Gate 5 - Attention Intelligence Gate
Each narrative claim should map to at least one Attention Intelligence dimension.

Gate 6 - Human Editorial Gate
No narrative brief can be marked approved_for_script_draft until a human review artifact exists.
```

Valid workflow outcomes:

```text
approved_for_script_draft
manual_editorial_review_required
rights_review_required
source_context_review_required
unsupported_claim_rejected
approved_for_generated_broll_only
hold_for_permission_or_replacement
```

## 17. n8n Workflow Acceptance

AICE P0.1.1 is accepted only if:

```text
- n8n workflow JSON exists.
- Workflow has at least 3 nodes.
- Workflow can be imported or documented for import.
- Workflow execution produces or triggers a generated AICE receipt packet.
- n8n_run_summary.json records node count, run timestamp, input topic, generated artifacts, output receipt path, and limitations.
```

Recommended minimum commands:

```bash
uv run profusion m8 demo support-triage-human-review --output-dir /tmp/profusion-support-baseline-verify
uv run profusion m8 demo aice-source-to-narrative-receipt --output-dir /tmp/profusion-aice-p0-1
uv run pytest tests/test_m8_gtm_receipt_harness.py -q
uv run pytest tests/test_m8_aice_receipt_harness.py -q
uv run pytest -q
uv run profusion smoke --offline
git diff --check
```

## 18. Implementation Constraints

AICE P0.1.1 must preserve these constraints:

```text
- Preserve existing support-triage P0 behavior.
- Do not break current baseline.
- Do not commit secrets.
- Do not download third-party YouTube/media audio/video.
- Do not make live publishing part of this sprint.
- Do not turn this into a giant platform refactor.
- Do not block on perfect YouTube/API integration.
- Do not stop at design docs.
- Use the smallest reliable path that generates the live receipt.
- Failed runs must not leave completed packets.
- HTML must escape fixture text.
- Supported claims, unsupported claims, limitations, and ambiguity register must be non-empty.
```

The system should prefer a small registry-first implementation rather than
piling AICE logic into hard-coded support-triage paths.

## 19. Relationship To n8n

n8n is the orchestration layer for the live sprint. It is not the product
itself.

n8n should coordinate:

```text
trigger / intake
source metadata generation or lookup
claim and quote candidate creation
rights / ambiguity classification
receipt command invocation
summary return
```

n8n may use fallback fixture data if live credentials are missing, but the
workflow must still run. The limitation must be recorded clearly.

Preferred n8n output artifact:

```json
{
  "workflow_name": "AICE Source-to-Narrative Workflow Receipt",
  "workflow_slug": "aice-source-to-narrative-receipt",
  "node_count": 6,
  "executed_at": "2026-05-19T00:00:00Z",
  "input_topic": "The Attention Crisis Schools Were Not Built to Solve",
  "receipt_packet_path": "/tmp/profusion-aice-p0-1/...",
  "limitations": [
    "No third-party audio/video was downloaded.",
    "Source metadata fallback was used because live credentials were unavailable.",
    "Receipt does not certify final publication safety."
  ]
}
```

## 20. Relationship To Video Generation Tools

Video generation tools are downstream of the receipt workflow.

AICE should not jump directly from topic to synthetic video. First generate the
research and receipt path. Then generate visual assets.

The correct order:

```text
1. Topic / thesis
2. Source / claim / quote candidate trail
3. Risk / rights / ambiguity review
4. Human editorial decision
5. Narrative brief
6. Visual plan
7. Generated B-roll / presenter / edit assets
8. Final human review
9. Publication decision
```

The tool stack may include Synthesia, Kling/Omni, HappyHorse, Runway, Veo, or
other models. But AICE should treat them as visual-generation engines, not
truth engines.

Generated video segments should be labeled by purpose:

```text
visual_metaphor
abstract_broll
chapter_transition
stylized_scene
presenter_segment
data_visualization_support
licensed_or_public_domain_clip_reference
```

AICE should avoid fake documentary footage that could mislead viewers into
thinking generated scenes are real events.

## 21. Future AICE Tasks: How Future Chats Should Interpret Them

When Kyle says "AICE," future chats should assume:

```text
AICE = Attention Intelligence Content Engine.
AICE is the source-to-narrative and receipt-generation layer for Profusion's AI-assisted educational media strategy.
AICE tasks should preserve evidence, source context, claim support, risk classification, ambiguity, human review, and no-claims boundaries.
AICE is allowed to use automation aggressively, but not to erase human accountability.
AICE should be OODA-driven and execution-oriented.
AICE should favor live proof packets over endless planning.
```

When Kyle says "new AICE task," future chats should ask internally:

```text
1. What is the topic/thesis?
2. What artifact or receipt should exist at the end?
3. What sources, claims, or evidence are involved?
4. What Attention Intelligence dimensions does this touch?
5. What AI actions are being delegated?
6. What must remain human-reviewed?
7. What ambiguity must be preserved?
8. What supported claims and unsupported claims must the receipt include?
9. Is this a live workflow, fixture-backed demo, or strategy/design artifact?
10. What is the smallest shippable proof?
```

Future assistants should not interpret AICE as generic content creation. AICE
is governed content creation with receipts.

## 22. Suggested Persistent Prompt For Future Agents

Use this when handing AICE to Codex, Claude, OpenClaw, or another
implementation agent:

```text
You are working on AICE, the Attention Intelligence Content Engine inside Profusion.AI Restart.

AICE is a source-to-narrative and workflow receipt engine for AI-assisted investigative educational media. It turns an episode thesis into source cards, claim maps, quote candidates, Attention Intelligence mappings, rights/risk classifications, human editorial review artifacts, narrative briefs, visual plans, and generated workflow receipts.

Do not treat AICE as a generic video generator. Do not treat it as a YouTube clip-ripper. Do not imply legal clearance, fair-use certification, journalistic neutrality, PBS/Frontline affiliation, final publication safety, or platform-policy compliance.

Current sprint: P0.1.1 AICE Source-to-Narrative Workflow Receipt.
Goal: execute a live minimum n8n-to-Profusion workflow with at least 3 nodes and produce a generated receipt packet.

Use OODA-driven development: Observe, Orient, Decide, Act. Use subagents where possible. Preserve existing support-triage baseline. Do not stop at design docs. Build the smallest live proof that produces a receipt.

Required slug: aice-source-to-narrative-receipt.
Required trust domain: ai_assisted_investigative_content.
Required receipt title: AICE Source-to-Narrative Workflow Receipt.

Minimum proof: n8n executed, at least three nodes participated, topic/thesis captured, source card captured, claim mapped to source, quote/segment candidate captured as metadata/reference only, Attention Intelligence dimension mapped, rights/risk/ambiguity item recorded, human editorial review artifact exists, receipt packet generated with artifact hashes, supported and unsupported claims included.
```

## 23. Current Strategic One-Liners

Use these to keep messaging coherent:

```text
AICE does not just generate content. AICE preserves the receipts behind the argument.

AICE is the evidence-to-narrative engine for Attention Intelligence media.

Profusion makes AI-assisted workflows reviewable enough to trust.

AI made output cheap. Review became the bottleneck. Profusion makes the review boundary visible.

Ambiguity is not a loophole. Ambiguity is an artifact.

The generator is never the evidence. The generator is a visual expression layer.

Borrow Frontline's seriousness, not PBS's costume.

The first proof is not a documentary. The first proof is a receipt.
```

## 24. Source Anchors For This Understanding

This renewed understanding is synthesized from the Profusion.AI Restart project
conversation and these project materials:

```text
attention_intelligence_north_star_blueprint.pdf
profusion-content-pipeline-prd.md
profusion-master-handoff-prompts.md
Cardmint P0.1 AI-Assisted Inventory Decision Receipt Handoff
Profusion AI Business Plan / workflow receipt strategy notes
Productivity-Reliability Paradox in AI notes
Event Background Investigation / SVB AI-native startup operating system prep
Local-first Language Assistant synthesis notes
```

Key inherited principles:

```text
- Attention Intelligence is human agency under machine abundance.
- Profusion is the business-shaped expression of that doctrine.
- The process matters as much as the output.
- Human review gates are reputation insurance.
- Workflow receipts should include limitations and unsupported claims.
- Do not overclaim what evidence proves.
- Ship small artifacts that someone can read, use, test, criticize, or share.
- Reality contact beats founder mythology.
```

## 25. Final North-Star Reminder

AICE should make this sentence true:

> A viewer, reviewer, or future collaborator can inspect not only the final
> content, but the attention, evidence, delegation, review, ambiguity, and human
> judgment that produced it.

That is the product.
