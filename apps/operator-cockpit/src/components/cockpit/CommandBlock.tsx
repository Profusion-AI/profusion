import { Clipboard, Terminal } from "lucide-react";
import { useState } from "react";
import type { CommandPresentation } from "../../domain/cockpitSignals";

export default function CommandBlock({
  title = "Next safe command",
  presentation,
}: {
  title?: string;
  presentation: CommandPresentation;
}) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    await navigator.clipboard.writeText(presentation.command);
    setCopied(true);
    setTimeout(() => setCopied(false), 1600);
  };

  return (
    <div className="cockpit-panel overflow-hidden">
      <div className="flex items-center gap-2 border-b border-[var(--cockpit-border)] px-4 py-3">
        <Terminal size={15} className="text-[var(--cockpit-gold)]" />
        <span className="section-label">{title}</span>
        {presentation.isMutation && (
          <span className="ml-auto rounded-full border border-[rgba(245,201,107,0.30)] bg-[var(--cockpit-warning-soft)] px-2 py-0.5 text-[10px] text-[var(--cockpit-warning)]">
            terminal only
          </span>
        )}
      </div>
      <div className="px-4 py-3">
        {presentation.warning && (
          <p className="mb-2 text-xs text-[var(--cockpit-warning)]">{presentation.warning}</p>
        )}
        <div className="flex items-start gap-3">
          <code className="min-w-0 flex-1 break-all text-xs leading-5 text-[var(--cockpit-info)]">
            {presentation.command}
          </code>
          <button
            type="button"
            onClick={copy}
            className="inline-flex h-8 shrink-0 items-center gap-1.5 rounded border border-[var(--cockpit-border)] bg-[var(--cockpit-row)] px-2.5 text-xs text-[var(--cockpit-text-2)] hover:bg-[var(--cockpit-row-hover)]"
          >
            <Clipboard size={13} />
            {copied ? "Copied" : presentation.buttonLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
