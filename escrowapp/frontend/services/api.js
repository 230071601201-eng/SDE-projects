// services/api.js
// ─────────────────────────────────────────────────────────────
// Centralized API client for the Escrow Payment System.
// All fetch calls go through here for consistent error handling,
// base URL management, and auth token injection.
// ─────────────────────────────────────────────────────────────

const BASE_URL = 'http://localhost:8000';

// ── Token Management ──────────────────────────────────────────

export const getToken = () => localStorage.getItem('escrow_token');
export const setToken = (t) => localStorage.setItem('escrow_token', t);
export const removeToken = () => localStorage.removeItem('escrow_token');

export const getUser = () => {
  const u = localStorage.getItem('escrow_user');
  return u ? JSON.parse(u) : null;
};
export const setUser = (u) => localStorage.setItem('escrow_user', JSON.stringify(u));
export const removeUser = () => localStorage.removeItem('escrow_user');

// ── Core Fetch Wrapper ────────────────────────────────────────

async function request(path, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  // Parse JSON (even error responses)
  let data;
  try { data = await res.json(); } catch { data = {}; }

  if (!res.ok) {
    const msg = data?.detail || data?.message || `HTTP ${res.status}`;
    throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
  }

  return data;
}

// ── Auth ──────────────────────────────────────────────────────

export const api = {
  auth: {
    signup: (body) => request('/auth/signup', { method: 'POST', body: JSON.stringify(body) }),
    login:  (body) => request('/auth/login',  { method: 'POST', body: JSON.stringify(body) }),
    me:     ()     => request('/auth/me'),
    sellers:()     => request('/auth/sellers'),
  },

  // ── Orders ──────────────────────────────────────────────────
  orders: {
    list:       ()       => request('/orders'),
    get:        (id)     => request(`/orders/${id}`),
    create:     (body)   => request('/orders', { method: 'POST', body: JSON.stringify(body) }),
    deliver:    (id)     => request(`/orders/${id}/deliver`, { method: 'POST' }),
    analytics:  ()       => request('/orders/analytics'),
  },

  // ── Escrow ──────────────────────────────────────────────────
  escrow: {
    deposit:      (order_id) => request('/escrow/deposit',  { method: 'POST', body: JSON.stringify({ order_id }) }),
    release:      (order_id) => request('/escrow/release',  { method: 'POST', body: JSON.stringify({ order_id }) }),
    dispute:      (order_id) => request('/escrow/dispute',  { method: 'POST', body: JSON.stringify({ order_id }) }),
    refund:       (order_id) => request('/escrow/refund',   { method: 'POST', body: JSON.stringify({ order_id }) }),
    transactions: (order_id) => request(`/escrow/transactions/${order_id}`),
  },
};
