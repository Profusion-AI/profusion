# Archived DECISIONS: 2026-05-08 Substack Publishing + Evidence Loop Spike

Archived on 2026-05-17 because Profusion and the education/content engine were
split into separate projects. This material is preserved for implementation
history only. It is not current Profusion guidance.

Current ownership:

- Profusion: B2B workflow trust, evidence boundaries, review gates, receipts,
  sanitized demo workflow, and generic workflow outcome observations.
- Attention Media Lab: education/content operations, Substack packaging, source
  packs, voice guides, owned-media drafts, and content-channel measurement.

## 2026-05-08 — M8 Substack Publishing + Evidence Loop Spike

### Substack starts as a manual package and readback adapter

**Decision:** Build the Substack working-concept path as a Profusion adapter and
CLI/service first: package an approved content item for manual Substack
publishing, record a human-published URL only after an existing package and
explicit confirmation, and verify the recorded URL through RSS readback.

**Rationale:**

- Substack's official Developer API documentation, reviewed 2026-05-08,
  describes public read-only profile lookup and does not document
  create/publish post endpoints.
- Substack's official publishing instructions still describe the web editor,
  dashboard, audience/email controls, and scheduling UI as the normal
  publishing path.
- Substack's default email/app inbox behavior makes ungated browser publish
  automation an unnecessary blast risk for the first spike.
- RSS readback is official and lightweight enough to verify that a public post
  exists before richer third-party readback is introduced.
- Stackhooks can be useful later for structured post/comment/engagement
  readback, but it is independent from Substack and should not become the
  publishing channel.

### Manual Substack article drafts need an explicit content-approval gate

**Decision:** Add a narrow `substack import-article` path for human-approved
local long-form drafts. The command requires `--confirm-content-approval`,
records the draft, voice guide, and source sample as source documents when
provided, and creates an approved package-ready content item without requiring
manual SQLite edits.

**Rationale:**

- The Substack voice run needs a safe path from local draft artifact to
  package-ready Profusion item.
- The command still does not publish to Substack, does not scrape Substack, and
  does not bypass the later `--confirm-publish` gate.
- The current content state machine is video-shaped, so this remains a bounded
  M8.1 spike path until article-native lifecycle states are warranted.

### MCP wraps Profusion commands later, not business logic first

**Decision:** Do not put core Substack publishing behavior directly in an MCP
script. MCP tools may later wrap safe Profusion commands after the adapter/CLI
contract is stable.

**Rationale:**

- Profusion's durable architecture keeps platform behavior behind
  `src/orchestrator/` adapters and services.
- MCP is a tool interface, not the source of business rules.
- Human approval, confirmation prompts, artifact logging, and
  receipt/measurement linkage are project invariants that should remain
  testable without an MCP host.
