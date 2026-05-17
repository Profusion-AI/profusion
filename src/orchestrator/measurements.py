"""File-first M8 workflow outcome observations."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator import db
from orchestrator.state import ContentStatus, transition


class MeasurementEligibilityError(ValueError):
    """Raised when a content item is not ready for measurement."""


class MeasurementValidationError(ValueError):
    """Raised when a measurement observation is malformed."""


DISPLAY_LABELS = {
    "measurement_group": "Outcome Observations",
    "platform": "Workflow Type",
    "hook_variant": "Scenario Variant",
    "content_format": "Workflow Type",
    "editorial_pillar": "Trust Domain",
}


def record_measurement_observation(
    *,
    db_path: Path,
    measurements_dir: Path,
    item_id: str,
    platform: str,
    observation_type: str,
    recorded_by: str,
    qualitative_signal: str | None = None,
    views: int | None = None,
    completion_rate: float | None = None,
    comments: int | None = None,
    hook_variant: str | None = None,
    content_format: str | None = None,
    editorial_pillar: str | None = None,
    recorded_at: str | None = None,
) -> dict[str, Any]:
    """Record one manual workflow outcome observation and close published -> measured."""

    item = db.get_item(db_path, item_id)
    if item is None:
        raise MeasurementEligibilityError(f"No content item found for {item_id!r}")

    status_before = str(item["status"])
    if status_before not in {ContentStatus.PUBLISHED.value, ContentStatus.MEASURED.value}:
        raise MeasurementEligibilityError(
            "Workflow item must be published or measured before an outcome observation can be "
            f"recorded; got {status_before!r}"
        )

    platform = _validate_slug(platform, "platform")
    observation_type = _validate_slug(observation_type, "observation_type")
    recorded_by = _validate_required_text(recorded_by, "recorded_by")
    qualitative_signal = _normalize_optional_text(qualitative_signal)
    views = _validate_nonnegative_int(views, "views")
    comments = _validate_nonnegative_int(comments, "comments")
    completion_rate = _validate_completion_rate(completion_rate)
    item_pillar = item.get("pillar")
    default_pillar = (
        _normalize_optional_text(str(item_pillar)) if item_pillar is not None else None
    )
    dimensions = {
        "hook_variant": _normalize_optional_text(hook_variant),
        "content_format": _normalize_optional_text(content_format),
        "editorial_pillar": _normalize_optional_text(editorial_pillar) or default_pillar,
    }
    display_dimensions = {
        "scenario_variant": dimensions["hook_variant"],
        "workflow_type": dimensions["content_format"] or platform,
        "trust_domain": dimensions["editorial_pillar"],
    }
    recorded_at = _normalize_timestamp(recorded_at) if recorded_at else _now_iso()
    created_at = _now_iso()

    status_after = status_before
    if status_before == ContentStatus.PUBLISHED.value:
        transition(status_before, ContentStatus.MEASURED)
        status_after = ContentStatus.MEASURED.value

    observation_id = (
        f"measure-{item_id[:12]}-"
        f"{created_at.replace(':', '').replace('-', '')}-{uuid4().hex[:8]}"
    )
    item_dir = measurements_dir / _safe_path_segment(item_id, "item_id")
    item_dir.mkdir(parents=True, exist_ok=True)
    observation_path = item_dir / f"{observation_id}.json"

    payload: dict[str, Any] = {
        "observation_id": observation_id,
        "content_item_id": item_id,
        "platform": platform,
        "observation_type": observation_type,
        "source": "manual",
        "recorded_by": recorded_by,
        "recorded_at": recorded_at,
        "created_at": created_at,
        "status_before": status_before,
        "status_after": status_after,
        "metrics": {
            "views": views,
            "completion_rate": completion_rate,
            "comments": comments,
        },
        "dimensions": dimensions,
        "display_dimensions": display_dimensions,
        "display_labels": DISPLAY_LABELS,
        "qualitative_signal": qualitative_signal,
        "item_snapshot": {
            "topic": item.get("topic"),
            "pillar": item.get("pillar"),
            "audience": item.get("audience"),
            "priority": item.get("priority"),
            "source": item.get("source"),
        },
        "observation_path": str(observation_path),
    }
    observation_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    if status_before == ContentStatus.PUBLISHED.value:
        db.update_item_status(db_path, item_id, ContentStatus.MEASURED.value)
    return payload


def measurements_payload(*, measurements_dir: Path, item_id: str) -> dict[str, Any]:
    """Return manual workflow outcome observations for one item."""

    observations = _read_observations_for_item(measurements_dir, item_id)
    return {
        "item_id": item_id,
        "measurement_count": len(observations),
        "display_labels": DISPLAY_LABELS,
        "latest_observation": observations[0] if observations else None,
        "observations": observations,
    }


def measurement_summary_payload(*, db_path: Path, measurements_dir: Path) -> dict[str, Any]:
    """Return aggregate M8 workflow outcome observation read-model data."""

    observations = _read_all_observations(measurements_dir)
    by_platform = Counter(str(obs.get("platform") or "unknown") for obs in observations)
    by_type = Counter(str(obs.get("observation_type") or "unknown") for obs in observations)
    by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for obs in observations:
        by_item[str(obs.get("content_item_id") or "unknown")].append(obs)

    measured_items = db.get_all_items(db_path, status=ContentStatus.MEASURED.value)
    measured_ids = {str(item["id"]) for item in measured_items}
    item_rows = []
    for item_id, item_observations in sorted(by_item.items()):
        latest = item_observations[0]
        item_rows.append(
            {
                "item_id": item_id,
                "observation_count": len(item_observations),
                "latest_observation": latest,
                "status": "measured" if item_id in measured_ids else None,
            }
        )

    return {
        "observation_count": len(observations),
        "measured_item_count": len(measured_items),
        "platforms": _counter_rows(by_platform, "platform"),
        "observation_types": _counter_rows(by_type, "observation_type"),
        "display_labels": DISPLAY_LABELS,
        "aggregate_metrics": _aggregate_metrics(observations),
        "comparisons": {
            "hook_variants": _comparison_rows(observations, "hook_variant"),
            "content_formats": _comparison_rows(observations, "content_format"),
            "editorial_pillars": _comparison_rows(observations, "editorial_pillar"),
        },
        "latest_observation": observations[0] if observations else None,
        "items": item_rows,
    }


def _read_observations_for_item(measurements_dir: Path, item_id: str) -> list[dict[str, Any]]:
    item_dir = measurements_dir / _safe_path_segment(item_id, "item_id")
    if not item_dir.exists():
        return []
    return _sort_observations(
        obs
        for path in item_dir.glob("*.json")
        if (obs := _read_observation(path)) is not None
    )


def _read_all_observations(measurements_dir: Path) -> list[dict[str, Any]]:
    if not measurements_dir.exists():
        return []
    return _sort_observations(
        obs
        for path in measurements_dir.glob("*/*.json")
        if (obs := _read_observation(path)) is not None
    )


def _read_observation(path: Path) -> dict[str, Any] | None:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(loaded, dict):
        return None
    loaded.setdefault("observation_path", str(path))
    return loaded


def _sort_observations(observations: Any) -> list[dict[str, Any]]:
    return sorted(
        list(observations),
        key=lambda obs: str(obs.get("recorded_at") or obs.get("created_at") or ""),
        reverse=True,
    )


def _counter_rows(counter: Counter[str], key: str) -> list[dict[str, Any]]:
    return [
        {key: name, "count": count}
        for name, count in sorted(counter.items(), key=lambda row: (-row[1], row[0]))
    ]


def _comparison_rows(
    observations: list[dict[str, Any]],
    dimension: str,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for obs in observations:
        value = _dimension_value(obs, dimension)
        if value is not None:
            grouped[value].append(obs)

    rows = []
    for value, group in grouped.items():
        item_ids = {
            str(obs.get("content_item_id"))
            for obs in group
            if obs.get("content_item_id")
        }
        rows.append(
            {
                dimension: value,
                "display_label": DISPLAY_LABELS.get(dimension, dimension),
                "display_value": value,
                "observation_count": len(group),
                "item_count": len(item_ids),
                "aggregate_metrics": _aggregate_metrics(group),
                "latest_observation": group[0],
            }
        )
    return sorted(
        rows,
        key=lambda row: (-int(row["observation_count"]), str(row[dimension])),
    )


def _dimension_value(obs: dict[str, Any], dimension: str) -> str | None:
    dimensions = obs.get("dimensions") if isinstance(obs.get("dimensions"), dict) else {}
    value = dimensions.get(dimension)
    if value is None and dimension == "editorial_pillar":
        snapshot = obs.get("item_snapshot") if isinstance(obs.get("item_snapshot"), dict) else {}
        value = snapshot.get("pillar")
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _aggregate_metrics(observations: list[dict[str, Any]]) -> dict[str, Any]:
    total_views = 0
    total_comments = 0
    completion_rates: list[float] = []
    for obs in observations:
        metrics = obs.get("metrics") if isinstance(obs.get("metrics"), dict) else {}
        views = metrics.get("views")
        comments = metrics.get("comments")
        completion_rate = metrics.get("completion_rate")
        if isinstance(views, int):
            total_views += views
        if isinstance(comments, int):
            total_comments += comments
        if isinstance(completion_rate, (int, float)):
            completion_rates.append(float(completion_rate))
    return {
        "views": total_views,
        "comments": total_comments,
        "average_completion_rate": (
            round(sum(completion_rates) / len(completion_rates), 4)
            if completion_rates
            else None
        ),
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _normalize_timestamp(value: str) -> str:
    raw = value.strip()
    if not raw:
        raise MeasurementValidationError("recorded_at cannot be empty")
    candidate = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise MeasurementValidationError(
            "recorded_at must be an ISO datetime like '2026-05-08T12:00:00-05:00'"
        ) from exc
    if parsed.tzinfo is None:
        raise MeasurementValidationError("recorded_at must include a timezone offset")
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _validate_slug(value: str, field: str) -> str:
    normalized = _validate_required_text(value, field)
    if any(ch.isspace() for ch in normalized) or "/" in normalized or "\\" in normalized:
        raise MeasurementValidationError(
            f"{field} must be a compact slug such as 'internal_demo'"
        )
    return normalized


def _validate_required_text(value: str, field: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise MeasurementValidationError(f"{field} cannot be empty")
    return normalized


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _validate_nonnegative_int(value: int | None, field: str) -> int | None:
    if value is None:
        return None
    if value < 0:
        raise MeasurementValidationError(f"{field} must be greater than or equal to 0")
    return value


def _validate_completion_rate(value: float | None) -> float | None:
    if value is None:
        return None
    if value < 0 or value > 1:
        raise MeasurementValidationError("completion_rate must be between 0 and 1")
    return value


def _safe_path_segment(value: str, field: str) -> str:
    if Path(value).name != value or "/" in value or "\\" in value:
        raise MeasurementValidationError(f"{field} cannot contain path separators")
    return value
