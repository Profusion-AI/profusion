import { useQuery } from "@tanstack/react-query";
import { getQueue } from "../api/queue";

export const useQueue = (status?: string) =>
  useQuery({
    queryKey: ["queue", status ?? null],
    queryFn: () => getQueue(status),
    staleTime: 15_000,
  });
