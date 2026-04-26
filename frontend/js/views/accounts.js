// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

/**
 * Wings of Capital — Accounts View Logic
 * Handles tab switching, profile updates, and security forms.
 */

'use strict';

document.addEventListener('DOMContentLoaded', async () => {
  if (!AuthManager.requireAuth()) return;

  Sidebar.render('accounts');

  const state = stateManager.getState();
  if (state.user) {
    populateProfileForm(state.user);
  }

  // ── Tab Navigation ───────────────────────────────────────────────

  const tabs = ['profile', 'security', 'api', 'preferences'];
  
  function switchTab(targetId) {
    tabs.forEach(id => {
      const tabBtn = document.getElementById(`tab-${id}`);
      const section = document.getElementById(`section-${id}`);
      
      if (id === targetId) {
        tabBtn.classList.add('active');
        section.classList.remove('d-none');
      } else {
        tabBtn.classList.remove('active');
        section.classList.add('d-none');
      }
    });
  }

  tabs.forEach(id => {
    const btn = document.getElementById(`tab-${id}`);
    if (btn) btn.addEventListener('click', () => switchTab(id));
  });

  // ── Profile Logic ────────────────────────────────────────────────

  function populateProfileForm(user) {
    const nameInput = document.getElementById('profile-name');
    const emailInput = document.getElementById('profile-email');
    const avatarEl = document.getElementById('profile-avatar');

    if (nameInput) nameInput.value = user.name || '';
    if (emailInput) emailInput.value = user.email || '';
    
    if (avatarEl) {
      const email = user.email || 'user@woc.io';
      const name = user.name || email.split('@')[0];
      avatarEl.textContent = name.slice(0, 2).toUpperCase();
    }
  }

  new WocForm('#form-profile', {
    onSubmit: async (data) => {
      // Simulate API call
      await new Promise(r => setTimeout(r, 800));
      
      // Update local state (in a real app, the API would return the updated user)
      const currentUser = stateManager.getState().user;
      const updatedUser = { ...currentUser, name: data.name, phone: data.phone };
      
      const tokens = stateManager.getState().tokens;
      // Re-save user state (need to extract expiresIn from existing token)
      stateManager.setUser(updatedUser, tokens.accessToken, tokens.refreshToken, 900);
      
      populateProfileForm(updatedUser);
    },
    onSuccess: () => {
      stateManager.addNotification('Profile updated successfully.', 'success');
      Sidebar.render('accounts'); // Re-render sidebar to update name/avatar
    }
  });

  // ── Security Logic ───────────────────────────────────────────────

  new WocForm('#form-password', {
    clearOnSubmit: true,
    onSubmit: async (data) => {
      // Simulate API call
      await new Promise(r => setTimeout(r, 1000));
      if (data.currentPassword === data.newPassword) {
         throw new Error('New password must be different from the current password.');
      }
    },
    onSuccess: () => {
      stateManager.addNotification('Password changed successfully.', 'success');
    }
  });

  // MFA Toggle Simulation
  const btnMfa = document.getElementById('btn-enable-mfa');
  const badgeMfa = document.getElementById('mfa-status-badge');
  let mfaEnabled = false;

  if (btnMfa) {
    btnMfa.addEventListener('click', () => {
      mfaEnabled = !mfaEnabled;
      if (mfaEnabled) {
        badgeMfa.textContent = 'Enabled';
        badgeMfa.className = 'badge badge-success mb-2 d-block text-center';
        btnMfa.textContent = 'Disable 2FA';
        btnMfa.classList.replace('btn-outline-primary', 'btn-outline-danger');
        stateManager.addNotification('Two-Factor Authentication enabled.', 'success');
      } else {
        badgeMfa.textContent = 'Disabled';
        badgeMfa.className = 'badge badge-danger mb-2 d-block text-center';
        btnMfa.textContent = 'Enable 2FA';
        btnMfa.classList.replace('btn-outline-danger', 'btn-outline-primary');
        stateManager.addNotification('Two-Factor Authentication disabled.', 'warning');
      }
    });
  }

});
