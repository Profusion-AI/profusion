# M8-GTM QC Cleanup

Date: 2026-05-18
Status: Cleanup plan and decision record after live repo QC audit.

## Audit Inputs

- `docs/milestones/M8_GTM_LIVE_REPO_QC_AUDIT_2026-05-18.md`
- `docs/milestones/M8_GTM_PATH_C_TURNKEY_REPRODUCTION_2026-05-18.md`

## Cleanup Scope

This cleanup handles the repo-hygiene and documentation items that can be
completed safely before P0.1 implementation:

- add a public active-surface map
- add fresh-clone Path C bootstrap and smoke scripts
- add first GitHub Actions CI for backend tests, offline smoke, and Path C
- remove fake-looking secret placeholder from `.env.example`
- expand `.gitignore` for local explorations and generated artifacts
- update README/runbook/status guidance so P0 users do not start from legacy
  vendor checks

## Explicit Non-Scope

This cleanup does not implement P1 HyperFrames video generation.

This cleanup does not implement canonical receipt comparison.

This cleanup does not harden the state machine.

This cleanup does not add read-only API mode.

This cleanup does not physically remove MoneyPrinterTurbo, MoneyPrinterV2, or
legacy render/publish code. Those surfaces are frozen for P1 and documented in
`docs/ACTIVE_SURFACES.md`.

## Exec-Level Decisions Surfaced

### 1. Physical vendor removal is separate from logical demotion

The QC audit is correct that P1 does not need MoneyPrinterTurbo or
MoneyPrinterV2. This cleanup demotes them to frozen historical compatibility.
Removing the submodules and legacy command code is a separate decision because
the repo still has historical milestone docs, tests, and compatibility paths
that refer to render/publish behavior.

Recommended default: keep frozen during P0.1, then remove or archive code only
after the P0.1 workflow issue and P1 claim-controlled video path are stable.

### 2. CI should prove P0 without vendor submodules

The first CI workflow intentionally uses `submodules: false`. If P0/P0.1 breaks
without vendor checkout, that is a product-boundary regression.

### 3. Public repo can keep high-level plans, not raw local artifacts

Plans, milestone notes, runbooks, and sanitized examples are public-safe.
Generated receipts, logs, source packs, drafts, private operating data, and
exploratory outputs stay ignored unless deliberately sanitized and approved.

### 4. P0.1 should stay receipt-first

The next implementation can address a real-world workflow issue, but it should
enter through the same evidence path: captured artifacts, review boundary,
receipt, supported/unsupported claims, and limitations. Do not widen into live
automation, public website copy, or cockpit mutation controls as a shortcut.
