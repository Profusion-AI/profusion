import { useSearchParams, Link } from "react-router-dom";
import { useLogs } from "../hooks/useLogs";
import LogEntry from "../components/logs/LogEntry";

export default function LogsPage() {
  const [params] = useSearchParams();
  const item_id = params.get("item_id") ?? undefined;
  const job_id = params.get("job_id") ?? undefined;

  const { data, isLoading, error } = useLogs({ item_id, job_id, limit: 50 });

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <h1 className="text-lg font-semibold text-white">Diagnostic Logs</h1>
        {item_id && (
          <span className="text-xs text-slate-400 font-mono">
            item: {item_id.slice(0, 12)}…{" "}
            <Link to="/logs" className="text-blue-400 hover:underline ml-1">
              clear
            </Link>
          </span>
        )}
        {job_id && (
          <span className="text-xs text-slate-400 font-mono">
            job: {job_id.slice(0, 12)}…{" "}
            <Link to="/logs" className="text-blue-400 hover:underline ml-1">
              clear
            </Link>
          </span>
        )}
      </div>

      {isLoading && <p className="text-slate-500 text-sm py-8 text-center">Loading…</p>}
      {error && (
        <p className="text-red-400 text-sm py-8 text-center">
          {(error as Error).message}
        </p>
      )}
      {data && data.logs.length === 0 && (
        <p className="text-slate-500 text-sm py-8 text-center">No diagnostic logs found.</p>
      )}
      {data && data.logs.map((entry) => (
        <LogEntry key={entry.path} entry={entry} />
      ))}
    </div>
  );
}
