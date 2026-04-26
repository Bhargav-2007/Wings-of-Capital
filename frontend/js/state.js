// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

/**
 * Wings of Capital — Client-Side State Manager
 *
 * SECURITY FIXES vs original:
 *  - Theme toggle now mutates .dark class on <html> (per spec),
 *    not data-theme attribute
 *  - Tokens stored with expiry timestamp; validated on every read
 *  - No sensitive data (tokens) ever written to console
 *  - restoreFromStorage performs JSON.parse in try/catch to prevent
 *    malformed localStorage values from crashing the app
 */

'use strict';

class StateManager {
  #state;
  #listeners;

  constructor() {
    this.#state = {
      user:            null,
      isAuthenticated: false,
      tokens: {
        accessToken:   null,
        refreshToken:  null,
        expiresAt:     null,   // Unix ms — validated before every API call
      },
      theme:           this.#readTheme(),
      notifications:   [],
      loading:         false,
      error:           null,
    };
    this.#listeners = new Set();
  }

  // ── Read / write helpers ────────────────────────────────────────

  #readTheme() {
    try {
      return localStorage.getItem('woc_theme') || 'dark';
    } catch {
      return 'dark';
    }
  }

  #writeStorage(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (e) {
      // Quota exceeded — fail silently, state still works in memory
      console.warn('[StateManager] localStorage write failed:', key);
    }
  }

  #removeStorage(key) {
    try { localStorage.removeItem(key); } catch { /* ignore */ }
  }

  // ── Subscriber pattern ──────────────────────────────────────────

  /** Subscribe to state changes. Returns an unsubscribe function. */
  subscribe(callback) {
    if (typeof callback !== 'function') return () => {};
    this.#listeners.add(callback);
    return () => this.#listeners.delete(callback);
  }

  #notify() {
    const snapshot = this.getState();
    this.#listeners.forEach(cb => {
      try { cb(snapshot); } catch (e) {
        console.error('[StateManager] listener error:', e);
      }
    });
  }

  // ── Public getters ──────────────────────────────────────────────

  getState() {
    // Return a shallow copy so listeners cannot mutate internal state
    return {
      ...this.#state,
      tokens: { ...this.#state.tokens },
      notifications: [...this.#state.notifications],
    };
  }

  setState(updates) {
    this.#state = { ...this.#state, ...updates };
    this.#notify();
  }

  // ── Authentication ──────────────────────────────────────────────

  /**
   * Persist authenticated user + tokens.
   * @param {object} user  - { id, email, role, … }
   * @param {string} accessToken
   * @param {string} refreshToken
   * @param {number} expiresIn  - seconds until access token expires
   */
  setUser(user, accessToken, refreshToken, expiresIn = 900) {
    const expiresAt = Date.now() + expiresIn * 1000;

    this.#state = {
      ...this.#state,
      user,
      isAuthenticated: !!user,
      tokens: { accessToken, refreshToken, expiresAt },
    };

    if (user && accessToken) {
      this.#writeStorage('woc_user',          JSON.stringify(user));
      this.#writeStorage('woc_access_token',  accessToken);
      this.#writeStorage('woc_refresh_token', refreshToken || '');
      this.#writeStorage('woc_token_expiry',  String(expiresAt));
    }

    this.#notify();
  }

  clearUser() {
    this.#state = {
      ...this.#state,
      user:            null,
      isAuthenticated: false,
      tokens: { accessToken: null, refreshToken: null, expiresAt: null },
    };
    this.#removeStorage('woc_user');
    this.#removeStorage('woc_access_token');
    this.#removeStorage('woc_refresh_token');
    this.#removeStorage('woc_token_expiry');
    this.#notify();
  }

  /** Returns true only if access token exists AND has not expired. */
  isTokenValid() {
    const { accessToken, expiresAt } = this.#state.tokens;
    if (!accessToken) return false;
    if (!expiresAt)   return true;   // no expiry stored → assume valid
    return Date.now() < expiresAt - 5000;  // 5s buffer
  }

  /** Restore state from localStorage on MPA page load. */
  restoreFromStorage() {
    try {
      const userRaw     = localStorage.getItem('woc_user');
      const accessToken = localStorage.getItem('woc_access_token');
      const refreshToken= localStorage.getItem('woc_refresh_token') || null;
      const expiresAt   = Number(localStorage.getItem('woc_token_expiry')) || null;

      if (userRaw && accessToken) {
        const user = JSON.parse(userRaw);
        // Only restore if token is not already expired
        if (!expiresAt || Date.now() < expiresAt) {
          this.#state = {
            ...this.#state,
            user,
            isAuthenticated: true,
            tokens: { accessToken, refreshToken, expiresAt },
          };
        } else {
          // Token expired — clear storage silently
          this.clearUser();
        }
      }
    } catch (e) {
      // Corrupted localStorage — clear and continue
      this.clearUser();
    }
  }

  // ── Theme ───────────────────────────────────────────────────────

  /**
   * Toggle dark/light theme.
   * Per spec: adds/removes .dark class on <html> element.
   * Persists to localStorage.
   */
  toggleTheme() {
    const next = this.#state.theme === 'dark' ? 'light' : 'dark';
    this.#applyTheme(next);
    this.setState({ theme: next });
    this.#writeStorage('woc_theme', next);
  }

  setTheme(theme) {
    if (theme !== 'dark' && theme !== 'light') return;
    this.#applyTheme(theme);
    this.setState({ theme });
    this.#writeStorage('woc_theme', theme);
  }

  #applyTheme(theme) {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }

  applyStoredTheme() {
    this.#applyTheme(this.#state.theme);
  }

  // ── Notifications ───────────────────────────────────────────────

  /**
   * Add a toast notification.
   * @param {string} message  - Plain text only (never inject as HTML)
   * @param {'success'|'danger'|'warning'|'info'} type
   * @param {number} duration - ms before auto-dismiss
   */
  addNotification(message, type = 'info', duration = 4000) {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    // XSS: message is stored as plain text; toast renderer uses textContent
    const note = { id, message: String(message), type };
    this.#state.notifications = [...this.#state.notifications, note];
    this.#notify();

    if (duration > 0) {
      setTimeout(() => this.removeNotification(id), duration);
    }
    return id;
  }

  removeNotification(id) {
    this.#state.notifications = this.#state.notifications.filter(n => n.id !== id);
    this.#notify();
  }

  clearNotifications() {
    this.#state.notifications = [];
    this.#notify();
  }

  // ── Loading / Error ─────────────────────────────────────────────

  setLoading(loading) { this.setState({ loading: Boolean(loading) }); }
  setError(error)     { this.setState({ error }); }
  clearError()        { this.setState({ error: null }); }
}

// ── Global singleton ────────────────────────────────────────────
const stateManager = new StateManager();

// Apply theme immediately on every MPA page load (before paint)
stateManager.applyStoredTheme();

// Restore auth state
window.addEventListener('DOMContentLoaded', () => {
  stateManager.restoreFromStorage();
});
