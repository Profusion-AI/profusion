import { useQuery } from "@tanstack/react-query";
import { getLogs } from "../api/logs";

export const useLogs = (params?: { item_id?: string; job_id?: string; limit?: number }) =>
  useQuery({
    queryKey: ["logs", params ?? {}],
    queryFn: () => getLogs(params),
    staleTime: 15_000,
  });
