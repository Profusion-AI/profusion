import type { CockpitMetric } from "../../domain/cockpitViewModel";

export default function MetricStrip({ metrics }: { metrics: CockpitMetric[] }) {
  return (
    <div className="cockpit-panel grid overflow-hidden sm:grid-cols-2 lg:grid-cols-5">
      {metrics.map((metric) => (
        <div
          key={metric.label}
          className="border-b border-r border-[var(--cockpit-border)] px-5 py-4 last:border-r-0 sm:[&:nth-last-child(-n+2)]:border-b-0 lg:border-b-0"
        >
          <div className={`mono mb-1 text-[24px] leading-none tone-${metric.tone}`}>
            {metric.value}
          </div>
          <div className="text-[11px] text-[var(--cockpit-muted)]">{metric.label}</div>
        </div>
      ))}
    </div>
  );
}
