import { apiFetch } from "./client";

export interface ContentItem {
  id: string;
  topic: string;
  status: string;
  pillar: string | null;
  audience: string | null;
  priority: number;
  source: string | null;
  created_at: string;
  updated_at: string;
  [key: string]: unknown;
}

export interface QueueSummaryRow {
  status: string;
  count: number;
}

export interface QueuePayload {
  items: ContentItem[];
  summary: QueueSummaryRow[];
  filters: { status: string | null };
}

export const getQueue = (status?: string): Promise<QueuePayload> =>
  apiFetch<QueuePayload>(`/api/queue${status ? `?status=${encodeURIComponent(status)}` : ""}`);
