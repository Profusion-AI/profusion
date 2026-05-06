import { useMemo } from "react";
import { Link } from "react-router-dom";
import CockpitBadge from "../components/cockpit/CockpitBadge";
import { useQueue } from "../hooks/useQueue";
import { useItemReceipts } from "../hooks/useItem";
import { getCommandPresentation, getReceiptLifecyclePresentation } from "../domain/cockpitSignals";
import { buildQueueModel, filterQueueRows, formatOperatorTime, type CockpitQueueRow } from "../domain/cockpitViewModel";

export default function EvidencePage() {
  const { data, isLoading, error } = useQueue();
  const model = useMemo(() => buildQueueModel(data?.items ?? []), [data?.items]);
  const rows = useMemo(() => filterQueueRows(model.rows, "Receipts", ""), [model.rows]);

  return (
    <div className="space-y-5">
      <div>
        <p className="section-label">Evidence</p>
        <h1 className="page-title mt-1">Artifacts and Receipt Readiness</h1>
        <p className="mt-1 text-sm text-[var(--cockpit-muted)]">
          Receipt packets are file-first reviewer artifacts. Draft generation remains a terminal command.
        </p>
      </div>
      {isLoading && <p className="py-8 text-center text-sm text-[var(--cockpit-muted)]">Loading…</p>}
      {error && <p className="py-8 text-center text-sm text-[var(--cockpit-danger)]">{(error as Error).message}</p>}
      {data && (
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {rows.length === 0 && (
            <div className="cockpit-panel p-5 text-sm text-[var(--cockpit-muted)]">
              No artifact-ready items in the current snapshot.
            </div>
          )}
          {rows.map((row) => <EvidenceCard key={row.id} row={row} />)}
        </div>
      )}
    </div>
  );
}

function EvidenceCard({ row }: { row: CockpitQueueRow }) {
  const { data, isLoading, error } = useItemReceipts(row.id);
  const draftCommand = getCommandPresentation(`uv run profusion receipt draft --item-id ${row.id}`);
  const latestReceipt = data?.receipts[0] ?? null;
  const lifecycle = latestReceipt ? getReceiptLifecyclePresentation(latestReceipt) : null;
  const nextLifecycleCommand = lifecycle?.nextCommand ? getCommandPresentation(lifecycle.nextCommand) : null;

  return (
    <div className="cockpit-panel p-4">
      <div className="mb-3 flex items-start justify-between gap-3">
        <div>
          <p className="mono text-[11px] text-[var(--cockpit-muted)]">{row.shortId}</p>
          <h2 className="mt-1 text-sm font-semibold text-[var(--cockpit-text)]">{row.title}</h2>
        </div>
        <CockpitBadge tone={latestReceipt ? "success" : row.stateTone}>
          {lifecycle ? lifecycle.badgeLabel : row.state}
        </CockpitBadge>
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs text-[var(--cockpit-text-2)]">
        <span>Artifacts</span>
        <span className="mono text-right">{row.artifacts}</span>
        <span>Approval</span>
        <span className="text-right">{row.approval}</span>
        <span>Receipts</span>
        <span className="mono text-right">
          {isLoading ? "…" : error ? "error" : String(data?.receipt_count ?? 0)}
        </span>
        <span>Latest</span>
        <span className="mono text-right">{formatOperatorTime(latestReceipt?.created_at)}</span>
      </div>

      {latestReceipt ? (
        <div className="mt-3 rounded border border-[var(--cockpit-border-soft)] bg-[var(--cockpit-row)] p-3 text-xs">
          <div className="mb-1 flex items-center justify-between gap-2">
            <span className="section-label">Packet</span>
            <CockpitBadge tone="info">{lifecycle?.statusLabel ?? latestReceipt.receipt_status}</CockpitBadge>
          </div>
          <code className="block break-all text-[var(--cockpit-info)]">{latestReceipt.packet_dir}</code>
          {nextLifecycleCommand && (
            <div className="mt-3 border-t border-[var(--cockpit-border-soft)] pt-3">
              <div className="mb-1 flex items-center gap-2">
                <span className="section-label">Next Receipt Command</span>
                {nextLifecycleCommand.isMutation && (
                  <span className="rounded-full border border-[rgba(245,201,107,0.30)] bg-[var(--cockpit-warning-soft)] px-2 py-0.5 text-[10px] text-[var(--cockpit-warning)]">
                    terminal only
                  </span>
                )}
              </div>
              <code className="block break-all text-[var(--cockpit-info)]">{nextLifecycleCommand.command}</code>
            </div>
          )}
        </div>
      ) : (
        <div className="mt-3 rounded border border-[var(--cockpit-border-soft)] bg-[var(--cockpit-row)] p-3 text-xs">
          <div className="mb-2 flex items-center gap-2">
            <span className="section-label">Draft Command</span>
            {draftCommand.isMutation && (
              <span className="rounded-full border border-[rgba(245,201,107,0.30)] bg-[var(--cockpit-warning-soft)] px-2 py-0.5 text-[10px] text-[var(--cockpit-warning)]">
                terminal only
              </span>
            )}
          </div>
          <code className="block break-all text-[var(--cockpit-info)]">{draftCommand.command}</code>
        </div>
      )}

      <Link
        to={`/items/${row.id}`}
        className="mt-3 inline-flex text-xs font-medium text-[var(--cockpit-gold)] hover:text-[var(--cockpit-text)]"
      >
        Open item
      </Link>
    </div>
  );
}
