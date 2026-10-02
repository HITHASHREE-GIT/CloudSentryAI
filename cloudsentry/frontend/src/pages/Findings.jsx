/**
 * CloudSentry AI — Findings Table
 * Lists all findings with severity/risk filters.
 */

import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';

function Findings() {
  const [findings, setFindings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [minRisk, setMinRisk] = useState(0);
  const [search, setSearch] = useState('');

  const load = () => {
    setLoading(true);
    api
      .findings()
      .then((data) => {
        setFindings(data.findings || []);
        setError(null);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  // Apply filters
  const filtered = findings.filter((f) => {
    if (severityFilter !== 'ALL' && f.severity !== severityFilter) return false;
    if ((f.risk_score || 0) < minRisk) return false;
    if (search) {
      const q = search.toLowerCase();
      const hay = `${f.rule_name} ${f.resource_id} ${f.service}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });

  if (loading) {
    return (
      <div className="center-message">
        <div className="spinner"></div>
        <div>Loading findings…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-box">
        <strong>⚠️ Could not load findings</strong>
        <p style={{ marginTop: 8 }}>{error}</p>
      </div>
    );
  }

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Findings</h1>
        <p className="page-subtitle">
          {filtered.length} of {findings.length} findings
        </p>
      </div>

      {/* ── Filters ── */}
      <div
        className="card"
        style={{ marginBottom: 24, display: 'flex', gap: 16, flexWrap: 'wrap' }}
      >
        <div style={{ flex: 1, minWidth: 200 }}>
          <label
            style={{
              display: 'block',
              fontSize: 12,
              color: 'var(--text-secondary)',
              marginBottom: 6,
              fontWeight: 600,
            }}
          >
            SEARCH
          </label>
          <input
            type="text"
            placeholder="Rule, resource, service…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px',
              background: 'var(--bg-primary)',
              border: '1px solid var(--border)',
              borderRadius: 6,
              color: 'var(--text-primary)',
              fontSize: 14,
            }}
          />
        </div>

        <div style={{ minWidth: 160 }}>
          <label
            style={{
              display: 'block',
              fontSize: 12,
              color: 'var(--text-secondary)',
              marginBottom: 6,
              fontWeight: 600,
            }}
          >
            SEVERITY
          </label>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px',
              background: 'var(--bg-primary)',
              border: '1px solid var(--border)',
              borderRadius: 6,
              color: 'var(--text-primary)',
              fontSize: 14,
            }}
          >
            <option value="ALL">All</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>

        <div style={{ minWidth: 160 }}>
          <label
            style={{
              display: 'block',
              fontSize: 12,
              color: 'var(--text-secondary)',
              marginBottom: 6,
              fontWeight: 600,
            }}
          >
            MIN RISK: {minRisk}
          </label>
          <input
            type="range"
            min="0"
            max="100"
            step="5"
            value={minRisk}
            onChange={(e) => setMinRisk(Number(e.target.value))}
            style={{ width: '100%' }}
          />
        </div>

        <button className="btn" onClick={load}>
          🔄 Refresh
        </button>
      </div>

      {/* ── Table ── */}
      {filtered.length === 0 ? (
        <div className="center-message">
          <div>No findings match your filters.</div>
        </div>
      ) : (
        <div className="table-container">
          <table className="findings-table">
            <thead>
              <tr>
                <th>Risk</th>
                <th>Severity</th>
                <th>Rule</th>
                <th>Resource</th>
                <th>Service</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((f) => {
                const cls = (f.severity || 'low').toLowerCase();
                return (
                  <tr
                    key={f.finding_id}
                    onClick={() =>
                      (window.location.href = `/findings/${f.finding_id}`)
                    }
                  >
                    <td>
                      <span className={`risk-pill ${cls}`}>
                        {f.risk_score}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${cls}`}>{f.severity}</span>
                    </td>
                    <td>{f.rule_name}</td>
                    <td
                      style={{
                        fontFamily: "'Consolas', monospace",
                        fontSize: 13,
                      }}
                    >
                      {f.resource_id}
                    </td>
                    <td>{f.service}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

export default Findings;