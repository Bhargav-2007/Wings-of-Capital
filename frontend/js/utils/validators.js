// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

/**
 * Wings of Capital — Validation and Sanitization Utilities
 * Focuses on OWASP Top 10 prevention for client-side inputs.
 */

'use strict';

const Validators = (() => {
  // ── Sanitization (XSS Prevention) ──────────────────────────────
  
  /**
   * Basic HTML sanitizer. 
   * Strips all tags, allowing only plain text.
   * For rich text, a proper library like DOMPurify would be needed.
   */
  function sanitize(input) {
    if (typeof input !== 'string') return input;
    const div = document.createElement('div');
    div.textContent = input; // Escapes HTML entities
    return div.innerHTML;    // Returns escaped string
  }

  // ── Validation Rules ───────────────────────────────────────────

  function isEmail(email) {
    if (!email || typeof email !== 'string') return false;
    // Standard RFC 5322 regex (simplified)
    const re = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
    return re.test(email);
  }

  /**
   * Enforces:
   * - Min 12 chars
   * - 1 uppercase
   * - 1 lowercase
   * - 1 number
   * - 1 symbol
   */
  function isStrongPassword(password) {
    if (!password || typeof password !== 'string') return false;
    if (password.length < 12) return false;
    if (!/[A-Z]/.test(password)) return false;
    if (!/[a-z]/.test(password)) return false;
    if (!/[0-9]/.test(password)) return false;
    if (!/[^A-Za-z0-9]/.test(password)) return false;
    return true;
  }
  
  function isNumeric(value) {
      if(value === null || value === undefined || value === '') return false;
      return !isNaN(Number(value));
  }

  return Object.freeze({
    sanitize,
    isEmail,
    isStrongPassword,
    isNumeric
  });
})();
