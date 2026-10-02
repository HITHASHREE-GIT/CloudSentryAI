/**
 * CloudSentry AI — Top Navigation Bar
 */

import { useEffect, useState } from 'react';
import { api } from '../api/client';

function Navbar() {
  const [apiStatus, setApiStatus] = useState('checking');
  const [version, setVersion] = useState('');

  useEffect(() => {
    api
      .health()
      .then((data) => {
        setApiStatus('online');
        setVersion(data.version || '');
      })
      .catch(() => {
        setApiStatus('offline');
      });
  }, []);

  return (
    <header className="navbar">
      <div className="navbar-brand">
        <span className="navbar-brand-icon">🛡️</span>
        <span>CloudSentry AI</span>
      </div>

      <div className="navbar-status">
        <span className={`status-dot ${apiStatus === 'offline' ? 'offline' : ''}`}></span>
        <span>
          API {apiStatus === 'checking' ? 'checking...' : apiStatus}
          {version && ` · v${version}`}
        </span>
      </div>
    </header>
  );
}

export default Navbar;