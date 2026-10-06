import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API = "http://127.0.0.1:8000/api/v1";

function App() {
  const [plate, setPlate] = useState("");
  const [result, setResult] = useState(null);
  const [cases, setCases] = useState([]);
  const [evidence, setEvidence] = useState([]);
  const [caseForm, setCaseForm] = useState({ title: "", registration: "", description: "" });
  const [evidenceForm, setEvidenceForm] = useState({ case_id: "", filename: "", content: "", source: "manual", notes: "" });
  const [error, setError] = useState("");

  async function api(path, options) {
    const response = await fetch(API + path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Request failed");
    return data;
  }

  async function refresh() {
    try {
      const [c, e] = await Promise.all([api("/cases"), api("/evidence")]);
      setCases(c);
      setEvidence(e);
    } catch (err) { setError(err.message); }
  }

  useEffect(() => { refresh(); }, []);

  async function investigate(event) {
    event.preventDefault();
    setError(""); setResult(null);
    try { setResult(await api(`/vehicles/${encodeURIComponent(plate)}`)); }
    catch (err) { setError(err.message); }
  }

  async function createCase(event) {
    event.preventDefault();
    try {
      await api("/cases", { method: "POST", body: JSON.stringify(caseForm) });
      setCaseForm({ title: "", registration: "", description: "" });
      refresh();
    } catch (err) { setError(err.message); }
  }

  async function addEvidence(event) {
    event.preventDefault();
    try {
      await api("/evidence", { method: "POST", body: JSON.stringify(evidenceForm) });
      setEvidenceForm({ case_id: "", filename: "", content: "", source: "manual", notes: "" });
      refresh();
    } catch (err) { setError(err.message); }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div><div className="brand">PLATE-X</div><div className="tagline">Vehicle Investigation & Intelligence Framework</div></div>
        <span className="status">API READY</span>
      </header>

      <section className="hero">
        <p className="eyebrow">INVESTIGATION WORKSPACE</p>
        <h1>Vehicle intelligence, with privacy by design.</h1>
        <p className="intro">Validate registrations, create investigations, and preserve evidence integrity without exposing private owner information.</p>

        <form className="search" onSubmit={investigate}>
          <input value={plate} onChange={e => setPlate(e.target.value)} placeholder="Enter registration e.g. KA01AB1234" />
          <button>Investigate</button>
        </form>
        {error && <div className="error">{error}</div>}

        {result && <section className="result-card">
          <div className="result-header"><div><span className="label">REGISTRATION</span><h2>{result.registration}</h2></div><span className={result.valid_format ? "pill good" : "pill bad"}>{result.valid_format ? "VALID FORMAT" : "INVALID FORMAT"}</span></div>
          <div className="grid">
            <div><span>State</span><strong>{result.rto?.state_name || "Unknown"}</strong></div>
            <div><span>State Code</span><strong>{result.rto?.state_code || "—"}</strong></div>
            <div><span>RTO Code</span><strong>{result.rto?.rto_code || "—"}</strong></div>
            <div><span>Owner Data</span><strong>Protected</strong></div>
          </div>
          <div className="notice">{result.message}</div>
        </section>}

        <div className="section-grid">
          <section className="panel">
            <div className="panel-head"><h2>Cases</h2><span>{cases.length}</span></div>
            <form onSubmit={createCase} className="stack">
              <input placeholder="Case title" value={caseForm.title} onChange={e => setCaseForm({...caseForm, title:e.target.value})} required />
              <input placeholder="Registration (optional)" value={caseForm.registration} onChange={e => setCaseForm({...caseForm, registration:e.target.value})} />
              <textarea placeholder="Investigation notes" value={caseForm.description} onChange={e => setCaseForm({...caseForm, description:e.target.value})} />
              <button>Create case</button>
            </form>
            <div className="list">{cases.map(c => <article className="item" key={c.id}><strong>{c.title}</strong><span>{c.registration || "No registration"} · {c.status}</span><small>{c.id}</small></article>)}</div>
          </section>

          <section className="panel">
            <div className="panel-head"><h2>Evidence</h2><span>{evidence.length}</span></div>
            <form onSubmit={addEvidence} className="stack">
              <select value={evidenceForm.case_id} onChange={e => setEvidenceForm({...evidenceForm, case_id:e.target.value})} required>
                <option value="">Select case</option>{cases.map(c => <option key={c.id} value={c.id}>{c.title}</option>)}
              </select>
              <input placeholder="Filename" value={evidenceForm.filename} onChange={e => setEvidenceForm({...evidenceForm, filename:e.target.value})} required />
              <textarea placeholder="Evidence content (demo)" value={evidenceForm.content} onChange={e => setEvidenceForm({...evidenceForm, content:e.target.value})} required />
              <input placeholder="Source" value={evidenceForm.source} onChange={e => setEvidenceForm({...evidenceForm, source:e.target.value})} />
              <button>Add evidence & hash</button>
            </form>
            <div className="list">{evidence.map(e => <article className="item" key={e.id}><strong>{e.filename}</strong><span>{e.source} · case {e.case_id.slice(0,8)}</span><small>SHA-256: {e.sha256}</small></article>)}</div>
          </section>
        </div>
      </section>
      <footer><span>PLATE-X · Privacy-first investigation tooling</span><span>Developed by Punith Kumar M G</span></footer>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<React.StrictMode><App /></React.StrictMode>);
