/**
 * LaunchNest — Team Members
 */

import { useEffect, useState } from 'react';
import { api } from '../api/client';

export default function Team() {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .team()
      .then((data) => setMembers(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="center-message">
        <div className="spinner"></div>
        <div>Loading team…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-box">
        <strong>⚠️ Could not load team</strong>
        <p style={{ marginTop: 8 }}>{error}</p>
      </div>
    );
  }

  const initials = (name) =>
    (name || 'U')
      .split(' ')
      .map((w) => w[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Team</h1>
        <p className="page-subtitle">{members.length} members</p>
      </div>

      <div className="grid-2">
        {members.map((m) => (
          <div key={m.user_id} className="project-card">
            <div style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
              <div
                className="user-avatar"
                style={{ width: 48, height: 48, fontSize: 16 }}
              >
                {initials(m.name)}
              </div>
              <div style={{ flex: 1 }}>
                <div className="project-name" style={{ marginBottom: 2 }}>
                  {m.name}
                </div>
                <div
                  className="project-desc"
                  style={{ marginBottom: 8, fontSize: 12 }}
                >
                  {m.email}
                </div>
                <span className={`badge ${m.role}`}>{m.role}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}