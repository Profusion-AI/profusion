"""v1 → v2 migration tests.

Simulates a database initialized at schema v1, then runs init_db() and
verifies the v2 additions land correctly without data loss.
"""

import sqlite3
import uuid

from orchestrator.db import SCHEMA_VERSION, init_db


V1_DDL = """
CREATE TABLE schema_migrations (
    version     INTEGER PRIMARY KEY,
    applied_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE content_items (
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
CREATE TABLE content_briefs (
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
"""


def _bootstrap_v1(db_path):
    conn = sqlite3.connect(str(db_path))
    conn.executescript(V1_DDL)
    conn.execute("INSERT INTO schema_migrations (version) VALUES (1)")
    conn.execute("PRAGMA user_version = 1")
    # Pre-existing data that must survive migration:
    item_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO content_items (id, topic) VALUES (?, ?)",
        (item_id, "legacy topic"),
    )
    conn.execute(
        "INSERT INTO content_briefs (id, content_item_id, thesis) VALUES (?, ?, ?)",
        (str(uuid.uuid4()), item_id, "legacy thesis"),
    )
    conn.commit()
    conn.close()
    return item_id


def _columns(conn, table):
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def test_v1_to_v2_adds_source_documents(tmp_path):
    db_path = tmp_path / "v1.db"
    _bootstrap_v1(db_path)

    init_db(db_path)

    conn = sqlite3.connect(str(db_path))
    tables = {
        r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    assert "source_documents" in tables
    assert conn.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    conn.close()


def test_v1_to_v2_adds_brief_risk_and_source_columns(tmp_path):
    db_path = tmp_path / "v1.db"
    _bootstrap_v1(db_path)

    init_db(db_path)

    conn = sqlite3.connect(str(db_path))
    cols = _columns(conn, "content_briefs")
    assert "risk_flags" in cols
    assert "source_refs" in cols
    conn.close()


def test_v1_to_v2_preserves_legacy_rows(tmp_path):
    db_path = tmp_path / "v1.db"
    legacy_item_id = _bootstrap_v1(db_path)

    init_db(db_path)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    item = conn.execute(
        "SELECT * FROM content_items WHERE id = ?", (legacy_item_id,)
    ).fetchone()
    assert item is not None
    assert item["topic"] == "legacy topic"
    brief = conn.execute(
        "SELECT * FROM content_briefs WHERE content_item_id = ?",
        (legacy_item_id,),
    ).fetchone()
    assert brief is not None
    # Defaults apply on ALTER-added columns:
    assert brief["risk_flags"] == "[]"
    assert brief["source_refs"] == "[]"
    conn.close()


def test_second_init_is_noop(tmp_path):
    db_path = tmp_path / "v1.db"
    _bootstrap_v1(db_path)
    init_db(db_path)
    init_db(db_path)  # must not raise or duplicate tables

    conn = sqlite3.connect(str(db_path))
    # ALTER TABLE ... ADD COLUMN errors if run twice without a guard; confirm we survive.
    cols = _columns(conn, "content_briefs")
    assert "risk_flags" in cols
    conn.close()
