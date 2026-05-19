# AICE Source-to-Narrative Receipt Fixture

This fixture is the minimum local-demo source for workflow slug:

```bash
aice-source-to-narrative-receipt
```

It models a source-to-narrative editorial workflow using metadata-only source
cards. No audio, video, images, transcripts, or third-party media files are
downloaded into this fixture.

The run demonstrates a narrow receipt boundary:

- Source cards are registered as metadata only.
- Quote candidates are extracted as short, attributed snippets.
- Claims are mapped to supporting source cards or marked unsupported.
- Rights and ambiguity review occur before the narrative brief is marked ready.
- Human editorial review approves the brief only for internal demo use.

Evidence mode:

```text
fixture_backed_local_demo
```

This fixture does not prove live n8n execution, live source access, publication
rights, factual truth beyond the listed source metadata, or external publication
approval.
