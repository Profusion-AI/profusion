import { useState } from "react";
import { useQueue } from "../hooks/useQueue";
import QueueTable from "../components/queue/QueueTable";
import SummaryBar from "../components/queue/SummaryBar";

const ALL_STATUSES = [
  "", "idea", "planned", "scripted", "rendered", "qa_failed",
  "qa_passed", "awaiting_approval", "approved", "scheduled", "published", "measured", "archived",
];

export default function QueuePage() {
  const [status, setStatus] = useState<string>("");
  const { data, isLoading, error } = useQueue(status || undefined);

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-lg font-semibold text-white">Queue</h1>
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded px-2 py-1"
        >
          {ALL_STATUSES.map((s) => (
            <option key={s} value={s}>
              {s || "All statuses"}
            </option>
          ))}
        </select>
      </div>

      {data && <SummaryBar summary={data.summary} />}

      {isLoading && (
        <p className="text-slate-500 text-sm py-8 text-center">Loading…</p>
      )}
      {error && (
        <p className="text-red-400 text-sm py-8 text-center">
          Failed to load queue: {(error as Error).message}
        </p>
      )}
      {data && <QueueTable items={data.items} />}
    </div>
  );
}
