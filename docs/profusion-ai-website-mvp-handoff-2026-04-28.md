# Profusion AI Website MVP Handoff

Date: 2026-04-28

## Purpose

This document wraps the initial MVP web page development for the Profusion AI public homepage. The next expected step is a Netlify deployment pass after context cleanup.

Deployment wrap-up after that pass is captured in:

- `docs/profusion-ai-netlify-deployment-wrapup-2026-04-28.md`

Profusion is still primarily a semi-autonomous educational media pipeline, but this website MVP is a separate public-facing surface for `profusion.ai`. It presents Profusion AI as a consulting and R&D practice focused on human trust for synthetic media, high-risk video workflows, and disciplined trust infrastructure.

## Current Site

The homepage is implemented as a Vite React/TypeScript app in `dashboard/`.

Primary files:

- `dashboard/index.html`: site title, metadata, Google font links, Vite entrypoint.
- `dashboard/src/main.tsx`: renders the homepage app.
- `dashboard/src/App.tsx`: all homepage content, interactions, and component state.
- `dashboard/src/index.css`: visual system, layout, responsiveness, hover states, scroll transitions, and animations.
- `dashboard/public/profusion-aperture.png`: cropped aperture logo asset derived from the provided logo image.

The local dev URL during this handoff was:

```bash
http://127.0.0.1:5173/
```

## Design Direction

The implementation follows the downloaded Claude/ChatGPT design references rather than the earlier operator dashboard UI.

Reference files used during this pass:

- `/home/kyle/Downloads/Profusion AI Website.html`
- `/home/kyle/Downloads/ChatGPT Image Apr 28, 2026, 12_12_33 PM.png`
- `/home/kyle/Downloads/ChatGPT Image Apr 28, 2026, 12_55_55 PM.png`

Visual system:

- Evergreen hero background with subtle grid texture.
- Bone and parchment section bands.
- Signal gold accent color.
- Manrope, Inter, and IBM Plex Mono typography.
- Aperture logo with a scoped glow/falloff so it remains visible on the dark hero background.
- Receipt-card motif for trust/audit/provenance language.

Important design behaviors:

- Wordmark text has the staggered hover animation and should remain separate from logo glow work.
- Navigation hover state uses a subtle gold glow and lighter text.
- Major sections animate into view on scroll and reverse when leaving view.
- Problem headline includes a 2.5s looping vertical word reel.
- Trust Layer steps are clickable.
- Video Trust Lab tabs switch among Overview, Architecture, and Status.
- Contact form validates name/email locally and shows a receipt-style confirmation.

## Homepage Structure

The page currently renders these sections:

1. Hero
   - Eyebrow: `AI TRUST CONSULTING & R&D`.
   - Headline: `Human trust for the age of synthetic media.`
   - Main copy: Profusion AI helps organizations design and prototype trust systems that make high-risk digital interactions governable again.
   - Animated session receipt.
   - Primary CTA: `Discuss a High-Risk Workflow`.
   - Secondary CTA: `View the Video Trust Lab`.

2. Problem
   - Headline begins: `Deepfakes are now commonplace.`
   - Rotating first word loop: `Institutions`, `Enterprises`, `Companies`, `Interviewers`, `Schools`, `Governments`.
   - Static second line: `still need proof.`
   - Cards for presence, disclosure, and evidence gaps.

3. Trust Layer
   - `Declare`, `Enforce`, `Watermark`, `Record`, `Review`.
   - Clickable step flow with detail receipt.

4. Video Trust Lab
   - Copy currently says:
     - `Before video can be trusted, it needs governance.`
     - Profusion AI is developing a local-first R&D prototype for high-risk webcam sessions: pre-session attestation, enforced disclosure for altered media, visible watermarking, and durable trust receipts that record what was declared, enforced, and reviewed.
     - `Current status: technical lab prototype, not a commercial detection product.`
   - Tabs: Overview, Architecture, Status.

5. Consulting Services
   - AI Trust & Governance Strategy.
   - Synthetic Media & Video Trust Prototyping.
   - Agentic Workflow Evaluation.
   - AI Product & MVP Advisory.

6. Ideal Clients
   - High-stakes video workflow organizations.
   - Agentic workflow teams.
   - Trust-sensitive product companies.
   - Governance, risk, and compliance leaders.

7. Operating Principles
   - Declare what is synthetic.
   - Preserve what is human.
   - Record what matters.
   - Escalate what is risky.
   - Never overclaim detection.

8. Contact
   - Netlify Forms-backed request form.
   - Form name: `trust-session`.
   - Submissions notify `kyle@profusion.ai`.

## Claim Boundaries

Keep the website conservative. The current posture is intentionally bounded:

- Profusion AI is a consulting and R&D practice.
- The Video Trust Lab is a technical lab prototype.
- It is not a commercial detection product.
- Do not claim production assurance, compliance certification, identity verification, liveness detection, or signed proof.
- Use language around declaration, enforcement, watermarking, receipt generation, review, and governance.
- The page may discuss deepfakes and synthetic media as a problem space, but should not market Profusion as a deepfake detector.

This matters because the website is public-facing and should not outrun the actual VerityCam/Video Trust Lab maturity.

## Verification Performed

Run from `dashboard/`:

```bash
pnpm lint
pnpm build
```

Both passed at the end of the MVP web page pass.

Additional browser checks were performed with local Vite and headless Chrome:

- Hero renders on desktop.
- Logo asset is visible against the dark hero background.
- Scroll reveal classes toggle as sections enter and leave the viewport.
- Problem headline and rotating word reel render in the DOM.
- Mobile/narrow layout was checked and tightened during the pass.

## Netlify Starting Point

No deployment was performed in the initial MVP pass.

Deployment prep was completed afterward:

- Existing Netlify project: `profusionai`.
- Site ID: `3a16f00c-b40e-4a48-a9d5-a6ac92f2b39e`.
- Primary URL: `https://profusion.ai`.
- Production deploy completed from local assets on 2026-04-28:
  - Deploy ID: `69f101e98f7b1d20da2ccf4f`.
  - Build ID: `69f101e78f7b1d20da2ccf4d`.
  - Deploy URL: `https://69f101e98f7b1d20da2ccf4f--profusionai.netlify.app`.
- Repo-level `netlify.toml` now sets:
  - Base directory: `dashboard`.
  - Build command: `pnpm build`.
  - Publish directory: `dist`.
  - Node version: `20.19.6`.
  - SPA fallback to `/index.html`.
  - Basic security headers and immutable asset caching.
- Netlify Forms are enabled for the project.
- The contact form now submits to Netlify Forms using the form name `trust-session`.
- `dashboard/public/__forms.html` contains the static form skeleton Netlify needs to detect the React-rendered form.
- Netlify registered the `trust-session` form on deploy with fields `subject`, `bot-field`, `name`, `org`, `email`, and `context`.
- A live POST smoke test returned HTTP 200, appeared in Netlify submissions, and was then deleted.
- Kyle manually configured Netlify to email `kyle@profusion.ai` on new verified `trust-session` submissions.
- Kyle confirmed a live test request delivered the expected notification to the `kyle@profusion.ai` inbox.

Before deploy or production promotion:

```bash
cd /home/kyle/profusion/dashboard
pnpm lint
pnpm build
```

If the local asdf `pnpm` shim reports that no preset version is installed, use Corepack instead:

```bash
cd /home/kyle/profusion/dashboard
corepack pnpm lint
corepack pnpm build
```

From the repo root, this verifies the Netlify config path without requiring the local CLI to be linked:

```bash
NETLIFY_SITE_ID=3a16f00c-b40e-4a48-a9d5-a6ac92f2b39e npx netlify build --offline
```

In the same local shim-failure case, wrap `pnpm` through Corepack before running the Netlify offline build:

```bash
cd /home/kyle/profusion
pnpm() { corepack pnpm "$@"; }
export -f pnpm
NETLIFY_SITE_ID=3a16f00c-b40e-4a48-a9d5-a6ac92f2b39e npx netlify build --offline
```

Optional next-step cleanup after production launch:

- Review final copy once more in a real browser before broader public traffic.
- Decide whether to add analytics, privacy/legal pages, and footer links before broader public traffic.

## Open Items

- Netlify production deployment to `https://profusion.ai` is done.
- Contact form submits to Netlify Forms and notification routing to `kyle@profusion.ai` is configured and confirmed.
- No analytics, privacy page, or legal footer content exists yet.
- No production asset optimization beyond the cropped logo PNG has been performed.
- The website is independent of the orchestration backend for now; it does not consume Profusion API/read-model data.

## Resume Notes

Start the next session by checking:

```bash
cd /home/kyle/profusion
git status --short
cd dashboard
corepack pnpm lint
corepack pnpm build
corepack pnpm dev --host 127.0.0.1
```

Then inspect `http://127.0.0.1:5173/` in a real browser before deploying.

For the completed Netlify deployment record, see `docs/profusion-ai-netlify-deployment-wrapup-2026-04-28.md`.
