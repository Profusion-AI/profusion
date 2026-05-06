# Workflow Receipt Simulator Fixtures

Date: 2026-05-06

## Purpose

The Workflow Receipt Simulator uses deterministic static fixtures. It does not call the internal cockpit API, mutate receipt lifecycle state, write customer data, or fetch live production artifacts.

## Template Status Labels

Use these labels consistently:

- Current sample: the path matches current shipped proof closely enough to use as the default.
- Simulated example: the path demonstrates receipt logic but is not generated from a live integration.
- Future integration concept: the path is a possible future capture route.
- Not offered: the path should not be represented as a Profusion capability.

## M7.75 Templates

### AI-Assisted Content Approval

Status: Current sample

Maps to current proof:

- `trust_domain: media_trust`
- `receipt_type: content_video_receipt`
- content item
- brief
- script
- render
- QA
- human approval
- schedule or publish readiness
- receipt limitation language

### Coding-Agent Output Review

Status: Simulated example

Future integration concept:

- task brief
- agent output summary
- changed files
- tests requested
- review notes
- approval context

Not claimed:

- production coding-agent instrumentation
- live MCP capture
- PR, diff, or CI capture
- code correctness validation

### AI-Mediated Contractor Readiness

Status: Simulated example

Future path only. Avoid ranking, selection, rejection, role-fit, hire, or no-hire language.

Not claimed:

- automated employment decisioning
- candidate ranking
- hiring recommendation
- compliance determination

## Copy Rules

Preferred language:

- Sample Workflow Receipt
- Evidence available
- Human review recorded
- QA checkpoint applied
- Limitations included
- Supported claim
- Unsupported claim
- Outside receipt boundary

Avoid:

- Certified
- Compliant
- Verified truth
- Production integration
- Live MCP capture
- Autonomous governance
- AI observability platform
- Hiring recommendation
- Candidate ranking
