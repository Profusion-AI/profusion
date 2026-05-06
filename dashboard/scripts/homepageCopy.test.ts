import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const appSource = readFileSync(new URL("../src/App.tsx", import.meta.url), "utf8");

test("homepage states the productivity-reliability wedge and shipped proof boundary", () => {
  assert.match(
    appSource,
    /Profusion does not make AI produce more work\. Profusion makes AI-produced work\s+reviewable enough to use\./,
  );
  assert.match(appSource, /Productivity-Reliability Paradox/);
  assert.match(appSource, /AI has moved the bottleneck from production to verification\./);
  assert.match(appSource, /Implemented proof", "AI-assisted content\/media receipt: content_video_receipt in media_trust/);
  assert.match(appSource, /Future integration concept", "MCP and coding-agent evidence capture/);
});

test("homepage keeps unsafe claims out of active positioning copy", () => {
  assert.doesNotMatch(appSource, /Profusion certifies/i);
  assert.doesNotMatch(appSource, /guarantees compliance/i);
  assert.doesNotMatch(appSource, /production coding-agent instrumentation/i);
  assert.doesNotMatch(appSource, /live MCP capture/i);
  assert.doesNotMatch(appSource, /candidate ranking/i);
});
