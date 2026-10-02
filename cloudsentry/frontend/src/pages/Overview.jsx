/**
 * CloudSentry AI — Overview Dashboard
 * Shows security score, severity breakdown, and top risks.
 */

import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';

function Overview() {
  const [findings, setFindings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .findings()
      .then((data) => {
        setFindings(data.findings || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load findings');
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="center-message">
        <div className="spinner"></div>
        <div>Loading security posture…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-box">
        <strong>⚠️ Could not connect to CloudSentry API</strong>
        <p style={{ marginTop: 8 }}>
          Make sure the backend is running on <code>http://localhost:8001</code>.
        </p>
        <p style={{ marginTop: 4, opacity: 0.8 }}>{error}</p>
      </div>
    );
  }

  // ── Calculate stats ──
  const counts = {
    CRITICAL: 0,
    HIGH: 0,
    MEDIUM: 0,
    LOW: 0,
  };
  findings.forEach((f) => {
    if (counts[f.severity] !== undefined) counts[f.severity] += 1;
  });

  const total = findings.length;
  const avgRisk =
    total === 0
      ? 0
      : Math.round(
          findings.reduce((sum, f) => sum + (f.risk_score || 0), 0) / total
        );

  // Security score = 100 - avg risk
  const securityScore = 100 - avgRisk;

  const scoreColor = (score) => {
    if (score >= 80) return 'low';
    if (score >= 60) return 'medium';
    if (score >= 40) return 'high';
    return 'critical';
  };

  const topRisks = [...findings]
    .sort((a, b) => (b.risk_score || 0) - (a.risk_score || 0))
    .slice(0, 5);

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Security Overview</h1>
        <p className="page-subtitle">
          LaunchNest AWS environment · Simulated scan
        </p>
      </div>

      {/* ── Top stats ── */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Security Score</div>
          <div className={`stat-value ${scoreColor(securityScore)}`}>
            {securityScore}
            <span style={{ fontSize: 16, color: 'var(--text-secondary)' }}>
              {' '}
              / 100
            </span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Total Findings</div>
          <div className="stat-value accent">{total}</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Avg Risk Score</div>
          <div className={`stat-value ${scoreColor(100 - avgRisk)}`}>
            {avgRisk}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Critical</div>
          <div className="stat-value critical">{counts.CRITICAL}</div>
        </div>
      </div>

      {/* ── Severity breakdown + Top risks ── */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1.4fr',
          gap: 24,
        }}
      >
        {/* Severity bar chart */}
        <div className="card">
          <div className="card-title">Findings by Severity</div>

          {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => {
            const count = counts[sev];
            const pct = total === 0 ? 0 : (count / total) * 100;
            const cls = sev.toLowerCase();
            return (
              <div className="chart-bar" key={sev}>
                <div className={`chart-label`} style={{ color: `var(--${cls})` }}>
                  {sev}
                </div>
                <div className="chart-track">
                  <div
                    className={`chart-fill ${cls}`}
                    style={{ width: `${pct}%` }}
                  ></div>
                </div>
                <div className="chart-count">{count}</div>
              </div>
            );
          })}
        </div>

        {/* Top 5 risks */}
        <div className="card">
          <div className="card-title">Top 5 Risks (by score)</div>

          <div className="top-risks">
            {topRisks.map((f) => {
              const cls = (f.severity || 'low').toLowerCase();
              return (
                <Link
                  key={f.finding_id}
                  to={`/findings/${f.finding_id}`}
                  className="risk-item"
                >
                  <div
                    className="risk-item-score"
                    style={{ color: `var(--${cls})` }}
                  >
                    {f.risk_score}
                  </div>
                  <div className="risk-item-body">
                    <div className="risk-item-title">{f.rule_name}</div>
                    <div className="risk-item-resource">
                      {f.resource_id}
                    </div>
                  </div>
                  <div className={`badge ${cls}`}>{f.severity}</div>
                </Link>
              );
            })}
          </div>

          <div style={{ marginTop: 16, textAlign: 'right' }}>
            <Link to="/findings" className="btn btn-primary">
              View all {total} findings →
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}

export default Overview;