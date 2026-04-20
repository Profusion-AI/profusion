import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import { getItem, getItemJobs, getItemRenders, getItemApprovals } from "../api/items";
import { postRetryQa, postRetryRender, postRetryPublish } from "../api/retry";

export const useItem = (id: string) =>
  useQuery({
    queryKey: ["item", id],
    queryFn: () => getItem(id),
    staleTime: 15_000,
  });

export const useItemJobs = (id: string) =>
  useQuery({
    queryKey: ["item", id, "jobs"],
    queryFn: () => getItemJobs(id),
    staleTime: 15_000,
  });

export const useItemRenders = (id: string) =>
  useQuery({
    queryKey: ["item", id, "renders"],
    queryFn: () => getItemRenders(id),
    staleTime: 15_000,
  });

export const useItemApprovals = (id: string) =>
  useQuery({
    queryKey: ["item", id, "approvals"],
    queryFn: () => getItemApprovals(id),
    staleTime: 15_000,
  });

export const useRetryQa = (item_id: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => postRetryQa(item_id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["item", item_id] });
      void qc.invalidateQueries({ queryKey: ["queue"] });
    },
  });
};

export const useRetryRender = (item_id: string, render_job_id: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => postRetryRender(render_job_id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["item", item_id] });
    },
  });
};

export const useRetryPublish = (item_id: string, job_id: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => postRetryPublish(job_id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["item", item_id] });
    },
  });
};
