"""Database init and idempotency tests."""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from orchestrator.db import SCHEMA_VERSION, init_db


EXPECTED_TABLES = {
    "schema_migrations",
    "content_items",
    "content_briefs",
    "script_variants",
    "render_jobs",
    "approval_records",
    "publish_jobs",
    "agent_runs",
    "source_documents",
}


@pytest.fixture
def tmp_db(tmp_path):
    return tmp_path / "test_content.db"


def _table_names(db_path: Path) -> set[str]:
    conn = sqlite3.connect(str(db_path))
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    conn.close()
    return {r[0] for r in rows}


def test_init_creates_all_tables(tmp_db):
    init_db(tmp_db)
    tables = _table_names(tmp_db)
    assert EXPECTED_TABLES.issubset(tables)


def test_init_is_idempotent(tmp_db):
    init_db(tmp_db)
    init_db(tmp_db)  # second call must not raise
    tables = _table_names(tmp_db)
    assert EXPECTED_TABLES.issubset(tables)


def test_schema_version_recorded(tmp_db):
    init_db(tmp_db)
    conn = sqlite3.connect(str(db_path := tmp_db))
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    migration_count = conn.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]
    conn.close()
    assert version == SCHEMA_VERSION
    assert migration_count >= 1


def test_foreign_keys_enforced(tmp_db):
    init_db(tmp_db)
    conn = sqlite3.connect(str(tmp_db))
    conn.execute("PRAGMA foreign_keys = ON")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO content_briefs (id, content_item_id, thesis) VALUES (?, ?, ?)",
            ("brief-1", "nonexistent-id", "test thesis"),
        )
        conn.commit()
    conn.close()


def test_status_check_constraint(tmp_db):
    import uuid
    init_db(tmp_db)
    conn = sqlite3.connect(str(tmp_db))
    conn.execute("PRAGMA foreign_keys = ON")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO content_items (id, topic, status) VALUES (?, ?, ?)",
            (str(uuid.uuid4()), "test topic", "invalid_status"),
        )
        conn.commit()
    conn.close()


def test_init_creates_parent_dirs(tmp_path):
    nested_path = tmp_path / "deep" / "nested" / "content.db"
    init_db(nested_path)
    assert nested_path.exists()
