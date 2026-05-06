export type StaticApiPath = {
  route: string;
  file: string;
};

export function itemApiPaths(itemId: string): StaticApiPath[] {
  const encoded = encodeURIComponent(itemId);
  return [
    { route: `api/items/${encoded}`, file: `api/items/${encoded}/index.json` },
    { route: `api/items/${encoded}/jobs`, file: `api/items/${encoded}/jobs.json` },
    { route: `api/items/${encoded}/renders`, file: `api/items/${encoded}/renders.json` },
    { route: `api/items/${encoded}/approvals`, file: `api/items/${encoded}/approvals.json` },
    { route: `api/items/${encoded}/receipts`, file: `api/items/${encoded}/receipts.json` },
  ];
}

export function snapshotApiPaths(itemIds: string[]): StaticApiPath[] {
  return [
    { route: "api/queue", file: "api/queue.json" },
    { route: "api/logs", file: "api/logs.json" },
    ...itemIds.flatMap((itemId) => itemApiPaths(itemId)),
  ];
}
