import { apiFetch } from "./client";

export interface RetryResult {
  action: string;
  item_id?: string;
  old_render_job_id?: string;
  new_render_job_id?: string;
  next_safe_command?: string;
  [key: string]: unknown;
}

export const postRetryQa = (item_id: string): Promise<RetryResult> =>
  apiFetch<RetryResult>(`/api/items/${encodeURIComponent(item_id)}/retry/qa`, {
    method: "POST",
  });

export const postRetryRender = (render_job_id: string): Promise<RetryResult> =>
  apiFetch<RetryResult>(`/api/jobs/render/${encodeURIComponent(render_job_id)}/retry`, {
    method: "POST",
  });

export const postRetryPublish = (job_id: string): Promise<RetryResult> =>
  apiFetch<RetryResult>(`/api/jobs/publish/${encodeURIComponent(job_id)}/retry`, {
    method: "POST",
  });
