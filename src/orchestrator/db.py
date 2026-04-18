"""SQLite database initialization and schema management.

init_db() is idempotent — safe to call multiple times.
Schema versioned via PRAGMA user_version + schema_migrations table.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 2


def _connect(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str | Path = "data/content.db") -> None:
    """Initialize or migrate the database schema. Safe to call multiple times."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = _connect(db_path)
    try:
        current_version = conn.execute("PRAGMA user_version").fetchone()[0]
        if current_version >= SCHEMA_VERSION:
            return
        if current_version == 0:
            _create_schema_v1(conn)
            conn.execute(
                "INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)",
                (1,),
            )
            current_version = 1
        if current_version == 1:
            _migrate_v1_to_v2(conn)
            conn.execute(
                "INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)",
                (2,),
            )
            current_version = 2
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        conn.commit()
    finally:
        conn.close()


def _create_schema_v1(conn: sqlite3.Connection) -> None:
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

        CREATE INDEX IF NOT EXISTS idx_content_items_status  ON content_items(status);
        CREATE INDEX IF NOT EXISTS idx_content_items_pillar  ON content_items(pillar);
        CREATE INDEX IF NOT EXISTS idx_script_variants_item  ON script_variants(content_item_id);
        CREATE INDEX IF NOT EXISTS idx_render_jobs_status    ON render_jobs(status);
    """)


def _migrate_v1_to_v2(conn: sqlite3.Connection) -> None:
    """v2: add source_documents table and risk/source JSON columns on content_briefs."""
    existing_cols = {
        row["name"] for row in conn.execute("PRAGMA table_info(content_briefs)").fetchall()
    }
    if "risk_flags" not in existing_cols:
        conn.execute(
            "ALTER TABLE content_briefs ADD COLUMN risk_flags TEXT NOT NULL DEFAULT '[]'"
        )
    if "source_refs" not in existing_cols:
        conn.execute(
            "ALTER TABLE content_briefs ADD COLUMN source_refs TEXT NOT NULL DEFAULT '[]'"
        )

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS source_documents (
            id               TEXT PRIMARY KEY,
            content_item_id  TEXT NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
            url              TEXT,
            title            TEXT,
            markdown         TEXT NOT NULL DEFAULT '',
            metadata         TEXT NOT NULL DEFAULT '{}',
            created_at       TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_source_documents_item ON source_documents(content_item_id);
    """)


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

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


def get_all_items(
    db_path: str | Path = "data/content.db",
    status: str | None = None,
) -> list[dict]:
    """Return content items ordered by priority desc, created_at desc.

    Optional status filter restricts results to a single lifecycle state.
    """
    db_path = Path(db_path)
    if not db_path.exists():
        return []
    conn = _connect(db_path)
    try:
        if status:
            rows = conn.execute(
                "SELECT * FROM content_items WHERE status = ? "
                "ORDER BY priority DESC, created_at DESC",
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM content_items ORDER BY priority DESC, created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_item(db_path: str | Path, item_id: str) -> dict | None:
    conn = _connect(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM content_items WHERE id = ?", (item_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def find_item_by_prefix(db_path: str | Path, prefix: str) -> dict | None:
    """Resolve a short id prefix to a unique content_item, or None.

    Raises ValueError if the prefix is ambiguous.
    """
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM content_items WHERE id LIKE ? LIMIT 2",
            (prefix + "%",),
        ).fetchall()
        if not rows:
            return None
        if len(rows) > 1:
            raise ValueError(f"Ambiguous id prefix {prefix!r}")
        return dict(rows[0])
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Writes
# ---------------------------------------------------------------------------

def insert_content_item(
    db_path: str | Path,
    *,
    topic: str,
    pillar: str | None = None,
    audience: str | None = None,
    priority: int = 0,
    source: str | None = None,
    status: str = "idea",
    item_id: str | None = None,
) -> str:
    item_id = item_id or str(uuid.uuid4())
    conn = _connect(db_path)
    try:
        conn.execute(
            "INSERT INTO content_items (id, topic, pillar, audience, status, priority, source) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (item_id, topic, pillar, audience, status, priority, source),
        )
        conn.commit()
        return item_id
    finally:
        conn.close()


def update_item_status(db_path: str | Path, item_id: str, new_status: str) -> None:
    conn = _connect(db_path)
    try:
        cur = conn.execute(
            "UPDATE content_items SET status = ?, updated_at = datetime('now') WHERE id = ?",
            (new_status, item_id),
        )
        if cur.rowcount == 0:
            raise LookupError(f"content_item {item_id} not found")
        conn.commit()
    finally:
        conn.close()


def insert_content_brief(
    db_path: str | Path,
    *,
    content_item_id: str,
    thesis: str,
    angle: str | None,
    hook_options: list[str],
    cta: str | None,
    claims_to_verify: list[dict | str],
    brand_notes: str | None,
    risk_flags: list[dict | str],
    source_refs: list[dict | str],
    brief_id: str | None = None,
) -> str:
    brief_id = brief_id or str(uuid.uuid4())
    conn = _connect(db_path)
    try:
        conn.execute(
            "INSERT INTO content_briefs "
            "(id, content_item_id, thesis, angle, hook_options, cta, "
            " claims_to_verify, brand_notes, risk_flags, source_refs) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                brief_id,
                content_item_id,
                thesis,
                angle,
                json.dumps(hook_options),
                cta,
                json.dumps(claims_to_verify),
                brand_notes,
                json.dumps(risk_flags),
                json.dumps(source_refs),
            ),
        )
        conn.commit()
        return brief_id
    finally:
        conn.close()


def get_latest_brief(db_path: str | Path, content_item_id: str) -> dict | None:
    conn = _connect(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM content_briefs WHERE content_item_id = ? "
            "ORDER BY created_at DESC LIMIT 1",
            (content_item_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def insert_script_variant(
    db_path: str | Path,
    *,
    content_item_id: str,
    variant_name: str,
    script_text: str,
    duration_target_seconds: int = 60,
    status: str = "draft",
    variant_id: str | None = None,
) -> str:
    variant_id = variant_id or str(uuid.uuid4())
    conn = _connect(db_path)
    try:
        conn.execute(
            "INSERT INTO script_variants "
            "(id, content_item_id, variant_name, script_text, duration_target_seconds, status) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                variant_id,
                content_item_id,
                variant_name,
                script_text,
                duration_target_seconds,
                status,
            ),
        )
        conn.commit()
        return variant_id
    finally:
        conn.close()


def get_script_variants(db_path: str | Path, content_item_id: str) -> list[dict]:
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM script_variants WHERE content_item_id = ? ORDER BY created_at",
            (content_item_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def insert_source_document(
    db_path: str | Path,
    *,
    content_item_id: str,
    url: str | None,
    title: str | None,
    markdown: str,
    metadata: dict[str, Any] | None = None,
    source_id: str | None = None,
) -> str:
    source_id = source_id or str(uuid.uuid4())
    conn = _connect(db_path)
    try:
        conn.execute(
            "INSERT INTO source_documents "
            "(id, content_item_id, url, title, markdown, metadata) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                source_id,
                content_item_id,
                url,
                title,
                markdown,
                json.dumps(metadata or {}),
            ),
        )
        conn.commit()
        return source_id
    finally:
        conn.close()


def get_source_documents(db_path: str | Path, content_item_id: str) -> list[dict]:
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM source_documents WHERE content_item_id = ? ORDER BY created_at",
            (content_item_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
