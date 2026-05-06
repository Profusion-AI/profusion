import type { LogEntry as LogEntryType } from "../../api/items";

function fmtBytes(n: number) {
  if (n < 1024) return `${n} B`;
  return `${(n / 1024).toFixed(1)} KB`;
}

function fmtDate(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

export default function LogEntry({ entry }: { entry: LogEntryType }) {
  return (
    <div className="flex items-center justify-between border-b border-[var(--cockpit-border-soft)] px-4 py-3 group">
      <span className="mono max-w-lg truncate text-xs text-[var(--cockpit-text-2)]">{entry.name}</span>
      <div className="ml-4 flex shrink-0 items-center gap-4">
        <span className="text-xs text-[var(--cockpit-muted)]">{fmtBytes(entry.size_bytes)}</span>
        <span className="mono text-xs text-[var(--cockpit-muted)]">{fmtDate(entry.modified_at)}</span>
      </div>
    </div>
  );
}
