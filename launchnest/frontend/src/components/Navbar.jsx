/**
 * LaunchNest — Top Navigation Bar
 */

import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  // Initials for avatar
  const initials = (user?.name || 'U')
    .split(' ')
    .map((w) => w[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();

  return (
    <header className="navbar">
      <div className="navbar-brand">
        <span className="navbar-brand-icon">🏢</span>
        <span>LaunchNest</span>
      </div>

      <div className="navbar-user">
        <div className="user-avatar">{initials}</div>
        <div className="user-name">
          {user?.name || 'User'}
          <br />
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            {user?.role || ''}
          </span>
        </div>
        <button className="logout-btn" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </header>
  );
}