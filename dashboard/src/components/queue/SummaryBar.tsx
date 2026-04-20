import type { QueueSummaryRow } from "../../api/queue";
import StatusBadge from "./StatusBadge";

export default function SummaryBar({ summary }: { summary: QueueSummaryRow[] }) {
  const nonEmpty = summary.filter((r) => r.count > 0);
  if (nonEmpty.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-2 mb-4">
      {nonEmpty.map((row) => (
        <span key={row.status} className="flex items-center gap-1.5">
          <StatusBadge status={row.status} />
          <span className="text-xs text-slate-400 tabular-nums">{row.count}</span>
        </span>
      ))}
    </div>
  );
}
