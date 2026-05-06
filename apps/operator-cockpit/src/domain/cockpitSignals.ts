type QueueLikeItem = {
  status?: string | null;
};

type RetryLike = {
  retryable?: boolean;
  command?: string | null;
};

type JobLike = {
  id?: string | null;
  error_code?: string | null;
  last_error?: string | null;
  status?: string | null;
  retry?: RetryLike | null;
};

export type QueueHealth = {
  active: number;
  blockedOrFailed: number;
  publishedOrArchived: number;
};

export type CommandPresentation = {
  command: string;
  isMutation: boolean;
  buttonLabel: string;
  warning: string | null;
};

export type FailureJobDescription = {
  id: string;
  stage: string;
  message: string;
  errorCode: string | null;
  retryable: boolean;
  retryCommand: string | null;
};

export type ReceiptLike = {
  receipt_id: string;
  receipt_status: string;
};

export type ReceiptLifecyclePresentation = {
  badgeLabel: string;
  statusLabel: string;
  nextCommand: string | null;
};

const BLOCKED_STATUSES = new Set(["failed", "qa_failed", "blocked"]);
const FINISHED_STATUSES = new Set(["published", "archived"]);
const MUTATING_COMMANDS = [
  "uv run profusion retry",
  "uv run profusion approve",
  "uv run profusion schedule",
  "uv run profusion publish-due",
  "uv run profusion receipt draft",
  "uv run profusion receipt transition",
];
const RECEIPT_LIFECYCLE_COPY: Record<string, { badgeLabel: string; next: string | null }> = {
  draft: { badgeLabel: "Receipt Draft", next: "reviewed" },
  reviewed: { badgeLabel: "Receipt Reviewed", next: "approved_for_packet" },
  approved_for_packet: { badgeLabel: "Packet Approved", next: "delivered" },
  delivered: { badgeLabel: "Packet Delivered", next: null },
};

export function getQueueHealth(items: QueueLikeItem[]): QueueHealth {
  return items.reduce<QueueHealth>(
    (health, item) => {
      const status = item.status ?? "";
      if (BLOCKED_STATUSES.has(status) || status.endsWith("_failed")) {
        health.blockedOrFailed += 1;
      } else if (FINISHED_STATUSES.has(status)) {
        health.publishedOrArchived += 1;
      } else {
        health.active += 1;
      }
      return health;
    },
    { active: 0, blockedOrFailed: 0, publishedOrArchived: 0 },
  );
}

export function getCommandPresentation(command: string): CommandPresentation {
  const isMutation = MUTATING_COMMANDS.some((prefix) => command.startsWith(prefix));
  return {
    command,
    isMutation,
    buttonLabel: "Copy command",
    warning: isMutation ? "Run this in a terminal after verifying the item state." : null,
  };
}

export function describeFailureJob(
  stage: "render" | "publish" | string,
  job: JobLike,
): FailureJobDescription | null {
  if (job.status !== "failed") {
    return null;
  }
  const retry = job.retry ?? null;
  return {
    id: job.id ?? "",
    stage,
    message: job.last_error ?? `${stage} job failed`,
    errorCode: job.error_code ?? null,
    retryable: Boolean(retry?.retryable),
    retryCommand: retry?.command ?? null,
  };
}

export function getReceiptLifecyclePresentation(
  receipt: ReceiptLike,
): ReceiptLifecyclePresentation {
  const lifecycle = RECEIPT_LIFECYCLE_COPY[receipt.receipt_status] ?? {
    badgeLabel: receipt.receipt_status || "Receipt",
    next: null,
  };
  return {
    badgeLabel: lifecycle.badgeLabel,
    statusLabel: receipt.receipt_status,
    nextCommand: lifecycle.next
      ? `uv run profusion receipt transition --receipt-id ${receipt.receipt_id} --to ${lifecycle.next}`
      : null,
  };
}
