/**
 * CloudSentry AI — Left Sidebar Navigation
 */

import { NavLink } from 'react-router-dom';

function Sidebar() {
  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            'sidebar-link' + (isActive ? ' active' : '')
          }
        >
          <span className="sidebar-icon">📊</span>
          <span>Overview</span>
        </NavLink>

        <NavLink
          to="/findings"
          className={({ isActive }) =>
            'sidebar-link' + (isActive ? ' active' : '')
          }
        >
          <span className="sidebar-icon">🚨</span>
          <span>Findings</span>
        </NavLink>
      </nav>
    </aside>
  );
}

export default Sidebar;