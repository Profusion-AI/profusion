import {
  type FormEvent,
  type ReactNode,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import WorkflowReceiptSimulator from "./pages/WorkflowReceiptSimulator";

type StatusName =
  | "AUTHENTIC"
  | "ALTERED DISCLOSED"
  | "REVIEW REQUIRED"
  | "EVIDENCE CAPTURED"
  | "HUMAN REVIEW"
  | "AGENTIC REVIEW GAP"
  | "LIMITED CLAIMS"
  | "BLOCKED"
  | "DEGRADED"
  | "NOT IMPLEMENTED";

type TrustStep = {
  label: string;
  title: string;
  desc: string;
  details: string[];
  icon: ReactNode;
};

type LabTab = "Overview" | "Architecture" | "Status";

const statusMap: Record<StatusName, { bg: string; color: string; dot: string }> = {
  AUTHENTIC: { bg: "rgba(47,107,79,0.12)", color: "#2F6B4F", dot: "#2F6B4F" },
  "ALTERED DISCLOSED": {
    bg: "rgba(91,111,149,0.12)",
    color: "#5B6F95",
    dot: "#5B6F95",
  },
  "REVIEW REQUIRED": {
    bg: "rgba(199,168,107,0.15)",
    color: "#9A7A3A",
    dot: "#C7A86B",
  },
  "EVIDENCE CAPTURED": {
    bg: "rgba(47,107,79,0.12)",
    color: "#2F6B4F",
    dot: "#2F6B4F",
  },
  "HUMAN REVIEW": {
    bg: "rgba(199,168,107,0.15)",
    color: "#9A7A3A",
    dot: "#C7A86B",
  },
  "AGENTIC REVIEW GAP": {
    bg: "rgba(91,111,149,0.12)",
    color: "#5B6F95",
    dot: "#5B6F95",
  },
  "LIMITED CLAIMS": {
    bg: "rgba(91,111,149,0.12)",
    color: "#5B6F95",
    dot: "#5B6F95",
  },
  BLOCKED: { bg: "rgba(143,47,47,0.10)", color: "#8F2F2F", dot: "#8F2F2F" },
  DEGRADED: { bg: "rgba(166,106,44,0.12)", color: "#A66A2C", dot: "#A66A2C" },
  "NOT IMPLEMENTED": {
    bg: "rgba(110,116,111,0.10)",
    color: "#6E746F",
    dot: "#6E746F",
  },
};

const receiptFields = [
  { key: "workflow_id", value: "wf_agentic_change_review_7F9A" },
  { key: "spec_boundary", value: "customer_visible_change" },
  { key: "artifacts_captured", value: "spec · diff · tests · review" },
  { key: "verification_tax", value: "measured_before_scale" },
  { key: "review_gate", value: "human_reviewed" },
  { key: "claims_supported", value: "process_evidence_only" },
];

const problemCards = [
  {
    icon: <EyeIcon />,
    heading: "AI moved the bottleneck from production to verification.",
    body: "Coding agents and AI assistants can generate code, content, analysis, and decisions faster than teams can reliably review them.",
    status: "REVIEW REQUIRED" as StatusName,
  },
  {
    icon: <ReviewIcon />,
    heading: "Review queues absorb the productivity gain.",
    body: "Bigger PRs, generated changes, and scattered artifacts turn senior people into validators unless the workflow captures evidence as it moves.",
    status: "AGENTIC REVIEW GAP" as StatusName,
  },
  {
    icon: <ShieldIcon />,
    heading: "Specification is now a governance boundary.",
    body: "The question is not only whether the model can produce work. It is whether the team defined what reliable enough means before approval.",
    status: "HUMAN REVIEW" as StatusName,
  },
  {
    icon: <ReceiptIcon />,
    heading: "The same gap appears outside engineering.",
    body: "AI content, synthetic media, recruiting workflows, and client-facing automation all need receipts that show what happened and what the evidence does not prove.",
    status: "LIMITED CLAIMS" as StatusName,
  },
];

const researchSignals = [
  {
    source: "arXiv PRP paper",
    metric: "v1",
    label: "specification discipline as the bottleneck",
    body: "A May 2026 preprint frames the reliability constraint as specification discipline, not model capability. Treat it as a design framework, not settled science.",
    href: "https://arxiv.org/html/2605.01160v1",
  },
  {
    source: "Faros AI telemetry",
    metric: "98%",
    label: "more merged pull requests",
    body: "High-adoption teams saw more merged PRs, but review time rose 91%, average PR size rose 154%, and bugs per developer rose 9%.",
    href: "https://www.faros.ai/blog/ai-software-engineering",
  },
  {
    source: "Google DORA",
    metric: "7.2%",
    label: "lower delivery stability",
    body: "For every 25% increase in AI adoption, DORA associated AI with lower throughput and lower delivery stability.",
    href: "https://dora.dev/ai/gen-ai-report/report/",
  },
  {
    source: "METR study",
    metric: "19%",
    label: "slower on familiar mature codebases",
    body: "Experienced developers in a METR study took longer with AI on mature repositories they already knew well.",
    href: "https://arxiv.org/abs/2507.09089",
  },
];

const proofWords = [
  "engineering teams",
  "coding-agent teams",
  "AI ops teams",
  "content ops",
  "recruiters",
  "automation teams",
  "risk teams",
  "executives",
];

const trustSteps: TrustStep[] = [
  {
    label: "Map",
    icon: <DeclareIcon />,
    title: "Define the workflow and risk boundary",
    desc: "Start with one AI-assisted or agentic workflow and make clear what is inside the pilot, what can fail, and who needs to approve the output.",
    details: ["workflow_scope", "risk_context", "approval_owner"],
  },
  {
    label: "Capture",
    icon: <EnforceIcon />,
    title: "Capture specs, artifacts, and tests",
    desc: "Preserve the specification, prompts, generated output, diffs, QA checks, test results, review notes, and approvals needed to reconstruct the work.",
    details: ["spec_boundary", "generated_outputs", "test_evidence"],
  },
  {
    label: "Review",
    icon: <WatermarkIcon />,
    title: "Make verification tax visible",
    desc: "Track where review time, rework, QA failures, approval latency, or senior-engineer validation burden enters the workflow.",
    details: ["review_gate", "rework_signal", "verification_tax"],
  },
  {
    label: "Bound",
    icon: <RecordIcon />,
    title: "State what the evidence supports",
    desc: "The receipt describes supported claims and known limitations so teams do not imply reliability, compliance, or assurance they have not actually proven.",
    details: ["supported_claims", "known_limits", "non_claims"],
  },
  {
    label: "Receipt",
    icon: <ReviewIcon />,
    title: "Produce a productivity-reliability receipt",
    desc: "Generate a plain-English packet that shows what happened, what passed, who reviewed it, and what remains uncertain before the workflow scales.",
    details: ["receipt_packet", "review_status", "delivery_record"],
  },
];

const governanceLevels = [
  {
    level: "Low risk",
    title: "Lightweight review",
    body: "Small, reversible AI work can move with a reviewer and basic artifact capture.",
  },
  {
    level: "Medium risk",
    title: "Written specification",
    body: "Client-visible or recurring work needs a specification boundary and targeted verification.",
  },
  {
    level: "Cross-cutting",
    title: "Executable checks",
    body: "Shared systems need tests, QA evidence, and approval gates before the output scales.",
  },
  {
    level: "High stakes",
    title: "Constitution plus receipt",
    body: "Security, privacy, finance, recruiting, or production-impacting workflows need constraints and receipt-level evidence.",
  },
];

const labOverview = [
  {
    label: "AI CODING AGENT RELIABILITY",
    title: "Make agentic engineering work reviewable enough to approve.",
    desc: "Map the spec boundary, generated changes, tests, review gates, rework signals, and approval evidence around one coding-agent workflow.",
  },
  {
    label: "AI CONTENT & MEDIA APPROVAL",
    title: "Show how client-facing AI work was reviewed.",
    desc: "Capture the brief, generated assets, QA checks, revisions, limitations, and human approval trail before public or client delivery.",
  },
  {
    label: "SYNTHETIC MEDIA RISK",
    title: "Make synthetic media reviewable before it reaches clients or the public.",
    desc: "Prototype disclosure, artifact trails, policy decisions, and receipt language for altered or AI-generated media.",
  },
  {
    label: "RECRUITING & STAFFING",
    title: "Keep AI-mediated work reviewable.",
    desc: "Prototype evidence receipts for work samples, contractor readiness, and recruiter workflows without automated ranking or hiring decisions.",
  },
  {
    label: "CLIENT-FACING AUTOMATION",
    title: "Give buyers an evidence layer.",
    desc: "Help AI automation agencies and consultants show where workflow evidence, human judgment, and limitations enter the system.",
  },
];

const architectureLayers = [
  "AI-Assisted or Agentic Workflow",
  "Profusion Reliability Evidence Layer",
  "Spec + Artifact + Test + Review Capture",
  "Engineering / Client / Risk Approval",
];

const statusItems = [
  ["Narrative signal", "Agentic engineering and coding-agent reliability"],
  ["Implemented proof", "AI-assisted content/media receipt: content_video_receipt in media_trust"],
  ["Future integration concept", "MCP and coding-agent evidence capture"],
  ["Current boundary", "Process evidence, not compliance or correctness certification"],
];

const services = [
  {
    num: "01",
    title: "AI Workflow Reliability Pilot",
    tagline: "One workflow, one reliability gap, one receipt.",
    desc: "Govern one AI-assisted or agentic workflow with a specification boundary, artifact capture, review gates, verification-tax signals, and a workflow receipt.",
    tags: ["Agentic Workflows", "Reliability", "Receipts"],
  },
  {
    num: "02",
    title: "Productivity-Reliability Diagnostic",
    tagline: "Find where AI output stops being dependable work.",
    desc: "Map how AI changes review time, PR size, QA failures, approval latency, rework, and senior-person verification burden before scaling the workflow.",
    tags: ["Verification Tax", "Risk Profile", "Scale Decision"],
  },
  {
    num: "03",
    title: "Workflow Receipt Prototyping",
    tagline: "Buyer-readable packets for AI work.",
    desc: "Design plain-English receipts for coding-agent outputs, AI-assisted content, synthetic media, recruiting workflows, and client-facing automation.",
    tags: ["Artifacts", "Reviews", "Limitations"],
  },
  {
    num: "04",
    title: "AI Coding Agent Reliability Pilot",
    tagline: "Product wedge, architecture, launch narrative.",
    desc: "For AI-forward engineering teams, map one coding-agent workflow around spec boundaries, review gates, verification tax, and receipt-ready evidence.",
    tags: ["Strategy", "Architecture", "Narrative"],
  },
];

const clients = [
  "AI-forward engineering and product teams adopting coding agents in mature codebases with active CI/CD and customer-facing reliability pressure.",
  "AI content and synthetic media teams that need review gates, artifact trails, and approval receipts.",
  "Recruiting and staffing firms exploring AI-assisted workflows without automated ranking or black-box hiring decisions.",
  "AI automation agencies and consultants whose clients need evidence that a workflow is governed.",
  "Governance, risk, and operations leaders who need workflow-level proof that policy became practice.",
];

const principles = [
  {
    verb: "Map",
    subject: "the workflow.",
    body: "The reliability layer starts with one concrete AI-assisted workflow, not a generic responsible-AI claim.",
  },
  {
    verb: "Specify",
    subject: "the boundary.",
    body: "Teams need to define what reliable enough means before they ask humans to approve generated work.",
  },
  {
    verb: "Capture",
    subject: "the evidence.",
    body: "Specs, artifacts, tests, review notes, approvals, and limitations should survive outside scattered tools and memory.",
  },
  {
    verb: "Preserve",
    subject: "human judgment.",
    body: "The point is not to automate responsibility away. The point is to show where human review entered the process.",
  },
  {
    verb: "Limit",
    subject: "the claim.",
    body: "A credible receipt says what the evidence supports and what remains outside the captured boundary.",
  },
  {
    verb: "Never overclaim",
    subject: "certainty.",
    body: "A trust system loses credibility the moment marketing outruns the evidence. We keep those two aligned.",
  },
];

function WordMark() {
  const [charStates, setCharStates] = useState<number[]>([]);
  const timeouts = useRef<number[]>([]);
  const chars = "Profusion AI".split("");

  useEffect(() => {
    return () => {
      timeouts.current.forEach((timeout) => window.clearTimeout(timeout));
    };
  }, []);

  function trigger() {
    timeouts.current.forEach((timeout) => window.clearTimeout(timeout));
    timeouts.current = [];
    setCharStates(chars.map(() => 0));

    chars.forEach((_, index) => {
      const rise = window.setTimeout(() => {
        setCharStates((previous) => {
          const next = [...previous];
          next[index] = 1;
          return next;
        });
      }, index * 55);
      const settle = window.setTimeout(() => {
        setCharStates((previous) => {
          const next = [...previous];
          next[index] = 2;
          return next;
        });
      }, index * 55 + 420);
      const rest = window.setTimeout(() => {
        setCharStates((previous) => {
          const next = [...previous];
          next[index] = 0;
          return next;
        });
      }, index * 55 + 900);
      timeouts.current.push(rise, settle, rest);
    });
  }

  return (
    <a className="wordmark" href="#top" onMouseEnter={trigger}>
      <LogoIcon />
      <span className="wordmark-text" aria-label="Profusion AI">
        {chars.map((char, index) => (
          <span className={`char phase-${charStates[index] ?? 0}`} key={`${char}-${index}`}>
            {char === " " ? "\u00a0" : char}
          </span>
        ))}
      </span>
    </a>
  );
}

function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const links = [
    { label: "Workflow", href: "#trust-layer" },
    { label: "Use Cases", href: "#video-lab" },
    { label: "Services", href: "#services" },
    { label: "Principles", href: "#principles" },
  ];

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    onScroll();
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <nav className={scrolled ? "site-nav is-scrolled" : "site-nav"}>
      <div className="nav-inner">
        <WordMark />
        <div className="nav-links">
          {links.map((link) => (
            <a href={link.href} key={link.label}>
              {link.label}
            </a>
          ))}
          <a className="nav-contact" href="#contact">
            Contact
          </a>
        </div>
      </div>
    </nav>
  );
}

function ReceiptCard({ animated = false }: { animated?: boolean }) {
  const [step, setStep] = useState(0);

  useEffect(() => {
    if (!animated) return undefined;
    const interval = window.setInterval(() => {
      setStep((current) => (current + 1) % receiptFields.length);
    }, 2200);
    return () => window.clearInterval(interval);
  }, [animated]);

  return (
    <div className="receipt-card">
      <div className="receipt-card-header">
        <span>RELIABILITY RECEIPT</span>
        <span className="recorded-pill">● REVIEWABLE</span>
      </div>
      <div className="receipt-fields">
        {receiptFields.map((field, index) => (
          <div
            className={animated && index > step ? "receipt-field is-pending" : "receipt-field"}
            key={field.key}
          >
            <span>{field.key}</span>
            <strong>{field.value}</strong>
          </div>
        ))}
      </div>
      <div className="receipt-status-row">
        <Pill status="EVIDENCE CAPTURED" />
        <Pill status="HUMAN REVIEW" />
      </div>
    </div>
  );
}

function ScrollReveal({
  children,
  className = "",
  delay = 0,
}: {
  children: ReactNode;
  className?: string;
  delay?: number;
}) {
  const elementRef = useRef<HTMLDivElement | null>(null);
  const [isVisible, setIsVisible] = useState(false);

  useLayoutEffect(() => {
    const element = elementRef.current;
    if (!element) return undefined;

    const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
    const initialRect = element.getBoundingClientRect();
    setIsVisible(initialRect.top < viewportHeight * 0.9 && initialRect.bottom > viewportHeight * 0.1);

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsVisible(entry.isIntersecting);
      },
      {
        rootMargin: "0px 0px -12% 0px",
        threshold: 0.18,
      }
    );

    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      className={`scroll-reveal${isVisible ? " is-visible" : ""}${className ? ` ${className}` : ""}`}
      ref={elementRef}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  );
}

function Hero() {
  return (
    <section className="hero" id="top">
      <div className="grid-texture" aria-hidden="true" />
      <ScrollReveal className="hero-inner">
        <div className="hero-copy">
          <div className="hero-badge">
            <span />
            AI WORKFLOW RELIABILITY PRACTICE
          </div>
          <h1>
            Close the reliability
            <br />
            <span>gap in AI-assisted</span>
            <br />
            work.
          </h1>
          <p className="hero-lede">
            AI agents can generate code, content, analysis, and workflow outputs faster than teams
            can reliably review them. Profusion helps organizations capture specs, artifacts, tests,
            reviews, approvals, and limitations into workflow receipts that make AI-assisted work
            inspectable.
          </p>
          <p className="hero-subcopy">
            Profusion does not make AI produce more work. Profusion makes AI-produced work
            reviewable enough to use. More output is not the same as dependable work.
          </p>
          <div className="hero-actions">
            <a className="button-primary is-light" href="#contact">
              Start with One Workflow
            </a>
            <a className="button-secondary is-light" href="#trust-layer">
              See the Reliability Method
            </a>
          </div>
        </div>
        <div className="hero-visual">
          <div className="hero-brand-lockup" aria-hidden="true">
            <img
              alt=""
              loading="eager"
              src="/widelogo.png"
            />
          </div>
          <div className="hero-receipt">
            <div className="receipt-glow" aria-hidden="true" />
            <ReceiptCard animated />
          </div>
        </div>
      </ScrollReveal>
      <div className="hero-fade" aria-hidden="true" />
    </section>
  );
}

function Problem() {
  return (
    <section className="section section-bone" id="problem">
      <ScrollReveal className="section-inner">
        <div className="section-heading narrow">
          <Eyebrow>Productivity-Reliability Paradox</Eyebrow>
          <h2
            aria-label="AI is producing work faster than engineering teams, coding-agent teams, AI operations teams, content operations, recruiters, automation teams, risk teams, and executives can reliably approve it."
            className="proof-headline"
          >
            AI is producing work faster than{" "}
            <RotatingProofWord />
            <br />
            <span>can reliably approve it.</span>
          </h2>
          <p>
            Organizations are buying AI productivity, then paying for it again through verification
            overhead, larger review queues, rework, reliability risk, and weak process evidence.
          </p>
        </div>
        <div className="problem-grid">
          {problemCards.map((card) => (
            <article className="problem-card" key={card.heading}>
              <div className="icon-wrap">{card.icon}</div>
              <h3>{card.heading}</h3>
              <p>{card.body}</p>
              <Pill status={card.status} />
            </article>
          ))}
        </div>
        <div className="research-panel">
          <div className="research-intro">
            <span className="mono-label gold">RESEARCH SIGNAL</span>
            <h3>AI has moved the bottleneck from production to verification.</h3>
            <p>
              The emerging evidence is not a reason to reject AI. It is a reason to govern the
              handoff from generated output to human approval with specifications, artifacts,
              tests, review gates, and receipts.
            </p>
          </div>
          <div className="research-grid">
            {researchSignals.map((signal) => (
              <a className="research-card" href={signal.href} key={signal.source} rel="noreferrer" target="_blank">
                <span>{signal.source}</span>
                <strong>{signal.metric}</strong>
                <h3>{signal.label}</h3>
                <p>{signal.body}</p>
              </a>
            ))}
          </div>
        </div>
      </ScrollReveal>
    </section>
  );
}

function RotatingProofWord() {
  const [step, setStep] = useState(0);
  const [canAnimate, setCanAnimate] = useState(true);
  const visibleWords = [...proofWords, proofWords[0]];

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return undefined;
    }

    const interval = window.setInterval(() => {
      setCanAnimate(true);
      setStep((current) => current + 1);
    }, 2500);

    return () => window.clearInterval(interval);
  }, []);

  function handleTransitionEnd() {
    if (step !== proofWords.length) return;

    setCanAnimate(false);
    setStep(0);
    window.requestAnimationFrame(() => {
      window.requestAnimationFrame(() => setCanAnimate(true));
    });
  }

  return (
    <span aria-hidden="true" className="rotating-word">
      <span
        className={canAnimate ? "rotating-word-track" : "rotating-word-track no-transition"}
        onTransitionEnd={handleTransitionEnd}
        style={{ transform: `translateY(-${step * 100}%)` }}
      >
        {visibleWords.map((word, index) => (
          <span className="rotating-word-item" key={`${word}-${index}`}>
            {word}
          </span>
        ))}
      </span>
    </span>
  );
}

function TrustLayer() {
  const [activeIndex, setActiveIndex] = useState(0);
  const activeStep = trustSteps[activeIndex];

  return (
    <section className="section section-parchment" id="trust-layer">
      <ScrollReveal className="section-inner">
        <div className="section-heading narrow">
          <Eyebrow>Workflow Trust Layer</Eyebrow>
          <h2>A reliability layer for high-risk AI-assisted work.</h2>
          <p>
            The goal is not generic AI governance. The goal is to make AI-assisted and agentic
            workflows inspectable: what was specified, what the system produced, what evidence
            exists, what humans reviewed, what changed, and what the receipt does and does not prove.
          </p>
        </div>

        <div className="trust-flow" aria-label="Trust layer workflow">
          {trustSteps.map((step, index) => (
            <div className="trust-node-wrap" key={step.label}>
              <button
                aria-pressed={activeIndex === index}
                className={activeIndex === index ? "trust-step is-active" : "trust-step"}
                onClick={() => setActiveIndex(index)}
                type="button"
              >
                <span className="trust-icon">{step.icon}</span>
                <span>{step.label}</span>
                {activeIndex === index ? <i aria-hidden="true" /> : null}
              </button>
              {index < trustSteps.length - 1 ? (
                <span
                  className={index < activeIndex ? "trust-connector is-active" : "trust-connector"}
                />
              ) : null}
            </div>
          ))}
        </div>

        <div className="trust-detail">
          <div>
            <div className="detail-icon">{activeStep.icon}</div>
            <span className="mono-label">STEP {activeIndex + 1} OF 5</span>
            <h3>{activeStep.title}</h3>
            <p>{activeStep.desc}</p>
          </div>
          <div className="detail-receipt">
            {activeStep.details.map((detail) => (
              <div key={detail}>
                <span>{detail}</span>
                <strong>recorded</strong>
              </div>
            ))}
          </div>
        </div>

        <div className="governance-guide">
          <div className="section-heading narrow">
            <Eyebrow>Specification Governance</Eyebrow>
            <h2>Match the evidence burden to the failure consequence.</h2>
            <p>
              Low-risk AI work does not need the same controls as production, security, privacy,
              recruiting, financial, or client-facing work. Profusion starts by classifying one
              workflow, then adds only the review infrastructure the risk justifies.
            </p>
          </div>
          <div className="governance-grid">
            {governanceLevels.map((item) => (
              <article className="governance-card" key={item.level}>
                <span>{item.level}</span>
                <h3>{item.title}</h3>
                <p>{item.body}</p>
              </article>
            ))}
          </div>
        </div>
      </ScrollReveal>
    </section>
  );
}

function VideoLab() {
  const [tab, setTab] = useState<LabTab>("Overview");
  const tabs: LabTab[] = ["Overview", "Architecture", "Status"];

  const content = useMemo(() => {
    if (tab === "Architecture") {
      return (
        <div className="architecture-panel">
          <span className="mono-label gold">SYSTEM ARCHITECTURE</span>
          <div className="architecture-stack">
            {architectureLayers.map((layer, index) => (
              <div className={index === 1 ? "architecture-layer is-active" : "architecture-layer"} key={layer}>
                <span>{layer}</span>
                <strong>{index === 1 ? "control point" : "context"}</strong>
              </div>
            ))}
          </div>
          <p className="architecture-note">
            <strong>Agentic workflow support:</strong> Profusion adds a receipt layer between
            agentic work and human approval. Planned integration path: MCP-compatible tools for
            capturing workflow events, specs, artifacts, test results, review checkpoints, and
            receipt metadata from agentic environments. Current public proof remains the
            content/media receipt path until that engineering fixture exists.
          </p>
        </div>
      );
    }

    if (tab === "Status") {
      return (
        <div className="status-panel">
          {statusItems.map(([label, value]) => (
            <div className="status-row" key={label}>
              <span>{label}</span>
              <strong>{value}</strong>
            </div>
          ))}
        </div>
      );
    }

    return (
      <div className="lab-card-grid">
        {labOverview.map((item) => (
          <article className="lab-card" key={item.label}>
            <span>{item.label}</span>
            <h3>{item.title}</h3>
            <p>{item.desc}</p>
          </article>
        ))}
      </div>
    );
  }, [tab]);

  return (
    <section className="section section-bone" id="video-lab">
      <ScrollReveal className="section-inner">
        <div className="section-heading narrow">
          <Eyebrow>Where We Start</Eyebrow>
          <h2>Start where AI productivity is creating review burden.</h2>
          <p>
            Coding agents are the sharpest signal because the review cost is visible in PRs, tests,
            rework, and release risk. The same pattern lands near-term in AI content, synthetic
            media, recruiting, and client-facing automation where final output is not enough.
          </p>
        </div>

        <div className="lab-status">
          <span />
          Pilot engagements begin with one workflow, one reliability question, and one reviewable receipt.
        </div>

        <div className="tabs" role="tablist" aria-label="Workflow trust use case tabs">
          {tabs.map((item) => (
            <button
              aria-selected={tab === item}
              className={tab === item ? "tab is-active" : "tab"}
              key={item}
              onClick={() => setTab(item)}
              role="tab"
              type="button"
            >
              {item}
            </button>
          ))}
        </div>

        <div className="tab-panel" role="tabpanel">
          {content}
        </div>
      </ScrollReveal>
    </section>
  );
}

function Services() {
  return (
    <section className="section section-parchment" id="services">
      <ScrollReveal className="section-inner">
        <div className="section-heading narrow">
          <Eyebrow>Consulting Services</Eyebrow>
          <h2>Turn AI productivity into reviewable evidence.</h2>
        </div>
        <div className="services-grid">
          {services.map((service) => (
            <article className="service-card" key={service.num}>
              <span>{service.num}</span>
              <h3>{service.title}</h3>
              <p className="tagline">{service.tagline}</p>
              <p>{service.desc}</p>
              <div>
                {service.tags.map((tag) => (
                  <small key={tag}>{tag}</small>
                ))}
              </div>
            </article>
          ))}
        </div>
      </ScrollReveal>
    </section>
  );
}

function IdealClients() {
  return (
    <section className="section section-bone" id="ideal-clients">
      <ScrollReveal className="section-inner clients-grid">
        <div>
          <Eyebrow>Ideal Clients</Eyebrow>
          <h2>For teams whose AI work needs to survive review.</h2>
          <p>
            We work best with teams who already feel the gap between moving faster with AI and
            proving the work was specified, tested, reviewed, approved, and honestly bounded.
          </p>
        </div>
        <div className="client-list">
          {clients.map((client, index) => (
            <div className="client-item" key={client}>
              <span>0{index + 1}</span>
              <p>{client}</p>
            </div>
          ))}
        </div>
      </ScrollReveal>
    </section>
  );
}

function Principles() {
  return (
    <section className="section principles-section" id="principles">
      <ScrollReveal className="section-inner">
        <div className="section-heading narrow">
          <Eyebrow light>Operating Principles</Eyebrow>
          <h2>Reliability is not a vibe.</h2>
          <p>It is workflow scope, specification discipline, artifact capture, human review, limitations, and receipts.</p>
        </div>
        <div className="principles-list">
          {principles.map((principle) => (
            <div className="principle-row" key={principle.verb}>
              <div>
                <strong>{principle.verb}</strong>
                <span>{principle.subject}</span>
              </div>
              <p>{principle.body}</p>
            </div>
          ))}
        </div>
      </ScrollReveal>
    </section>
  );
}

function Contact() {
  const [form, setForm] = useState({ name: "", org: "", email: "", context: "" });
  const [status, setStatus] = useState<"idle" | "submitting" | "sent" | "error">("idle");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const target = event.currentTarget;
    if (!form.name.trim() || !form.email.trim() || !target.checkValidity()) {
      target.reportValidity();
      return;
    }

    setStatus("submitting");

    const formData = new FormData(target);
    const body = new URLSearchParams(
      Array.from(formData.entries()).map(([key, value]) => [key, String(value)]),
    );

    try {
      const response = await fetch("/__forms.html", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });

      if (!response.ok) {
        throw new Error(`Netlify Forms returned ${response.status}`);
      }

      setStatus("sent");
    } catch {
      setStatus("error");
    }
  }

  function updateField(field: keyof typeof form, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  return (
    <section className="section contact-section" id="contact">
      <ScrollReveal className="section-inner contact-grid">
        <div>
          <Eyebrow light>Contact</Eyebrow>
          <h2>Start with one workflow where review is the bottleneck.</h2>
          <p>
            We work with a small number of teams at a time. If one AI-assisted or agentic workflow
            is producing output faster than your team can confidently approve it, start there.
          </p>
          <div className="contact-notes">
            <ContactNote icon={<ReceiptIcon small />} text="First session: map one workflow, its spec boundary, and its verification tax." />
            <ContactNote icon={<ShieldIcon small />} text="Work product: reliability receipts, review gates, and limitation language." />
            <ContactNote icon={<EyeIcon small />} text="No long-term lock-in. Engagements are scoped around a defined workflow." />
          </div>
        </div>

        {status !== "sent" ? (
          <form
            className="contact-form"
            data-netlify="true"
            method="POST"
            name="trust-session"
            netlify-honeypot="bot-field"
            onSubmit={handleSubmit}
          >
            <input type="hidden" name="form-name" value="trust-session" />
            <input
              type="hidden"
              name="subject"
              value="Profusion AI workflow reliability session request"
            />
            <p hidden>
              <label>
                Do not fill this out
                <input name="bot-field" tabIndex={-1} />
              </label>
            </p>
            <span className="mono-label gold">WORKFLOW RELIABILITY SESSION REQUEST</span>
            <label>
              Name
              <input
                name="name"
                onChange={(event) => updateField("name", event.target.value)}
                placeholder="Your name"
                required
                type="text"
                value={form.name}
              />
            </label>
            <label>
              Organization
              <input
                name="org"
                onChange={(event) => updateField("org", event.target.value)}
                placeholder="Company or institution"
                type="text"
                value={form.org}
              />
            </label>
            <label>
              Email
              <input
                name="email"
                onChange={(event) => updateField("email", event.target.value)}
                placeholder="Work email"
                required
                type="email"
                value={form.email}
              />
            </label>
            <label>
              Workflow context
              <textarea
                name="context"
                onChange={(event) => updateField("context", event.target.value)}
                placeholder="Briefly describe the AI-assisted or agentic workflow, output, review burden, or reliability problem..."
                rows={4}
                value={form.context}
              />
            </label>
            {status === "error" ? (
              <p className="form-error" role="alert">
                The request could not be sent. Please try again.
              </p>
            ) : null}
            <button disabled={status === "submitting"} type="submit">
              {status === "submitting" ? "Sending..." : "Request a Session"}
            </button>
          </form>
        ) : (
          <div className="confirmation" role="status">
            <CheckIcon />
            <span>REQUEST RECORDED</span>
            <h3>We&apos;ll be in touch.</h3>
            <p>
              Thank you, {form.name}. We review all requests personally and will respond within two
              business days.
            </p>
          </div>
        )}
      </ScrollReveal>
    </section>
  );
}

function ContactNote({ icon, text }: { icon: ReactNode; text: string }) {
  return (
    <div className="contact-note">
      <span>{icon}</span>
      <p>{text}</p>
    </div>
  );
}

function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-mark">
          <LogoIcon />
          <span>Profusion AI</span>
        </div>
        <span>Reliability evidence for AI-assisted work. © 2026</span>
        <div className="footer-links">
          <a href="#trust-layer">Workflow Trust</a>
          <a href="#video-lab">Use Cases</a>
          <a href="#services">Services</a>
          <a href="#contact">Contact</a>
        </div>
      </div>
    </footer>
  );
}

function Eyebrow({ children, light = false }: { children: string; light?: boolean }) {
  return <div className={light ? "eyebrow is-light" : "eyebrow"}>{children}</div>;
}

function Pill({ status }: { status: StatusName }) {
  const style = statusMap[status];

  return (
    <span className="status-pill" style={{ background: style.bg, color: style.color }}>
      <span style={{ background: style.dot }} />
      {status}
    </span>
  );
}

function LogoIcon() {
  return <img alt="" aria-hidden="true" className="logo-icon" src="/aperture-logo-alone.png" />;
}

function IconSvg({
  children,
  small = false,
}: {
  children: ReactNode;
  small?: boolean;
}) {
  return (
    <svg
      aria-hidden="true"
      className={small ? "inline-icon is-small" : "inline-icon"}
      fill="none"
      viewBox="0 0 28 28"
    >
      {children}
    </svg>
  );
}

function EyeIcon({ small = false }: { small?: boolean }) {
  return (
    <IconSvg small={small}>
      <ellipse cx="14" cy="14" rx="11" ry="7" />
      <circle cx="14" cy="14" r="3.5" />
    </IconSvg>
  );
}

function ShieldIcon({ small = false }: { small?: boolean }) {
  return (
    <IconSvg small={small}>
      <path d="M14 3 4 7v7c0 5.5 4.4 10.6 10 12 5.6-1.4 10-6.5 10-12V7L14 3z" />
      <path d="m10 14 3 3 5-5" />
    </IconSvg>
  );
}

function ReceiptIcon({ small = false }: { small?: boolean }) {
  return (
    <IconSvg small={small}>
      <rect height="22" rx="3" width="18" x="5" y="3" />
      <line x1="9" x2="19" y1="9" y2="9" />
      <line x1="9" x2="19" y1="13" y2="13" />
      <line x1="9" x2="15" y1="17" y2="17" />
    </IconSvg>
  );
}

function DeclareIcon() {
  return (
    <IconSvg>
      <circle cx="14" cy="10" r="5" />
      <path d="M6 24c0-4.4 3.6-8 8-8s8 3.6 8 8" />
      <line x1="14" x2="14" y1="3" y2="1" />
    </IconSvg>
  );
}

function EnforceIcon() {
  return (
    <IconSvg>
      <path d="M14 3 4 7v7c0 5.5 4.4 10.6 10 12 5.6-1.4 10-6.5 10-12V7L14 3z" />
      <line x1="10" x2="18" y1="14" y2="14" />
    </IconSvg>
  );
}

function WatermarkIcon() {
  return (
    <IconSvg>
      <rect height="14" rx="3" width="22" x="3" y="7" />
      <path d="m8 14 3 3 6-6" />
      <line strokeDasharray="2 2" x1="3" x2="25" y1="11" y2="11" />
    </IconSvg>
  );
}

function RecordIcon() {
  return (
    <IconSvg>
      <circle cx="14" cy="14" r="11" />
      <circle className="icon-fill-soft" cx="14" cy="14" r="5" />
      <circle className="icon-fill" cx="14" cy="14" r="2" />
    </IconSvg>
  );
}

function ReviewIcon() {
  return (
    <IconSvg>
      <path d="M3 5h22M3 10h16M3 15h18M3 20h12" />
      <circle cx="22" cy="20" r="4" />
      <line x1="25" x2="27" y1="23" y2="25" />
    </IconSvg>
  );
}

function CheckIcon() {
  return (
    <svg aria-hidden="true" className="check-icon" fill="none" viewBox="0 0 48 48">
      <circle cx="24" cy="24" r="23" />
      <path d="m14 24 7 7 13-14" />
    </svg>
  );
}

export default function App() {
  const isSimulatorRoute = ["/workflow-receipt-simulator", "/simulator"].includes(
    window.location.pathname,
  );

  return (
    <>
      <Nav />
      <main>
        {isSimulatorRoute ? (
          <WorkflowReceiptSimulator />
        ) : (
          <>
            <Hero />
            <Problem />
            <TrustLayer />
            <VideoLab />
            <Services />
            <IdealClients />
            <Principles />
            <Contact />
          </>
        )}
      </main>
      <Footer />
    </>
  );
}
