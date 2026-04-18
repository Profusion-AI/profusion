"""Anthropic Claude adapter.

Safe to import without a live API key. Only generate() requires the key.
"""

from __future__ import annotations

import orchestrator.config as config


class MissingAPIKeyError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "ANTHROPIC_API_KEY is not set. "
            "Copy .env.example to .env and add your key, then re-run."
        )


def generate(
    system: str,
    user: str,
    model: str | None = None,
    max_tokens: int = 4096,
) -> str:
    """Call Claude and return the text response.

    Raises MissingAPIKeyError if ANTHROPIC_API_KEY is not configured.
    """
    if not config.ANTHROPIC_API_KEY:
        raise MissingAPIKeyError()

    import anthropic  # deferred import so module loads without the package present in tests

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=model or config.CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return message.content[0].text
