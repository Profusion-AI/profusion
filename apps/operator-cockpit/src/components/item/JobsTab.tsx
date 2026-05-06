import StatusBadge from "../queue/StatusBadge";
import { useRetryRender, useRetryPublish } from "../../hooks/useItem";
import { describeFailureJob } from "../../domain/cockpitSignals";

function fmtDate(iso?: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString(undefined, {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

function RetryRenderBtn({ item_id, job_id }: { item_id: string; job_id: string }) {
  const m = useRetryRender(item_id, job_id);
  return (
    <button
      onClick={() => m.mutate()}
      disabled={m.isPending}
      className="px-2 py-0.5 rounded text-xs bg-slate-700 hover:bg-slate-600 disabled:opacity-50 transition-colors"
    >
      {m.isPending ? "…" : "Retry"}
    </button>
  );
}

function RetryPublishBtn({ item_id, job_id }: { item_id: string; job_id: string }) {
  const m = useRetryPublish(item_id, job_id);
  return (
    <button
      onClick={() => m.mutate()}
      disabled={m.isPending}
      className="px-2 py-0.5 rounded text-xs bg-slate-700 hover:bg-slate-600 disabled:opacity-50 transition-colors"
    >
      {m.isPending ? "…" : "Retry"}
    </button>
  );
}

interface Props {
  item_id: string;
  renderJobs: Record<string, unknown>[];
  publishJobs: Record<string, unknown>[];
}

export default function JobsTab({ item_id, renderJobs, publishJobs }: Props) {
  return (
    <div className="space-y-6">
      <section>
        <h3 className="text-sm font-medium text-slate-300 mb-2">Render Jobs</h3>
        {renderJobs.length === 0 ? (
          <p className="text-slate-500 text-sm">No render jobs yet.</p>
        ) : (
          <div className="overflow-x-auto rounded border border-slate-800">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 text-left">
                  <th className="px-3 py-2">ID</th>
                  <th className="px-3 py-2">Status</th>
                  <th className="px-3 py-2">Engine</th>
                  <th className="px-3 py-2">Failure</th>
                  <th className="px-3 py-2">Created</th>
                  <th className="px-3 py-2"></th>
                </tr>
              </thead>
              <tbody>
                {renderJobs.map((j) => {
                  const job = j as Record<string, unknown>;
                  const failure = describeFailureJob("render", job);
                  return (
                    <tr key={String(job.id)} className="border-b border-slate-800/50">
                      <td className="px-3 py-2 font-mono text-slate-400">
                        {String(job.id).slice(0, 12)}
                      </td>
                      <td className="px-3 py-2">
                        <StatusBadge status={String(job.status)} />
                      </td>
                      <td className="px-3 py-2 text-slate-400">{String(job.engine ?? "—")}</td>
                      <td className="px-3 py-2 text-slate-400">
                        {failure ? (
                          <div className="max-w-sm space-y-1">
                            <p className="text-red-300">{failure.message}</p>
                            {failure.errorCode && (
                              <p className="font-mono text-red-400">{failure.errorCode}</p>
                            )}
                            {failure.retryCommand && (
                              <code className="block break-all text-emerald-300">
                                {failure.retryCommand}
                              </code>
                            )}
                          </div>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td className="px-3 py-2 text-slate-400">
                        {fmtDate(job.created_at as string)}
                      </td>
                      <td className="px-3 py-2">
                        {job.status === "failed" && (
                          <RetryRenderBtn item_id={item_id} job_id={String(job.id)} />
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section>
        <h3 className="text-sm font-medium text-slate-300 mb-2">Publish Jobs</h3>
        {publishJobs.length === 0 ? (
          <p className="text-slate-500 text-sm">No publish jobs yet.</p>
        ) : (
          <div className="overflow-x-auto rounded border border-slate-800">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 text-left">
                  <th className="px-3 py-2">ID</th>
                  <th className="px-3 py-2">Platform</th>
                  <th className="px-3 py-2">Status</th>
                  <th className="px-3 py-2">Failure</th>
                  <th className="px-3 py-2">Scheduled</th>
                  <th className="px-3 py-2"></th>
                </tr>
              </thead>
              <tbody>
                {publishJobs.map((j) => {
                  const job = j as Record<string, unknown>;
                  const failure = describeFailureJob("publish", job);
                  return (
                    <tr key={String(job.id)} className="border-b border-slate-800/50">
                      <td className="px-3 py-2 font-mono text-slate-400">
                        {String(job.id).slice(0, 12)}
                      </td>
                      <td className="px-3 py-2 text-slate-300">{String(job.platform ?? "—")}</td>
                      <td className="px-3 py-2">
                        <StatusBadge status={String(job.status)} />
                      </td>
                      <td className="px-3 py-2 text-slate-400">
                        {failure ? (
                          <div className="max-w-sm space-y-1">
                            <p className="text-red-300">{failure.message}</p>
                            {failure.errorCode && (
                              <p className="font-mono text-red-400">{failure.errorCode}</p>
                            )}
                            {failure.retryCommand && (
                              <code className="block break-all text-emerald-300">
                                {failure.retryCommand}
                              </code>
                            )}
                          </div>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td className="px-3 py-2 text-slate-400">
                        {fmtDate(job.scheduled_for as string | null)}
                      </td>
                      <td className="px-3 py-2">
                        {job.status === "failed" && (
                          <RetryPublishBtn item_id={item_id} job_id={String(job.id)} />
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
