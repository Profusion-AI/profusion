import type { ItemPayload } from "../../api/items";

function Value({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="border-b border-slate-800/50 py-2">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <div className="mt-1 text-sm text-slate-200">{children}</div>
    </div>
  );
}

export default function HandoffTab({ data }: { data: ItemPayload }) {
  const item = data.item as Record<string, unknown>;

  return (
    <div className="grid gap-6 md:grid-cols-[1fr_1fr]">
      <section>
        <h3 className="text-sm font-medium text-slate-300 mb-2">Resume Context</h3>
        <div className="rounded border border-slate-800 px-3">
          <Value label="Item ID">
            <code className="break-all text-slate-300">{String(item.id)}</code>
          </Value>
          <Value label="Topic">{String(item.topic ?? "Untitled")}</Value>
          <Value label="Lifecycle">{data.lifecycle_state}</Value>
          <Value label="Blockage">
            {data.blockage ? (
              <span>
                {data.blockage.stage}: {data.blockage.message}
              </span>
            ) : (
              <span className="text-slate-500">No blockage reported</span>
            )}
          </Value>
          <Value label="Retry">
            {data.retry.retryable ? (
              <code className="break-all text-emerald-300">{data.retry.command}</code>
            ) : (
              <span className="text-slate-500">{data.retry.reason ?? "No retry surface"}</span>
            )}
          </Value>
          <Value label="Next safe command">
            {data.next_safe_command ? (
              <code className="break-all text-emerald-300">{data.next_safe_command}</code>
            ) : (
              <span className="text-slate-500">No command available</span>
            )}
          </Value>
        </div>
      </section>

      <section>
        <h3 className="text-sm font-medium text-slate-300 mb-2">Evidence Pointers</h3>
        <div className="rounded border border-slate-800 px-3">
          <Value label="Latest brief">
            {data.latest_brief ? "present" : <span className="text-slate-500">missing</span>}
          </Value>
          <Value label="Script variants">{data.script_variants.length}</Value>
          <Value label="Render artifacts">
            <span className="text-slate-300">
              mp4 {data.artifacts.mp4_exists ? "present" : "missing"}, manifest{" "}
              {data.artifacts.manifest_exists ? "present" : "missing"}, QA report{" "}
              {data.artifacts.qa_report_exists ? "present" : "missing"}
            </span>
          </Value>
          <Value label="Latest approval">
            {data.latest_approval ? (
              String((data.latest_approval as Record<string, unknown>).decision ?? "recorded")
            ) : (
              <span className="text-slate-500">none</span>
            )}
          </Value>
          <Value label="Recent logs">{data.recent_logs.length}</Value>
        </div>
      </section>
    </div>
  );
}
