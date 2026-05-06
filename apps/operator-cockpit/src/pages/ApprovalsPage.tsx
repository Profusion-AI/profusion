import { useMemo } from "react";
import OperatorTable from "../components/cockpit/OperatorTable";
import { useQueue } from "../hooks/useQueue";
import { buildQueueModel, filterQueueRows } from "../domain/cockpitViewModel";

export default function ApprovalsPage() {
  const { data, isLoading, error } = useQueue();
  const model = useMemo(() => buildQueueModel(data?.items ?? []), [data?.items]);
  const awaiting = useMemo(
    () => filterQueueRows(model.rows, "Awaiting Approval", ""),
    [model.rows],
  );
  const approved = useMemo(
    () => model.rows.filter((row) => row.approval === "Approved"),
    [model.rows],
  );

  return (
    <div className="space-y-5">
      <div>
        <p className="section-label">Approvals</p>
        <h1 className="page-title mt-1">Approval Queue</h1>
        <p className="mt-1 text-sm text-[var(--cockpit-muted)]">
          Approval remains an explicit operator step. This view surfaces candidates; it does not approve them.
        </p>
      </div>
      {isLoading && <p className="py-8 text-center text-sm text-[var(--cockpit-muted)]">Loading…</p>}
      {error && <p className="py-8 text-center text-sm text-[var(--cockpit-danger)]">{(error as Error).message}</p>}
      {data && (
        <>
          <section className="space-y-2">
            <p className="section-label">Awaiting Approval — {awaiting.length}</p>
            <OperatorTable rows={awaiting} />
          </section>
          <section className="space-y-2">
            <p className="section-label">Approved — {approved.length}</p>
            <OperatorTable rows={approved} />
          </section>
        </>
      )}
    </div>
  );
}
