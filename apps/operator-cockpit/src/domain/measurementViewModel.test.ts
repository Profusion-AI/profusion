import { describe, expect, it } from "vitest";
import {
  buildMeasurementComparisonRows,
  formatMeasurementRate,
  measurementComparisonLabels,
} from "./measurementViewModel";
import type { MeasurementComparison } from "../api/items";

const rows: MeasurementComparison[] = [
  {
    hook_variant: "proof_first",
    display_label: "Scenario Variant",
    display_value: "proof_first",
    observation_count: 2,
    item_count: 2,
    aggregate_metrics: {
      views: 150,
      comments: 3,
      average_completion_rate: 0.625,
    },
    latest_observation: {
      observation_id: "measure-1",
      content_item_id: "item-1",
      platform: "founder_review",
      observation_type: "workflow_outcome",
      recorded_by: "Kyle",
      recorded_at: "2026-05-08T13:00:00Z",
      created_at: "2026-05-08T13:01:00Z",
      status_before: "published",
      status_after: "measured",
      metrics: {
        views: 50,
        completion_rate: 0.75,
        comments: 1,
      },
      qualitative_signal: "The evidence boundary clarified ownership.",
      observation_path: "data/measurements/item-1/measure-1.json",
    },
  },
];

describe("measurement view model", () => {
  it("formats manual workflow outcome comparison rows for cockpit display", () => {
    expect(buildMeasurementComparisonRows(rows, "hook_variant")).toEqual([
      {
        label: "proof_first",
        displayLabel: "Scenario Variant",
        displayValue: "proof_first",
        countLabel: "2 observations / 2 items",
        metricsLabel: "150 views / 3 comments / 63% avg completion",
        latestSignal: "The evidence boundary clarified ownership.",
      },
    ]);
  });

  it("keeps compatibility field names behind generic labels", () => {
    expect(measurementComparisonLabels).toEqual({
      hook_variant: "Scenario Variant",
      content_format: "Workflow Type",
      editorial_pillar: "Trust Domain",
    });
  });

  it("keeps missing rates explicit", () => {
    expect(formatMeasurementRate(null)).toBe("—");
    expect(formatMeasurementRate(0.421)).toBe("42%");
  });
});
