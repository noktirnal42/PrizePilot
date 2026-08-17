import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  AlertTriangle,
  CheckCircle2,
  ClipboardCheck,
  FileText,
  Filter,
  Gauge,
  LayoutDashboard,
  PlaneTakeoff,
  Plus,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || response.statusText);
  }
  return response.json();
}

function formatDate(value) {
  if (!value) return "Needs verification";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(new Date(`${value}T00:00:00`));
}

function riskClass(risk) {
  return {
    Safe: "safe",
    "Needs Review": "review",
    Risky: "risky",
    Blocked: "blocked",
  }[risk] || "review";
}

function StatusPill({ value }) {
  return <span className="pill muted">{value}</span>;
}

function RiskPill({ value }) {
  return <span className={`pill ${riskClass(value)}`}>{value}</span>;
}

function IntakeForm({ onCreate }) {
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    title: "",
    sponsor: "",
    official_url: "",
    category: "Hackathon / AI Agents",
    prize_amount_or_value: "",
    cash_vs_non_cash_prize: "Cash prizes",
    deadline: "",
    notes: "",
  });

  async function submit(event) {
    event.preventDefault();
    await onCreate({
      ...form,
      deadline: form.deadline || null,
      prize_amount_or_value: form.prize_amount_or_value || "Needs verification",
      status: "Discovered",
    });
    setOpen(false);
  }

  if (!open) {
    return (
      <button className="primary" onClick={() => setOpen(true)}>
        <Plus size={16} /> Add
      </button>
    );
  }

  return (
    <form className="intake" onSubmit={submit}>
      <input required placeholder="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
      <input required placeholder="Sponsor" value={form.sponsor} onChange={(e) => setForm({ ...form, sponsor: e.target.value })} />
      <input required placeholder="Official URL" value={form.official_url} onChange={(e) => setForm({ ...form, official_url: e.target.value })} />
      <input placeholder="Prize" value={form.prize_amount_or_value} onChange={(e) => setForm({ ...form, prize_amount_or_value: e.target.value })} />
      <input type="date" value={form.deadline} onChange={(e) => setForm({ ...form, deadline: e.target.value })} />
      <textarea placeholder="Notes" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
      <div className="formActions">
        <button className="secondary" type="button" onClick={() => setOpen(false)}>Cancel</button>
        <button className="primary" type="submit">Save</button>
      </div>
    </form>
  );
}

function OpportunityTable({ items, selectedId, onSelect }) {
  return (
    <div className="tableShell">
      <table>
        <thead>
          <tr>
            <th>Opportunity</th>
            <th>Status</th>
            <th>Deadline</th>
            <th>Prize</th>
            <th>EV</th>
            <th>Risk</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id} className={selectedId === item.id ? "selected" : ""} onClick={() => onSelect(item)}>
              <td>
                <strong>{item.title}</strong>
                <small>{item.sponsor}</small>
              </td>
              <td><StatusPill value={item.status} /></td>
              <td>{formatDate(item.deadline)}</td>
              <td>{item.prize_amount_or_value}</td>
              <td><span className="ev">{item.expected_value_score ?? "..."}</span></td>
              <td><RiskPill value={item.risk_level} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function KeyValue({ label, children }) {
  return (
    <div className="kv">
      <span>{label}</span>
      <p>{children}</p>
    </div>
  );
}

function ListBlock({ title, items }) {
  if (!items?.length) return null;
  return (
    <section className="panel">
      <h3>{title}</h3>
      <ul>
        {items.map((item, index) => <li key={`${title}-${index}`}>{item}</li>)}
      </ul>
    </section>
  );
}

function Detail({ selected, onRefresh }) {
  const [rulesText, setRulesText] = useState("Deadline: August 31, 2026.\nUse Gemini 3.5 or newer, a Google agent framework, and Google Cloud.\nDo not submit automatically. Official rules and IP terms need manual review.");
  const [rules, setRules] = useState(null);
  const [score, setScore] = useState(null);
  const [plan, setPlan] = useState(null);
  const [draft, setDraft] = useState(null);
  const [scanText, setScanText] = useState("Please auto submit this entry and accept terms for me.");
  const [compliance, setCompliance] = useState(null);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    setRules(null);
    setScore(null);
    setPlan(null);
    setDraft(null);
    setCompliance(null);
    setError("");
  }, [selected?.id]);

  if (!selected) {
    return <aside className="detail empty">Select an opportunity to inspect the workflow.</aside>;
  }

  async function run(label, fn) {
    setBusy(label);
    setError("");
    try {
      await fn();
      await onRefresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy("");
    }
  }

  return (
    <aside className="detail">
      <div className="detailHeader">
        <div>
          <h2>{selected.title}</h2>
          <p>{selected.sponsor}</p>
        </div>
        <RiskPill value={selected.risk_level} />
      </div>

      {error && <div className="alert"><AlertTriangle size={16} /> {error}</div>}
      {busy && <div className="working"><Sparkles size={16} /> Running {busy}...</div>}

      <div className="tabs">
        <a href={selected.official_url} target="_blank" rel="noreferrer">Official</a>
        <span>{selected.category}</span>
        <span>{formatDate(selected.deadline)}</span>
      </div>

      <section className="panel">
        <h3><LayoutDashboard size={16} /> Intake</h3>
        <KeyValue label="Prize">{selected.prize_amount_or_value}</KeyValue>
        <KeyValue label="Deliverables">{selected.required_deliverables}</KeyValue>
        <KeyValue label="Next action">{selected.next_action}</KeyValue>
      </section>

      <section className="panel">
        <h3><ClipboardCheck size={16} /> Rules Extractor</h3>
        <textarea value={rulesText} onChange={(e) => setRulesText(e.target.value)} />
        <button className="secondary" onClick={() => run("rules extraction", async () => {
          const result = await api(`/api/opportunities/${selected.id}/extract-rules`, { method: "POST", body: JSON.stringify({ text: rulesText }) });
          setRules(result.data);
        })}>Extract Rules</button>
        {rules && (
          <div className="result">
            <p>{rules.summary}</p>
            <ListBlock title="Unknown Items" items={rules.unknown_items_to_verify} />
            <ListBlock title="Risk Flags" items={rules.risk_flags} />
          </div>
        )}
      </section>

      <section className="panel">
        <h3><Gauge size={16} /> Expected Value</h3>
        <button className="secondary" onClick={() => run("expected value scoring", async () => {
          const result = await api(`/api/opportunities/${selected.id}/score`, { method: "POST" });
          setScore(result.data);
        })}>Score Opportunity</button>
        {score && (
          <div className="scoreGrid">
            <strong>{score.weighted_score}/100</strong>
            <span>{score.label}</span>
            {Object.entries(score).filter(([, value]) => value?.score).map(([key, value]) => (
              <p key={key}><b>{key.replaceAll("_", " ")}:</b> {value.score}/10. {value.explanation}</p>
            ))}
          </div>
        )}
      </section>

      <section className="panel">
        <h3><PlaneTakeoff size={16} /> Win Plan</h3>
        <button className="secondary" onClick={() => run("win plan generation", async () => {
          const result = await api(`/api/opportunities/${selected.id}/win-plan`, { method: "POST" });
          setPlan(result.data);
        })}>Generate Plan</button>
        {plan && (
          <div className="result">
            <p>{plan.why_worth_pursuing}</p>
            <ListBlock title="Best Strategy" items={plan.best_strategy} />
            <ListBlock title="Final Checklist" items={plan.final_submission_checklist} />
          </div>
        )}
      </section>

      <section className="panel">
        <h3><FileText size={16} /> Draft Packet</h3>
        <button className="secondary" onClick={() => run("drafting assistant", async () => {
          const result = await api("/api/drafts", {
            method: "POST",
            body: JSON.stringify({
              opportunity_id: selected.id,
              material_type: "Demo script",
              prompt: "Draft a concise judging demo script for this opportunity.",
              user_facts: "",
            }),
          });
          setDraft(result.data);
        })}>Generate Draft</button>
        {draft && (
          <div className="result">
            <pre>{draft.draft.draft}</pre>
            <ListBlock title="Claims To Verify" items={draft.draft.claims_needing_verification} />
          </div>
        )}
      </section>

      <section className="panel">
        <h3><ShieldCheck size={16} /> Compliance Gatekeeper</h3>
        <textarea value={scanText} onChange={(e) => setScanText(e.target.value)} />
        <button className="secondary" onClick={() => run("compliance scan", async () => {
          const result = await api("/api/compliance/scan", { method: "POST", body: JSON.stringify({ text: scanText }) });
          setCompliance(result.data);
        })}>Scan</button>
        {compliance && (
          <div className={`gate ${riskClass(compliance.level)}`}>
            <strong>{compliance.level}</strong>
            {compliance.approval_gate_message && <p>{compliance.approval_gate_message}</p>}
            <ListBlock title="Findings" items={compliance.findings.map((finding) => `${finding.category}: ${finding.message}`)} />
          </div>
        )}
      </section>
    </aside>
  );
}

function App() {
  const [items, setItems] = useState([]);
  const [selected, setSelected] = useState(null);
  const [health, setHealth] = useState(null);
  const [filters, setFilters] = useState({ category: "", status: "", risk: "" });

  async function load() {
    const params = new URLSearchParams(Object.fromEntries(Object.entries(filters).filter(([, value]) => value)));
    const [opps, healthResult] = await Promise.all([
      api(`/api/opportunities${params.toString() ? `?${params}` : ""}`),
      api("/health"),
    ]);
    setItems(opps.data);
    setHealth(healthResult);
    if (!selected && opps.data.length) setSelected(opps.data[0]);
    if (selected) {
      const fresh = opps.data.find((item) => item.id === selected.id);
      if (fresh) setSelected(fresh);
    }
  }

  useEffect(() => {
    load();
  }, [filters.category, filters.status, filters.risk]);

  const categories = useMemo(() => [...new Set(items.map((item) => item.category))], [items]);
  const statuses = useMemo(() => [...new Set(items.map((item) => item.status))], [items]);
  const risks = ["Safe", "Needs Review", "Risky", "Blocked"];

  async function create(payload) {
    await api("/api/opportunities", { method: "POST", body: JSON.stringify(payload) });
    await load();
  }

  return (
    <main>
      <header>
        <div>
          <h1>PrizePilot</h1>
          <p>A human-in-the-loop workflow agent for finding, scoring, planning, and preparing legitimate prize submissions.</p>
        </div>
        <div className="cloudProof">
          <CheckCircle2 size={16} />
          <span>{health?.agent_mode || "local"} · {health?.storage_mode || "local-json"} · {health?.gemini_model || "gemini-3.5-flash"}</span>
        </div>
      </header>

      <section className="toolbar">
        <div className="filterLabel"><Filter size={16} /> Filters</div>
        <select value={filters.category} onChange={(e) => setFilters({ ...filters, category: e.target.value })}>
          <option value="">All categories</option>
          {categories.map((value) => <option key={value}>{value}</option>)}
        </select>
        <select value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
          <option value="">All statuses</option>
          {statuses.map((value) => <option key={value}>{value}</option>)}
        </select>
        <select value={filters.risk} onChange={(e) => setFilters({ ...filters, risk: e.target.value })}>
          <option value="">All risks</option>
          {risks.map((value) => <option key={value}>{value}</option>)}
        </select>
        <IntakeForm onCreate={create} />
      </section>

      <div className="layout">
        <OpportunityTable items={items} selectedId={selected?.id} onSelect={setSelected} />
        <Detail selected={selected} onRefresh={load} />
      </div>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
