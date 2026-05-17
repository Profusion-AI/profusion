import { describe, expect, it } from "vitest";
import {
  buildQueueModel,
  buildItemModel,
  filterQueueRows,
  formatOperatorTime,
} from "./cockpitViewModel";
import type { ContentItem } from "../api/queue";
import type { ItemPayload } from "../api/items";

const queueItems: ContentItem[] = [
  {
    id: "item-idea",
    topic: "Why schools optimize for compliance",
    status: "idea",
    pillar: "education_reform",
    audience: "educators",
    priority: 5,
    source: null,
    created_at: "2026-04-18T15:46:26Z",
    updated_at: "2026-04-18T15:46:26Z",
  },
  {
    id: "item-failed",
    topic: "Render failure case",
    status: "qa_failed",
    pillar: "trust",
    audience: "operators",
    priority: 2,
    source: "manual",
    created_at: "2026-05-01T10:00:00Z",
    updated_at: "2026-05-03T14:18:00Z",
  },
  {
    id: "item-approval",
    topic: "Approval queue case",
    status: "awaiting_approval",
    pillar: null,
    audience: null,
    priority: 3,
    source: null,
    created_at: "2026-05-02T10:00:00Z",
    updated_at: "2026-05-03T15:00:00Z",
  },
  {
    id: "item-published",
    topic: "Published case",
    status: "published",
    pillar: null,
    audience: "founders",
    priority: 1,
    source: null,
    created_at: "2026-05-02T10:00:00Z",
    updated_at: "2026-05-03T15:30:00Z",
  },
  {
    id: "item-measured",
    topic: "Measured case",
    status: "measured",
    pillar: "education",
    audience: "operators",
    priority: 2,
    source: null,
    created_at: "2026-05-02T10:00:00Z",
    updated_at: "2026-05-04T15:30:00Z",
  },
];

describe("cockpit view model", () => {
  it("builds artifact-style queue rows and metrics from existing queue payloads", () => {
    const model = buildQueueModel(queueItems);

    expect(model.metrics).toEqual([
      { label: "Queue", value: 5, tone: "neutral" },
      { label: "Needs Attention", value: 1, tone: "danger" },
      { label: "Awaiting Approval", value: 1, tone: "warning" },
      { label: "Evidence Ready", value: 2, tone: "success" },
      { label: "Measured", value: 1, tone: "info" },
    ]);
    expect(model.rows[0]).toMatchObject({
      id: "item-idea",
      shortId: "item-idea",
      title: "Why schools optimize for compliance",
      state: "Idea",
      stateTone: "neutral",
      lastEvent: "Created",
      artifacts: "0 available",
      approval: "Not required",
      failure: "—",
      nextCommand: "uv run profusion inspect --item-id item-idea",
      priority: "P5",
    });
    expect(model.rows[1]).toMatchObject({
      state: "QA Failed",
      stateTone: "danger",
      failure: "Needs operator review",
    });
  });

  it("filters queue rows by artifact-style categories and search text", () => {
    const { rows } = buildQueueModel(queueItems);

    expect(filterQueueRows(rows, "Failed / Blocked", "")).toHaveLength(1);
    expect(filterQueueRows(rows, "Awaiting Approval", "")).toHaveLength(1);
    expect(filterQueueRows(rows, "Published", "")).toHaveLength(1);
    expect(filterQueueRows(rows, "Measured", "")).toHaveLength(1);
    expect(filterQueueRows(rows, "All", "schools")).toEqual([rows[0]]);
    expect(filterQueueRows(rows, "Needs Attention", "approval")).toEqual([rows[2]]);
  });

  it("builds detail panels without broad mutation buttons", () => {
    const payload: ItemPayload = {
      item: queueItems[0],
      lifecycle_state: "idea",
      milestone: "M6",
      latest_brief: null,
      script_variants: [],
      latest_script_variant: null,
      latest_render_job: null,
      latest_qa: null,
      latest_approval: null,
      latest_publish_job: null,
      jobs: [],
      artifacts: {
        mp4_exists: false,
        manifest_exists: false,
        qa_report_exists: false,
      },
      recent_logs: [],
      blockage: null,
      retry: {
        retryable: false,
        reason: "No failed retry surface detected",
      },
      next_safe_command: "uv run profusion approve --item-id item-idea",
    };

    expect(buildItemModel(payload)).toMatchObject({
      id: "item-idea",
      title: "Why schools optimize for compliance",
      lifecycle: "Idea",
      command: {
        command: "uv run profusion approve --item-id item-idea",
        isMutation: true,
        warning: "Run this in a terminal after verifying the item state.",
      },
      evidence: [
        { label: "Brief", value: "Missing", tone: "muted" },
        { label: "Script Variants", value: "0", tone: "muted" },
        { label: "MP4", value: "Missing", tone: "muted" },
        { label: "Manifest", value: "Missing", tone: "muted" },
        { label: "QA Report", value: "Missing", tone: "muted" },
      ],
    });
  });

  it("formats operator timestamps compactly and keeps missing values explicit", () => {
    expect(formatOperatorTime(null)).toBe("—");
    expect(formatOperatorTime("2026-05-03T14:18:00Z")).toContain("May 3");
  });
});
