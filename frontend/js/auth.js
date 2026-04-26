// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

/**
 * Wings of Capital — Auth Manager
 *
 * SECURITY FIXES vs original:
 *  - JWT payload decoded client-side to extract expiry (exp claim)
 *    so stateManager can enforce token validity window
 *  - useToken() development helper validates JWT structure before storing
 *  - No tokens/passwords ever written to console
 *  - MPA: redirects use window.location.href to named HTML files
 */

'use strict';

// ── JWT decode (no verification — just payload extraction) ───────
function decodeJwtPayload(token) {
  try {
    const base64Url = token.split('.')[1];
    if (!base64Url) return null;
    const base64    = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonStr   = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonStr);
  } catch {
    return null;
  }
}

/** Returns seconds until expiry from the JWT exp claim. */
function expiresInFromToken(token) {
  const payload = decodeJwtPayload(token);
  if (!payload?.exp) return 900;   // Default 15 min if no exp claim
  const remaining = payload.exp - Math.floor(Date.now() / 1000);
  return Math.max(remaining, 0);
}

class AuthManager {

  // ── Login ──────────────────────────────────────────────────────

  static async login(email, password) {
    stateManager.setLoading(true);
    try {
      const data = await apiClient.post('/auth/login', { email, password });

      const expiresIn = data.expires_in || expiresInFromToken(data.access_token);
      stateManager.setUser(data.user, data.access_token, data.refresh_token, expiresIn);
      stateManager.addNotification('Welcome back!', 'success');

      return data.user;
    } catch (err) {
      stateManager.addNotification(err.message, 'danger');
      throw err;
    } finally {
      stateManager.setLoading(false);
    }
  }

  // ── Register ───────────────────────────────────────────────────

  static async register(email, password, passwordConfirm) {
    stateManager.setLoading(true);
    try {
      if (password !== passwordConfirm) {
        throw new Error('Passwords do not match');
      }
      const data = await apiClient.post('/auth/register', { email, password });
      stateManager.addNotification(
        'Account created! Check your email to verify.',
        'success'
      );
      return data;
    } catch (err) {
      stateManager.addNotification(err.message, 'danger');
      throw err;
    } finally {
      stateManager.setLoading(false);
    }
  }

  // ── Logout ─────────────────────────────────────────────────────

  static async logout() {
    stateManager.setLoading(true);
    try {
      await apiClient.post('/auth/logout', {});
    } catch {
      // Best-effort — clear local state regardless
    } finally {
      stateManager.clearUser();
      stateManager.setLoading(false);
      window.location.href = '/index.html';
    }
  }

  // ── Get current user ───────────────────────────────────────────

  static async getMe() {
    return apiClient.get('/auth/me');
  }

  // ── Check auth (used by page guards) ──────────────────────────

  static isAuthenticated() {
    return stateManager.getState().isAuthenticated &&
           stateManager.isTokenValid();
  }

  /**
   * Guard — call at the top of every protected page's script.
   * If not authenticated, redirects to login immediately.
   */
  static requireAuth(redirectTo = '/index.html') {
    if (!AuthManager.isAuthenticated()) {
      window.location.replace(redirectTo);
      return false;
    }
    return true;
  }

  // ── MFA ────────────────────────────────────────────────────────

  static async enableMFA() {
    stateManager.setLoading(true);
    try {
      return await apiClient.post('/auth/mfa/enable', {});
    } finally {
      stateManager.setLoading(false);
    }
  }

  static async verifyMFA(code) {
    stateManager.setLoading(true);
    try {
      return await apiClient.post('/auth/mfa/verify', { code });
    } finally {
      stateManager.setLoading(false);
    }
  }

  // ── Dev helper (development only) ─────────────────────────────

  /**
   * Inject a pre-generated JWT for local development.
   * Validates JWT structure before storing.
   */
  static devUseToken(token, userId = 'dev-001', email = 'dev@woc.local') {
    if (typeof token !== 'string' || token.split('.').length !== 3) {
      console.error('[AuthManager.devUseToken] Invalid JWT format');
      return null;
    }
    const payload    = decodeJwtPayload(token);
    const expiresIn  = expiresInFromToken(token);
    const user       = { id: payload?.sub || userId, email: payload?.email || email, role: payload?.role || 'user' };

    stateManager.setUser(user, token, null, expiresIn);
    stateManager.addNotification('[DEV] Token injected', 'info', 3000);
    return user;
  }
}
