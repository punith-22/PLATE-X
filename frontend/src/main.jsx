import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api/v1";

function App() {
  const [token, setToken] = useState(() => sessionStorage.getItem("plate_x_token") || "");
  const [user, setUser] = useState(null);
  const [login, setLogin] = useState({ username: "", password: "" });
  const [plate, setPlate] = useState("");
  const [result, setResult] = useState(null);
  const [cases, setCases] = useState([]);
  const [evidence, setEvidence] = useState([]);
  const [caseForm, setCaseForm] = useState({ title: "", registration: "", description: "" });
  const [evidenceForm, setEvidenceForm] = useState({ case_id: "", filename: "", content: "", source: "manual", notes: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function api(path, options = {}) {
    const headers = { ...(options.body ? { "Content-Type": "application/json" } : {}), ...(token ? { Authorization: `Bearer ${token}` } : {}) };
    const response = await fetch(API + path, { ...options, headers });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (response.status === 401) logout();
      throw new Error(data.detail || "Request failed");
    }
    return data;
  }

  async function authenticate(event) {
    event.preventDefault();
    setBusy(true); setError("");
    try {
      const response = await fetch(API + "/auth/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(login) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Login failed");
      sessionStorage.setItem("plate_x_token", data.access_token);
      setToken(data.access_token);
      const me = await fetch(API + "/auth/me", { headers: { Authorization: `Bearer ${data.access_token}` } });
      setUser(await me.json());
      setLogin({ username: "", password: "" });
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }

  function logout() {
    sessionStorage.removeItem("plate_x_token");
    setToken(""); setUser(null); setCases([]); setEvidence([]); setResult(null);
  }

  async function refresh() {
    try {
      const [me, c, e] = await Promise.all([api("/auth/me"), api("/cases"), api("/evidence")]);
      setUser(me); setCases(c); setEvidence(e);
    } catch (err) { setError(err.message); }
  }

  useEffect(() => { if (token) refresh(); }, [token]);

  async function investigate(event) {
    event.preventDefault(); setError(""); setResult(null);
    try { setResult(await api(`/vehicles/${encodeURIComponent(plate)}`)); }
    catch (err) { setError(err.message); }
  }

  async function createCase(event) {
    event.preventDefault(); setError("");
    try { await api("/cases", { method: "POST", body: JSON.stringify(caseForm) }); setCaseForm({ title:"", registration:"", description:"" }); await refresh(); }
    catch (err) { setError(err.message); }
  }

  async function addEvidence(event) {
    event.preventDefault(); setError("");
    try { await api("/evidence", { method:"POST", body:JSON.stringify(evidenceForm) }); setEvidenceForm({ case_id:"", filename:"", content:"", source:"manual", notes:"" }); await refresh(); }
    catch (err) { setError(err.message); }
  }

  if (!token) return (
    <main className="auth-shell">
      <section className="login-card">
        <div className="brand">PLATE-X</div>
        <p className="eyebrow">SECURE INVESTIGATION WORKSPACE</p>
        <h1>Sign in</h1>
        <p className="muted">Authorized personnel only. Private owner data is not exposed by this system.</p>
        {error && <div className="error">{error}</div>}
        <form onSubmit={authenticate} className="stack">
          <input autoComplete="username" placeholder="Username" value={login.username} onChange={e=>setLogin({...login,username:e.target.value})} required />
          <input autoComplete="current-password" type="password" placeholder="Password" value={login.password} onChange={e=>setLogin({...login,password:e.target.value})} required />
          <button disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
        </form>
      </section>
    </main>
  );

  return (
    <main className="shell">
      <header className="topbar">
        <div><div className="brand">PLATE-X</div><div className="tagline">Vehicle Investigation & Intelligence Framework</div></div>
        <div className="top-actions"><span className="role">{user?.username} · {user?.role}</span><button className="ghost" onClick={logout}>Sign out</button></div>
      </header>
      <section className="hero">
        <p className="eyebrow">INVESTIGATION WORKSPACE</p>
        <h1>Vehicle intelligence, with privacy by design.</h1>
        <p className="intro">Validate registrations, create investigations, preserve evidence integrity, and keep an auditable trail.</p>
        <form className="search" onSubmit={investigate}>
          <input value={plate} onChange={e=>setPlate(e.target.value)} placeholder="Enter registration e.g. KA01AB1234" />
          <button>Investigate</button>
        </form>
        {error && <div className="error">{error}</div>}
        {result && <section className="result-card">
          <div className="result-header"><div><span className="label">REGISTRATION</span><h2>{result.registration}</h2></div><span className={result.valid_format?"pill good":"pill bad"}>{result.valid_format?"VALID FORMAT":"INVALID FORMAT"}</span></div>
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
            {user?.role !== "viewer" && <form onSubmit={createCase} className="stack">
              <input placeholder="Case title" value={caseForm.title} onChange={e=>setCaseForm({...caseForm,title:e.target.value})} required />
              <input placeholder="Registration (optional)" value={caseForm.registration} onChange={e=>setCaseForm({...caseForm,registration:e.target.value})} />
              <textarea placeholder="Investigation notes" value={caseForm.description} onChange={e=>setCaseForm({...caseForm,description:e.target.value})} />
              <button>Create case</button>
            </form>}
            <div className="list">{cases.map(c=><article className="item" key={c.id}><strong>{c.title}</strong><span>{c.registration || "No registration"} · {c.status}</span><small>{c.id}</small></article>)}</div>
          </section>
          <section className="panel">
            <div className="panel-head"><h2>Evidence</h2><span>{evidence.length}</span></div>
            {user?.role !== "viewer" && <form onSubmit={addEvidence} className="stack">
              <select value={evidenceForm.case_id} onChange={e=>setEvidenceForm({...evidenceForm,case_id:e.target.value})} required><option value="">Select case</option>{cases.map(c=><option key={c.id} value={c.id}>{c.title}</option>)}</select>
              <input placeholder="Filename" value={evidenceForm.filename} onChange={e=>setEvidenceForm({...evidenceForm,filename:e.target.value})} required />
              <textarea placeholder="Evidence content (demo)" value={evidenceForm.content} onChange={e=>setEvidenceForm({...evidenceForm,content:e.target.value})} required />
              <input placeholder="Source" value={evidenceForm.source} onChange={e=>setEvidenceForm({...evidenceForm,source:e.target.value})} />
              <button>Add evidence & hash</button>
            </form>}
            <div className="list">{evidence.map(e=><article className="item" key={e.id}><strong>{e.filename}</strong><span>{e.source} · case {e.case_id.slice(0,8)}</span><small>SHA-256: {e.sha256}</small></article>)}</div>
          </section>
        </div>
      </section>
      <footer><span>PLATE-X · Privacy-first investigation tooling</span><span>Developed by Punith Kumar M G</span></footer>
    </main>
  );
}
createRoot(document.getElementById("root")).render(<React.StrictMode><App /></React.StrictMode>);
