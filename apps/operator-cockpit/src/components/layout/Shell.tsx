import { Outlet, NavLink } from "react-router-dom";
import {
  AlertTriangle,
  CheckCircle2,
  Cpu,
  FileArchive,
  ListTodo,
  ScrollText,
  ShieldCheck,
} from "lucide-react";

export default function Shell() {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `rail-link ${isActive ? "active" : ""}`;

  const navItems = [
    { to: "/queue", label: "Queue", icon: ListTodo },
    { to: "/failures", label: "Failures", icon: AlertTriangle },
    { to: "/approvals", label: "Approvals", icon: CheckCircle2 },
    { to: "/evidence", label: "Evidence", icon: FileArchive },
    { to: "/logs", label: "Logs", icon: ScrollText },
    { to: "/system", label: "System", icon: Cpu },
  ];

  return (
    <div className="cockpit-shell">
      <nav className="cockpit-rail" aria-label="Operator cockpit">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} className={linkClass} title={label} aria-label={label}>
            <Icon size={18} strokeWidth={1.8} />
          </NavLink>
        ))}
      </nav>
      <main className="cockpit-main">
        <header className="cockpit-topbar">
          <div>
            <div className="flex items-center gap-2">
              <ShieldCheck size={17} className="text-[var(--cockpit-gold)]" />
              <span className="page-title">Profusion Operator Cockpit</span>
            </div>
            <p className="mt-1 hidden text-xs text-[var(--cockpit-muted)] sm:block">
              Internal M7 surface over FastAPI read models and static Netlify snapshots
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2 text-[10px] uppercase tracking-[0.08em] text-[var(--cockpit-muted)]">
            <span className="rounded-full border border-[var(--cockpit-border)] px-2 py-1">
              M7 cockpit
            </span>
            <span className="rounded-full border border-[var(--cockpit-border)] px-2 py-1">
              read-only preview
            </span>
            <span className="rounded-full border border-[var(--cockpit-border)] px-2 py-1">
              terminal commands
            </span>
          </div>
        </header>
        <div className="cockpit-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
