# Customer Trust Triage Receipt Fixture

This fixture is the P0 local-demo source for:

```bash
uv run profusion m8 demo support-triage-human-review
```

It simulates an n8n-style support triage workflow using local artifacts only.
It does not prove live n8n execution, live Gmail/Slack/Sheets/HubSpot
integration, or live customer sends.

Cases:

- `routine_invoice`: a routine invoice resend request proceeds without a human
  review boundary.
- `sensitive_billing_complaint`: a sensitive billing complaint triggers human
  review before the final reply artifact is marked ready.

Evidence mode:

```text
fixture_backed_local_demo
```
