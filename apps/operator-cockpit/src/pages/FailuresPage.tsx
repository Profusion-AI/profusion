import { useMemo } from "react";
import MetricStrip from "../components/cockpit/MetricStrip";
import OperatorTable from "../components/cockpit/OperatorTable";
import { useQueue } from "../hooks/useQueue";
import { buildQueueModel, filterQueueRows } from "../domain/cockpitViewModel";

export default function FailuresPage() {
  const { data, isLoading, error } = useQueue();
  const model = useMemo(() => buildQueueModel(data?.items ?? []), [data?.items]);
  const rows = useMemo(() => filterQueueRows(model.rows, "Failed / Blocked", ""), [model.rows]);

  return (
    <div className="space-y-5">
      <div>
        <p className="section-label">Failures</p>
        <h1 className="page-title mt-1">Blocked and Failed Items</h1>
        <p className="mt-1 text-sm text-[var(--cockpit-muted)]">
          Items that need operator review before the pipeline moves forward.
        </p>
      </div>
      <MetricStrip metrics={model.metrics} />
      {isLoading && <p className="py-8 text-center text-sm text-[var(--cockpit-muted)]">Loading…</p>}
      {error && <p className="py-8 text-center text-sm text-[var(--cockpit-danger)]">{(error as Error).message}</p>}
      {data && <OperatorTable rows={rows} />}
    </div>
  );
}
