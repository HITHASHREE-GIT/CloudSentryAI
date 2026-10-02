/**
 * LaunchNest — Tasks List
 */

import { useEffect, useState } from 'react';
import { api } from '../api/client';

export default function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [search, setSearch] = useState('');

  const load = () => {
    setLoading(true);
    api
      .tasks()
      .then((data) => {
        setTasks(data);
        setError(null);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const filtered = tasks.filter((t) => {
    if (statusFilter !== 'ALL' && t.status !== statusFilter) return false;
    if (search) {
      const q = search.toLowerCase();
      if (!t.title.toLowerCase().includes(q)) return false;
    }
    return true;
  });

  const counts = {
    todo: tasks.filter((t) => t.status === 'todo').length,
    in_progress: tasks.filter((t) => t.status === 'in_progress').length,
    completed: tasks.filter((t) => t.status === 'completed').length,
  };

  if (loading) {
    return (
      <div className="center-message">
        <div className="spinner"></div>
        <div>Loading tasks…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-box">
        <strong>⚠️ Could not load tasks</strong>
        <p style={{ marginTop: 8 }}>{error}</p>
      </div>
    );
  }

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Tasks</h1>
        <p className="page-subtitle">
          {filtered.length} of {tasks.length} tasks
        </p>
      </div>

      {/* ── Status summary ── */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">To Do</div>
          <div className="stat-value">{counts.todo}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">In Progress</div>
          <div className="stat-value warning">{counts.in_progress}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Completed</div>
          <div className="stat-value success">{counts.completed}</div>
        </div>
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
            placeholder="Search tasks…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div style={{ minWidth: 180 }}>
          <label className="form-label">Status</label>
          <select
            className="form-input"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="ALL">All</option>
            <option value="todo">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
        </div>
        <div style={{ display: 'flex', alignItems: 'flex-end' }}>
          <button className="btn" onClick={load}>
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* ── Tasks Table ── */}
      {filtered.length === 0 ? (
        <div className="center-message">
          <div>No tasks match your filters.</div>
        </div>
      ) : (
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Task</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Project ID</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((t) => (
                <tr key={t.task_id}>
                  <td>
                    <div style={{ fontWeight: 500 }}>{t.title}</div>
                    {t.description && (
                      <div
                        style={{
                          fontSize: 12,
                          color: 'var(--text-secondary)',
                          marginTop: 2,
                        }}
                      >
                        {t.description}
                      </div>
                    )}
                  </td>
                  <td>
                    <span className={`badge ${t.status}`}>
                      {t.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${t.priority}`}>
                      {t.priority}
                    </span>
                  </td>
                  <td className="text-muted">#{t.project_id}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}