import { useParams, Link } from "react-router-dom";
import {
  useItem,
  useItemJobs,
  useItemRenders,
  useItemApprovals,
} from "../hooks/useItem";
import LogsPanel from "../components/item/LogsPanel";
import CockpitBadge from "../components/cockpit/CockpitBadge";
import CommandBlock from "../components/cockpit/CommandBlock";
import { buildItemModel, labelStatus, toneForStatus, type CockpitFact } from "../domain/cockpitViewModel";
import { describeFailureJob, getCommandPresentation } from "../domain/cockpitSignals";

function FactList({ facts }: { facts: CockpitFact[] }) {
  return (
    <div className="divide-y divide-[var(--cockpit-border-soft)]">
      {facts.map((fact) => (
        <div key={fact.label} className="grid grid-cols-[140px_1fr] gap-3 py-2 text-sm">
          <span className="section-label">{fact.label}</span>
          <span className={`tone-${fact.tone}`}>{fact.value}</span>
        </div>
      ))}
    </div>
  );
}

function JobTable({
  title,
  jobs,
  stage,
}: {
  title: string;
  jobs: Record<string, unknown>[];
  stage: "render" | "publish";
}) {
  return (
    <section className="cockpit-panel overflow-hidden">
      <div className="border-b border-[var(--cockpit-border)] px-4 py-3">
        <p className="section-label">{title} — {jobs.length}</p>
      </div>
      {jobs.length === 0 ? (
        <p className="px-4 py-5 text-sm text-[var(--cockpit-muted)]">No {stage} jobs yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="cockpit-table min-w-[720px]">
            <thead>
              <tr>
                <th>ID</th>
                <th>Status</th>
                <th>Target</th>
                <th>Failure</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((job) => {
                const failure = describeFailureJob(stage, job);
                return (
                  <tr key={String(job.id)}>
                    <td className="mono text-[11px]">{String(job.id ?? "—").slice(0, 14)}</td>
                    <td>
                      <CockpitBadge tone={toneForStatus(String(job.status ?? ""))}>
                        {labelStatus(String(job.status ?? "unknown"))}
                      </CockpitBadge>
                    </td>
                    <td>{String(job.engine ?? job.platform ?? "—")}</td>
                    <td className={failure ? "text-[var(--cockpit-danger)]" : "text-[var(--cockpit-muted)]"}>
                      {failure?.message ?? "—"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default function ItemPage() {
  const { id } = useParams<{ id: string }>();

  const { data, isLoading, error } = useItem(id!);
  const jobsQ = useItemJobs(id!);
  const rendersQ = useItemRenders(id!);
  const approvalsQ = useItemApprovals(id!);

  if (isLoading) {
    return <p className="py-12 text-center text-sm text-[var(--cockpit-muted)]">Loading…</p>;
  }
  if (error) {
    return (
      <div className="py-12 text-center">
        <p className="mb-2 text-sm text-[var(--cockpit-danger)]">{(error as Error).message}</p>
        <Link to="/queue" className="text-sm text-[var(--cockpit-info)] hover:underline">
          ← Back to queue
        </Link>
      </div>
    );
  }
  if (!data) return null;

  const model = buildItemModel(data);
  const renderJobs = (jobsQ.data?.render_jobs ?? []) as Record<string, unknown>[];
  const publishJobs = (jobsQ.data?.publish_jobs ?? []) as Record<string, unknown>[];
  const retryCommand = data.retry.retryable && data.retry.command
    ? getCommandPresentation(data.retry.command)
    : null;

  return (
    <div className="space-y-5">
      <div>
        <Link to="/queue" className="text-xs text-[var(--cockpit-muted)] hover:text-[var(--cockpit-text-2)]">
          ← Queue
        </Link>
      </div>

      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-start">
        <div>
          <p className="section-label">Item Detail</p>
          <div className="mt-1 flex flex-wrap items-center gap-3">
            <h1 className="page-title">{model.title}</h1>
            <CockpitBadge tone={model.stateTone}>{model.lifecycle}</CockpitBadge>
          </div>
          <p className="mono mt-2 text-xs text-[var(--cockpit-muted)]">{model.id}</p>
        </div>
        <div className="mono text-xs text-[var(--cockpit-muted)]">updated {model.updatedAt}</div>
      </div>

      {data.blockage && (
        <div className="cockpit-panel border-[rgba(248,113,113,0.35)] bg-[var(--cockpit-danger-soft)] p-4">
          <p className="section-label text-[var(--cockpit-danger)]">Blocked at {data.blockage.stage}</p>
          <p className="mt-2 text-sm text-[var(--cockpit-text)]">{data.blockage.message}</p>
          {data.blockage.error_code && (
            <p className="mono mt-1 text-xs text-[var(--cockpit-danger)]">{data.blockage.error_code}</p>
          )}
        </div>
      )}

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1.4fr)_minmax(320px,0.6fr)]">
        <div className="space-y-4">
          <JobTable title="Render Jobs" jobs={renderJobs} stage="render" />
          <JobTable title="Publish Jobs" jobs={publishJobs} stage="publish" />
          <section className="cockpit-panel p-4">
            <p className="section-label mb-3">Logs</p>
            <LogsPanel logs={data.recent_logs} item_id={id!} />
          </section>
        </div>
        <div className="space-y-4">
          {retryCommand && <CommandBlock title="Retry command" presentation={retryCommand} />}
          {model.command && <CommandBlock presentation={model.command} />}
          <section className="cockpit-panel p-4">
            <p className="section-label mb-3">Evidence</p>
            <FactList facts={model.evidence} />
          </section>
          <section className="cockpit-panel p-4">
            <p className="section-label mb-3">Context</p>
            <FactList facts={model.context} />
          </section>
          <section className="cockpit-panel p-4">
            <p className="section-label mb-3">Approvals</p>
            {approvalsQ.isLoading && <p className="text-sm text-[var(--cockpit-muted)]">Loading…</p>}
            {approvalsQ.data && (
              <FactList
                facts={[
                  {
                    label: "Decision",
                    value: approvalsQ.data.effective_decision ?? "None",
                    tone: approvalsQ.data.effective_decision ? "success" : "muted",
                  },
                  {
                    label: "Eligible",
                    value: approvalsQ.data.eligible_for_publish ? "Yes" : "No",
                    tone: approvalsQ.data.eligible_for_publish ? "success" : "muted",
                  },
                  {
                    label: "Records",
                    value: String(approvalsQ.data.approval_records.length),
                    tone: approvalsQ.data.approval_records.length > 0 ? "info" : "muted",
                  },
                ]}
              />
            )}
          </section>
          <section className="cockpit-panel p-4">
            <p className="section-label mb-3">Artifacts</p>
            {rendersQ.isLoading && <p className="text-sm text-[var(--cockpit-muted)]">Loading…</p>}
            {rendersQ.data && (
              <FactList
                facts={[
                  { label: "MP4", value: rendersQ.data.artifacts.mp4_exists ? "Present" : "Missing", tone: rendersQ.data.artifacts.mp4_exists ? "success" : "muted" },
                  { label: "Manifest", value: rendersQ.data.artifacts.manifest_exists ? "Present" : "Missing", tone: rendersQ.data.artifacts.manifest_exists ? "success" : "muted" },
                  { label: "QA Report", value: rendersQ.data.artifacts.qa_report_exists ? "Present" : "Missing", tone: rendersQ.data.artifacts.qa_report_exists ? "success" : "muted" },
                ]}
              />
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
