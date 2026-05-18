# M8-GTM HyperFrames Demo Decision

Date: 2026-05-18

## Decision

Use HyperFrames as the preferred demo-video production path for the M8-GTM
Overlay, but do not make video generation a release blocker.

The first shippable demo remains:

```text
CLI + durable artifacts + generated receipt
```

HyperFrames becomes the agent-first way to turn that receipt loop into a
repeatable demo video after the evidence loop works.

## Executive Verdict

Do not depend on Atlassian Loom for the first M8-GTM demo.

HyperFrames is a better fit for this sprint because it is HTML-native,
agent-friendly, locally renderable, deterministic, and does not require a new
hosted recording workflow before Profusion has a clean receipt loop.

The working rule:

```text
Receipt-real first. HyperFrames-rendered second. Cockpit-visible later.
```

## Why This Fits Profusion

M8-GTM Overlay is proving the workflow evidence loop, not the UI and not the
video tool.

The product proof is:

```text
n8n workflow fixture -> Profusion evidence capture -> M8 outcome observation -> workflow receipt
```

The demo proof is:

```text
receipt artifacts -> HTML receipt -> HyperFrames demo composition -> MP4
```

This keeps the core product artifact separate from the marketing/demo artifact.
The receipt must stand on its own. The video explains it.

## Source Check

HyperFrames describes itself as "Write HTML. Render video. Built for agents."
Its docs and README support the relevant assumptions:

- HTML is the authoring surface for video compositions.
- The CLI supports local preview and MP4 rendering.
- Rendering is deterministic and frame-by-frame.
- The tool is built for AI-agent workflows.
- Requirements are Node.js 22+ and FFmpeg.
- The GitHub README states Apache 2.0 licensing.

Local environment check on 2026-05-18:

```text
node --version -> v22.22.0
ffmpeg -version -> 8.0.1
npx hyperframes --version -> 0.6.22
```

Sources:

- `https://github.com/heygen-com/hyperframes`
- `https://hyperframes.heygen.com/introduction`
- `https://hyperframes.heygen.com/quickstart`
- `https://hyperframes.mintlify.app/guides/rendering`

Rendering note:
HyperFrames local mode is acceptable for fast iteration. For final shareable
renders, prefer Docker mode where available because HyperFrames docs
distinguish local-mode convenience from Docker-mode reproducibility. If Docker
is unavailable, record the limitation in the video manifest. Do not claim
cross-machine deterministic rendering unless Docker mode was used.

## Scope Decision

P0 remains the M8 receipt harness:

- support-triage-human-review fixture
- durable local artifacts
- `m8_observation.json`
- `workflow_receipt.json`
- `workflow_receipt.md`
- preferably `workflow_receipt.html`
- one reproducible CLI command
- runbook
- clear limitations
- supported and unsupported claims

P1 becomes HyperFrames demo production:

- create a short HTML-authored demo composition from the generated receipt
- show the routine ticket and sensitive billing complaint contrast
- show where AI acted and where human review entered
- show supported and unsupported claims
- render a local MP4 for sharing or review
- write `hyperframes_video_manifest.json` recording the source receipt, source
  observation, source artifacts, render command, render mode, tool versions,
  output path, and limitations

P2 remains optional cockpit visibility:

- read-only receipt preview only
- no mutation logic
- no approval buttons
- no scheduling or publishing controls
- no public website changes

## Demo Narrative

The demo is not:

```text
AI answers support tickets.
```

The demo is:

```text
Profusion shows when AI work was safe to approve.
```

The HyperFrames video should use the Customer Trust Triage Receipt story:

1. Routine invoice request completes through standard handling.
2. Sensitive billing complaint triggers the review boundary.
3. AI drafts a response.
4. Human reviewer edits or approves the final response.
5. Profusion generates the receipt.
6. The receipt states what happened, what was reviewed, what is supported, and
   what is not proven.

## Non-Goals

Do not use this sprint to build:

- a generalized video marketing pipeline
- a HyperFrames integration inside Profusion's product surface
- a cockpit video viewer
- a public website demo page
- a hosted video workflow
- a replacement for the M8 receipt harness

## Failure Rules

If HyperFrames setup, composition authoring, linting, inspection, or rendering
threatens the 36-hour receipt target, stop video work and ship the receipt loop.

Claim drift rule:
If the HyperFrames composition introduces any claim not present in the receipt
artifacts, remove the claim or update the receipt first. The video may not
outrun the evidence.

Fallback:

```text
workflow_receipt.html + manual walkthrough notes
```

HyperFrames is the preferred demo accelerator. It is not the product.

## Acceptance Test

The M8-GTM first pass is accepted when one command produces durable receipt
artifacts that let a reviewer answer:

1. What workflow ran?
2. What inputs were used?
3. Where did AI act?
4. Where did human review occur?
5. What final action happened?
6. What artifacts were captured?
7. What claim does the receipt support?
8. What claim does the receipt not support?
9. What are the limitations?
10. What should be reviewed next?

The HyperFrames pass is accepted when a local MP4 can explain that receipt loop
without adding claims the receipt itself does not support.
