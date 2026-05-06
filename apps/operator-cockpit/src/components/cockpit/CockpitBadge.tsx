import { clsx } from "clsx";
import type { CockpitTone } from "../../domain/cockpitViewModel";

const TONE_CLASS: Record<CockpitTone, string> = {
  neutral: "border-[var(--cockpit-border)] bg-[rgba(255,255,255,0.03)] text-[var(--cockpit-text-2)]",
  muted: "border-[var(--cockpit-border)] bg-[rgba(255,255,255,0.02)] text-[var(--cockpit-muted)]",
  info: "border-[rgba(122,167,255,0.28)] bg-[var(--cockpit-info-soft)] text-[var(--cockpit-info)]",
  success: "border-[rgba(125,211,168,0.28)] bg-[var(--cockpit-success-soft)] text-[var(--cockpit-success)]",
  warning: "border-[rgba(245,201,107,0.30)] bg-[var(--cockpit-warning-soft)] text-[var(--cockpit-warning)]",
  danger: "border-[rgba(248,113,113,0.30)] bg-[var(--cockpit-danger-soft)] text-[var(--cockpit-danger)]",
};

const DOT_CLASS: Record<CockpitTone, string> = {
  neutral: "bg-[var(--cockpit-text-2)]",
  muted: "bg-[var(--cockpit-muted)]",
  info: "bg-[var(--cockpit-info)]",
  success: "bg-[var(--cockpit-success)]",
  warning: "bg-[var(--cockpit-warning)]",
  danger: "bg-[var(--cockpit-danger)]",
};

export default function CockpitBadge({
  tone = "neutral",
  children,
}: {
  tone?: CockpitTone;
  children: React.ReactNode;
}) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[11px] font-medium whitespace-nowrap",
        TONE_CLASS[tone],
      )}
    >
      <span className={clsx("h-1.5 w-1.5 rounded-full", DOT_CLASS[tone])} />
      {children}
    </span>
  );
}
