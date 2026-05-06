# Governed AI Workflow Receipt Pilot

Date: 2026-05-06

## Offer

The Governed AI Workflow Receipt Pilot turns one AI-assisted workflow into a reviewer-readable evidence packet. The pilot defines the workflow boundary, captures the right artifacts, applies human review gates, and produces a plain-English receipt showing what happened, what evidence exists, who reviewed it, and what the receipt does not prove.

The first implementation wedge is AI-assisted content and media governance. The current shipped proof is a `content_video_receipt` in the `media_trust` domain.

## Best First Workflow

The strongest first workflow is an AI-assisted content approval path:

```text
topic or brief
-> script or generated content
-> rendered or finalized asset
-> QA checkpoint
-> human approval
-> schedule or publish readiness
-> receipt packet
```

This path matches the current Profusion implementation more closely than coding-agent reliability, contractor readiness, or measurement-loop analytics.

## Pilot Deliverables

- Workflow map.
- Evidence boundary.
- Artifact checklist.
- Review gate design.
- Limitation language.
- Sample or live receipt packet, depending on available artifacts.
- Buyer-readable pilot closeout memo.

## What The Receipt Can Support

- Evidence was available for the declared workflow.
- AI touchpoints were identified.
- Review gates were applied or marked missing.
- Human review was recorded where applicable.
- Limitations and unsupported claims were documented.
- The workflow is easier to inspect after the fact.

## What The Receipt Does Not Prove

- Certified compliance.
- Legal sufficiency.
- Verified truth of every output claim.
- Universal synthetic-media detection.
- Identity or liveness verification.
- Code correctness.
- Production coding-agent instrumentation.
- Autonomous governance.
- Hiring recommendation, ranking, selection, or rejection.

## Pilot Shape

The pilot should remain founder-led and narrow:

- one workflow
- one accountable owner
- one evidence boundary
- one receipt type
- one packet
- one decision about whether to expand

Do not turn the first pilot into a platform migration, customer portal, login system, billing project, AI observability product, or M8 measurement-loop build.

## Success Criteria

The pilot is successful if the buyer can answer:

- What happened in the workflow?
- What artifacts support that account?
- Which AI touchpoints mattered?
- Who reviewed or approved the output?
- What risks remain outside the receipt boundary?
- Would a receipt reduce review burden, defensibility risk, or buyer anxiety enough to justify paid expansion?
