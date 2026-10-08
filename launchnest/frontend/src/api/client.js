/**
 * LaunchNest — API Client
 * Axios instance pointing at the LaunchNest backend (port 8000).
 *
 * Production: uses VITE_API_URL env var (set on Render).
 * Fallback:  if env var missing, uses Render backend URL in production,
 *            or localhost in development.
 */

import axios from 'axios';

// Detect environment
const isLocalhost =
  window.location.hostname === 'localhost' ||
  window.location.hostname === '127.0.0.1';

// Choose backend URL with 3-level fallback:
//   1. Env var (VITE_API_URL) — set on Render
//   2. Production default — Render backend URL
//   3. Development default — localhost
const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  (isLocalhost
    ? 'http://localhost:8000'
    : 'https://launchnest-backend-xtgl.onrender.com');

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Request interceptor: attach JWT ──
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('ln_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response interceptor: handle 401 ──
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('ln_token');
      localStorage.removeItem('ln_user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ── API methods ──

export const api = {
  // Auth
  login: (email, password) =>
    client.post('/api/auth/login', { email, password }).then((r) => r.data),

  register: (payload) =>
    client.post('/api/auth/register', payload).then((r) => r.data),

  me: () => client.get('/api/auth/me').then((r) => r.data),

  // Dashboard
  stats: () => client.get('/api/dashboard/stats').then((r) => r.data),

  // Projects
  projects: () => client.get('/api/projects').then((r) => r.data),
  project: (id) => client.get(`/api/projects/${id}`).then((r) => r.data),
  createProject: (payload) =>
    client.post('/api/projects', payload).then((r) => r.data),
  updateProject: (id, payload) =>
    client.put(`/api/projects/${id}`, payload).then((r) => r.data),
  deleteProject: (id) =>
    client.delete(`/api/projects/${id}`).then((r) => r.data),

  // Tasks
  tasks: (params = {}) =>
    client.get('/api/tasks', { params }).then((r) => r.data),
  createTask: (payload) =>
    client.post('/api/tasks', payload).then((r) => r.data),
  updateTask: (id, payload) =>
    client.put(`/api/tasks/${id}`, payload).then((r) => r.data),
  deleteTask: (id) =>
    client.delete(`/api/tasks/${id}`).then((r) => r.data),

  // Team
  team: () => client.get('/api/team').then((r) => r.data),
};

export default client;