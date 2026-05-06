# Profusion Homepage Reliability Gap Update

Date: 2026-05-05

Production URL:

- `https://profusion.ai`

Netlify production deploy:

- Site: `profusionai`
- Site ID: `3a16f00c-b40e-4a48-a9d5-a6ac92f2b39e`
- Deploy ID: `69fa4353664ea81f953623f4`
- Deploy URL: `https://69fa4353664ea81f953623f4--profusionai.netlify.app`
- Deploy logs: `https://app.netlify.com/projects/profusionai/deploys/69fa4353664ea81f953623f4`

## Latest Summarized Progress

Profusion's public front page has been updated and deployed to production with
the new productivity-reliability wedge. The site now presents Profusion as a
practical reliability and evidence layer for AI-assisted and agentic work,
slightly prioritizing coding-agent and engineering workflows while preserving
AI content, synthetic media, recruiting, and client-facing automation as the
near-term first-client surface.

The live page now communicates that AI has moved the bottleneck from production
to verification, and that Profusion helps teams make AI-produced work
reviewable enough to approve through specification boundaries, artifact capture,
test/review evidence, human approval gates, limitations, and workflow receipts.

Production is live at `https://profusion.ai`. Local lint/build passed before
deploy, Netlify reports the production deploy as ready, and live browser/HTTP
checks confirmed the new copy and assets are being served.

## Positioning Change

The homepage now leads with the productivity-reliability wedge:

> Close the reliability gap in AI-assisted work.

The page slightly prioritizes agentic engineering and coding-agent reliability,
while keeping AI content, synthetic media, recruiting, and client-facing
automation visible as the likely first-client wedge.

Current hierarchy:

```text
Category: AI workflow reliability / evidence layer
Primary signal: agentic engineering and coding-agent reliability
First-client wedge: AI content, media, recruiting, and client-facing automation
Offer: AI Workflow Reliability Pilot
Diagnostic language: productivity-reliability gap, review burden, verification tax
Artifact: productivity-reliability workflow receipt
Guardrail: process evidence, not compliance or code-quality certification
```

## Main Copy Changes

- Hero changed from workflow-trust language to reliability-gap language.
- Receipt card changed from `WORKFLOW RECEIPT` to `RELIABILITY RECEIPT`.
- Receipt fields now foreground spec boundary, generated-work artifacts, tests,
  review, verification tax, and supported claims.
- The problem section now leads with AI moving the bottleneck from production to
  verification.
- The first use case is now `AI CODING AGENT RELIABILITY`.
- Services now lead with `AI Workflow Reliability Pilot` and
  `Productivity-Reliability Diagnostic`.
- Ideal-client list now starts with AI-forward engineering and product teams
  adopting coding agents in mature codebases.
- Contact form now asks for workflow reliability context.

## Research Posture

The update is informed by, but does not overclaim, the Productivity-Reliability
Paradox framing. The page does not claim Profusion proves code quality,
certifies compliance, validates synthetic media, or replaces specification
tools. It positions Profusion as the layer that records specs, artifacts, tests,
reviews, approvals, limitations, and receipts around AI-assisted work.

Relevant external anchors used for copy discipline:

- Productivity-Reliability Paradox paper: `https://arxiv.org/html/2605.01160v1`
- Faros AI productivity telemetry: `https://www.faros.ai/blog/ai-software-engineering`
- DORA generative AI report: `https://dora.dev/ai/gen-ai-report/`
- MCP docs: `https://modelcontextprotocol.io/docs/getting-started/intro`
- GitHub Spec Kit: `https://github.com/github/spec-kit`

## Verification

Local:

```bash
corepack pnpm lint
corepack pnpm build
```

Build output:

```text
dashboard/dist/index.html
dashboard/dist/assets/index-B-FFNL2g.css
dashboard/dist/assets/index-DnAjgt9x.js
dashboard/dist/__forms.html
```

Visual checks:

- Local desktop screenshot: clean first viewport at `1440x1200`.
- Local mobile screenshot: clean first viewport at `390x1200`.
- Live desktop screenshot: clean first viewport at `1440x1200`.
- Live mobile screenshot: clean first viewport at `390x1200`.

Live checks:

- `curl -I https://profusion.ai/` returned HTTP 200.
- `curl -I https://69fa4353664ea81f953623f4--profusionai.netlify.app/`
  returned HTTP 200.
- Live HTML serves:
  - `/assets/index-DnAjgt9x.js`
  - `/assets/index-B-FFNL2g.css`
- Headless Chrome DOM check against `https://profusion.ai/` confirmed:
  - `Close the reliability gap in AI-assisted work.`
  - `AI WORKFLOW RELIABILITY PRACTICE`
  - `RELIABILITY RECEIPT`
  - `AI CODING AGENT RELIABILITY`
  - `AI Workflow Reliability Pilot`
  - `Productivity-Reliability Diagnostic`
  - `WORKFLOW RELIABILITY SESSION REQUEST`

## Deployment Notes

The Netlify MCP deploy path successfully created deploy
`69fa433878d12e2187d3eca4`, but the remote build failed while extracting the
uploaded source zip because `dashboard/node_modules` was included:

```text
Failed during stage 'fetching build zip': extracting zip file: creating file:
open /opt/build/repo/dashboard/node_modules/.pnpm/@babel+code-frame@7.29.0/node_modules/@babel/helper-validator-identifier: is a directory
```

The successful production deploy used the already verified local build output:

```bash
npx netlify deploy --prod --no-build --dir=dashboard/dist --site=3a16f00c-b40e-4a48-a9d5-a6ac92f2b39e --message "Profusion reliability gap homepage update 2026-05-05" --json
```

This is consistent with the prior reliable deployment lane for this site:
build locally with `corepack pnpm build`, then upload `dashboard/dist` with
`--no-build`.
