import assert from "node:assert/strict";
import test from "node:test";

import { workflowReceiptTemplates } from "../src/data/workflowReceiptTemplates.js";
import { buildWorkflowReceiptSimulation } from "../src/domain/workflowReceiptSimulator.js";

test("content approval is the default current sample with bounded receipt output", () => {
  const template = workflowReceiptTemplates.find((item) => item.id === "content_approval");

  assert.ok(template);
  assert.equal(template.capabilityStatus, "Current sample");
  assert.equal(template.trustDomain, "media_trust");
  assert.equal(template.receiptType, "content_video_receipt");

  const result = buildWorkflowReceiptSimulation({
    templateId: "content_approval",
    businessGoal: "Publish a short product education video with reviewable AI assistance.",
    outputType: "Short-form video",
    audienceOrReviewer: "Content lead",
    aiTouchpoints: ["brief generation", "script drafting", "render assembly"],
    riskIfWrong: "Brand claim or synthetic-media ambiguity reaches a prospect.",
    humanReviewerRole: "Content lead",
  }, template);

  assert.equal(result.templateLabel, "AI-Assisted Content Approval");
  assert.equal(result.capabilityStatus, "Current sample");
  assert.ok(result.workflowMap.artifacts.some((artifact) => artifact.label === "QA report"));
  assert.ok(result.businessValue.trustValue.includes("reviewable"));
  assert.ok(result.evidenceBoundary.insideReceipt.includes("AI-assisted brief, script, render, QA, approval, and artifact trail"));
  assert.ok(result.evidenceBoundary.outsideReceipt.includes("Universal synthetic-media detection"));
  assert.ok(result.limitations.includes("A sample receipt does not certify compliance, truth, identity, liveness, or correctness."));
  assert.ok(result.receiptPreview.unsupportedClaims.includes("Certified compliance or legal sufficiency"));
  assert.equal(result.nextStep.ctaLabel, "Book a Workflow Reliability Session");
});

test("coding-agent review remains a simulated example and does not claim live integration", () => {
  const template = workflowReceiptTemplates.find((item) => item.id === "coding_agent_review_simulated");

  assert.ok(template);
  assert.equal(template.capabilityStatus, "Simulated example");
  assert.equal(template.integrationStatus, "Future integration concept");

  const result = buildWorkflowReceiptSimulation({
    templateId: "coding_agent_review_simulated",
    businessGoal: "Review an AI-generated code change before merge.",
    outputType: "Pull request",
    audienceOrReviewer: "Engineering lead",
    aiTouchpoints: ["coding-agent output"],
    riskIfWrong: "A generated change ships without enough review evidence.",
    humanReviewerRole: "Senior engineer",
  }, template);

  assert.equal(result.capabilityStatus, "Simulated example");
  assert.ok(result.receiptPreview.boundaryNotice.includes("simulated"));
  assert.ok(result.receiptPreview.unsupportedClaims.includes("Production coding-agent instrumentation"));
  assert.ok(result.receiptPreview.unsupportedClaims.includes("Live MCP capture"));
  assert.ok(result.limitations.includes("Coding-agent, contractor-readiness, and MCP examples are simulated unless explicitly marked otherwise."));
});
