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

from orchestrator.state import ContentStatus, InvalidTransitionError, transition

SCHEMA_VERSION = 4


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
        if current_version == 2:
            _migrate_v2_to_v3(conn)
            conn.execute(
                "INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)",
                (3,),
            )
            current_version = 3
        if current_version == 3:
            _migrate_v3_to_v4(conn)
            conn.execute(
                "INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)",
                (4,),
            )
            current_version = 4
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


def _migrate_v2_to_v3(conn: sqlite3.Connection) -> None:
    """v3: add scheduling/cross-post metadata to publish_jobs."""
    conn.executescript("""
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
    """)


def _migrate_v3_to_v4(conn: sqlite3.Connection) -> None:
    """v4: add M6 retry lineage and diagnostic metadata."""
    # Some early test/legacy v1 databases contain only the tables used by M1.
    # Re-running the base CREATE TABLE IF NOT EXISTS block fills missing M0 tables
    # before additive v4 ALTERs run.
    _create_schema_v1(conn)
    table_additions = {
        "publish_jobs": [
            ("retry_of_job_id", "TEXT"),
            ("attempt_group_id", "TEXT"),
            ("error_code", "TEXT"),
            ("log_path", "TEXT"),
        ],
        "render_jobs": [
            ("retry_of_job_id", "TEXT"),
            ("attempt_group_id", "TEXT"),
            ("error_code", "TEXT"),
        ],
    }
    for table, additions in table_additions.items():
        existing_cols = {
            row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
        }
        for name, ddl in additions:
            if name not in existing_cols:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}")

    conn.executescript("""
        CREATE INDEX IF NOT EXISTS idx_publish_jobs_retry_of
            ON publish_jobs(retry_of_job_id);
        CREATE INDEX IF NOT EXISTS idx_publish_jobs_attempt_group
            ON publish_jobs(attempt_group_id);
        CREATE INDEX IF NOT EXISTS idx_render_jobs_retry_of
            ON render_jobs(retry_of_job_id);
        CREATE INDEX IF NOT EXISTS idx_render_jobs_attempt_group
            ON render_jobs(attempt_group_id);
    """)
    existing_cols = {
        row["name"] for row in conn.execute("PRAGMA table_info(publish_jobs)").fetchall()
    }
    additions = [
        ("account_id", "INTEGER"),
        ("title", "TEXT"),
        ("description", "TEXT"),
        ("scheduled_for", "TEXT"),
        ("platform_metadata", "TEXT NOT NULL DEFAULT '{}'"),
        ("last_error", "TEXT"),
        ("attempt_count", "INTEGER NOT NULL DEFAULT 0"),
        ("updated_at", "TEXT"),
    ]
    for name, ddl in additions:
        if name not in existing_cols:
            conn.execute(f"ALTER TABLE publish_jobs ADD COLUMN {name} {ddl}")

    conn.executescript("""
        CREATE INDEX IF NOT EXISTS idx_publish_jobs_status_due
            ON publish_jobs(status, scheduled_for);
        CREATE INDEX IF NOT EXISTS idx_publish_jobs_item
            ON publish_jobs(content_item_id);
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


# ---------------------------------------------------------------------------
# Render jobs
# ---------------------------------------------------------------------------

def insert_render_job(
    db_path: str | Path,
    *,
    task_id: str,
    script_variant_id: str,
    render_profile: dict,
    retry_of_job_id: str | None = None,
    attempt_group_id: str | None = None,
) -> str:
    """Insert a render job using Turbo's task_id as primary key. Returns task_id."""
    attempt_group_id = attempt_group_id or retry_of_job_id or task_id
    conn = _connect(db_path)
    try:
        conn.execute(
            "INSERT INTO render_jobs "
            "(id, script_variant_id, render_profile, retry_of_job_id, attempt_group_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                task_id,
                script_variant_id,
                json.dumps(render_profile),
                retry_of_job_id,
                attempt_group_id,
            ),
        )
        conn.commit()
        return task_id
    finally:
        conn.close()


def get_render_job(db_path: str | Path, job_id: str) -> dict | None:
    conn = _connect(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM render_jobs WHERE id = ?", (job_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_render_job_with_item(db_path: str | Path, job_id: str) -> dict | None:
    conn = _connect(db_path)
    try:
        row = conn.execute(
            "SELECT rj.*, sv.content_item_id, sv.variant_name, sv.script_text, "
            "       ci.topic, ci.status AS item_status "
            "FROM render_jobs rj "
            "JOIN script_variants sv ON sv.id = rj.script_variant_id "
            "JOIN content_items ci ON ci.id = sv.content_item_id "
            "WHERE rj.id = ?",
            (job_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_render_jobs_for_item(db_path: str | Path, content_item_id: str) -> list[dict]:
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT rj.*, sv.content_item_id, sv.variant_name "
            "FROM render_jobs rj "
            "JOIN script_variants sv ON sv.id = rj.script_variant_id "
            "WHERE sv.content_item_id = ? "
            "ORDER BY rj.created_at DESC",
            (content_item_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_render_jobs_by_variant(
    db_path: str | Path, script_variant_id: str
) -> list[dict]:
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM render_jobs WHERE script_variant_id = ? "
            "ORDER BY created_at DESC",
            (script_variant_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_render_job(
    db_path: str | Path,
    job_id: str,
    *,
    status: str,
    output_path: str | None = None,
    log_path: str | None = None,
    error_code: str | None = None,
) -> None:
    conn = _connect(db_path)
    try:
        conn.execute(
            "UPDATE render_jobs "
            "SET status = ?, "
            "    output_path = COALESCE(?, output_path), "
            "    log_path = COALESCE(?, log_path), "
            "    error_code = COALESCE(?, error_code) "
            "WHERE id = ?",
            (status, output_path, log_path, error_code, job_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_completed_render_job_for_item(
    db_path: str | Path, content_item_id: str
) -> dict | None:
    """Return the most recent completed render job for a content item."""
    conn = _connect(db_path)
    try:
        row = conn.execute(
            "SELECT rj.* FROM render_jobs rj "
            "JOIN script_variants sv ON sv.id = rj.script_variant_id "
            "WHERE sv.content_item_id = ? AND rj.status = 'completed' "
            "ORDER BY rj.created_at DESC LIMIT 1",
            (content_item_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_approval_records(
    db_path: str | Path, content_item_id: str
) -> list[dict]:
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM approval_records WHERE content_item_id = ? "
            "ORDER BY timestamp DESC",
            (content_item_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def record_approval_decision(
    db_path: str | Path,
    *,
    content_item_id: str,
    decision: str,
    approved_by: str,
    notes: str | None = None,
    record_id: str | None = None,
) -> str:
    """Atomically insert approval record and walk item status to its final state.

    Decision → final status:
        approved             → approved
        rejected             → archived
        revision_requested   → scripted

    Raises ValueError if current item status is not qa_passed.
    Raises ValueError if decision is not a recognised value.
    """
    _DECISION_TO_FINAL: dict[str, str] = {
        "approved": "approved",
        "rejected": "archived",
        "revision_requested": "scripted",
    }
    if decision not in _DECISION_TO_FINAL:
        raise ValueError(f"Unknown decision: {decision!r}")
    final_status = _DECISION_TO_FINAL[decision]
    record_id = record_id or str(uuid.uuid4())
    conn = _connect(db_path)
    try:
        conn.execute("BEGIN")
        row = conn.execute(
            "SELECT status FROM content_items WHERE id = ?",
            (content_item_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Content item {content_item_id!r} not found")
        transition(row["status"], ContentStatus.AWAITING_APPROVAL)
        transition(ContentStatus.AWAITING_APPROVAL, ContentStatus(final_status))
        conn.execute(
            "INSERT INTO approval_records (id, content_item_id, approved_by, decision, notes) "
            "VALUES (?, ?, ?, ?, ?)",
            (record_id, content_item_id, approved_by, decision, notes),
        )
        conn.execute(
            "UPDATE content_items SET status = 'awaiting_approval', updated_at = datetime('now') "
            "WHERE id = ?",
            (content_item_id,),
        )
        conn.execute(
            "UPDATE content_items SET status = ?, updated_at = datetime('now') WHERE id = ?",
            (final_status, content_item_id),
        )
        conn.commit()
        return record_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Publish jobs
# ---------------------------------------------------------------------------

def insert_publish_job(
    db_path: str | Path,
    *,
    content_item_id: str,
    platform: str,
    account_id: int | None = None,
    title: str | None = None,
    description: str | None = None,
    scheduled_for: str | None = None,
    platform_metadata: dict[str, Any] | None = None,
    status: str = "pending",
    job_id: str | None = None,
    retry_of_job_id: str | None = None,
    attempt_group_id: str | None = None,
) -> str:
    """Insert a publish job. Returns the job id."""
    job_id = job_id or str(uuid.uuid4())
    attempt_group_id = attempt_group_id or retry_of_job_id or job_id
    conn = _connect(db_path)
    try:
        conn.execute(
            "INSERT INTO publish_jobs "
            "(id, content_item_id, platform, status, account_id, title, description, "
            " scheduled_for, platform_metadata, retry_of_job_id, attempt_group_id, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))",
            (
                job_id,
                content_item_id,
                platform,
                status,
                account_id,
                title,
                description,
                scheduled_for,
                json.dumps(platform_metadata or {}),
                retry_of_job_id,
                attempt_group_id,
            ),
        )
        conn.commit()
        return job_id
    finally:
        conn.close()


def update_publish_job(
    db_path: str | Path,
    job_id: str,
    *,
    status: str,
    published_url: str | None = None,
    external_post_id: str | None = None,
    published_at: str | None = None,
    last_error: str | None = None,
    error_code: str | None = None,
    log_path: str | None = None,
    increment_attempt: bool = False,
) -> None:
    conn = _connect(db_path)
    try:
        conn.execute(
            "UPDATE publish_jobs "
            "SET status = ?, "
            "    published_url = COALESCE(?, published_url), "
            "    external_post_id = COALESCE(?, external_post_id), "
            "    published_at = COALESCE(?, published_at), "
            "    last_error = COALESCE(?, last_error), "
            "    error_code = COALESCE(?, error_code), "
            "    log_path = COALESCE(?, log_path), "
            "    attempt_count = attempt_count + ?, "
            "    updated_at = datetime('now') "
            "WHERE id = ?",
            (
                status,
                published_url,
                external_post_id,
                published_at,
                last_error,
                error_code,
                log_path,
                1 if increment_attempt else 0,
                job_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_publish_job(db_path: str | Path, job_id: str) -> dict | None:
    conn = _connect(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM publish_jobs WHERE id = ?", (job_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_publish_jobs_for_item(
    db_path: str | Path, content_item_id: str
) -> list[dict]:
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM publish_jobs WHERE content_item_id = ? ORDER BY created_at DESC",
            (content_item_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_failed_publish_jobs(db_path: str | Path) -> list[dict]:
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM publish_jobs WHERE status = 'failed' ORDER BY updated_at DESC, created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_publish_jobs_by_status(db_path: str | Path, status: str) -> list[dict]:
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM publish_jobs WHERE status = ? ORDER BY created_at DESC",
            (status,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def record_schedule_created(
    db_path: str | Path,
    *,
    content_item_id: str,
    jobs: list[dict[str, Any]],
) -> list[str]:
    """Atomically create scheduled publish jobs and transition approved -> scheduled."""
    if not jobs:
        raise ValueError("At least one scheduled publish job is required")

    job_ids = [job.get("id") or str(uuid.uuid4()) for job in jobs]
    conn = _connect(db_path)
    try:
        conn.execute("BEGIN")
        row = conn.execute(
            "SELECT status FROM content_items WHERE id = ?",
            (content_item_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Content item {content_item_id!r} not found")
        transition(row["status"], ContentStatus.SCHEDULED)

        for job_id, job in zip(job_ids, jobs):
            conn.execute(
                "INSERT INTO publish_jobs "
                "(id, content_item_id, platform, status, account_id, title, description, "
                " scheduled_for, platform_metadata, attempt_group_id, updated_at) "
                "VALUES (?, ?, ?, 'scheduled', ?, ?, ?, ?, ?, ?, datetime('now'))",
                (
                    job_id,
                    content_item_id,
                    job["platform"],
                    job["account_id"],
                    job.get("title"),
                    job.get("description"),
                    job["scheduled_for"],
                    json.dumps(job.get("platform_metadata") or {}),
                    job_id,
                ),
            )

        conn.execute(
            "UPDATE content_items SET status = 'scheduled', updated_at = datetime('now') "
            "WHERE id = ?",
            (content_item_id,),
        )
        conn.commit()
        return job_ids
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_due_publish_jobs(
    db_path: str | Path,
    *,
    now: str,
    limit: int | None = None,
) -> list[dict]:
    conn = _connect(db_path)
    try:
        query = (
            "SELECT * FROM publish_jobs "
            "WHERE status = 'scheduled' AND scheduled_for IS NOT NULL AND scheduled_for <= ? "
            "ORDER BY scheduled_for ASC, created_at ASC"
        )
        params: list[Any] = [now]
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def mark_publish_job_processing(db_path: str | Path, job_id: str) -> None:
    conn = _connect(db_path)
    try:
        conn.execute(
            "UPDATE publish_jobs "
            "SET status = 'processing', last_error = NULL, "
            "    attempt_count = attempt_count + 1, updated_at = datetime('now') "
            "WHERE id = ?",
            (job_id,),
        )
        conn.commit()
    finally:
        conn.close()


def mark_publish_job_failed(
    db_path: str | Path,
    job_id: str,
    error: str,
    *,
    error_code: str | None = None,
    log_path: str | None = None,
) -> None:
    conn = _connect(db_path)
    try:
        conn.execute(
            "UPDATE publish_jobs "
            "SET status = 'failed', last_error = ?, "
            "    error_code = COALESCE(?, error_code), "
            "    log_path = COALESCE(?, log_path), "
            "    updated_at = datetime('now') "
            "WHERE id = ?",
            (error[:1000], error_code, log_path, job_id),
        )
        conn.commit()
    finally:
        conn.close()


def requeue_failed_scheduled_publish_job(db_path: str | Path, job_id: str) -> None:
    conn = _connect(db_path)
    try:
        cur = conn.execute(
            "UPDATE publish_jobs "
            "SET status = 'scheduled', last_error = NULL, error_code = NULL, "
            "    updated_at = datetime('now') "
            "WHERE id = ? AND status = 'failed' AND scheduled_for IS NOT NULL",
            (job_id,),
        )
        if cur.rowcount == 0:
            raise ValueError(f"Failed scheduled publish job {job_id!r} not found")
        conn.commit()
    finally:
        conn.close()


def find_duplicate_scheduled_publish_jobs(
    db_path: str | Path,
    *,
    content_item_id: str,
    platform: str,
    account_id: int,
    scheduled_for: str,
) -> list[dict]:
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM publish_jobs "
            "WHERE content_item_id = ? AND platform = ? AND account_id = ? "
            "  AND scheduled_for = ? AND status IN ('scheduled', 'processing', 'completed')",
            (content_item_id, platform, account_id, scheduled_for),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def record_publish_complete(
    db_path: str | Path,
    *,
    content_item_id: str,
    job_id: str,
    published_url: str | None,
    external_post_id: str | None,
) -> None:
    """Atomically transition approved → scheduled → published and update publish job.

    Raises ValueError if item is not in 'approved' status.
    Raises InvalidTransitionError if state machine rejects the transitions.
    """
    conn = _connect(db_path)
    try:
        conn.execute("BEGIN")
        row = conn.execute(
            "SELECT status FROM content_items WHERE id = ?",
            (content_item_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Content item {content_item_id!r} not found")
        transition(row["status"], ContentStatus.SCHEDULED)
        transition(ContentStatus.SCHEDULED, ContentStatus.PUBLISHED)
        conn.execute(
            "UPDATE content_items SET status = 'scheduled', updated_at = datetime('now') WHERE id = ?",
            (content_item_id,),
        )
        conn.execute(
            "UPDATE content_items SET status = 'published', updated_at = datetime('now') WHERE id = ?",
            (content_item_id,),
        )
        conn.execute(
            "UPDATE publish_jobs "
            "SET status = 'completed', published_url = ?, external_post_id = ?, published_at = datetime('now') "
            "WHERE id = ?",
            (published_url, external_post_id, job_id),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def record_scheduled_publish_complete(
    db_path: str | Path,
    *,
    content_item_id: str,
    job_id: str,
    published_url: str | None,
    external_post_id: str | None,
) -> bool:
    """Complete one scheduled job; publish item when all scheduled jobs are complete.

    Returns True if this call transitioned the item scheduled -> published.
    """
    conn = _connect(db_path)
    try:
        conn.execute("BEGIN")
        row = conn.execute(
            "SELECT status FROM content_items WHERE id = ?",
            (content_item_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Content item {content_item_id!r} not found")
        transition(row["status"], ContentStatus.PUBLISHED)

        cur = conn.execute(
            "UPDATE publish_jobs "
            "SET status = 'completed', published_url = ?, external_post_id = ?, "
            "    published_at = datetime('now'), last_error = NULL, updated_at = datetime('now') "
            "WHERE id = ? AND content_item_id = ? AND scheduled_for IS NOT NULL",
            (published_url, external_post_id, job_id, content_item_id),
        )
        if cur.rowcount == 0:
            raise ValueError(f"Scheduled publish job {job_id!r} not found")

        remaining = conn.execute(
            "SELECT COUNT(*) FROM publish_jobs "
            "WHERE content_item_id = ? AND scheduled_for IS NOT NULL "
            "  AND status != 'completed'",
            (content_item_id,),
        ).fetchone()[0]

        transitioned = remaining == 0
        if transitioned:
            conn.execute(
                "UPDATE content_items SET status = 'published', updated_at = datetime('now') "
                "WHERE id = ?",
                (content_item_id,),
            )

        conn.commit()
        return transitioned
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
