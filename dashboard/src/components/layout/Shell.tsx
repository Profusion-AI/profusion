import { Outlet, NavLink } from "react-router-dom";

export default function Shell() {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `px-3 py-1.5 rounded text-sm font-medium transition-colors ${
      isActive
        ? "bg-slate-800 text-white"
        : "text-slate-400 hover:text-white hover:bg-slate-700"
    }`;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 px-4 py-3 flex items-center gap-6">
        <span className="font-semibold text-sm tracking-wide text-white">
          profusion
        </span>
        <nav className="flex gap-1">
          <NavLink to="/queue" className={linkClass}>
            Queue
          </NavLink>
          <NavLink to="/logs" className={linkClass}>
            Logs
          </NavLink>
        </nav>
      </header>
      <main className="px-4 py-6 max-w-6xl mx-auto">
        <Outlet />
      </main>
    </div>
  );
}
