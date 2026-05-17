import type { MeasurementComparison } from "../api/items";

export type MeasurementComparisonKey = "hook_variant" | "content_format" | "editorial_pillar";

export const measurementComparisonLabels: Record<MeasurementComparisonKey, string> = {
  hook_variant: "Scenario Variant",
  content_format: "Workflow Type",
  editorial_pillar: "Trust Domain",
};

export interface MeasurementComparisonRow {
  label: string;
  displayLabel: string;
  displayValue: string;
  countLabel: string;
  metricsLabel: string;
  latestSignal: string;
}

export function formatMeasurementRate(value: number | null): string {
  if (value === null) return "—";
  return `${Math.round(value * 100)}%`;
}

export function buildMeasurementComparisonRows(
  rows: MeasurementComparison[],
  key: MeasurementComparisonKey,
): MeasurementComparisonRow[] {
  return rows.map((row) => {
    const metrics = row.aggregate_metrics;
    return {
      label: String(row[key] ?? "—"),
      displayLabel: row.display_label ?? measurementComparisonLabels[key],
      displayValue: row.display_value ?? String(row[key] ?? "—"),
      countLabel: `${row.observation_count} observations / ${row.item_count} items`,
      metricsLabel: [
        `${metrics.views} views`,
        `${metrics.comments} comments`,
        `${formatMeasurementRate(metrics.average_completion_rate)} avg completion`,
      ].join(" / "),
      latestSignal: row.latest_observation.qualitative_signal ?? "—",
    };
  });
}
