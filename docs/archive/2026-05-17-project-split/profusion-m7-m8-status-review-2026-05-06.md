# Profusion M7-M8 Development Status Review

Date: 2026-05-06

## 2026-05-07 Update

This review was written before the final M7 lock commit. It remains useful as a
technical/business analysis of the M7-to-M8 boundary, but the closeout state has
changed:

2026-05-08 update: M8 has now started as the canonical content measurement
loop after explicit product-owner instruction. Use `STATUS.md`,
`docs/ROADMAP.md`, and
`docs/milestones/M8_MEASUREMENT_LOOPS_FIRST_SLICE_2026-05-08.md` for current
M8 scope.

- M7 is now formally locked and shipped.
- The broad dirty-worktree risk called out below was resolved by commit
  `f711908 M7 closeout: lock operator cockpit and receipt preview`.
- The current M7 source of truth is
  `docs/milestones/M7_OPERATOR_COCKPIT_FINAL_CLOSEOUT_2026-05-06.md`.
- M8 remains deferred. Do not start measurement loops from this review unless
  the roadmap is explicitly updated or buyer/pilot signal makes measurement the
  blocking requirement.
- The current real demo receipt remains `draft` unless Kyle explicitly reviews
  and advances it.

Purpose: review Profusion's development status between M7 and M8, analyze the project from technical and business perspectives using the two newest authored markdown documents, and surface assumptions to resolve before executing the next milestones.

## Scope And Source Notes

The two newest authored markdown documents in the repo, excluding generated dependency docs under `.netlify/node_modules`, are:

- `docs/profusion-homepage-reliability-gap-update-2026-05-05.md`
- `docs/profusion-homepage-launch-handoff-2026-05-05.md`

Supporting source-of-truth files reviewed:

- `STATUS.md`
- `DECISIONS.md`
- `docs/ROADMAP.md`
- `docs/milestones/M7_M7_5_TO_M8_HANDOFF_2026-05-03.md`
- `docs/profusion-zero-to-one-plan-2026-05-05.md`
- `docs/profusion-status-business-case-2026-05-05.md`
- `dashboard/src/App.tsx`
- `src/orchestrator/receipts/generator.py`
- `src/orchestrator/api.py`
- `src/orchestrator/cli.py`
- `apps/operator-cockpit/src/pages/EvidencePage.tsx`
- `apps/operator-cockpit/src/domain/cockpitSignals.ts`

## Current Verdict

Profusion is between M7.5 closeout and M8 start.

M7 is complete as an internal operator cockpit baseline. M7.5 has a complete first evidence slice for the current content workflow. M8 should not start as a general measurement-loop build until the receipt packet is reviewed, advanced through the intended lifecycle, and used as a selling or reviewer artifact.

The project is technically real, but still narrow. It has an operable local workflow substrate, a separate internal cockpit, a file-first receipt generator, receipt lifecycle commands, a read API, static preview export, and passing tests. It does not yet have a hosted mutable backend, customer portal, integrations, coding-agent receipt generator, Work Trust scenario runner, or measurement loops.

The business status is more ambiguous. The two newest homepage docs show a deliberate public-positioning expansion from AI workflow trust and media evidence toward a broader productivity-reliability wedge, especially coding-agent and agentic engineering review. That market frame may be stronger, but the implemented receipt model still proves media-trust content workflow evidence, not engineering reliability evidence. Treat the homepage expansion as a hypothesis until the product has one concrete sample receipt for that wedge.

## Fresh Verification

Commands run on 2026-05-06:

```text
uv run pytest: 182 passed
uv run profusion smoke --offline: passed
cd dashboard && corepack pnpm lint: passed
cd dashboard && corepack pnpm build: passed
cd apps/operator-cockpit && corepack pnpm test: 9 passed
cd apps/operator-cockpit && corepack pnpm lint: passed
cd apps/operator-cockpit && corepack pnpm build:netlify: passed
cd apps/operator-cockpit && corepack pnpm smoke:static: passed for 2 item(s)
```

Live checks:

```text
https://profusion.ai/: HTTP 200
Production homepage serves /assets/index-DnAjgt9x.js and /assets/index-B-FFNL2g.css
The JS bundle contains: AI WORKFLOW RELIABILITY PRACTICE, RELIABILITY RECEIPT, AI CODING AGENT RELIABILITY, AI Workflow Reliability Pilot, Productivity-Reliability Diagnostic

https://69f770eec1439a4cd6b2a8c9--profusionai.netlify.app/queue: HTTP 200
Draft response includes x-robots-tag: noindex / nofollow
GET /api/items/m75-demo-content-video-receipt/receipts: receipt_count=1, receipt_status=draft, receipt_type=content_video_receipt
```

## M7 Status

M7 is complete for the current sprint.

Implemented and verified:

- Separate internal Vite app at `apps/operator-cockpit/`.
- FastAPI/read-model consumption rather than direct SQLite access.
- Queue, item detail, jobs/failures, artifacts, approvals, logs, handoff, and evidence views.
- Next safe command presentation.
- Guarded mutation posture: commands are visible, but broad state-moving actions remain terminal-only.
- Static Netlify preview export using generated read-only `/api/*` JSON.
- Public `dashboard/` boundary preserved for the production website.

Residual M7 risks as of the original review:

- Resolved after the original review: the M7/M7.5 worktree had not yet been
  captured in a clean commit.
- Remote cockpit preview is static, not a live hosted cockpit.
- The cockpit is internal-operator tooling, not a buyer-facing product.

2026-05-07 note: the dirty-worktree risk was resolved by commit `f711908`.
The static-preview and internal-tooling boundaries still apply.

## M7.5 Status

M7.5 first slice is complete, but the demo packet remains in draft state.

Implemented and verified:

- `content_video_receipt` generator under `src/orchestrator/receipts/`.
- Packet generation to `data/receipts/<receipt_id>/`.
- Packet files: `receipt.md`, `summary.md`, `limitations.md`, `reviewer_notes.md`, `evidence.json`.
- CLI commands:
  - `uv run profusion receipt draft --item-id <id> --json`
  - `uv run profusion receipt list --item-id <id> --json`
  - `uv run profusion receipt transition --receipt-id <id> --to reviewed --json`
  - `uv run profusion receipt transition --receipt-id <id> --to approved_for_packet --json`
  - `uv run profusion receipt transition --receipt-id <id> --to delivered --json`
- API route: `GET /api/items/{item_id}/receipts`.
- Cockpit Evidence page surfaces receipt status and next terminal-only lifecycle command.
- Static snapshot exports receipt JSON for demo preview.

Current demo receipt:

```text
data/receipts/content-video-m75-demo-con-20260503T155812Z-ceb13ddd/
receipt_status: draft
receipt_type: content_video_receipt
trust_domain: media_trust
subject_id: m75-demo-content-video-receipt
```

M7.5 limitation:

The current receipt documents the content workflow only: item, brief, script, render, QA, approval, schedule/publish state, artifact pointers, evidence sources, and limitations. It does not document coding-agent diffs, tests, PR review, CI results, review burden, verification tax, or engineering reliability signals.

## M8 Status

M8 has not started.

The planned M8 scope remains measurement and learning loops:

- file-first/manual measurement imports for published content metrics
- item-level and aggregate measurement read models
- CLI commands for recording observations
- transition eligible `published` items to `measured`
- cockpit visibility after CLI/read-model behavior is tested

M8 should stay deferred until one of these is true:

- a buyer conversation proves measurement is the blocker for selling the pilot
- the current media receipt packet has been reviewed and used externally
- a signed or near-signed pilot requires measurement as part of delivery

Starting M8 now risks optimizing an internal content pipeline while the business question is still whether anyone will pay for a receipt packet.

## Technical Analysis

The strongest technical asset is the disciplined local workflow substrate. The repo has an explicit state machine, SQLite source of truth, CLI surfaces, read models, FastAPI boundary, internal cockpit, file-first receipt artifacts, and a working static-preview deployment lane. That is enough to support founder-led pilot delivery.

The architecture remains appropriately conservative. Keeping receipts file-first avoids premature schema lock-in. Keeping approval/schedule/publish/receipt transitions terminal-only protects operational integrity. Keeping public website and internal cockpit separated prevents M7 from being swallowed by marketing-site churn.

The main technical gap is not test coverage or implementation quality. It is model-product alignment. The implementation proves a `content_video_receipt`; the newest public website talks most loudly about productivity-reliability and coding-agent reliability. That gap can be acceptable as positioning, but it should not be mistaken for shipped capability.

The second technical gap is demo polish around the packet itself. The cockpit can show receipt presence, but Kyle still needs a sales-ready artifact that makes sense without explaining the cockpit, FastAPI, SQLite, or milestone history.

## Business Analysis

The two newest homepage docs make a material strategic change.

The May 5 launch handoff frames Profusion as AI workflow trust: reviewable evidence for high-risk AI-assisted and agentic work. It still points the first offer at one workflow, one evidence boundary, one human review gate, and one reviewer-readable receipt.

The later May 5 reliability-gap update reframes the public page around the productivity-reliability gap in AI-assisted work. It foregrounds coding-agent and engineering workflows while preserving content, synthetic media, recruiting, and client-facing automation as likely first-client surfaces.

This is directionally strong because "reliability gap" is more buyer-readable than generic trust language. It connects to an obvious pain: AI increases output speed, but review, verification, approval, and accountability become the bottleneck.

The risk is wedge dilution. The current implemented receipt is closest to AI-assisted media/content governance. The homepage now leads with coding-agent reliability. If outbound starts with engineering reliability, prospects may expect PR, CI, test, diff, code-review, and production-change receipts that Profusion does not yet produce.

The business path should therefore be:

1. Sell the repeatable kernel, not the cockpit: workflow boundary -> evidence map -> captured artifacts -> review decision -> limitations -> receipt packet.
2. Pick one first-client wedge for outreach. Media/content governance is closest to shipped product. Coding-agent reliability is plausible but needs a purpose-built sample receipt first.
3. Use the public website as top-level category language, but keep calls and pilots grounded in one real workflow and one packet.
4. Do not build platform surfaces before buyer evidence: portal, login, billing, integrations, external reviewer queue, full MCP, or Work Trust runner.

## Questions And Assumptions To Resolve

1. Which wedge owns the next two weeks: AI-assisted media/content governance, or coding-agent reliability?

The site now leads with coding-agent reliability, but the product evidence is still media-trust `content_video_receipt`. If the answer is coding-agent reliability, the next build should probably be a sanitized engineering reliability sample receipt before M8.

2. Is the demo receipt ready to be reviewed and advanced from `draft` to `reviewed` / `approved_for_packet`?

The lifecycle exists, but the current packet is still draft. Advancing it should mean Kyle has actually reviewed the packet language and limitations, not just that the command works.

3. What is the first prospect supposed to receive before a call?

The cockpit preview is useful for internal credibility, but a prospect likely needs a one-page sample receipt and pilot scope more than a dashboard.

4. Are we comfortable with the homepage promising "productivity-reliability" before the repo has engineering-specific receipt artifacts?

This can be fine as a positioning hypothesis, but it should be explicit. Otherwise the public site may pull the roadmap toward coding-agent infrastructure before the first paid pilot validates that direction.

5. What counts as the M8 trigger?

If M8 means content measurement loops, it should wait for buyer signal. If M8 is being reinterpreted as reliability measurement for AI workflows, the roadmap needs to be updated before execution.

6. Is the first sale a manual service product or a software demo?

The current docs mostly say founder-led paid pilot. That implies templates, packet quality, scope, and buyer conversations outrank new code unless a signed pilot requires it.

7. Should `docs/current-copy-splash.md` be treated as stale?

It still preserves the earlier workflow-trust copy, while `dashboard/src/App.tsx` and the latest reliability-gap handoff now use reliability-gap language. This should be updated or marked as superseded before more copy work.

8. When should the broad dirty worktree be committed?

The repo contains a coherent M7/M7.5 sprint state plus later homepage work. Before the next milestone, it should be split deliberately into commits or at least documented as a handoff boundary so future agents do not accidentally revert or conflate unrelated changes.

## Recommended Next Execution Order

1. Decide the next wedge explicitly.
2. Review the current demo receipt packet and either keep it draft or transition it to `reviewed` / `approved_for_packet`.
3. Create a sales-ready sample receipt that can be read without the cockpit.
4. Create the pilot operating kit: intake, evidence-boundary worksheet, receipt-review checklist, pilot-scope template.
5. Build the first 20-prospect outbound list and test the payment question.
6. Defer M8 measurement loops unless a buyer conversation makes measurement the blocking requirement.

The near-term milestone is not "M8 shipped." It is "one credible receipt packet used in one serious buyer conversation."
