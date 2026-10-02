/**
 * LaunchNest — Dashboard Overview
 */

import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([api.stats(), api.projects()])
      .then(([s, p]) => {
        setStats(s);
        setProjects(p);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="center-message">
        <div className="spinner"></div>
        <div>Loading dashboard…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-box">
        <strong>⚠️ Could not load dashboard</strong>
        <p style={{ marginTop: 8 }}>{error}</p>
      </div>
    );
  }

  const activeProjects = projects
    .filter((p) => p.status === 'active')
    .slice(0, 5);

  const firstName = (user?.name || 'User').split(' ')[0];

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Welcome, {firstName} 👋</h1>
        <p className="page-subtitle">
          Here's what's happening at LaunchNest today
        </p>
      </div>

      {/* ── Stats ── */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Projects</div>
          <div className="stat-value brand">{stats.total_projects}</div>
          <div className="text-muted" style={{ fontSize: 12, marginTop: 4 }}>
            {stats.active_projects} active
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Tasks</div>
          <div className="stat-value">{stats.total_tasks}</div>
          <div className="text-muted" style={{ fontSize: 12, marginTop: 4 }}>
            {stats.completed_tasks} completed
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">In Progress</div>
          <div className="stat-value warning">
            {stats.in_progress_tasks}
          </div>
          <div className="text-muted" style={{ fontSize: 12, marginTop: 4 }}>
            tasks ongoing
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Team</div>
          <div className="stat-value success">{stats.team_members}</div>
          <div className="text-muted" style={{ fontSize: 12, marginTop: 4 }}>
            members
          </div>
        </div>
      </div>

      {/* ── Active Projects ── */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: 16,
          }}
        >
          <div className="card-title" style={{ marginBottom: 0 }}>
            Active Projects
          </div>
          <Link to="/projects" style={{ fontSize: 13 }}>
            View all →
          </Link>
        </div>

        <div className="grid-2">
          {activeProjects.map((p) => (
            <Link
              key={p.project_id}
              to={`/projects`}
              className="project-card"
            >
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
                <span>{p.progress}%</span>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* ── Quick Actions ── */}
      <div className="card">
        <div className="card-title">Quick Actions</div>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <Link to="/projects" className="btn btn-primary">
            📁 Manage Projects
          </Link>
          <Link to="/tasks" className="btn">
            ✅ View Tasks
          </Link>
          <Link to="/team" className="btn">
            👥 Team Members
          </Link>
        </div>
      </div>
    </>
  );
}