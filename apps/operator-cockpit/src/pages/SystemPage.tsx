import { useMemo } from "react";
import CommandBlock from "../components/cockpit/CommandBlock";
import MetricStrip from "../components/cockpit/MetricStrip";
import { useQueue } from "../hooks/useQueue";
import { buildQueueModel } from "../domain/cockpitViewModel";
import { getCommandPresentation } from "../domain/cockpitSignals";

export default function SystemPage() {
  const { data, isLoading, error } = useQueue();
  const model = useMemo(() => buildQueueModel(data?.items ?? []), [data?.items]);

  return (
    <div className="space-y-5">
      <div>
        <p className="section-label">System</p>
        <h1 className="page-title mt-1">Preview Boundary</h1>
        <p className="mt-1 text-sm text-[var(--cockpit-muted)]">
          This Netlify draft is static. It consumes generated JSON snapshots and does not run FastAPI or SQLite.
        </p>
      </div>
      <MetricStrip metrics={model.metrics} />
      {isLoading && <p className="py-8 text-center text-sm text-[var(--cockpit-muted)]">Loading…</p>}
      {error && <p className="py-8 text-center text-sm text-[var(--cockpit-danger)]">{(error as Error).message}</p>}
      <div className="grid gap-4 lg:grid-cols-[1fr_1fr]">
        <section className="cockpit-panel p-4">
          <p className="section-label mb-3">Contracts</p>
          <div className="space-y-3 text-sm text-[var(--cockpit-text-2)]">
            <p>Queue: <code className="text-[var(--cockpit-info)]">/api/queue</code></p>
            <p>Logs: <code className="text-[var(--cockpit-info)]">/api/logs</code></p>
            <p>Item detail: <code className="text-[var(--cockpit-info)]">/api/items/:id</code></p>
            <p>Item jobs, renders, and approvals stay under the existing item read-model routes.</p>
          </div>
        </section>
        <CommandBlock
          title="Regenerate static snapshot"
          presentation={getCommandPresentation("cd apps/operator-cockpit && corepack pnpm build:netlify")}
        />
      </div>
    </div>
  );
}
