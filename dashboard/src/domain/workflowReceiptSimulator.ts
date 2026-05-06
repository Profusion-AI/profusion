export type WorkflowTemplateId =
  | "content_approval"
  | "coding_agent_review_simulated"
  | "contractor_readiness_simulated";

export type CapabilityStatus =
  | "Current sample"
  | "Simulated example"
  | "Future integration concept"
  | "Not offered";

export interface WorkflowSimulatorInput {
  templateId: WorkflowTemplateId;
  businessGoal: string;
  outputType: string;
  audienceOrReviewer: string;
  aiTouchpoints: string[];
  riskIfWrong: string;
  humanReviewerRole: string;
}

export interface ReceiptArtifact {
  id: string;
  label: string;
  artifactType: string;
  simulated: boolean;
  description: string;
}

export interface ReviewGate {
  id: string;
  label: string;
  reviewerRole: string;
  decision: "passed" | "needs_review" | "simulated_passed";
  notes: string;
}

export interface BusinessValueBrief {
  trustValue: string;
  operationalValue: string;
  riskValue: string;
  differentiationValue: string;
}

export interface EvidenceBoundary {
  insideReceipt: string[];
  outsideReceipt: string[];
  limitations: string[];
}

export interface WorkflowReceiptTemplate {
  id: WorkflowTemplateId;
  label: string;
  capabilityStatus: CapabilityStatus;
  integrationStatus: CapabilityStatus;
  trustDomain: string;
  receiptType: string;
  defaultInput: WorkflowSimulatorInput;
  workflowGoal: string;
  actors: string[];
  aiTouchpoints: string[];
  artifacts: ReceiptArtifact[];
  reviewGates: ReviewGate[];
  riskPoints: string[];
  businessValue: BusinessValueBrief;
  evidenceBoundary: EvidenceBoundary;
  supportedClaims: string[];
  unsupportedClaims: string[];
  limitations: string[];
}

export interface WorkflowMap {
  goal: string;
  actors: string[];
  aiTouchpoints: string[];
  artifacts: ReceiptArtifact[];
  reviewGates: ReviewGate[];
  riskPoints: string[];
}

export interface ReceiptPreview {
  title: string;
  boundaryNotice: string;
  evidenceAvailable: string[];
  humanReviewRecorded: string[];
  supportedClaims: string[];
  unsupportedClaims: string[];
}

export interface WorkflowReceiptSimulation {
  templateId: WorkflowTemplateId;
  templateLabel: string;
  capabilityStatus: CapabilityStatus;
  integrationStatus: CapabilityStatus;
  workflowMap: WorkflowMap;
  businessValue: BusinessValueBrief;
  evidenceBoundary: EvidenceBoundary;
  artifactTrail: ReceiptArtifact[];
  receiptPreview: ReceiptPreview;
  limitations: string[];
  nextStep: {
    ctaLabel: string;
    ctaHref: string;
    summary: string;
  };
}

const generalLimitations = [
  "A sample receipt does not certify compliance, truth, identity, liveness, or correctness.",
  "A workflow receipt records available process evidence and limitation language; it does not replace legal, compliance, engineering, brand, hiring, or executive judgment.",
  "Coding-agent, contractor-readiness, and MCP examples are simulated unless explicitly marked otherwise.",
];

export function buildWorkflowReceiptSimulation(
  input: WorkflowSimulatorInput,
  template: WorkflowReceiptTemplate,
): WorkflowReceiptSimulation {
  const aiTouchpoints = uniqueList([...template.aiTouchpoints, ...input.aiTouchpoints]);
  const reviewerRole = input.humanReviewerRole.trim() || template.defaultInput.humanReviewerRole;
  const reviewGates = template.reviewGates.map((gate) => ({
    ...gate,
    reviewerRole: gate.reviewerRole === "User supplied reviewer" ? reviewerRole : gate.reviewerRole,
  }));

  return {
    templateId: template.id,
    templateLabel: template.label,
    capabilityStatus: template.capabilityStatus,
    integrationStatus: template.integrationStatus,
    workflowMap: {
      goal: input.businessGoal.trim() || template.workflowGoal,
      actors: uniqueList([...template.actors, input.audienceOrReviewer, reviewerRole]),
      aiTouchpoints,
      artifacts: template.artifacts,
      reviewGates,
      riskPoints: uniqueList([...template.riskPoints, input.riskIfWrong]),
    },
    businessValue: template.businessValue,
    evidenceBoundary: template.evidenceBoundary,
    artifactTrail: template.artifacts,
    receiptPreview: {
      title: `Sample Workflow Receipt: ${template.label}`,
      boundaryNotice: makeBoundaryNotice(template),
      evidenceAvailable: template.evidenceBoundary.insideReceipt,
      humanReviewRecorded: reviewGates.map(
        (gate) => `${gate.label}: ${gate.decision.replaceAll("_", " ")} by ${gate.reviewerRole}`,
      ),
      supportedClaims: template.supportedClaims,
      unsupportedClaims: template.unsupportedClaims,
    },
    limitations: uniqueList([...template.limitations, ...template.evidenceBoundary.limitations, ...generalLimitations]),
    nextStep: {
      ctaLabel: "Book a Workflow Reliability Session",
      ctaHref: "#contact",
      summary: "Bring one workflow. We will identify the evidence boundary, review gates, artifact trail, and receipt opportunity before proposing a pilot.",
    },
  };
}

function makeBoundaryNotice(template: WorkflowReceiptTemplate): string {
  if (template.capabilityStatus === "Current sample") {
    return "Current sample generated from Profusion's AI-assisted content approval receipt pattern.";
  }

  if (template.capabilityStatus === "Simulated example") {
    return "This is a simulated example. It is not generated from live production integration or customer data.";
  }

  return "Future integration concept. This path describes a possible receipt boundary, not a shipped integration.";
}

function uniqueList(values: string[]): string[] {
  return values
    .map((value) => value.trim())
    .filter((value, index, allValues) => value.length > 0 && allValues.indexOf(value) === index);
}
