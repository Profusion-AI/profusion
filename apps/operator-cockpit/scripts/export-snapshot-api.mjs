import { execFileSync } from "node:child_process";
import { mkdirSync, rmSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = resolve(appRoot, "../..");
const publicApiRoot = resolve(appRoot, "public/api");

function profusionJson(args) {
  const stdout = execFileSync("uv", ["run", "profusion", ...args, "--json"], {
    cwd: repoRoot,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "inherit"],
  });
  return JSON.parse(stdout);
}

function writeJson(relativePath, value) {
  const target = resolve(publicApiRoot, relativePath);
  mkdirSync(dirname(target), { recursive: true });
  writeFileSync(target, `${JSON.stringify(value)}\n`, "utf8");
}

rmSync(publicApiRoot, { recursive: true, force: true });
mkdirSync(publicApiRoot, { recursive: true });

const queue = profusionJson(["status"]);
writeJson("queue.json", queue);
writeJson("logs.json", profusionJson(["logs", "--limit", "50"]));

for (const item of queue.items ?? []) {
  const itemId = item.id;
  const encoded = encodeURIComponent(itemId);
  writeJson(`items/${encoded}/index.json`, profusionJson(["inspect", "--item-id", itemId]));
  writeJson(`items/${encoded}/jobs.json`, profusionJson(["jobs", "--item-id", itemId]));
  writeJson(`items/${encoded}/renders.json`, profusionJson(["renders", "--item-id", itemId]));
  writeJson(`items/${encoded}/approvals.json`, profusionJson(["approvals", "--item-id", itemId]));
  writeJson(`items/${encoded}/receipts.json`, profusionJson(["receipt", "list", "--item-id", itemId]));
}

console.log(`Exported static cockpit API snapshot for ${(queue.items ?? []).length} item(s).`);
