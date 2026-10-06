import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API = "http://127.0.0.1:8000/api/v1";

function App() {
  const [plate, setPlate] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function investigate(event) {
    event.preventDefault();
    setError("");
    setResult(null);
    if (!plate.trim()) return;
    try {
      const response = await fetch(`${API}/vehicles/${encodeURIComponent(plate)}`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Lookup failed");
      setResult(data);
    } catch (err) {
      setError(err.message || "Unable to connect to PLATE-X API");
    }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <div className="brand">PLATE-X</div>
          <div className="tagline">Vehicle Investigation & Intelligence Framework</div>
        </div>
        <span className="status">API READY</span>
      </header>

      <section className="hero">
        <p className="eyebrow">INVESTIGATION WORKSPACE</p>
        <h1>Vehicle intelligence, with privacy by design.</h1>
        <p className="intro">
          Validate a registration, identify its state/RTO metadata, and build an
          auditable investigation without exposing private owner information.
        </p>

        <form className="search" onSubmit={investigate}>
          <input
            value={plate}
            onChange={(e) => setPlate(e.target.value)}
            placeholder="Enter registration e.g. KA01AB1234"
            aria-label="Vehicle registration"
          />
          <button type="submit">Investigate</button>
        </form>

        {error && <div className="error">{error}</div>}

        {result && (
          <section className="result-card">
            <div className="result-header">
              <div>
                <span className="label">REGISTRATION</span>
                <h2>{result.registration}</h2>
              </div>
              <span className={result.valid_format ? "pill good" : "pill bad"}>
                {result.valid_format ? "VALID FORMAT" : "INVALID FORMAT"}
              </span>
            </div>

            <div className="grid">
              <div><span>State</span><strong>{result.rto?.state_name || "Unknown"}</strong></div>
              <div><span>State Code</span><strong>{result.rto?.state_code || "—"}</strong></div>
              <div><span>RTO Code</span><strong>{result.rto?.rto_code || "—"}</strong></div>
              <div><span>Owner Data</span><strong>Protected</strong></div>
            </div>

            <div className="notice">
              {result.message}
            </div>
          </section>
        )}
      </section>

      <footer>
        <span>PLATE-X · Privacy-first investigation tooling</span>
        <span>Developed by Punith Kumar M G</span>
      </footer>
    </main>
  );
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode><App /></React.StrictMode>
);