import { Link } from "react-router-dom";
import type { CockpitQueueRow } from "../../domain/cockpitViewModel";
import CockpitBadge from "./CockpitBadge";

export default function OperatorTable({ rows }: { rows: CockpitQueueRow[] }) {
  if (rows.length === 0) {
    return (
      <div className="cockpit-panel py-12 text-center text-sm text-[var(--cockpit-muted)]">
        No items match the current filter.
      </div>
    );
  }

  return (
    <div className="cockpit-panel overflow-x-auto">
      <table className="cockpit-table">
        <thead>
          <tr>
            <th>Item</th>
            <th>State</th>
            <th>Last Event</th>
            <th>Artifacts</th>
            <th>Approval</th>
            <th>Failure</th>
            <th>Next Safe Command</th>
            <th>Updated</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              <td>
                <Link to={`/items/${row.id}`} className="block max-w-[280px]">
                  <span className="mono block text-[11px] text-[var(--cockpit-muted)]">
                    {row.shortId}
                  </span>
                  <span className="block truncate text-[var(--cockpit-text)] hover:text-[var(--cockpit-gold)]">
                    {row.title}
                  </span>
                  <span className="mt-1 block text-[11px] text-[var(--cockpit-muted)]">
                    {row.priority} · {row.pillar} · {row.audience}
                  </span>
                </Link>
              </td>
              <td>
                <CockpitBadge tone={row.stateTone}>{row.state}</CockpitBadge>
              </td>
              <td>{row.lastEvent}</td>
              <td className="mono text-[11px]">{row.artifacts}</td>
              <td>{row.approval}</td>
              <td className={row.failure === "—" ? "text-[var(--cockpit-muted)]" : "text-[var(--cockpit-danger)]"}>
                {row.failure}
              </td>
              <td>
                <code className="block max-w-[260px] truncate text-[11px] text-[var(--cockpit-info)]">
                  {row.nextCommand}
                </code>
              </td>
              <td className="mono text-[11px]">{row.updatedAt}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
