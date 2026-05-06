import { useMemo, useState } from "react";

import { workflowReceiptTemplates } from "../data/workflowReceiptTemplates.js";
import {
  buildWorkflowReceiptSimulation,
  type BusinessValueBrief,
  type WorkflowReceiptTemplate,
  type WorkflowTemplateId,
} from "../domain/workflowReceiptSimulator.js";

type SimulatorForm = {
  businessGoal: string;
  outputType: string;
  audienceOrReviewer: string;
  aiTouchpoints: string;
  riskIfWrong: string;
  humanReviewerRole: string;
};

const statusTone: Record<string, string> = {
  "Current sample": "current",
  "Simulated example": "simulated",
  "Future integration concept": "future",
  "Not offered": "not-offered",
};

export default function WorkflowReceiptSimulator() {
  const [selectedTemplateId, setSelectedTemplateId] = useState<WorkflowTemplateId>("content_approval");
  const selectedTemplate = workflowReceiptTemplates.find((template) => template.id === selectedTemplateId)
    ?? workflowReceiptTemplates[0];
  const [form, setForm] = useState<SimulatorForm>(() => formFromTemplate(selectedTemplate));

  const simulation = useMemo(() => buildWorkflowReceiptSimulation({
    templateId: selectedTemplate.id,
    businessGoal: form.businessGoal,
    outputType: form.outputType,
    audienceOrReviewer: form.audienceOrReviewer,
    aiTouchpoints: splitTouchpoints(form.aiTouchpoints),
    riskIfWrong: form.riskIfWrong,
    humanReviewerRole: form.humanReviewerRole,
  }, selectedTemplate), [form, selectedTemplate]);

  function updateForm(field: keyof SimulatorForm, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function chooseTemplate(template: WorkflowReceiptTemplate) {
    setSelectedTemplateId(template.id);
    setForm(formFromTemplate(template));
  }

  return (
    <section className="simulator-page" id="top">
      <div className="simulator-hero">
        <div className="simulator-kicker">
          <span />
          M7.75 SEMI-PRIVATE PREVIEW
        </div>
        <div className="simulator-hero-grid">
          <div>
            <h1>Workflow Receipt Simulator</h1>
            <p>
              Choose one AI-assisted workflow and see how Profusion turns it into a
              bounded receipt: actors, AI touchpoints, artifacts, review gates,
              business value, supported claims, unsupported claims, and limitations.
            </p>
          </div>
          <div className="simulator-boundary">
            <strong>Capability boundary</strong>
            <span>Current sample: AI-assisted content approval</span>
            <span>Secondary examples: simulated only</span>
            <span>No live backend, MCP capture, portal, or receipt mutation</span>
          </div>
        </div>
      </div>

      <div className="simulator-shell">
        <div className="simulator-config">
          <div className="simulator-section-heading">
            <span>1</span>
            <div>
              <h2>Choose a workflow</h2>
              <p>Templates are fixed so the preview stays controlled and claim-bounded.</p>
            </div>
          </div>

          <div className="template-segments" role="tablist" aria-label="Workflow templates">
            {workflowReceiptTemplates.map((template) => (
              <button
                aria-selected={selectedTemplateId === template.id}
                className={selectedTemplateId === template.id ? "template-segment is-active" : "template-segment"}
                key={template.id}
                onClick={() => chooseTemplate(template)}
                role="tab"
                type="button"
              >
                <span>{template.label}</span>
                <CapabilityBadge label={template.capabilityStatus} />
              </button>
            ))}
          </div>

          <div className="simulator-section-heading">
            <span>2</span>
            <div>
              <h2>Add context</h2>
              <p>This context changes the preview only in your browser.</p>
            </div>
          </div>

          <div className="simulator-form-grid">
            <label>
              Business goal
              <textarea
                onChange={(event) => updateForm("businessGoal", event.target.value)}
                rows={3}
                value={form.businessGoal}
              />
            </label>
            <label>
              Output type
              <input
                onChange={(event) => updateForm("outputType", event.target.value)}
                type="text"
                value={form.outputType}
              />
            </label>
            <label>
              Audience or reviewer
              <input
                onChange={(event) => updateForm("audienceOrReviewer", event.target.value)}
                type="text"
                value={form.audienceOrReviewer}
              />
            </label>
            <label>
              AI touchpoints
              <textarea
                onChange={(event) => updateForm("aiTouchpoints", event.target.value)}
                rows={3}
                value={form.aiTouchpoints}
              />
            </label>
            <label>
              Risk if wrong
              <textarea
                onChange={(event) => updateForm("riskIfWrong", event.target.value)}
                rows={3}
                value={form.riskIfWrong}
              />
            </label>
            <label>
              Human reviewer role
              <input
                onChange={(event) => updateForm("humanReviewerRole", event.target.value)}
                type="text"
                value={form.humanReviewerRole}
              />
            </label>
          </div>
        </div>

        <div className="simulator-output">
          <div className="receipt-preview-header">
            <div>
              <span className="mono-label gold">SAMPLE WORKFLOW RECEIPT</span>
              <h2>{simulation.templateLabel}</h2>
            </div>
            <CapabilityBadge label={simulation.capabilityStatus} />
          </div>

          <section className="simulator-panel workflow-map-panel">
            <PanelTitle index="3" title="Workflow Map" />
            <div className="workflow-map-grid">
              <MapColumn title="Actors" values={simulation.workflowMap.actors} />
              <MapColumn title="AI touchpoints" values={simulation.workflowMap.aiTouchpoints} />
              <MapColumn title="Risk points" values={simulation.workflowMap.riskPoints} />
            </div>
            <div className="review-gates">
              {simulation.workflowMap.reviewGates.map((gate) => (
                <div className="review-gate" key={gate.id}>
                  <span>{gate.label}</span>
                  <strong>{gate.decision.replaceAll("_", " ")}</strong>
                  <p>{gate.notes}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="simulator-panel business-value-panel">
            <PanelTitle index="4" title="Business Value Brief" />
            <ValueGrid values={simulation.businessValue} />
          </section>

          <section className="simulator-panel boundary-panel">
            <PanelTitle index="5" title="Evidence Boundary" />
            <div className="boundary-grid">
              <BoundaryList title="Inside receipt" values={simulation.evidenceBoundary.insideReceipt} />
              <BoundaryList title="Outside receipt" values={simulation.evidenceBoundary.outsideReceipt} />
            </div>
          </section>

          <section className="simulator-panel artifact-panel">
            <PanelTitle index="6" title="Simulated Artifact Trail" />
            <div className="artifact-trail">
              {simulation.artifactTrail.map((artifact) => (
                <article className="artifact-item" key={artifact.id}>
                  <div>
                    <span>{artifact.artifactType}</span>
                    <h3>{artifact.label}</h3>
                  </div>
                  {artifact.simulated ? <small>SIMULATED</small> : <small>CURRENT SAMPLE</small>}
                  <p>{artifact.description}</p>
                </article>
              ))}
            </div>
          </section>

          <section className="receipt-preview-panel">
            <div>
              <span>Boundary notice</span>
              <p>{simulation.receiptPreview.boundaryNotice}</p>
            </div>
            <ReceiptList title="Evidence available" values={simulation.receiptPreview.evidenceAvailable} />
            <ReceiptList title="Human review recorded" values={simulation.receiptPreview.humanReviewRecorded} />
            <ReceiptList title="Supported claim" values={simulation.receiptPreview.supportedClaims} />
            <ReceiptList title="Unsupported claim" values={simulation.receiptPreview.unsupportedClaims} />
          </section>

          <section className="simulator-panel limitations-panel">
            <PanelTitle index="7" title="Limitations" />
            <ul>
              {simulation.limitations.map((limitation) => (
                <li key={limitation}>{limitation}</li>
              ))}
            </ul>
          </section>

          <section className="simulator-next-step">
            <div>
              <span className="mono-label gold">NEXT STEP</span>
              <h2>{simulation.nextStep.ctaLabel}</h2>
              <p>{simulation.nextStep.summary}</p>
            </div>
            <a className="button-primary" href={simulation.nextStep.ctaHref}>
              Request Session
            </a>
          </section>
        </div>
      </div>
    </section>
  );
}

function formFromTemplate(template: WorkflowReceiptTemplate): SimulatorForm {
  return {
    businessGoal: template.defaultInput.businessGoal,
    outputType: template.defaultInput.outputType,
    audienceOrReviewer: template.defaultInput.audienceOrReviewer,
    aiTouchpoints: template.defaultInput.aiTouchpoints.join(", "),
    riskIfWrong: template.defaultInput.riskIfWrong,
    humanReviewerRole: template.defaultInput.humanReviewerRole,
  };
}

function splitTouchpoints(value: string): string[] {
  return value.split(",").map((item) => item.trim()).filter(Boolean);
}

function CapabilityBadge({ label }: { label: string }) {
  return <span className={`capability-badge is-${statusTone[label] ?? "future"}`}>{label}</span>;
}

function PanelTitle({ index, title }: { index: string; title: string }) {
  return (
    <div className="panel-title">
      <span>{index}</span>
      <h3>{title}</h3>
    </div>
  );
}

function MapColumn({ title, values }: { title: string; values: string[] }) {
  return (
    <div className="map-column">
      <span>{title}</span>
      {values.map((value) => <p key={value}>{value}</p>)}
    </div>
  );
}

function ValueGrid({ values }: { values: BusinessValueBrief }) {
  const rows = [
    ["trust value", values.trustValue],
    ["operational value", values.operationalValue],
    ["risk value", values.riskValue],
    ["differentiation value", values.differentiationValue],
  ];

  return (
    <div className="value-grid">
      {rows.map(([label, value]) => (
        <div key={label}>
          <span>{label}</span>
          <p>{value}</p>
        </div>
      ))}
    </div>
  );
}

function BoundaryList({ title, values }: { title: string; values: string[] }) {
  return (
    <div className="boundary-list">
      <strong>{title}</strong>
      <ul>
        {values.map((value) => <li key={value}>{value}</li>)}
      </ul>
    </div>
  );
}

function ReceiptList({ title, values }: { title: string; values: string[] }) {
  return (
    <div className="receipt-list">
      <span>{title}</span>
      <ul>
        {values.map((value) => <li key={value}>{value}</li>)}
      </ul>
    </div>
  );
}
