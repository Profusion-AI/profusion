import type { ApprovalsPayload } from "../../api/items";
import StatusBadge from "../queue/StatusBadge";

function fmtDate(iso?: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString(undefined, {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

export default function ApprovalsTab({ data }: { data: ApprovalsPayload }) {
  return (
    <div className="space-y-4">
      <div className="flex gap-4 text-sm">
        <span className="text-slate-400">Effective decision:</span>
        <span>
          {data.effective_decision ? (
            <StatusBadge status={data.effective_decision} />
          ) : (
            <span className="text-slate-500">none</span>
          )}
        </span>
        <span className="text-slate-400 ml-auto">
          Eligible for publish:{" "}
          <span className={data.eligible_for_publish ? "text-emerald-400" : "text-slate-500"}>
            {data.eligible_for_publish ? "yes" : "no"}
          </span>
        </span>
      </div>

      {data.approval_records.length === 0 ? (
        <p className="text-slate-500 text-sm">No approval records yet.</p>
      ) : (
        <div className="overflow-x-auto rounded border border-slate-800">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-left">
                <th className="px-3 py-2">Decision</th>
                <th className="px-3 py-2">Notes</th>
                <th className="px-3 py-2">At</th>
              </tr>
            </thead>
            <tbody>
              {data.approval_records.map((r, i) => {
                const rec = r as Record<string, unknown>;
                return (
                  <tr key={i} className="border-b border-slate-800/50">
                    <td className="px-3 py-2">
                      <StatusBadge status={String(rec.decision)} />
                    </td>
                    <td className="px-3 py-2 text-slate-400 max-w-xs truncate">
                      {String(rec.notes ?? "—")}
                    </td>
                    <td className="px-3 py-2 text-slate-400">
                      {fmtDate(rec.timestamp as string | null)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
