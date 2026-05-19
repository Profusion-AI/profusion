"""Render buyer-readable M8-GTM workflow receipts."""

from __future__ import annotations

from html import escape
from typing import Any


def render_receipt_markdown(receipt: dict[str, Any]) -> str:
    """Render the workflow receipt as plain Markdown."""

    lines = [
        f"# {receipt['workflow_name']}",
        "",
        f"- Receipt ID: `{receipt['receipt_id']}`",
        f"- Evidence mode: `{receipt['evidence_mode']}`",
        f"- Generated at: `{receipt['generated_at']}`",
        "",
        "## Workflow Boundary",
        str(receipt["evidence_boundary"]),
        "",
    ]
    if receipt.get("topic_episode_thesis"):
        lines.extend(
            [
                "## Topic / Episode Thesis",
                str(receipt["topic_episode_thesis"]),
                "",
            ]
        )
    lines.extend(
        [
        "## What Happened",
        *_markdown_list(receipt["what_happened"]),
        "",
        "## Where AI Acted",
        *_markdown_list(receipt["where_ai_acted"]),
        "",
        ]
    )
    if receipt.get("where_n8n_acted"):
        lines.extend(
            [
                "## Where n8n Acted",
                *_markdown_list(receipt["where_n8n_acted"]),
                "",
            ]
        )
    human_review_title = (
        "Where Human Editorial Review Entered"
        if receipt.get("trust_domain") == "ai_assisted_investigative_content"
        else "Where Human Review Entered"
    )
    lines.extend(
        [
        f"## {human_review_title}",
        *_markdown_list(receipt["where_human_review_entered"]),
        "",
        ]
    )
    _extend_optional_markdown_section(lines, "Source Cards Captured", receipt.get("source_cards"))
    _extend_optional_markdown_section(
        lines,
        "Claims and Quote Candidates",
        receipt.get("claims_and_quote_candidates") or receipt.get("quote_candidates"),
    )
    _extend_optional_markdown_section(
        lines,
        "Rights / Use / Ambiguity Classification",
        receipt.get("rights_use_ambiguity_classification"),
    )
    _extend_optional_markdown_section(
        lines,
        "Attention Intelligence Mapping",
        receipt.get("attention_intelligence_mapping"),
    )
    _extend_optional_markdown_section(
        lines,
        "Narrative Decisions",
        receipt.get("narrative_decisions"),
    )
    _extend_optional_markdown_section(
        lines,
        "Generated / Synthetic Media Plan",
        receipt.get("generated_synthetic_media_plan"),
    )
    lines.extend(
        [
        "## Artifacts Captured",
        *_artifact_list(receipt["artifacts_reviewed"]),
        "",
        "## Final Outcome",
        *_key_value_list(receipt["final_action"]),
        "",
        "## Supported Claims",
        *_markdown_list(receipt["claims_supported"]),
        "",
        "## Claims Not Supported",
        *_markdown_list(receipt["claims_not_supported"]),
        "",
        "## Limitations",
        *_markdown_list(receipt["limitations"]),
        "",
        "## Next Recommended Review",
        str(receipt["next_recommended_review"]),
        "",
        ]
    )
    return "\n".join(lines)


def render_receipt_html(receipt: dict[str, Any]) -> str:
    """Render the workflow receipt as escaped standalone HTML."""

    title = escape(str(receipt["workflow_name"]))
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            f"  <title>{title}</title>",
            "  <style>",
            "    body { font-family: system-ui, sans-serif; line-height: 1.55; margin: 2rem; max-width: 920px; }",
            "    code { background: #f2f2f2; padding: 0.1rem 0.25rem; }",
            "    section { margin: 1.5rem 0; }",
            "  </style>",
            "</head>",
            "<body>",
            f"  <h1>{title}</h1>",
            f"  <p><strong>Receipt ID:</strong> <code>{escape(str(receipt['receipt_id']))}</code></p>",
            f"  <p><strong>Evidence mode:</strong> <code>{escape(str(receipt['evidence_mode']))}</code></p>",
            f"  <p><strong>Generated at:</strong> <code>{escape(str(receipt['generated_at']))}</code></p>",
            _section("Workflow Boundary", f"<p>{escape(str(receipt['evidence_boundary']))}</p>"),
            _optional_section("Topic / Episode Thesis", receipt.get("topic_episode_thesis")),
            _section("What Happened", _html_list(receipt["what_happened"])),
            _section("Where AI Acted", _html_list(receipt["where_ai_acted"])),
            _optional_section("Where n8n Acted", receipt.get("where_n8n_acted")),
            _section(
                "Where Human Editorial Review Entered"
                if receipt.get("trust_domain") == "ai_assisted_investigative_content"
                else "Where Human Review Entered",
                _html_list(receipt["where_human_review_entered"]),
            ),
            _optional_section("Source Cards Captured", receipt.get("source_cards")),
            _optional_section(
                "Claims and Quote Candidates",
                receipt.get("claims_and_quote_candidates") or receipt.get("quote_candidates"),
            ),
            _optional_section(
                "Rights / Use / Ambiguity Classification",
                receipt.get("rights_use_ambiguity_classification"),
            ),
            _optional_section(
                "Attention Intelligence Mapping",
                receipt.get("attention_intelligence_mapping"),
            ),
            _optional_section("Narrative Decisions", receipt.get("narrative_decisions")),
            _optional_section(
                "Generated / Synthetic Media Plan",
                receipt.get("generated_synthetic_media_plan"),
            ),
            _section("Artifacts Captured", _html_artifacts(receipt["artifacts_reviewed"])),
            _section("Final Outcome", _html_key_values(receipt["final_action"])),
            _section("Supported Claims", _html_list(receipt["claims_supported"])),
            _section("Claims Not Supported", _html_list(receipt["claims_not_supported"])),
            _section("Limitations", _html_list(receipt["limitations"])),
            _section("Next Recommended Review", f"<p>{escape(str(receipt['next_recommended_review']))}</p>"),
            "</body>",
            "</html>",
            "",
        ]
    )


def _markdown_list(values: list[Any]) -> list[str]:
    return [f"- {_markdown_value(value)}" for value in values]


def _extend_optional_markdown_section(
    lines: list[str],
    title: str,
    value: Any,
) -> None:
    if value is None:
        return
    lines.extend([f"## {title}"])
    if isinstance(value, list):
        lines.extend(_markdown_list(value))
    else:
        lines.extend(_markdown_list([value]))
    lines.append("")


def _artifact_list(values: list[dict[str, Any]]) -> list[str]:
    return [
        f"- `{row['artifact_id']}`: {row['label']} ({row['packet_path']})"
        for row in values
    ]


def _key_value_list(values: dict[str, Any]) -> list[str]:
    return [
        f"- {_label_key(str(key))}: {_markdown_value(value)}"
        for key, value in values.items()
    ]


def _section(title: str, body: str) -> str:
    return f"  <section>\n    <h2>{escape(title)}</h2>\n    {body}\n  </section>"


def _optional_section(title: str, value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return _section(title, _html_list(value))
    return _section(title, _html_list([value]))


def _html_list(values: list[Any]) -> str:
    items = "\n".join(f"      <li>{_html_value(value)}</li>" for value in values)
    return f"<ul>\n{items}\n    </ul>"


def _html_artifacts(values: list[dict[str, Any]]) -> str:
    items = "\n".join(
        "      <li>"
        f"<code>{escape(str(row['artifact_id']))}</code>: "
        f"{escape(str(row['label']))} "
        f"(<code>{escape(str(row['packet_path']))}</code>)"
        "</li>"
        for row in values
    )
    return f"<ul>\n{items}\n    </ul>"


def _html_key_values(values: dict[str, Any]) -> str:
    items = "\n".join(
        f"      <li><strong>{escape(_label_key(str(key)))}:</strong> {_html_value(value)}</li>"
        for key, value in values.items()
    )
    return f"<ul>\n{items}\n    </ul>"


def _markdown_value(value: Any) -> str:
    if isinstance(value, dict):
        return "; ".join(
            f"{_label_key(str(key))}: {_markdown_value(nested)}"
            for key, nested in value.items()
        )
    if isinstance(value, list):
        return ", ".join(_markdown_value(item) for item in value)
    if value is None:
        return "None"
    return str(value)


def _html_value(value: Any) -> str:
    if isinstance(value, dict):
        return "; ".join(
            f"<strong>{escape(_label_key(str(key)))}:</strong> {_html_value(nested)}"
            for key, nested in value.items()
        )
    if isinstance(value, list):
        return ", ".join(_html_value(item) for item in value)
    if value is None:
        return "None"
    return escape(str(value))


def _label_key(key: str) -> str:
    special = {
        "ai": "AI",
        "api": "API",
        "html": "HTML",
        "id": "ID",
        "json": "JSON",
        "n8n": "n8n",
        "qa": "QA",
        "url": "URL",
    }
    return " ".join(
        special.get(part.lower(), part.replace("-", " ").capitalize())
        for part in key.split("_")
    )
