import type { Blockage, RetryInfo } from "../../api/items";

function retryLabel(stage: string): string {
  if (stage === "render") return "Retry Render";
  if (stage === "publish") return "Retry Publish";
  return "Retry QA";
}

interface Props {
  blockage: Blockage;
  retry: RetryInfo;
  onRetry?: () => void;
  retryPending?: boolean;
}

export default function BlockageCallout({ blockage, retry, onRetry, retryPending }: Props) {
  return (
    <div className="rounded border border-red-800 bg-red-950/50 px-4 py-3 mb-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-red-300 text-sm font-medium mb-1">
            Blocked at <span className="font-mono">{blockage.stage}</span>
          </p>
          <p className="text-red-200 text-sm">{blockage.message}</p>
          {blockage.error_code && (
            <p className="text-red-400 text-xs font-mono mt-1">{blockage.error_code}</p>
          )}
        </div>
        {retry.retryable && onRetry && (
          <button
            onClick={onRetry}
            disabled={retryPending}
            className="shrink-0 px-3 py-1.5 rounded bg-red-700 hover:bg-red-600 disabled:opacity-50 text-white text-xs font-medium transition-colors"
          >
            {retryPending ? "Retrying…" : retryLabel(blockage.stage)}
          </button>
        )}
      </div>
      {retry.reason && !retry.retryable && (
        <p className="text-red-400 text-xs mt-2">{retry.reason}</p>
      )}
    </div>
  );
}
