# Profusion AI Netlify Deployment Wrap-up

Date: 2026-04-28

## Outcome

The Profusion AI public website MVP is deployed successfully to Netlify and is live at:

- Production URL: `https://profusion.ai`
- Netlify project: `profusionai`
- Site ID: `3a16f00c-b40e-4a48-a9d5-a6ac92f2b39e`
- Netlify project admin: `https://app.netlify.com/projects/profusionai`

This deployment was pushed from the local `/home/kyle/profusion` workspace through Netlify's direct upload/API path. It did not depend on a linked GitHub repository or a Git-backed CI/CD trigger.

## Production Deploy

- Deploy ID: `69f101e98f7b1d20da2ccf4f`
- Build ID: `69f101e78f7b1d20da2ccf4d`
- Deploy URL: `https://69f101e98f7b1d20da2ccf4f--profusionai.netlify.app`
- Production alias: `https://profusion.ai`
- Deploy context: `production`
- Deploy source: direct upload/API
- Deploy state: `ready`
- Published at: `2026-04-28T18:53:04.428Z`
- Deploy completed at: `2026-04-28T18:53:13.076Z`

Netlify deploy summary reported:

- `index.html` deployed.
- `__forms.html` deployed.
- 3 static assets changed.
- 1 redirect rule processed successfully.
- 2 header rules processed successfully.

## Local Assets Deployed

The website is a Vite React/TypeScript app in `dashboard/`.

Primary files:

- `dashboard/index.html`
- `dashboard/src/main.tsx`
- `dashboard/src/App.tsx`
- `dashboard/src/index.css`
- `dashboard/public/profusion-aperture.png`
- `dashboard/public/__forms.html`
- `netlify.toml`

The deployed homepage is a standalone public-facing Profusion AI site. It is separate from the local Profusion operator dashboard/API surface and does not consume the orchestration backend.

## Netlify Configuration

The repo root now contains `netlify.toml`:

```toml
[build]
  base = "dashboard"
  command = "pnpm build"
  publish = "dist"

[build.environment]
  NODE_VERSION = "20.19.6"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    X-Frame-Options = "DENY"
    Referrer-Policy = "strict-origin-when-cross-origin"

[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

The SPA fallback is intentionally present so front-end routes resolve to `index.html`. There is no public API route on this static website deployment.

## Form Handling

Netlify Form detection is enabled for the project.

The contact form is registered as:

- Form name: `trust-session`
- Form ID: `69f1020fef3bd4000827b1d3`
- Honeypot: enabled
- reCAPTCHA: disabled
- Submission count immediately after smoke-test cleanup: `0`
- Current submission count may be higher after Kyle's later manual notification test.

Registered fields:

- `subject`
- `bot-field`
- `name`
- `org`
- `email`
- `context`

Because the visible form is rendered by React, `dashboard/public/__forms.html` provides the static hidden form Netlify needs at build time. The visible React form includes the matching hidden `form-name` field and submits URL-encoded data to Netlify Forms.

Relevant Netlify docs:

- Form setup: `https://docs.netlify.com/manage/forms/setup/`
- Form notifications: `https://docs.netlify.com/manage/forms/notifications/`

## Notification Routing

Kyle manually configured the Netlify form notification:

- Event: new verified submission from `trust-session`
- Destination: `kyle@profusion.ai`

Kyle then submitted a test request through the live site and confirmed that the notification arrived in the `kyle@profusion.ai` inbox.

The Netlify plugin/tooling used during deployment could verify the form and submissions, but it did not expose notification-rule inspection. The notification success is therefore based on Kyle's manual dashboard configuration plus the inbox receipt confirmation.

## Verification Performed

Local verification from `dashboard/`:

```bash
pnpm lint
pnpm build
```

Netlify-config verification from repo root:

```bash
NETLIFY_SITE_ID=3a16f00c-b40e-4a48-a9d5-a6ac92f2b39e npx netlify build --offline
```

Production HTTP checks:

```bash
curl -I https://profusion.ai
curl -s https://profusion.ai | rg -n "Human trust|Profusion AI|synthetic media|assets"
curl -s https://profusion.ai/__forms.html
```

Observed production headers included:

- `HTTP/2 200`
- `server: Netlify`
- `strict-transport-security: max-age=31536000`
- `x-content-type-options: nosniff`
- `x-frame-options: DENY`
- `referrer-policy: strict-origin-when-cross-origin`

Live form smoke test:

- A POST to `https://profusion.ai/__forms.html` returned HTTP `200`.
- Netlify recorded the submission under `trust-session`.
- The smoke-test submission was deleted afterward.
- Kyle later submitted a manual test through the live site and confirmed email notification delivery to `kyle@profusion.ai`.

## Current Operational State

Done:

- Public site deployed to `https://profusion.ai`.
- Direct Netlify deployment path works without GitHub linkage.
- Build configuration is repo-owned in `netlify.toml`.
- Contact form is registered and accepts submissions.
- Email notification to `kyle@profusion.ai` is configured and confirmed.
- Deployment and form state are documented.

Still open:

- No analytics are configured.
- No privacy/legal pages exist yet.
- No broader production asset optimization has been performed beyond the cropped aperture logo PNG and Vite's standard static asset hashing.
- The site is not currently wired to GitHub CI/CD, by design after the previous GitHub-linked splash-page flow was unlinked.

## Repeat Deployment Path

To validate before the next direct deploy:

```bash
cd /home/kyle/profusion/dashboard
pnpm lint
pnpm build
```

Then verify the Netlify config from repo root:

```bash
cd /home/kyle/profusion
NETLIFY_SITE_ID=3a16f00c-b40e-4a48-a9d5-a6ac92f2b39e npx netlify build --offline
```

If the local asdf `pnpm` shim reports that no preset version is installed, use Corepack for local validation:

```bash
cd /home/kyle/profusion/dashboard
corepack pnpm lint
corepack pnpm build
```

For the Netlify offline build in that same local shell, wrap `pnpm` through Corepack before running the build command:

```bash
cd /home/kyle/profusion
pnpm() { corepack pnpm "$@"; }
export -f pnpm
NETLIFY_SITE_ID=3a16f00c-b40e-4a48-a9d5-a6ac92f2b39e npx netlify build --offline
```

For another plugin-assisted direct deploy, target:

```text
siteId=3a16f00c-b40e-4a48-a9d5-a6ac92f2b39e
```

After deploy, check:

```bash
curl -I https://profusion.ai
curl -s https://profusion.ai/__forms.html
```

Then submit one live contact-form test and confirm the notification reaches `kyle@profusion.ai`.
