import { clsx } from "clsx";

const STATUS_COLORS: Record<string, string> = {
  idea: "bg-slate-700 text-slate-200",
  planned: "bg-blue-900 text-blue-200",
  scripted: "bg-violet-900 text-violet-200",
  rendered: "bg-indigo-900 text-indigo-200",
  qa_failed: "bg-red-900 text-red-300",
  qa_passed: "bg-green-900 text-green-200",
  awaiting_approval: "bg-yellow-900 text-yellow-200",
  approved: "bg-emerald-900 text-emerald-200",
  scheduled: "bg-cyan-900 text-cyan-200",
  published: "bg-teal-900 text-teal-200",
  measured: "bg-pink-900 text-pink-200",
  archived: "bg-slate-800 text-slate-400",
};

export default function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={clsx(
        "inline-block px-2 py-0.5 rounded text-xs font-mono",
        STATUS_COLORS[status] ?? "bg-slate-700 text-slate-200"
      )}
    >
      {status}
    </span>
  );
}
