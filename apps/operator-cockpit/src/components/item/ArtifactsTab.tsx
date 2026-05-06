import type { Artifacts } from "../../api/items";

function Flag({ label, exists, path }: { label: string; exists: boolean; path?: string | null }) {
  return (
    <div className="flex items-start gap-3 py-2 border-b border-slate-800/50">
      <span
        className={`mt-0.5 text-xs font-bold ${exists ? "text-emerald-400" : "text-slate-600"}`}
      >
        {exists ? "✓" : "✗"}
      </span>
      <div>
        <span className="text-sm text-slate-200">{label}</span>
        {path && (
          <p className="text-xs font-mono text-slate-500 mt-0.5 break-all">{path}</p>
        )}
      </div>
    </div>
  );
}

export default function ArtifactsTab({ artifacts }: { artifacts: Artifacts }) {
  return (
    <div className="divide-y divide-slate-800/50">
      <Flag
        label="MP4 video"
        exists={artifacts.mp4_exists}
        path={artifacts.mp4_path}
      />
      <Flag
        label="manifest.json"
        exists={artifacts.manifest_exists}
      />
      <Flag
        label="qa_report.json"
        exists={artifacts.qa_report_exists}
      />
    </div>
  );
}
