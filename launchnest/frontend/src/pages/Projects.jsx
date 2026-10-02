/**
 * LaunchNest — Projects List
 */

import { useEffect, useState } from 'react';
import { api } from '../api/client';

export default function Projects() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('ALL');
  const [search, setSearch] = useState('');

  const load = () => {
    setLoading(true);
    api
      .projects()
      .then((data) => {
        setProjects(data);
        setError(null);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const filtered = projects.filter((p) => {
    if (filter !== 'ALL' && p.status !== filter) return false;
    if (search) {
      const q = search.toLowerCase();
      if (!p.name.toLowerCase().includes(q)) return false;
    }
    return true;
  });

  if (loading) {
    return (
      <div className="center-message">
        <div className="spinner"></div>
        <div>Loading projects…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-box">
        <strong>⚠️ Could not load projects</strong>
        <p style={{ marginTop: 8 }}>{error}</p>
      </div>
    );
  }

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Projects</h1>
        <p className="page-subtitle">
          {filtered.length} of {projects.length} projects
        </p>
      </div>

      {/* ── Filters ── */}
      <div
        className="card"
        style={{ marginBottom: 20, display: 'flex', gap: 16, flexWrap: 'wrap' }}
      >
        <div style={{ flex: 1, minWidth: 200 }}>
          <label className="form-label">Search</label>
          <input
            type="text"
            className="form-input"
            placeholder="Search projects…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div style={{ minWidth: 160 }}>
          <label className="form-label">Status</label>
          <select
            className="form-input"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="ALL">All</option>
            <option value="active">Active</option>
            <option value="planning">Planning</option>
            <option value="archived">Archived</option>
          </select>
        </div>
        <div style={{ display: 'flex', alignItems: 'flex-end' }}>
          <button className="btn" onClick={load}>
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* ── Projects Grid ── */}
      {filtered.length === 0 ? (
        <div className="center-message">
          <div>No projects match your filters.</div>
        </div>
      ) : (
        <div className="grid-2">
          {filtered.map((p) => (
            <div key={p.project_id} className="project-card">
              <div className="project-name">{p.name}</div>
              <div className="project-desc">{p.description}</div>
              <div className="progress">
                <div
                  className="progress-fill"
                  style={{ width: `${p.progress}%` }}
                ></div>
              </div>
              <div className="project-meta">
                <span className={`badge ${p.status}`}>{p.status}</span>
                <span>{p.progress}% complete</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}