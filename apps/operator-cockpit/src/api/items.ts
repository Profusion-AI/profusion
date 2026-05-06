import { apiFetch } from "./client";

export interface Blockage {
  stage: string;
  message: string;
  error_code?: string | null;
  [key: string]: unknown;
}

export interface RetryInfo {
  retryable: boolean;
  reason?: string;
  command?: string;
}

export interface Artifacts {
  mp4_exists: boolean;
  mp4_path?: string | null;
  manifest_exists: boolean;
  qa_report_exists: boolean;
  [key: string]: unknown;
}

export interface LogEntry {
  path: string;
  name: string;
  size_bytes: number;
  modified_at: string;
}

export interface ItemPayload {
  item: Record<string, unknown>;
  lifecycle_state: string;
  milestone: string | null;
  latest_brief: Record<string, unknown> | null;
  script_variants: unknown[];
  latest_script_variant: Record<string, unknown> | null;
  latest_render_job: Record<string, unknown> | null;
  latest_qa: Record<string, unknown> | null;
  latest_approval: Record<string, unknown> | null;
  latest_publish_job: Record<string, unknown> | null;
  jobs: unknown[];
  artifacts: Artifacts;
  recent_logs: LogEntry[];
  blockage: Blockage | null;
  retry: RetryInfo;
  next_safe_command: string | null;
}

export interface JobsPayload {
  render_jobs: unknown[];
  publish_jobs: unknown[];
  [key: string]: unknown;
}

export interface RendersPayload {
  latest_render_job: Record<string, unknown> | null;
  render_jobs: unknown[];
  artifacts: Artifacts;
  retry: RetryInfo;
  [key: string]: unknown;
}

export interface ApprovalsPayload {
  latest_approval: Record<string, unknown> | null;
  approval_records: unknown[];
  effective_decision: string | null;
  eligible_for_publish: boolean;
  [key: string]: unknown;
}

export interface ReceiptSummary {
  receipt_id: string;
  receipt_type: string;
  receipt_status: string;
  subject_id: string;
  packet_dir: string;
  receipt_md: string;
  evidence_json: string;
  created_at: string;
  [key: string]: unknown;
}

export interface ReceiptsPayload {
  item_id: string;
  receipt_count: number;
  receipts: ReceiptSummary[];
}

export const getItem = (id: string): Promise<ItemPayload> =>
  apiFetch<ItemPayload>(`/api/items/${encodeURIComponent(id)}`);

export const getItemJobs = (id: string): Promise<JobsPayload> =>
  apiFetch<JobsPayload>(`/api/items/${encodeURIComponent(id)}/jobs`);

export const getItemRenders = (id: string): Promise<RendersPayload> =>
  apiFetch<RendersPayload>(`/api/items/${encodeURIComponent(id)}/renders`);

export const getItemApprovals = (id: string): Promise<ApprovalsPayload> =>
  apiFetch<ApprovalsPayload>(`/api/items/${encodeURIComponent(id)}/approvals`);

export const getItemReceipts = (id: string): Promise<ReceiptsPayload> =>
  apiFetch<ReceiptsPayload>(`/api/items/${encodeURIComponent(id)}/receipts`);
