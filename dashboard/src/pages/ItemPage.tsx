import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  useItem,
  useItemJobs,
  useItemRenders,
  useItemApprovals,
  useRetryQa,
} from "../hooks/useItem";
import StatusBadge from "../components/queue/StatusBadge";
import BlockageCallout from "../components/item/BlockageCallout";
import NextSafeCommand from "../components/item/NextSafeCommand";
import JobsTab from "../components/item/JobsTab";
import ArtifactsTab from "../components/item/ArtifactsTab";
import ApprovalsTab from "../components/item/ApprovalsTab";
import LogsPanel from "../components/item/LogsPanel";

type Tab = "jobs" | "artifacts" | "approvals" | "logs";

export default function ItemPage() {
  const { id } = useParams<{ id: string }>();
  const [tab, setTab] = useState<Tab>("jobs");

  const { data, isLoading, error } = useItem(id!);
  const jobsQ = useItemJobs(id!);
  const rendersQ = useItemRenders(id!);
  const approvalsQ = useItemApprovals(id!);
  const retryQa = useRetryQa(id!);

  if (isLoading) {
    return <p className="text-slate-500 text-sm py-12 text-center">Loading…</p>;
  }
  if (error) {
    return (
      <div className="py-12 text-center">
        <p className="text-red-400 text-sm mb-2">{(error as Error).message}</p>
        <Link to="/queue" className="text-blue-400 text-sm hover:underline">
          ← Back to queue
        </Link>
      </div>
    );
  }
  if (!data) return null;

  const item = data.item as Record<string, unknown>;

  const tabs: { key: Tab; label: string }[] = [
    { key: "jobs", label: "Jobs" },
    { key: "artifacts", label: "Artifacts" },
    { key: "approvals", label: "Approvals" },
    { key: "logs", label: "Logs" },
  ];

  return (
    <div>
      <div className="mb-4">
        <Link to="/queue" className="text-slate-500 text-xs hover:text-slate-300">
          ← Queue
        </Link>
      </div>

      <div className="mb-6">
        <div className="flex items-start gap-3 mb-2">
          <h1 className="text-lg font-semibold text-white flex-1">
            {String(item.topic)}
          </h1>
          <StatusBadge status={String(item.status)} />
        </div>
        <p className="text-slate-400 text-sm font-mono">{data.lifecycle_state}</p>
      </div>

      {data.blockage && (
        <BlockageCallout
          blockage={data.blockage}
          retry={data.retry}
          item_id={id!}
          onRetryQa={() => retryQa.mutate()}
          retryPending={retryQa.isPending}
        />
      )}

      {data.next_safe_command && !data.blockage && (
        <NextSafeCommand command={data.next_safe_command} />
      )}

      {data.next_safe_command && data.blockage && data.retry.retryable === false && (
        <NextSafeCommand command={data.next_safe_command} />
      )}

      <div className="border-b border-slate-800 mb-4">
        <nav className="flex gap-1">
          {tabs.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={`px-3 py-2 text-sm border-b-2 transition-colors ${
                tab === key
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              {label}
            </button>
          ))}
        </nav>
      </div>

      <div>
        {tab === "jobs" && (
          jobsQ.data ? (
            <JobsTab
              item_id={id!}
              renderJobs={jobsQ.data.render_jobs as Record<string, unknown>[]}
              publishJobs={jobsQ.data.publish_jobs as Record<string, unknown>[]}
            />
          ) : jobsQ.isLoading ? (
            <p className="text-slate-500 text-sm">Loading…</p>
          ) : null
        )}

        {tab === "artifacts" && (
          rendersQ.data ? (
            <ArtifactsTab artifacts={rendersQ.data.artifacts} />
          ) : rendersQ.isLoading ? (
            <p className="text-slate-500 text-sm">Loading…</p>
          ) : (
            <p className="text-slate-500 text-sm">No render data.</p>
          )
        )}

        {tab === "approvals" && (
          approvalsQ.data ? (
            <ApprovalsTab data={approvalsQ.data} />
          ) : approvalsQ.isLoading ? (
            <p className="text-slate-500 text-sm">Loading…</p>
          ) : null
        )}

        {tab === "logs" && (
          <LogsPanel logs={data.recent_logs} item_id={id!} />
        )}
      </div>
    </div>
  );
}
