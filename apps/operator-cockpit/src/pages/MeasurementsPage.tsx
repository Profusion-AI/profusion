import { Link } from "react-router-dom";
import CockpitBadge from "../components/cockpit/CockpitBadge";
import { useMeasurementSummary } from "../hooks/useItem";
import { formatOperatorTime } from "../domain/cockpitViewModel";
import {
  buildMeasurementComparisonRows,
  formatMeasurementRate,
  type MeasurementComparisonKey,
} from "../domain/measurementViewModel";

export default function MeasurementsPage() {
  const { data, isLoading, error } = useMeasurementSummary();

  return (
    <div className="space-y-5">
      <div>
        <p className="section-label">M8 Workflow Outcome Observations</p>
        <h1 className="page-title mt-1">Outcome Observations</h1>
      </div>

      {isLoading && <p className="py-8 text-center text-sm text-[var(--cockpit-muted)]">Loading…</p>}
      {error && <p className="py-8 text-center text-sm text-[var(--cockpit-danger)]">{(error as Error).message}</p>}

      {data && (
        <>
          <div className="cockpit-panel grid overflow-hidden sm:grid-cols-2 lg:grid-cols-5">
            <Metric label="Observations" value={String(data.observation_count)} />
            <Metric label="Observed Items" value={String(data.measured_item_count)} />
            <Metric label="Views" value={String(data.aggregate_metrics.views)} />
            <Metric label="Comments" value={String(data.aggregate_metrics.comments)} />
            <Metric
              label="Avg Completion"
              value={formatMeasurementRate(data.aggregate_metrics.average_completion_rate)}
            />
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <section className="cockpit-panel overflow-hidden">
              <div className="border-b border-[var(--cockpit-border)] px-4 py-3">
                <p className="section-label">Workflow Types</p>
              </div>
              <ListRows
                emptyLabel="No workflow outcome observations recorded."
                rows={data.platforms.map((row) => ({
                  label: row.platform,
                  count: row.count,
                }))}
              />
            </section>

            <section className="cockpit-panel overflow-hidden">
              <div className="border-b border-[var(--cockpit-border)] px-4 py-3">
                <p className="section-label">Observation Types</p>
              </div>
              <ListRows
                emptyLabel="No observation types recorded."
                rows={data.observation_types.map((row) => ({
                  label: row.observation_type,
                  count: row.count,
                }))}
              />
            </section>
          </div>

          <section className="cockpit-panel overflow-hidden">
            <div className="border-b border-[var(--cockpit-border)] px-4 py-3">
              <p className="section-label">Observed Items</p>
            </div>
            {data.items.length === 0 ? (
              <p className="px-4 py-6 text-sm text-[var(--cockpit-muted)]">
                No observed workflow items in the current snapshot.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="cockpit-table min-w-[760px]">
                  <thead>
                    <tr>
                      <th>Item</th>
                      <th>Status</th>
                      <th>Workflow Type</th>
                      <th>Type</th>
                      <th>Recorded</th>
                      <th>Signal</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.items.map((row) => (
                      <tr key={row.item_id}>
                        <td>
                          <Link to={`/items/${row.item_id}`} className="mono text-[11px] text-[var(--cockpit-info)]">
                            {row.item_id}
                          </Link>
                        </td>
                        <td>
                          <CockpitBadge tone={row.status === "measured" ? "info" : "muted"}>
                            {row.status ?? "observation only"}
                          </CockpitBadge>
                        </td>
                        <td>{row.latest_observation.platform}</td>
                        <td>{row.latest_observation.observation_type}</td>
                        <td className="mono text-[11px]">
                          {formatOperatorTime(row.latest_observation.recorded_at)}
                        </td>
                        <td className="max-w-[360px] truncate">
                          {row.latest_observation.qualitative_signal ?? "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <div className="grid gap-4 xl:grid-cols-3">
            <ComparisonPanel
              title="Scenario Variants"
              field="hook_variant"
              emptyLabel="No scenario variant dimensions recorded."
              rows={data.comparisons.hook_variants}
            />
            <ComparisonPanel
              title="Workflow Types"
              field="content_format"
              emptyLabel="No workflow type dimensions recorded."
              rows={data.comparisons.content_formats}
            />
            <ComparisonPanel
              title="Trust Domains"
              field="editorial_pillar"
              emptyLabel="No trust domain dimensions recorded."
              rows={data.comparisons.editorial_pillars}
            />
          </div>
        </>
      )}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="border-b border-r border-[var(--cockpit-border)] px-5 py-4 last:border-r-0 sm:[&:nth-last-child(-n+2)]:border-b-0 lg:border-b-0">
      <div className="mono mb-1 text-[24px] leading-none text-[var(--cockpit-info)]">{value}</div>
      <div className="text-[11px] text-[var(--cockpit-muted)]">{label}</div>
    </div>
  );
}

function ListRows({
  rows,
  emptyLabel,
}: {
  rows: Array<{ label: string; count: number }>;
  emptyLabel: string;
}) {
  if (rows.length === 0) {
    return <p className="px-4 py-6 text-sm text-[var(--cockpit-muted)]">{emptyLabel}</p>;
  }
  return (
    <div className="divide-y divide-[var(--cockpit-border-soft)]">
      {rows.map((row) => (
        <div key={row.label} className="flex items-center justify-between gap-3 px-4 py-3 text-sm">
          <span className="mono break-all text-[var(--cockpit-text)]">{row.label}</span>
          <CockpitBadge tone="info">{row.count}</CockpitBadge>
        </div>
      ))}
    </div>
  );
}

function ComparisonPanel({
  title,
  field,
  rows,
  emptyLabel,
}: {
  title: string;
  field: MeasurementComparisonKey;
  rows: Parameters<typeof buildMeasurementComparisonRows>[0];
  emptyLabel: string;
}) {
  const viewRows = buildMeasurementComparisonRows(rows, field);
  return (
    <section className="cockpit-panel overflow-hidden">
      <div className="border-b border-[var(--cockpit-border)] px-4 py-3">
        <p className="section-label">{title}</p>
      </div>
      {viewRows.length === 0 ? (
        <p className="px-4 py-6 text-sm text-[var(--cockpit-muted)]">{emptyLabel}</p>
      ) : (
        <div className="divide-y divide-[var(--cockpit-border-soft)]">
          {viewRows.map((row) => (
            <div key={row.label} className="space-y-1 px-4 py-3 text-sm">
              <div className="flex min-w-0 items-center justify-between gap-3">
                <span className="mono min-w-0 break-all text-[var(--cockpit-text)]">{row.displayValue}</span>
                <span className="shrink-0">
                  <CockpitBadge tone="info">{row.countLabel}</CockpitBadge>
                </span>
              </div>
              <p className="mono text-[11px] text-[var(--cockpit-muted)]">{row.metricsLabel}</p>
              <p className="truncate text-[12px] text-[var(--cockpit-muted)]">{row.latestSignal}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
