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
        <p className="text-sm text-[var(--cockpit-muted)]">No diagnostic logs.</p>
      ) : (
        <div className="space-y-1">
          {logs.map((entry) => (
            <div
              key={entry.path}
              className="flex items-center justify-between border-b border-[var(--cockpit-border-soft)] py-1.5"
            >
              <span className="mono max-w-xs truncate text-xs text-[var(--cockpit-text-2)]">
                {entry.name}
              </span>
              <span className="ml-4 shrink-0 text-xs text-[var(--cockpit-muted)]">{fmtBytes(entry.size_bytes)}</span>
            </div>
          ))}
        </div>
      )}
      <Link
        to={`/logs?item_id=${item_id}`}
        className="mt-3 inline-block text-xs text-[var(--cockpit-info)] hover:underline"
      >
        View all logs →
      </Link>
    </div>
  );
}
