/**
 * CloudSentry AI — Finding Detail View
 * Full details for a single finding.
 *
 * Note: Since the API regenerates finding IDs on each call,
 * we fetch all findings and locate the one matching the URL id.
 *
 * Displays both rule-based severity (authoritative) and ML-predicted
 * priority (supplementary signal).
 */

import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api/client';

function FindingDetail() {
  const { id } = useParams();
  const [finding, setFinding] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .findings()
      .then((data) => {
        const all = data.findings || [];
        const match = all.find((f) => f.finding_id === id);
        if (match) {
          setFinding(match);
        } else {
          setError('Finding not found — the scan may have refreshed. Try again.');
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="center-message">
        <div className="spinner"></div>
        <div>Loading finding…</div>
      </div>
    );
  }

  if (error || !finding) {
    return (
      <>
        <div className="error-box">
          <strong>⚠️ Finding not found</strong>
          <p style={{ marginTop: 8 }}>{error || 'Unknown error'}</p>
          <p style={{ marginTop: 8, opacity: 0.8, fontSize: 13 }}>
            Note: The scan regenerates finding IDs on each run. Try refreshing the
            findings list and clicking again.
          </p>
        </div>
        <Link to="/findings" className="btn">
          ← Back to findings
        </Link>
      </>
    );
  }

  const cls = (finding.severity || 'low').toLowerCase();
  const mlConfidence = finding.ml_confidence
    ? (finding.ml_confidence * 100).toFixed(1)
    : null;

  return (
    <>
      <div style={{ marginBottom: 20 }}>
        <Link to="/findings" className="btn">
          ← Back to findings
        </Link>
      </div>

      <div className="page-header">
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            marginBottom: 8,
            flexWrap: 'wrap',
          }}
        >
          <span className={`badge ${cls}`}>{finding.severity}</span>
          <span className={`risk-pill ${cls}`}>
            Risk {finding.risk_score}/100
          </span>
          {finding.ml_priority && (
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                padding: '3px 10px',
                borderRadius: 12,
                background: 'rgba(88, 166, 255, 0.15)',
                color: '#58a6ff',
                border: '1px solid rgba(88, 166, 255, 0.4)',
                fontSize: 11,
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: 0.5,
              }}
              title={`ML predicted priority (confidence: ${mlConfidence}%)`}
            >
              🤖 ML: {finding.ml_priority}
              {mlConfidence && (
                <span style={{ opacity: 0.7, fontWeight: 500 }}>
                  {mlConfidence}%
                </span>
              )}
            </span>
          )}
        </div>
        <h1 className="page-title">{finding.rule_name}</h1>
        <p className="page-subtitle">
          {finding.service} · {finding.resource_type} · {finding.region}
        </p>
      </div>

      {/* ── Overview ── */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-title">Overview</div>

        <div className="detail-row">
          <div className="detail-label">Resource</div>
          <div className="detail-value">
            <code>{finding.resource_id}</code>
          </div>
        </div>

        <div className="detail-row">
          <div className="detail-label">Rule ID</div>
          <div className="detail-value">
            <code>{finding.rule_id}</code>
          </div>
        </div>

        <div className="detail-row">
          <div className="detail-label">Finding ID</div>
          <div className="detail-value">
            <code>{finding.finding_id}</code>
          </div>
        </div>

        <div className="detail-row">
          <div className="detail-label">Detected</div>
          <div className="detail-value">{finding.created_at}</div>
        </div>

        {finding.ml_priority && (
          <div className="detail-row">
            <div className="detail-label">ML Prediction</div>
            <div className="detail-value">
              <strong style={{ color: '#58a6ff' }}>
                {finding.ml_priority}
              </strong>
              {mlConfidence && (
                <span
                  style={{
                    color: 'var(--text-secondary)',
                    marginLeft: 8,
                    fontSize: 13,
                  }}
                >
                  · confidence {mlConfidence}%
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* ── Description ── */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-title">Description</div>
        <p>{finding.description}</p>
      </div>

      {/* ── Why dangerous ── */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-title">Why This Is Dangerous</div>
        <p>{finding.why_dangerous}</p>
      </div>

      {/* ── Evidence ── */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-title">Evidence</div>
        <pre className="evidence-box">
          {JSON.stringify(finding.evidence, null, 2)}
        </pre>
      </div>

      {/* ── Remediation ── */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-title">Remediation</div>
        <p>{finding.recommendation}</p>
      </div>

      {/* ── Reference ── */}
      {finding.reference && (
        <div className="card">
          <div className="card-title">Reference</div>
          <p>{finding.reference}</p>
        </div>
      )}
    </>
  );
}

export default FindingDetail;