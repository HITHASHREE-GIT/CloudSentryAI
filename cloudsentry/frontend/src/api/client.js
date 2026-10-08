/**
 * CloudSentry AI — API Client
 * Axios instance pointing at the FastAPI backend (port 8001).
 *
 * Production: uses VITE_API_URL env var (set on Render).
 * Local:      falls back to http://localhost:8001
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Request interceptor (for future auth token) ──
client.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
);

// ── Response interceptor (for error handling) ──
client.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('[CloudSentry API Error]', error.message);
    return Promise.reject(error);
  }
);

// ── API methods ──

export const api = {
  /** Health check */
  health: () => client.get('/health').then((r) => r.data),

  /** Trigger a full scan */
  scan: () => client.post('/scan').then((r) => r.data),

  /** List all findings (optional filters) */
  findings: (params = {}) =>
    client.get('/findings', { params }).then((r) => r.data),

  /** Get one finding by id */
  finding: (findingId) =>
    client.get(`/findings/${findingId}`).then((r) => r.data),
};

export default client;