import CockpitBadge from "../cockpit/CockpitBadge";
import { labelStatus, toneForStatus } from "../../domain/cockpitViewModel";

export default function StatusBadge({ status }: { status: string }) {
  return <CockpitBadge tone={toneForStatus(status)}>{labelStatus(status)}</CockpitBadge>;
}
