import { Link } from "react-router-dom";
import type { ContentItem } from "../../api/queue";
import StatusBadge from "./StatusBadge";

function fmtDate(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function QueueTable({ items }: { items: ContentItem[] }) {
  if (items.length === 0) {
    return (
      <p className="text-slate-500 text-sm py-8 text-center">
        No items found.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto rounded border border-slate-800">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-800 text-slate-400 text-left">
            <th className="px-3 py-2 font-medium">Topic</th>
            <th className="px-3 py-2 font-medium">Status</th>
            <th className="px-3 py-2 font-medium hidden sm:table-cell">Pillar</th>
            <th className="px-3 py-2 font-medium hidden md:table-cell">Priority</th>
            <th className="px-3 py-2 font-medium hidden lg:table-cell">Created</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr
              key={item.id}
              className="border-b border-slate-800/50 hover:bg-slate-800/40 transition-colors"
            >
              <td className="px-3 py-2">
                <Link
                  to={`/items/${item.id}`}
                  className="text-blue-400 hover:text-blue-300 hover:underline"
                >
                  {item.topic}
                </Link>
              </td>
              <td className="px-3 py-2">
                <StatusBadge status={item.status} />
              </td>
              <td className="px-3 py-2 text-slate-400 hidden sm:table-cell">
                {item.pillar ?? "—"}
              </td>
              <td className="px-3 py-2 text-slate-400 tabular-nums hidden md:table-cell">
                {item.priority}
              </td>
              <td className="px-3 py-2 text-slate-400 text-xs hidden lg:table-cell">
                {fmtDate(item.created_at)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
