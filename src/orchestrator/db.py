"""SQLite database initialization and schema management.

init_db() is idempotent — safe to call multiple times.
Schema versioned via PRAGMA user_version + schema_migrations table.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

SCHEMA_VERSION = 1


def _connect(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str | Path = "data/content.db") -> None:
    """Initialize database schema. Safe to call multiple times."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = _connect(db_path)
    try:
        current_version = conn.execute("PRAGMA user_version").fetchone()[0]
        if current_version >= SCHEMA_VERSION:
            return
        _create_schema(conn)
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        conn.commit()
    finally:
        conn.close()


def _create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version     INTEGER PRIMARY KEY,
            applied_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS content_items (
            id          TEXT PRIMARY KEY,
            topic       TEXT NOT NULL,
            pillar      TEXT,
            audience    TEXT,
            status      TEXT NOT NULL DEFAULT 'idea'
                            CHECK(status IN (
                                'idea','planned','scripted','rendered',
                                'qa_failed','qa_passed','awaiting_approval',
                                'approved','scheduled','published','measured','archived'
                            )),
            priority    INTEGER NOT NULL DEFAULT 0,
            source      TEXT,
            created_at  TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS content_briefs (
            id                  TEXT PRIMARY KEY,
            content_item_id     TEXT NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
            thesis              TEXT NOT NULL,
            angle               TEXT,
            hook_options        TEXT NOT NULL DEFAULT '[]',
            cta                 TEXT,
            claims_to_verify    TEXT NOT NULL DEFAULT '[]',
            brand_notes         TEXT,
            created_at          TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS script_variants (
            id                      TEXT PRIMARY KEY,
            content_item_id         TEXT NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
            variant_name            TEXT NOT NULL,
            script_text             TEXT NOT NULL,
            duration_target_seconds INTEGER NOT NULL DEFAULT 60,
            status                  TEXT NOT NULL DEFAULT 'draft',
            created_at              TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS render_jobs (
            id                  TEXT PRIMARY KEY,
            script_variant_id   TEXT NOT NULL REFERENCES script_variants(id) ON DELETE CASCADE,
            engine              TEXT NOT NULL DEFAULT 'moneyprinterturbo',
            render_profile      TEXT NOT NULL DEFAULT '{}',
            output_path         TEXT,
            status              TEXT NOT NULL DEFAULT 'pending',
            log_path            TEXT,
            created_at          TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS approval_records (
            id                  TEXT PRIMARY KEY,
            content_item_id     TEXT NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
            approved_by         TEXT NOT NULL,
            decision            TEXT NOT NULL CHECK(decision IN ('approved','rejected','revision_requested')),
            notes               TEXT,
            timestamp           TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS publish_jobs (
            id                  TEXT PRIMARY KEY,
            content_item_id     TEXT NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
            platform            TEXT NOT NULL,
            engine              TEXT NOT NULL DEFAULT 'moneyprinterv2',
            status              TEXT NOT NULL DEFAULT 'pending',
            published_url       TEXT,
            external_post_id    TEXT,
            published_at        TEXT,
            created_at          TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS agent_runs (
            id          TEXT PRIMARY KEY,
            started_at  TEXT NOT NULL DEFAULT (datetime('now')),
            ended_at    TEXT,
            goal        TEXT NOT NULL,
            status      TEXT NOT NULL DEFAULT 'running'
                            CHECK(status IN ('running','completed','failed')),
            summary     TEXT,
            error_class TEXT
        );

        -- Indexes for common query patterns
        CREATE INDEX IF NOT EXISTS idx_content_items_status  ON content_items(status);
        CREATE INDEX IF NOT EXISTS idx_content_items_pillar  ON content_items(pillar);
        CREATE INDEX IF NOT EXISTS idx_script_variants_item  ON script_variants(content_item_id);
        CREATE INDEX IF NOT EXISTS idx_render_jobs_status    ON render_jobs(status);
    """)

    conn.execute(
        "INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)",
        (SCHEMA_VERSION,),
    )


def get_queue_summary(db_path: str | Path = "data/content.db") -> list[dict]:
    """Return content items grouped by status for queue display."""
    db_path = Path(db_path)
    if not db_path.exists():
        return []
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT status, COUNT(*) as count FROM content_items GROUP BY status ORDER BY status"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_all_items(db_path: str | Path = "data/content.db") -> list[dict]:
    """Return all content items ordered by priority desc, created_at desc."""
    db_path = Path(db_path)
    if not db_path.exists():
        return []
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM content_items ORDER BY priority DESC, created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
