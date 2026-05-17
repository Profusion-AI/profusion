import { describe, expect, it } from "vitest";
import { snapshotApiPaths } from "./staticApiPaths";

describe("static API snapshot paths", () => {
  it("maps queue, logs, and item read-model routes to extensionless Netlify files", () => {
    expect(snapshotApiPaths(["item 1"])).toEqual([
      { route: "api/queue", file: "api/queue.json" },
      { route: "api/logs", file: "api/logs.json" },
      { route: "api/measurements/summary", file: "api/measurements/summary.json" },
      { route: "api/items/item%201", file: "api/items/item%201/index.json" },
      { route: "api/items/item%201/jobs", file: "api/items/item%201/jobs.json" },
      { route: "api/items/item%201/renders", file: "api/items/item%201/renders.json" },
      { route: "api/items/item%201/approvals", file: "api/items/item%201/approvals.json" },
      { route: "api/items/item%201/receipts", file: "api/items/item%201/receipts.json" },
      { route: "api/items/item%201/measurements", file: "api/items/item%201/measurements.json" },
    ]);
  });
});
