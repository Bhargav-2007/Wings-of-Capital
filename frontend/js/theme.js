// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

/**
 * Wings of Capital — Theme Manager
 *
 * Dedicated module for dark/light theme lifecycle.
 * Per spec: toggles .dark class on <html> element.
 * Reads system preference as default fallback.
 * Persists via localStorage (key: woc_theme).
 *
 * Usage (every HTML page):
 *   <script src="/js/theme.js"></script>   ← must load before body paint
 */

'use strict';

const ThemeManager = (() => {
  const STORAGE_KEY  = 'woc_theme';
  const DARK_CLASS   = 'dark';
  const VALID_THEMES = new Set(['dark', 'light']);

  // ── Internal ────────────────────────────────────────────────────

  function getSystemPreference() {
    return window.matchMedia?.('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';
  }

  function readStored() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return VALID_THEMES.has(stored) ? stored : null;
    } catch {
      return null;
    }
  }

  function persist(theme) {
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch { /* quota — ignore */ }
  }

  function apply(theme) {
    const html = document.documentElement;
    if (theme === 'dark') {
      html.classList.add(DARK_CLASS);
    } else {
      html.classList.remove(DARK_CLASS);
    }
    html.setAttribute('data-theme', theme);   // for any attr-based selectors
  }

  function updateToggleIcons(theme) {
    document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
      const icon = btn.querySelector('[data-theme-icon]') || btn;
      icon.textContent = theme === 'dark' ? '☀️' : '🌙';
      btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
      btn.setAttribute('title',      theme === 'dark' ? 'Light mode' : 'Dark mode');
    });
  }

  // ── Current theme state ─────────────────────────────────────────
  let _current = readStored() || getSystemPreference();

  // ── Apply immediately (before first paint) ─────────────────────
  apply(_current);

  // ── Public API ──────────────────────────────────────────────────

  function getCurrent()    { return _current; }
  function isDark()        { return _current === 'dark'; }

  function set(theme) {
    if (!VALID_THEMES.has(theme)) return;
    _current = theme;
    apply(_current);
    persist(_current);
    updateToggleIcons(_current);
    stateManager?.setTheme?.(_current);   // sync to state manager if loaded

    // Dispatch custom event for any listeners
    document.dispatchEvent(new CustomEvent('woc:themechange', { detail: { theme: _current } }));
  }

  function toggle() {
    set(_current === 'dark' ? 'light' : 'dark');
  }

  /**
   * Bind all [data-theme-toggle] buttons automatically.
   * Call once after DOMContentLoaded.
   */
  function bindToggleButtons() {
    document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
      btn.addEventListener('click', toggle);
    });
    updateToggleIcons(_current);
  }

  /**
   * Watch system preference changes (e.g., OS switches theme).
   * Only activates if user has not explicitly chosen a theme.
   */
  function watchSystemPreference() {
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    mq.addEventListener('change', e => {
      // Only auto-switch if no explicit user preference stored
      if (!readStored()) {
        set(e.matches ? 'dark' : 'light');
      }
    });
  }

  return Object.freeze({ getCurrent, isDark, set, toggle, bindToggleButtons, watchSystemPreference });
})();

// ── Auto-init on DOM ready ───────────────────────────────────────
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.bindToggleButtons();
    ThemeManager.watchSystemPreference();
  });
} else {
  ThemeManager.bindToggleButtons();
  ThemeManager.watchSystemPreference();
}
