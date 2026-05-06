import { Search } from "lucide-react";
import { useMemo, useState } from "react";
import { useQueue } from "../hooks/useQueue";
import MetricStrip from "../components/cockpit/MetricStrip";
import OperatorTable from "../components/cockpit/OperatorTable";
import {
  buildQueueModel,
  filterQueueRows,
  QUEUE_FILTERS,
  type QueueFilter,
} from "../domain/cockpitViewModel";

export default function QueuePage() {
  const [filter, setFilter] = useState<QueueFilter>("All");
  const [search, setSearch] = useState("");
  const { data, isLoading, error } = useQueue();

  const model = useMemo(() => buildQueueModel(data?.items ?? []), [data?.items]);
  const rows = useMemo(
    () => filterQueueRows(model.rows, filter, search),
    [model.rows, filter, search],
  );

  return (
    <div className="space-y-5">
      <div className="flex flex-col justify-between gap-3 lg:flex-row lg:items-end">
        <div>
          <p className="section-label">Queue</p>
          <h1 className="page-title mt-1">Operator Workbench</h1>
          <p className="mt-1 text-sm text-[var(--cockpit-muted)]">
            Review queue state and evidence.
          </p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <label className="relative">
            <Search
              size={14}
              className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--cockpit-muted)]"
            />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              className="cockpit-input w-full pl-8 sm:w-[260px]"
              placeholder="Search topic, id, pillar"
            />
          </label>
          <select
            value={filter}
            onChange={(event) => setFilter(event.target.value as QueueFilter)}
            className="cockpit-select"
          >
            {QUEUE_FILTERS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>
      </div>

      <MetricStrip metrics={model.metrics} />

      {isLoading && (
        <p className="py-8 text-center text-sm text-[var(--cockpit-muted)]">Loading…</p>
      )}
      {error && (
        <p className="py-8 text-center text-sm text-[var(--cockpit-danger)]">
          Failed to load queue: {(error as Error).message}
        </p>
      )}
      {data && <OperatorTable rows={rows} />}
    </div>
  );
}
