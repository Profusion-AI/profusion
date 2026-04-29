import {
  type FormEvent,
  type ReactNode,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";

type StatusName =
  | "AUTHENTIC"
  | "ALTERED DISCLOSED"
  | "REVIEW REQUIRED"
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
  BLOCKED: { bg: "rgba(143,47,47,0.10)", color: "#8F2F2F", dot: "#8F2F2F" },
  DEGRADED: { bg: "rgba(166,106,44,0.12)", color: "#A66A2C", dot: "#A66A2C" },
  "NOT IMPLEMENTED": {
    bg: "rgba(110,116,111,0.10)",
    color: "#6E746F",
    dot: "#6E746F",
  },
};

const receiptFields = [
  { key: "session_id", value: "vt_20260428_7F9A" },
  { key: "declared_mode", value: "altered_disclosed" },
  { key: "policy_decision", value: "allow_with_watermark" },
  { key: "watermark_state", value: "enforced" },
  { key: "runtime_state", value: "local_cpu_degraded" },
  { key: "outcome", value: "completed · degraded_runtime" },
];

const problemCards = [
  {
    icon: <EyeIcon />,
    heading: "Presence is no longer proof.",
    body: "A live webcam feed can be altered before it reaches a meeting. The institution cannot trust what it sees.",
    status: "ALTERED DISCLOSED" as StatusName,
  },
  {
    icon: <ShieldIcon />,
    heading: "Disclosure is inconsistent.",
    body: "Most workflows do not force a clear declaration of synthetic or altered media before a session begins.",
    status: "REVIEW REQUIRED" as StatusName,
  },
  {
    icon: <ReceiptIcon />,
    heading: "Evidence is missing.",
    body: "After the call, organizations often lack a durable record of what was declared, enforced, and reviewed.",
    status: "NOT IMPLEMENTED" as StatusName,
  },
];

const proofWords = [
  "Institutions",
  "Enterprises",
  "Companies",
  "Interviewers",
  "Schools",
  "Governments",
];

const trustSteps: TrustStep[] = [
  {
    label: "Declare",
    icon: <DeclareIcon />,
    title: "Attestation before entry",
    desc: "A session does not enter a high-risk workflow until authenticity or alteration has been explicitly declared by the participant.",
    details: ["participant_state", "declared_mode", "source_context"],
  },
  {
    label: "Enforce",
    icon: <EnforceIcon />,
    title: "Policy-driven access",
    desc: "Policy rules determine whether a declared state is permitted, requires review, or must be blocked before proceeding.",
    details: ["policy_rules", "access_decision", "review_route"],
  },
  {
    label: "Watermark",
    icon: <WatermarkIcon />,
    title: "Visible disclosure layer",
    desc: "Declared synthetic or altered sessions receive a visible watermark, making the disclosed state persistent in recordings.",
    details: ["visible_overlay", "metadata_hint", "recording_state"],
  },
  {
    label: "Record",
    icon: <RecordIcon />,
    title: "Durable audit receipt",
    desc: "Every session generates a structured receipt — session ID, declared mode, policy decision, watermark state, timestamp, and runtime.",
    details: ["session_id", "policy_decision", "runtime_context"],
  },
  {
    label: "Review",
    icon: <ReviewIcon />,
    title: "Human oversight pathway",
    desc: "Receipts are available for human review. Flagged sessions can be routed to compliance, legal, or trust-and-safety workflows.",
    details: ["review_queue", "human_decision", "appeal_context"],
  },
];

const labOverview = [
  {
    label: "WEBCAM ATTESTATION",
    title: "Declare before the camera starts.",
    desc: "A session should not enter a high-risk workflow until authenticity or alteration has been explicitly declared.",
  },
  {
    label: "DISCLOSURE POLICY",
    title: "Policy enforces declared state.",
    desc: "Undeclared synthetic media in high-risk workflows is the problem. The system enforces declaration before access.",
  },
  {
    label: "VISIBLE WATERMARKING",
    title: "Alteration stays visible.",
    desc: "Declared altered or test sessions carry a visible watermark so the disclosure is persistent across recordings.",
  },
  {
    label: "AUDIT RECEIPT",
    title: "The institution has a record.",
    desc: "Every session generates structured evidence: session ID, declared mode, policy decision, watermark state, runtime.",
  },
];

const architectureLayers = [
  "Meeting Platform / Workflow",
  "Profusion Trust Layer",
  "Policy + Audit + Receipt Engine",
  "Human Review / Compliance Trail",
];

const statusItems = [
  ["Prototype status", "Technical lab prototype"],
  ["Commercial posture", "Not a commercial detection product"],
  ["Trust mechanism", "Declaration, policy, watermark, receipt, review"],
  ["Current boundary", "No production assurance or compliance certification"],
];

const services = [
  {
    num: "01",
    title: "AI Trust & Governance Strategy",
    tagline: "Risk maps, control design, governance roadmap.",
    desc: "Map the workflows where AI imitation, synthetic media, or agentic automation creates operational risk — then define the controls that make those workflows governable.",
    tags: ["Risk Mapping", "Policy Design", "Governance"],
  },
  {
    num: "02",
    title: "Synthetic Media & Video Trust Prototyping",
    tagline: "Attestation UX, disclosure policy, receipt schema, red-team scenarios.",
    desc: "Design and prototype the trust layer for video-intensive workflows: declaration flows, policy enforcement, watermarking, and durable receipt generation.",
    tags: ["Attestation", "Watermarking", "Receipts"],
  },
  {
    num: "03",
    title: "Agentic Workflow Evaluation",
    tagline: "Measurement systems for AI-assisted work.",
    desc: "Build measurement systems for AI-assisted workflows: productivity scoring, correction loop analysis, risk flagging, and human-oversight integration.",
    tags: ["Measurement", "Oversight", "Correction Loops"],
  },
  {
    num: "04",
    title: "AI Product & MVP Advisory",
    tagline: "Product wedge, architecture, launch narrative.",
    desc: "Define the product wedge, technical architecture, open-source and commercial boundary, and a launch narrative that does not overclaim.",
    tags: ["Strategy", "Architecture", "Narrative"],
  },
];

const clients = [
  "Organizations running high-stakes video-based workflows — identity, compliance, legal, HR, finance.",
  "Teams deploying AI agents and needing measurement beyond simple output counts.",
  "Product companies building trust-sensitive tools for regulated industries.",
  "Governance, risk, and compliance leaders who need a map before they need a product.",
];

const principles = [
  {
    verb: "Declare",
    subject: "what is synthetic.",
    body: "Synthetic media is not automatically malicious. Undisclosed synthetic media in high-risk workflows is the problem.",
  },
  {
    verb: "Preserve",
    subject: "what is human.",
    body: "The system should protect consent, identity, context, and human accountability — not just flag anomalies.",
  },
  {
    verb: "Record",
    subject: "what matters.",
    body: "Trust requires artifacts: receipts, timestamps, decisions, policy states, and review trails.",
  },
  {
    verb: "Escalate",
    subject: "what is risky.",
    body: "Not every event should be blocked. Some should be watermarked, reviewed, or routed to a higher-trust flow.",
  },
  {
    verb: "Never overclaim",
    subject: "detection.",
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
    { label: "Trust Layer", href: "#trust-layer" },
    { label: "Video Trust Lab", href: "#video-lab" },
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
        <span>SESSION RECEIPT</span>
        <span className="recorded-pill">● RECORDED</span>
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
        <Pill status="ALTERED DISCLOSED" />
        <Pill status="REVIEW REQUIRED" />
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
            AI TRUST CONSULTING & R&D
          </div>
          <h1>
            Human trust
            <br />
            <span>for the age of</span>
            <br />
            synthetic media.
          </h1>
          <p className="hero-lede">
            AI can imitate a face, a voice, a meeting, and a workflow. Profusion AI helps
            organizations design and prototype trust systems that make high-risk digital
            interactions governable again.
          </p>
          <p className="hero-subcopy">
            We are a consulting and R&D practice focused on synthetic media, video trust, audit
            receipts, and AI-mediated work.
          </p>
          <div className="hero-actions">
            <a className="button-primary is-light" href="#contact">
              Discuss a High-Risk Workflow
            </a>
            <a className="button-secondary is-light" href="#video-lab">
              View the Video Trust Lab
            </a>
          </div>
        </div>
        <div className="hero-receipt">
          <div className="receipt-glow" aria-hidden="true" />
          <ReceiptCard animated />
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
          <Eyebrow>The Problem</Eyebrow>
          <h2
            aria-label="Deepfakes are now commonplace. Institutions, Enterprises, Companies, Interviewers, Schools, and Governments still need proof."
            className="proof-headline"
          >
            Deepfakes are now commonplace.{" "}
            <RotatingProofWord />
            <br />
            <span>still need proof.</span>
          </h2>
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
          <Eyebrow>Trust Layer</Eyebrow>
          <h2>A control layer for high-risk video interactions.</h2>
          <p>
            The goal is not detection alone. The goal is to make video interactions governable —
            through a sequence of declarations, controls, evidence, and review.
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
          <Eyebrow>Video Trust Lab</Eyebrow>
          <h2>Before video can be trusted, it needs governance.</h2>
          <p>
            Profusion AI is developing a local-first R&D prototype for high-risk webcam sessions:
            pre-session attestation, enforced disclosure for altered media, visible watermarking,
            and durable trust receipts that record what was declared, enforced, and reviewed.
          </p>
        </div>

        <div className="lab-status">
          <span />
          Current status: technical lab prototype, not a commercial detection product.
        </div>

        <div className="tabs" role="tablist" aria-label="Video Trust Lab tabs">
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
          <h2>Governance by design. Not panic by PowerPoint.</h2>
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
          <h2>For organizations where a trust failure has real consequences.</h2>
          <p>
            We work best with teams who understand that the threat model has changed, and who need
            a structured approach — not a vendor pitch.
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
          <h2>Trust is not a vibe.</h2>
          <p>It is a sequence of declarations, controls, evidence, and review.</p>
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
          <h2>Start a trust strategy session.</h2>
          <p>
            We work with a small number of organizations at a time. If you are building governance
            for AI-mediated workflows, let&apos;s talk.
          </p>
          <div className="contact-notes">
            <ContactNote icon={<ReceiptIcon small />} text="First session is diagnostic: map risks, identify control gaps." />
            <ContactNote icon={<ShieldIcon small />} text="Work product: receipts, policy specs, governance recommendations." />
            <ContactNote icon={<EyeIcon small />} text="No retainers, no lock-in. Engagements by scope." />
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
              value="Profusion AI trust strategy session request"
            />
            <p hidden>
              <label>
                Do not fill this out
                <input name="bot-field" tabIndex={-1} />
              </label>
            </p>
            <span className="mono-label gold">TRUST STRATEGY SESSION REQUEST</span>
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
                placeholder="Briefly describe the workflow or risk you're thinking about..."
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
        <span>Human trust for the age of synthetic media. © 2026</span>
        <div className="footer-links">
          <a href="#trust-layer">Trust Layer</a>
          <a href="#video-lab">Video Trust Lab</a>
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
  return <img alt="" aria-hidden="true" className="logo-icon" src="/profusion-aperture.png" />;
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
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <Problem />
        <TrustLayer />
        <VideoLab />
        <Services />
        <IdealClients />
        <Principles />
        <Contact />
      </main>
      <Footer />
    </>
  );
}
