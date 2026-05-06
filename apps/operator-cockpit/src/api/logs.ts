import { apiFetch } from "./client";
import type { LogEntry } from "./items";

export interface LogsPayload {
  logs: LogEntry[];
}

export const getLogs = (params?: {
  item_id?: string;
  job_id?: string;
  limit?: number;
}): Promise<LogsPayload> => {
  const q = new URLSearchParams();
  if (params?.item_id) q.set("item_id", params.item_id);
  if (params?.job_id) q.set("job_id", params.job_id);
  if (params?.limit != null) q.set("limit", String(params.limit));
  const qs = q.toString();
  return apiFetch<LogsPayload>(`/api/logs${qs ? `?${qs}` : ""}`);
};
