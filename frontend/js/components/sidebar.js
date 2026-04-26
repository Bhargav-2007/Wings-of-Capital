// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

/**
 * Wings of Capital — Sidebar Component
 *
 * Renders the shared fixed sidebar on all authenticated pages.
 * Active state is set by passing the current page identifier.
 * All nav links open target="_blank" per MPA spec.
 *
 * Usage:
 *   Sidebar.render('dashboard');
 *   Sidebar.render('portfolio');
 */

'use strict';

const Sidebar = (() => {

  const NAV_ITEMS = [
    { id: 'dashboard', label: 'Dashboard',  icon: '⬛', href: '/dashboard.html' },
    { id: 'portfolio', label: 'Portfolio',  icon: '📊', href: '/portfolio.html' },
    { id: 'trading',   label: 'Trading',    icon: '⚡', href: '/trading.html'   },
    { id: 'analytics', label: 'Analytics',  icon: '📈', href: '/analytics.html' },
    { id: 'neuro-ai',  label: 'Neuro AI',   icon: '🤖', href: '/neuro-ai.html'  },
    { id: 'accounts',  label: 'Accounts',   icon: '🏦', href: '/accounts.html'  },
  ];

  // ── Safe text node creation (XSS prevention) ───────────────────
  function el(tag, attrs = {}, ...children) {
    const node = document.createElement(tag);
    Object.entries(attrs).forEach(([k, v]) => {
      if (k === 'className') node.className = v;
      else if (k === 'textContent') node.textContent = v;
      else node.setAttribute(k, v);
    });
    children.forEach(child => {
      if (child == null) return;
      node.appendChild(typeof child === 'string'
        ? document.createTextNode(child)
        : child
      );
    });
    return node;
  }

  function buildLogo() {
    const wrap = el('div', { className: 'sidebar-logo' });

    const icon = el('div', { className: 'sidebar-logo-icon' });
    icon.textContent = '🪶';

    const textWrap = el('div', {});
    const name = el('div', { className: 'sidebar-logo-text nav-item-label', textContent: 'Wings of Capital' });
    const sub  = el('div', { className: 'sidebar-logo-sub  nav-item-label', textContent: 'Institutional Grade' });
    textWrap.append(name, sub);

    wrap.append(icon, textWrap);
    return wrap;
  }

  function buildNavItem(item, activeId) {
    const isActive = item.id === activeId;
    const a = el('a', {
      className:   `nav-item${isActive ? ' active' : ''}`,
      href:        item.href,
      target:      '_blank',         // per MPA spec: open in new tab
      rel:         'noopener noreferrer',
      'aria-current': isActive ? 'page' : 'false',
      'aria-label':   item.label,
    });

    const icon  = el('span', { className: 'nav-item-icon' });
    icon.textContent = item.icon;

    const label = el('span', { className: 'nav-item-label', textContent: item.label });

    a.append(icon, label);
    return a;
  }

  function buildUserCard() {
    const state = stateManager.getState();
    const user  = state.user;
    const email = user?.email || 'user@woc.io';
    const name  = user?.name  || email.split('@')[0];
    const initials = name.slice(0, 2).toUpperCase();

    const wrap   = el('div', { className: 'sidebar-user', role: 'button', tabindex: '0', 'aria-label': 'User menu' });
    const avatar = el('div', { className: 'sidebar-avatar', textContent: initials });
    const info   = el('div', {});
    const uname  = el('div', { className: 'sidebar-user-name nav-item-label', textContent: name });
    const uemail = el('div', { className: 'sidebar-user-email nav-item-label', textContent: email });
    info.append(uname, uemail);
    wrap.append(avatar, info);
    return wrap;
  }

  function buildThemeToggle() {
    const btn = el('button', {
      className:        'theme-toggle nav-item-label',
      'data-theme-toggle': 'true',
      'aria-label':     'Toggle theme',
      title:            'Toggle theme',
      style:            'width:100%; margin-bottom: var(--space-2); border-radius: var(--radius-lg); justify-content: flex-start; gap: var(--space-3); padding: var(--space-3) var(--space-4); background: transparent; color: var(--color-sidebar-text);',
    });

    const icon = el('span', { 'data-theme-icon': 'true', className: 'nav-item-icon' });
    icon.textContent = ThemeManager.isDark() ? '☀️' : '🌙';

    const label = el('span', { className: 'nav-item-label' });
    label.textContent = ThemeManager.isDark() ? 'Light Mode' : 'Dark Mode';

    btn.append(icon, label);
    return btn;
  }

  function buildLogoutBtn() {
    const btn = el('button', {
      className: 'nav-item',
      id:        'sidebar-logout',
      style:     'width:100%; text-align:left; color: var(--color-danger);',
      'aria-label': 'Logout',
    });
    const icon  = el('span', { className: 'nav-item-icon', textContent: '🚪' });
    const label = el('span', { className: 'nav-item-label', textContent: 'Logout' });
    btn.append(icon, label);
    btn.addEventListener('click', () => AuthManager.logout());
    return btn;
  }

  // ── Main render ─────────────────────────────────────────────────

  function render(activePageId = '') {
    const target = document.querySelector('.app-sidebar');
    if (!target) {
      console.warn('[Sidebar] No .app-sidebar element found');
      return;
    }

    // Logo
    target.appendChild(buildLogo());

    // Nav
    const nav = el('nav', { className: 'sidebar-nav', 'aria-label': 'Main navigation' });
    const sectionTitle = el('div', { className: 'sidebar-section-title', textContent: 'Main Menu' });
    nav.appendChild(sectionTitle);
    NAV_ITEMS.forEach(item => nav.appendChild(buildNavItem(item, activePageId)));
    target.appendChild(nav);

    // Footer
    const footer = el('div', { className: 'sidebar-footer' });
    footer.append(buildThemeToggle(), buildUserCard(), buildLogoutBtn());
    target.appendChild(footer);

    // Bind theme toggle
    ThemeManager.bindToggleButtons();
  }

  return Object.freeze({ render });
})();
