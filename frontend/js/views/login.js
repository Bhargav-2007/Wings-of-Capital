// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

/**
 * Wings of Capital — Login View Logic
 * Handles the tab switching and form submission for the login page.
 */

'use strict';

document.addEventListener('DOMContentLoaded', () => {
  // ── Tab Switching ──────────────────────────────────────────────

  const tabLogin = document.getElementById('tab-login');
  const tabReg   = document.getElementById('tab-register');
  const formLogin= document.getElementById('form-login');
  const formReg  = document.getElementById('form-register');

  function switchTab(isLogin) {
    if (isLogin) {
      tabLogin.style.borderBottom = '2px solid var(--color-primary)';
      tabLogin.classList.replace('text-tertiary', 'text-primary');
      tabLogin.classList.replace('font-medium', 'font-semi');
      
      tabReg.style.borderBottom = 'none';
      tabReg.classList.replace('text-primary', 'text-tertiary');
      tabReg.classList.replace('font-semi', 'font-medium');
      
      formLogin.classList.remove('d-none');
      formReg.classList.add('d-none');
    } else {
      tabReg.style.borderBottom = '2px solid var(--color-primary)';
      tabReg.classList.replace('text-tertiary', 'text-primary');
      tabReg.classList.replace('font-medium', 'font-semi');
      
      tabLogin.style.borderBottom = 'none';
      tabLogin.classList.replace('text-primary', 'text-tertiary');
      tabLogin.classList.replace('font-semi', 'font-medium');
      
      formReg.classList.remove('d-none');
      formLogin.classList.add('d-none');
    }
  }

  tabLogin.addEventListener('click', () => switchTab(true));
  tabReg.addEventListener('click', () => switchTab(false));

  // ── Password Visibility Toggle ─────────────────────────────────

  document.querySelectorAll('.pwd-toggle').forEach(toggle => {
    toggle.addEventListener('click', (e) => {
      const targetId = e.target.dataset.target;
      const input = document.getElementById(targetId);
      if (!input) return;
      
      if (input.type === 'password') {
        input.type = 'text';
        e.target.textContent = '🙈';
      } else {
        input.type = 'password';
        e.target.textContent = '👁️';
      }
    });
  });

  // ── Form Initialization ────────────────────────────────────────

  new WocForm('#form-login', {
    onSubmit: async (data) => {
      await AuthManager.login(data.email, data.password);
    },
    onSuccess: () => {
      window.location.href = '/dashboard.html';
    }
  });

  new WocForm('#form-register', {
    onSubmit: async (data) => {
      await AuthManager.register(data.email, data.password, data.passwordConfirm);
    },
    onSuccess: () => {
      // Switch back to login tab on success
      switchTab(true);
      document.getElementById('form-register').reset();
    }
  });

  // ── Auto-redirect if already logged in ─────────────────────────
  if (AuthManager.isAuthenticated()) {
    window.location.replace('/dashboard.html');
  }
});
