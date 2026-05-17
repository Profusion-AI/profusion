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

export interface MeasurementObservation {
  observation_id: string;
  content_item_id: string;
  platform: string;
  observation_type: string;
  recorded_by: string;
  recorded_at: string;
  created_at: string;
  status_before: string;
  status_after: string;
  metrics: {
    views: number | null;
    completion_rate: number | null;
    comments: number | null;
  };
  dimensions?: {
    hook_variant: string | null;
    content_format: string | null;
    editorial_pillar: string | null;
  };
  display_dimensions?: {
    scenario_variant: string | null;
    workflow_type: string | null;
    trust_domain: string | null;
  };
  display_labels?: Record<string, string>;
  qualitative_signal: string | null;
  observation_path: string;
  [key: string]: unknown;
}

export interface MeasurementsPayload {
  item_id: string;
  measurement_count: number;
  display_labels?: Record<string, string>;
  latest_observation: MeasurementObservation | null;
  observations: MeasurementObservation[];
}

export interface MeasurementSummaryPayload {
  observation_count: number;
  measured_item_count: number;
  platforms: Array<{ platform: string; count: number }>;
  observation_types: Array<{ observation_type: string; count: number }>;
  display_labels?: Record<string, string>;
  aggregate_metrics: {
    views: number;
    comments: number;
    average_completion_rate: number | null;
  };
  comparisons: {
    hook_variants: MeasurementComparison[];
    content_formats: MeasurementComparison[];
    editorial_pillars: MeasurementComparison[];
  };
  latest_observation: MeasurementObservation | null;
  items: Array<{
    item_id: string;
    observation_count: number;
    latest_observation: MeasurementObservation;
    status: string | null;
  }>;
}

export interface MeasurementComparison {
  hook_variant?: string;
  content_format?: string;
  editorial_pillar?: string;
  display_label?: string;
  display_value?: string;
  observation_count: number;
  item_count: number;
  aggregate_metrics: {
    views: number;
    comments: number;
    average_completion_rate: number | null;
  };
  latest_observation: MeasurementObservation;
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

export const getItemMeasurements = (id: string): Promise<MeasurementsPayload> =>
  apiFetch<MeasurementsPayload>(`/api/items/${encodeURIComponent(id)}/measurements`);

export const getMeasurementSummary = (): Promise<MeasurementSummaryPayload> =>
  apiFetch<MeasurementSummaryPayload>("/api/measurements/summary");
