import { Link } from "react-router-dom";
import type { LogEntry } from "../../api/items";

function fmtBytes(n: number) {
  if (n < 1024) return `${n} B`;
  return `${(n / 1024).toFixed(1)} KB`;
}

export default function LogsPanel({ logs, item_id }: { logs: LogEntry[]; item_id: string }) {
  return (
    <div>
      {logs.length === 0 ? (
        <p className="text-slate-500 text-sm">No diagnostic logs.</p>
      ) : (
        <div className="space-y-1">
          {logs.map((entry) => (
            <div
              key={entry.path}
              className="flex items-center justify-between py-1.5 border-b border-slate-800/50"
            >
              <span className="text-xs font-mono text-slate-300 truncate max-w-xs">
                {entry.name}
              </span>
              <span className="text-xs text-slate-500 shrink-0 ml-4">{fmtBytes(entry.size_bytes)}</span>
            </div>
          ))}
        </div>
      )}
      <Link
        to={`/logs?item_id=${item_id}`}
        className="inline-block mt-3 text-xs text-blue-400 hover:text-blue-300 hover:underline"
      >
        View all logs →
      </Link>
    </div>
  );
}
