import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { dirname } from "node:path";

const appRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const publicApiRoot = resolve(appRoot, "public/api");

const requiredRoutes = [
  "/queue",
  "/failures",
  "/approvals",
  "/evidence",
  "/logs",
  "/system",
];

function readJson(relativePath) {
  const target = resolve(publicApiRoot, relativePath);
  if (!existsSync(target)) {
    throw new Error(`Missing snapshot file: ${relativePath}`);
  }
  return JSON.parse(readFileSync(target, "utf8"));
}

const queue = readJson("queue.json");
readJson("logs.json");

for (const item of queue.items ?? []) {
  const encoded = encodeURIComponent(item.id);
  readJson(`items/${encoded}/index.json`);
  readJson(`items/${encoded}/jobs.json`);
  readJson(`items/${encoded}/renders.json`);
  readJson(`items/${encoded}/approvals.json`);
  readJson(`items/${encoded}/receipts.json`);
}

const demo = (queue.items ?? []).find((item) => item.source === "m7.5-demo-receipt");
if (!demo) {
  throw new Error("Static snapshot does not include the M7.5 demo receipt item.");
}
const demoReceipts = readJson(`items/${encodeURIComponent(demo.id)}/receipts.json`);
if (demoReceipts.receipt_count < 1) {
  throw new Error("M7.5 demo receipt item has no receipt packet in the snapshot.");
}

const baseUrl = process.env.COCKPIT_BASE_URL;
if (baseUrl) {
  for (const route of requiredRoutes) {
    const response = await fetch(new URL(route, baseUrl));
    if (!response.ok) {
      throw new Error(`${route} returned HTTP ${response.status}`);
    }
  }
  const receiptsResponse = await fetch(
    new URL(`/api/items/${encodeURIComponent(demo.id)}/receipts`, baseUrl),
  );
  if (!receiptsResponse.ok) {
    throw new Error(`receipt endpoint returned HTTP ${receiptsResponse.status}`);
  }
  const remoteReceipts = await receiptsResponse.json();
  if (remoteReceipts.receipt_count < 1) {
    throw new Error("remote receipt endpoint returned no demo receipts");
  }
}

console.log(
  `Static cockpit smoke passed for ${(queue.items ?? []).length} item(s)` +
    (baseUrl ? ` at ${baseUrl}` : ""),
);
