"""M5 scheduling and cross-posting CLI tests."""

from pathlib import Path

from typer.testing import CliRunner

from orchestrator.cli import app
from orchestrator.db import (
    get_all_items,
    get_publish_jobs_for_item,
    init_db,
    insert_content_item,
    update_item_status,
)
from tests.test_publish import _seed_approved_item, _use_tmp_db


def _schedule_args(item_id: str, *targets: str, at: str = "2026-04-21T09:00:00-05:00") -> list[str]:
    args = ["schedule", "--item-id", item_id, "--at", at]
    for target in targets or ("youtube_shorts:99",):
        args.extend(["--target", target])
    return args


def _publish_due_args(now: str = "2026-04-21T14:00:00Z") -> list[str]:
    return ["publish-due", "--now", now]


def test_schedule_refuses_non_approved_item(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id = insert_content_item(db_path, topic="not approved")
    update_item_status(db_path, item_id, "planned")

    result = CliRunner().invoke(app, _schedule_args(item_id))

    assert result.exit_code != 0
    assert "[error]" in result.output
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "planned"
    assert get_publish_jobs_for_item(db_path, item_id) == []


def test_schedule_creates_scheduled_job_and_transitions_item(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)

    result = CliRunner().invoke(
        app,
        _schedule_args(item_id, "youtube_shorts:99"),
    )

    assert result.exit_code == 0
    assert "[scheduled]" in result.output
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "scheduled"

    jobs = get_publish_jobs_for_item(db_path, item_id)
    assert len(jobs) == 1
    assert jobs[0]["status"] == "scheduled"
    assert jobs[0]["platform"] == "youtube_shorts"
    assert jobs[0]["account_id"] == 99
    assert jobs[0]["scheduled_for"] == "2026-04-21T14:00:00Z"


def test_schedule_creates_crosspost_jobs_atomically(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)

    result = CliRunner().invoke(
        app,
        _schedule_args(item_id, "youtube_shorts:99", "tiktok:100"),
    )

    assert result.exit_code == 0
    jobs = get_publish_jobs_for_item(db_path, item_id)
    assert {j["platform"] for j in jobs} == {"youtube_shorts", "tiktok"}
    assert all(j["status"] == "scheduled" for j in jobs)
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "scheduled"


def test_schedule_fails_if_package_invalid_without_partial_state(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, mp4_path = _seed_approved_item(db_path, tmp_path)
    Path(mp4_path).unlink()

    result = CliRunner().invoke(app, _schedule_args(item_id))

    assert result.exit_code != 0
    assert "[error]" in result.output
    jobs = get_publish_jobs_for_item(db_path, item_id)
    assert jobs == []
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "approved"


def test_publish_due_ignores_future_jobs(monkeypatch, tmp_path):
    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)
    CliRunner().invoke(app, _schedule_args(item_id, at="2026-04-21T09:00:00-05:00"))

    result = CliRunner().invoke(app, _publish_due_args(now="2026-04-21T13:59:59Z"))

    assert result.exit_code == 0
    assert "No scheduled publish jobs due" in result.output
    jobs = get_publish_jobs_for_item(db_path, item_id)
    assert jobs[0]["status"] == "scheduled"


def test_publish_due_processes_due_job(monkeypatch, tmp_path):
    from orchestrator.adapters.v2 import PublishResult

    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)
    CliRunner().invoke(app, _schedule_args(item_id, "youtube_shorts:99"))

    monkeypatch.setattr(
        "orchestrator.adapters.v2.publish",
        lambda *a, **kw: PublishResult(
            platform="youtube_shorts",
            external_post_id="post-1",
            published_url="https://example.com/post-1",
        ),
    )

    result = CliRunner().invoke(app, _publish_due_args())

    assert result.exit_code == 0
    assert "[published]" in result.output
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "published"
    jobs = get_publish_jobs_for_item(db_path, item_id)
    assert jobs[0]["status"] == "completed"
    assert jobs[0]["external_post_id"] == "post-1"
    assert jobs[0]["attempt_count"] == 1


def test_publish_due_partial_crosspost_failure_keeps_item_scheduled(monkeypatch, tmp_path):
    from orchestrator.adapters.v2 import PublishResult, V2PublishError

    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)
    CliRunner().invoke(
        app,
        _schedule_args(item_id, "youtube_shorts:99", "tiktok:100"),
    )

    def publish_stub(video_path, profile, **kw):
        if profile.platform == "tiktok":
            raise V2PublishError("network error")
        return PublishResult(
            platform=profile.platform,
            external_post_id=f"post-{profile.platform}",
            published_url=None,
        )

    monkeypatch.setattr("orchestrator.adapters.v2.publish", publish_stub)

    result = CliRunner().invoke(app, _publish_due_args())

    assert result.exit_code != 0
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "scheduled"
    jobs = get_publish_jobs_for_item(db_path, item_id)
    by_platform = {j["platform"]: j for j in jobs}
    assert by_platform["youtube_shorts"]["status"] == "completed"
    assert by_platform["tiktok"]["status"] == "failed"
    assert "network error" in by_platform["tiktok"]["last_error"]


def test_publish_due_crosspost_all_complete_publishes_item(monkeypatch, tmp_path):
    from orchestrator.adapters.v2 import PublishResult

    db_path = _use_tmp_db(monkeypatch, tmp_path)
    init_db(db_path)
    item_id, _, _ = _seed_approved_item(db_path, tmp_path)
    CliRunner().invoke(
        app,
        _schedule_args(item_id, "youtube_shorts:99", "tiktok:100"),
    )

    def publish_stub(video_path, profile, **kw):
        return PublishResult(
            platform=profile.platform,
            external_post_id=f"post-{profile.platform}",
            published_url=None,
        )

    monkeypatch.setattr("orchestrator.adapters.v2.publish", publish_stub)

    result = CliRunner().invoke(app, _publish_due_args())

    assert result.exit_code == 0
    items = [i for i in get_all_items(db_path) if i["id"] == item_id]
    assert items[0]["status"] == "published"
    jobs = get_publish_jobs_for_item(db_path, item_id)
    assert all(j["status"] == "completed" for j in jobs)
