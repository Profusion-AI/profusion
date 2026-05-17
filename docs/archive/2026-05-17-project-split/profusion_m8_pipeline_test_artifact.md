---
artifact_id: m8-test-attention-intelligence-001
artifact_type: content_pipeline_test_packet
created: 2026-05-03
pipeline_target: Profusion M7.5 -> M8 readiness
recommended_initial_status: idea
recommended_receipt_status: draft
trust_domain: media_trust
receipt_type: content_video_receipt
pillar: education_reform
secondary_pillars:
  - post_labor_pedagogy
  - attention_intelligence
  - ai_literacy
priority: P4
audience:
  - educators
  - parents
  - education-policy observers
  - AI-curious operators
format: short_vertical_video
runtime_target_seconds: 60
source_refs:
  - new-ed.md
  - new-ed2.md
  - Turing and Post-Labor Society.txt
  - M7_M7_5_TO_M8_HANDOFF_2026-05-03.md
---

# Profusion M8 Pipeline Test Artifact: Attention Intelligence vs. Compliance Schooling

## 1. Purpose of this artifact

This packet is designed to test whether the Profusion pipeline can ingest a source-grounded idea, preserve its thesis, generate a short-form script, mark uncertainty honestly, produce a reviewer-facing evidence packet, and transition a receipt through the proposed lifecycle:

```text
draft -> reviewed -> approved_for_packet -> delivered
```

The artifact is deliberately small. It should exercise the orchestration, cockpit, receipt, and future measurement surfaces without pretending to be a full production campaign.

## 2. Content item metadata

```yaml
content_item_id: m8-test-attention-intelligence-001
title: "Why Schools Still Optimize for Compliance"
working_slug: why-schools-optimize-for-compliance
state: idea
last_event: artifact_created
approval_state: not_required_yet
receipt_state: draft_pending
next_safe_command: uv run profusion ingest --file sources/test_packets/profusion_m8_pipeline_test_artifact.md
```

## 3. Core thesis

American schooling still rewards compliance, pacing, and institutional legibility because the legacy model was built around preparing students to fit labor-market and bureaucratic structures. In an AI-disrupted, post-labor direction of travel, the more important educational outcome is not obedience to the workflow. It is attention intelligence: the ability to direct focus, interpret ambiguity, reason under uncertainty, and construct purpose when traditional career identity becomes unstable.

## 4. Editorial angle

This should not be framed as “schools are bad.” That is cheap heat and the internet has enough of that compost pile already.

Frame it as a design mismatch:

- The old school model optimized for compliance because compliance had market value.
- The AI era makes procedural compliance less uniquely human.
- The scarce human capacities are agency, discernment, purpose, relational depth, creativity, and resilient reasoning.
- Education reform should build those capacities without abandoning academic rigor.

## 5. Target audience

Primary: Educators and parents who feel something is structurally wrong with school but do not want cynical anti-school rage bait.

Secondary: AI-aware professionals, civic reformers, and policy-curious viewers who are beginning to see that “career readiness” may be too narrow as the organizing purpose of education.

## 6. Claim-confidence map

| Claim | Confidence | Notes for reviewer |
|---|---:|---|
| Schools still often reward compliance, pacing, and institutional legibility. | Medium | Persuasive framing; should be treated as analysis rather than a universal empirical claim. |
| AI and automation weaken the assumption that employability alone should define schooling. | Medium | Strong thesis, but future-facing; avoid deterministic certainty. |
| Attention management, discernment, purpose, creativity, and resilient reasoning are important human capacities. | High | Supported by the project’s education framework and broader developmental logic. |
| Texas or any state can adopt this immediately without new legislation. | Needs verification | Do not include in this short unless explicitly sourced and reviewed. |
| Human labor will collapse by a specific year. | Needs verification | Avoid date-specific claims unless backed by current external research. |

## 7. Risk flags

- Do not claim AI has already made schooling obsolete.
- Do not claim all teachers or districts intentionally suppress agency.
- Do not use “SEL” framing in Texas-facing variants unless deliberately discussing terminology.
- Do not imply the framework replaces literacy, numeracy, science, history, or academic content.
- Do not present a receipt as certification, truth verification, liveness proof, or customer-ready compliance evidence.

## 8. 60-second script draft

**Hook:**
Schools are not broken because teachers do not care. They are misaligned because the system still rewards the wrong human behavior.

**Body:**
For a long time, compliance had economic value. Show up on time. Follow instructions. Move through the worksheet. Get the credential. Enter the workforce.

That model made sense when school was mainly a pipeline into stable work.

But AI changes the question. If machines can increasingly perform routine cognitive tasks, then the most important human capacity is not just completing assigned work. It is knowing what deserves attention in the first place.

That is what I mean by Attention Intelligence.

It is the ability to direct focus, interpret ambiguity, reason under uncertainty, and build purpose when the old career map stops being reliable.

The future of education is not anti-rigor. It is deeper rigor.

Less compliance theater. More agency.
Less passive pacing. More judgment.
Less “what job will you get?” More “what kind of person can you become?”

**CTA:**
If education is still preparing students for yesterday’s economy, we need to ask a better question: what human capacities remain valuable no matter what the labor market does next?

## 9. Alternate hooks

1. The biggest problem in school may not be what students are learning. It may be what the system is training them to become.
2. AI is forcing a brutal question onto education: what is school for when “career readiness” is no longer enough?
3. Compliance made sense in an industrial economy. In an AI economy, it may be the wrong operating system.

## 10. Caption options

**Caption A:**
The future of education is not less rigor. It is a different kind of rigor: attention, discernment, agency, and purpose.

**Caption B:**
Career readiness still matters. But if we stop there, we are building students for a world that may not exist by the time they graduate.

**Caption C:**
Attention Intelligence may become one of the most important educational capacities of the AI era.

## 11. Title options

1. Why Schools Still Optimize for Compliance
2. AI Is Changing What School Is For
3. Attention Intelligence: The Skill Schools Are Missing
4. Career Readiness Is No Longer Enough

## 12. Visual direction for render

- Tone: sober, precise, founder/educator voice.
- Avoid: screaming thumbnails, dystopian robot classrooms, generic AI-glow slop.
- Visual motifs: classroom hallway, scantron/test forms, student notebook, clock/time pressure, attention split-screen, human eye/focus imagery, civic/community scenes.
- Suggested on-screen text beats:
  - “Compliance had economic value.”
  - “AI changes the question.”
  - “Attention Intelligence”
  - “Less compliance theater. More agency.”

## 13. QA checklist

```yaml
editorial_qa:
  unsupported_claims: pass_if_no_specific_dates_or_sweeping_empirical_claims
  tone: serious_accessible_not_ragebait
  brand_fit: pass
  source_alignment: pass
  clear_thesis: pass
  avoids_overclaiming: pass
technical_qa:
  target_duration_seconds: 60
  subtitle_readability_required: true
  audio_sync_required: true
  vertical_format_required: true
  mp4_required: true
receipt_qa:
  limitations_included: true
  reviewer_notes_required_before_approved_for_packet: true
  no_identity_or_liveness_claims: true
  no_candidate_evaluation_claims: true
```

## 14. Receipt lifecycle test expectations

This artifact should initially produce a draft `content_video_receipt`. Before it is shown outside the internal team, the receipt should be explicitly advanced by command or equivalent backend operation.

Expected lifecycle commands, subject to implementation naming:

```bash
uv run profusion receipt draft --item-id m8-test-attention-intelligence-001 --json
uv run profusion receipt transition --receipt-id <receipt_id> --to reviewed --reviewer Kyle --notes "Reviewed as pipeline test packet; no external truth or identity claims."
uv run profusion receipt transition --receipt-id <receipt_id> --to approved_for_packet --reviewer Kyle --notes "Approved for reviewer packet, not production certification."
uv run profusion receipt transition --receipt-id <receipt_id> --to delivered --channel internal_demo --recipient-alias codex-review
```

If the implementation prefers explicit verbs rather than a generic transition command, acceptable equivalents are:

```bash
uv run profusion receipt review --receipt-id <receipt_id> --reviewer Kyle
uv run profusion receipt approve-packet --receipt-id <receipt_id> --reviewer Kyle
uv run profusion receipt deliver --receipt-id <receipt_id> --channel internal_demo
```

## 15. Expected receipt limitations text

This receipt documents the declared Profusion workflow for a short-form content item. It records source references, generated artifacts, QA notes, review state, approval state, and delivery state where available. It does not certify truth, identity, authorship, liveness, platform publication, or absence of external manipulation outside the captured workflow.

## 16. M8 measurement stub

2026-05-08 implementation note: this stub now maps to
`uv run profusion measure record`, file-first observations under
`data/measurements/<item_id>/`, and the `published -> measured` transition.

After publication or controlled test delivery, M8 should support manual measurement imports such as:

```yaml
measurement_observation:
  content_item_id: m8-test-attention-intelligence-001
  platform: internal_demo
  observation_type: reviewer_feedback
  views: null
  completion_rate: null
  comments: null
  qualitative_signal: "Reviewer understood Attention Intelligence thesis and receipt boundary."
  recorded_by: Kyle
  recorded_at: 2026-05-03T00:00:00Z
```

This stub intentionally avoids optimization-loop behavior. It is a measurement seed, not an algorithmic growth lever.
