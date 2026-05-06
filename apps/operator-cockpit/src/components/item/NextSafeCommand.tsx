import { useState } from "react";
import { getCommandPresentation } from "../../domain/cockpitSignals";

export default function NextSafeCommand({ command }: { command: string }) {
  const [copied, setCopied] = useState(false);
  const presentation = getCommandPresentation(command);

  const copy = async () => {
    await navigator.clipboard.writeText(command);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded border border-emerald-800 bg-emerald-950/30 px-4 py-3 mb-4">
      <p className="text-emerald-400 text-xs font-medium mb-1.5">Next safe command</p>
      {presentation.warning && (
        <p className="text-emerald-300/80 text-xs mb-2">{presentation.warning}</p>
      )}
      <div className="flex items-center gap-2">
        <code className="text-emerald-200 text-sm flex-1 break-all">{command}</code>
        <button
          onClick={copy}
          className="shrink-0 px-2.5 py-1 rounded bg-emerald-800 hover:bg-emerald-700 text-emerald-100 text-xs transition-colors"
        >
          {copied ? "Copied!" : presentation.buttonLabel}
        </button>
      </div>
    </div>
  );
}
