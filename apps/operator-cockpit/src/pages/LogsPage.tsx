import { useSearchParams, Link } from "react-router-dom";
import { useLogs } from "../hooks/useLogs";
import LogEntry from "../components/logs/LogEntry";

export default function LogsPage() {
  const [params] = useSearchParams();
  const item_id = params.get("item_id") ?? undefined;
  const job_id = params.get("job_id") ?? undefined;

  const { data, isLoading, error } = useLogs({ item_id, job_id, limit: 50 });

  return (
    <div className="space-y-5">
      <div>
        <p className="section-label">Logs</p>
        <h1 className="page-title mt-1">Diagnostic Logs</h1>
        <p className="mt-1 text-sm text-[var(--cockpit-muted)]">
          Read-only pointers into generated log metadata for the current snapshot.
        </p>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        {item_id && (
          <span className="mono text-xs text-[var(--cockpit-muted)]">
            item: {item_id.slice(0, 12)}…{" "}
            <Link to="/logs" className="ml-1 text-[var(--cockpit-info)] hover:underline">
              clear
            </Link>
          </span>
        )}
        {job_id && (
          <span className="mono text-xs text-[var(--cockpit-muted)]">
            job: {job_id.slice(0, 12)}…{" "}
            <Link to="/logs" className="ml-1 text-[var(--cockpit-info)] hover:underline">
              clear
            </Link>
          </span>
        )}
      </div>

      {isLoading && <p className="py-8 text-center text-sm text-[var(--cockpit-muted)]">Loading…</p>}
      {error && (
        <p className="py-8 text-center text-sm text-[var(--cockpit-danger)]">
          {(error as Error).message}
        </p>
      )}
      {data && data.logs.length === 0 && (
        <div className="cockpit-panel py-12 text-center text-sm text-[var(--cockpit-muted)]">
          No diagnostic logs found.
        </div>
      )}
      {data && data.logs.length > 0 && (
        <div className="cockpit-panel overflow-hidden">
          {data.logs.map((entry) => (
            <LogEntry key={entry.path} entry={entry} />
          ))}
        </div>
      )}
    </div>
  );
}
