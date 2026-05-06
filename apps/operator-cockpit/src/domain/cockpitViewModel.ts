import type { ItemPayload } from "../api/items";
import type { ContentItem } from "../api/queue";
import {
  getCommandPresentation,
  type CommandPresentation,
} from "./cockpitSignals";

export type CockpitTone = "neutral" | "info" | "success" | "warning" | "danger" | "muted";

export type CockpitMetric = {
  label: string;
  value: number;
  tone: CockpitTone;
};

export type CockpitQueueRow = {
  id: string;
  shortId: string;
  title: string;
  state: string;
  stateTone: CockpitTone;
  lastEvent: string;
  artifacts: string;
  approval: string;
  failure: string;
  nextCommand: string;
  updatedAt: string;
  priority: string;
  pillar: string;
  audience: string;
};

export type CockpitQueueModel = {
  rows: CockpitQueueRow[];
  metrics: CockpitMetric[];
};

export type CockpitFact = {
  label: string;
  value: string;
  tone: CockpitTone;
};

export type CockpitItemModel = {
  id: string;
  title: string;
  lifecycle: string;
  stateTone: CockpitTone;
  updatedAt: string;
  command: CommandPresentation | null;
  evidence: CockpitFact[];
  context: CockpitFact[];
};

const NEEDS_ATTENTION = new Set(["blocked", "failed", "qa_failed"]);
const AWAITING_APPROVAL = new Set(["awaiting_approval"]);
const EVIDENCE_READY = new Set(["rendered", "qa_passed", "approved", "scheduled", "published"]);

export const QUEUE_FILTERS = [
  "All",
  "Needs Attention",
  "Failed / Blocked",
  "Awaiting Approval",
  "Rendered",
  "Scripted",
  "Scheduled",
  "Published",
  "Receipts",
] as const;

export type QueueFilter = (typeof QUEUE_FILTERS)[number];

export function formatOperatorTime(iso?: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function labelStatus(status?: string | null): string {
  if (!status) return "Unknown";
  return status
    .split("_")
    .filter(Boolean)
    .map((part) => (part.toLowerCase() === "qa" ? "QA" : part[0].toUpperCase() + part.slice(1)))
    .join(" ");
}

export function toneForStatus(status?: string | null): CockpitTone {
  if (!status) return "muted";
  if (NEEDS_ATTENTION.has(status) || status.endsWith("_failed")) return "danger";
  if (status === "awaiting_approval") return "warning";
  if (["approved", "scheduled", "published", "qa_passed"].includes(status)) return "success";
  if (["scripted", "rendered", "planned"].includes(status)) return "info";
  return "neutral";
}

function lastEventForStatus(status: string): string {
  if (NEEDS_ATTENTION.has(status) || status.endsWith("_failed")) return "Operator review needed";
  if (status === "awaiting_approval") return "Waiting for approval";
  if (status === "published") return "Published";
  if (status === "scheduled") return "Scheduled";
  if (status === "scripted") return "Script finalized";
  if (status === "rendered") return "Render available";
  if (status === "planned") return "Planned";
  return "Created";
}

function approvalForStatus(status: string): string {
  if (status === "awaiting_approval") return "Awaiting Approval";
  if (["approved", "scheduled", "published"].includes(status)) return "Approved";
  return "Not required";
}

function artifactsForStatus(status: string): string {
  if (["rendered", "qa_passed", "awaiting_approval", "approved", "scheduled", "published"].includes(status)) {
    return "3 available";
  }
  if (status === "scripted") return "1 available";
  return "0 available";
}

function failureForStatus(status: string): string {
  if (NEEDS_ATTENTION.has(status) || status.endsWith("_failed")) return "Needs operator review";
  return "—";
}

export function buildQueueRow(item: ContentItem): CockpitQueueRow {
  const status = item.status ?? "";
  return {
    id: item.id,
    shortId: item.id.length > 12 ? `${item.id.slice(0, 8)}…` : item.id,
    title: item.topic || "Untitled item",
    state: labelStatus(status),
    stateTone: toneForStatus(status),
    lastEvent: lastEventForStatus(status),
    artifacts: artifactsForStatus(status),
    approval: approvalForStatus(status),
    failure: failureForStatus(status),
    nextCommand: `uv run profusion inspect --item-id ${item.id}`,
    updatedAt: formatOperatorTime(item.updated_at),
    priority: `P${item.priority}`,
    pillar: item.pillar ?? "—",
    audience: item.audience ?? "—",
  };
}

export function buildQueueModel(items: ContentItem[]): CockpitQueueModel {
  const rows = items.map(buildQueueRow);
  const needsAttention = items.filter((item) => {
    const status = item.status ?? "";
    return NEEDS_ATTENTION.has(status) || status.endsWith("_failed");
  }).length;
  const awaitingApproval = items.filter((item) => AWAITING_APPROVAL.has(item.status ?? "")).length;
  const evidenceReady = items.filter((item) => EVIDENCE_READY.has(item.status ?? "")).length;
  return {
    rows,
    metrics: [
      { label: "Queue", value: items.length, tone: "neutral" },
      { label: "Needs Attention", value: needsAttention, tone: "danger" },
      { label: "Awaiting Approval", value: awaitingApproval, tone: "warning" },
      { label: "Evidence Ready", value: evidenceReady, tone: "success" },
      { label: "Safe Commands", value: rows.filter((row) => row.nextCommand).length, tone: "info" },
    ],
  };
}

export function filterQueueRows(
  rows: CockpitQueueRow[],
  filter: QueueFilter,
  search: string,
): CockpitQueueRow[] {
  const needle = search.trim().toLowerCase();
  return rows.filter((row) => {
    const matchesSearch =
      !needle ||
      row.title.toLowerCase().includes(needle) ||
      row.id.toLowerCase().includes(needle) ||
      row.pillar.toLowerCase().includes(needle) ||
      row.audience.toLowerCase().includes(needle);
    if (!matchesSearch) return false;
    if (filter === "All") return true;
    if (filter === "Needs Attention") return row.stateTone === "danger" || row.approval === "Awaiting Approval";
    if (filter === "Failed / Blocked") return row.stateTone === "danger";
    if (filter === "Awaiting Approval") return row.approval === "Awaiting Approval";
    if (filter === "Rendered") return row.state === "Rendered";
    if (filter === "Scripted") return row.state === "Scripted";
    if (filter === "Scheduled") return row.state === "Scheduled";
    if (filter === "Published") return row.state === "Published";
    if (filter === "Receipts") return row.artifacts !== "0 available";
    return true;
  });
}

function evidenceFact(label: string, ready: boolean, value?: string): CockpitFact {
  return {
    label,
    value: value ?? (ready ? "Present" : "Missing"),
    tone: ready ? "success" : "muted",
  };
}

export function buildItemModel(payload: ItemPayload): CockpitItemModel {
  const item = payload.item as ContentItem;
  const command = payload.next_safe_command
    ? getCommandPresentation(payload.next_safe_command)
    : null;
  return {
    id: item.id,
    title: item.topic || "Untitled item",
    lifecycle: labelStatus(payload.lifecycle_state),
    stateTone: toneForStatus(payload.lifecycle_state),
    updatedAt: formatOperatorTime(item.updated_at),
    command,
    evidence: [
      evidenceFact("Brief", Boolean(payload.latest_brief)),
      evidenceFact("Script Variants", payload.script_variants.length > 0, String(payload.script_variants.length)),
      evidenceFact("MP4", payload.artifacts.mp4_exists),
      evidenceFact("Manifest", payload.artifacts.manifest_exists),
      evidenceFact("QA Report", payload.artifacts.qa_report_exists),
    ],
    context: [
      { label: "Milestone", value: payload.milestone ?? "—", tone: payload.milestone ? "info" : "muted" },
      { label: "Priority", value: `P${item.priority}`, tone: "neutral" },
      { label: "Audience", value: item.audience ?? "—", tone: item.audience ? "neutral" : "muted" },
      { label: "Pillar", value: item.pillar ?? "—", tone: item.pillar ? "neutral" : "muted" },
    ],
  };
}
