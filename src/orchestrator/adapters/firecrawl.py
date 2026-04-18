"""Firecrawl source ingestion adapter — stub.

Firecrawl is running locally at localhost:3002 (systemd service).
Implement in Milestone 1 for educational source ingestion.

Interface:
    scrape(url) -> SourceDocument
    crawl(start_url, max_pages) -> list[SourceDocument]
"""

from __future__ import annotations

from dataclasses import dataclass, field

import orchestrator.config as config


@dataclass
class SourceDocument:
    url: str
    title: str
    markdown: str
    metadata: dict = field(default_factory=dict)


def scrape(url: str) -> SourceDocument:
    """Scrape a single URL via the local Firecrawl instance.

    Uses FIRECRAWL_URL from config (default: http://localhost:3002).
    """
    raise NotImplementedError(
        f"firecrawl.scrape() not yet implemented. "
        f"Firecrawl is at {config.FIRECRAWL_URL}. Implement in Milestone 1."
    )


def crawl(start_url: str, max_pages: int = 10) -> list[SourceDocument]:
    """Crawl a site via the local Firecrawl instance."""
    raise NotImplementedError(
        "firecrawl.crawl() not yet implemented. Implement in Milestone 1."
    )
