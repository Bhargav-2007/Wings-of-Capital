// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

/**
 * Wings of Capital — Form Management Component
 * Handles validation, loading states, and error display for forms.
 *
 * Usage:
 *   const form = new WocForm('#login-form', {
 *     onSubmit: async (data) => await AuthManager.login(data.email, data.password),
 *     onSuccess: () => window.location.href = '/dashboard.html',
 *   });
 */

'use strict';

class WocForm {
  #formEl;
  #submitBtn;
  #opts;
  #errorContainer;

  constructor(selector, opts = {}) {
    this.#formEl = typeof selector === 'string' ? document.querySelector(selector) : selector;
    if (!this.#formEl) {
      console.warn('[WocForm] Form not found:', selector);
      return;
    }

    this.#opts = Object.assign({
      validateOnBlur: true,
      clearOnSubmit: false,
    }, opts);

    this.#submitBtn = this.#formEl.querySelector('button[type="submit"]');
    
    // Create or find error container
    this.#errorContainer = this.#formEl.querySelector('.form-global-error');
    if (!this.#errorContainer) {
      this.#errorContainer = document.createElement('div');
      this.#errorContainer.className = 'form-global-error form-error d-none';
      this.#errorContainer.style.marginBottom = 'var(--space-4)';
      this.#formEl.insertBefore(this.#errorContainer, this.#formEl.firstChild);
    }

    this.#bindEvents();
  }

  // ── Event Binding ──────────────────────────────────────────────

  #bindEvents() {
    this.#formEl.addEventListener('submit', this.#handleSubmit.bind(this));

    if (this.#opts.validateOnBlur) {
      const inputs = this.#formEl.querySelectorAll('input, select, textarea');
      inputs.forEach(input => {
        input.addEventListener('blur', () => this.#validateField(input));
        input.addEventListener('input', () => this.#clearFieldError(input));
      });
    }
  }

  // ── Validation ─────────────────────────────────────────────────

  #validateField(input) {
    let isValid = true;
    let errorMsg = '';

    // HTML5 Validation
    if (!input.checkValidity()) {
      isValid = false;
      errorMsg = input.validationMessage;
    }

    // Custom Validation (via data-validate attribute)
    if (isValid && input.dataset.validate) {
      const rule = input.dataset.validate;
      if (rule === 'email' && !Validators.isEmail(input.value)) {
        isValid = false;
        errorMsg = 'Please enter a valid email address.';
      } else if (rule === 'password' && !Validators.isStrongPassword(input.value)) {
        isValid = false;
        errorMsg = 'Password must be at least 12 characters with uppercase, lowercase, numbers, and symbols.';
      } else if (rule === 'match') {
        const targetId = input.dataset.matchTarget;
        const targetInput = document.getElementById(targetId);
        if (targetInput && input.value !== targetInput.value) {
          isValid = false;
          errorMsg = 'Values do not match.';
        }
      }
    }

    this.#showFieldError(input, isValid ? null : errorMsg);
    return isValid;
  }

  #validateForm() {
    let isFormValid = true;
    const inputs = this.#formEl.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
      if (!this.#validateField(input)) {
        isFormValid = false;
      }
    });
    return isFormValid;
  }

  // ── Error Display ──────────────────────────────────────────────

  #showFieldError(input, message) {
    const group = input.closest('.form-group') || input.parentElement;
    let errorEl = group.querySelector('.form-error-msg');
    
    if (message) {
      input.classList.add('input-error');
      input.setAttribute('aria-invalid', 'true');
      if (!errorEl) {
        errorEl = document.createElement('div');
        errorEl.className = 'form-error-msg form-error';
        errorEl.id = `${input.id}-error`;
        group.appendChild(errorEl);
        input.setAttribute('aria-describedby', errorEl.id);
      }
      errorEl.textContent = message;
      errorEl.classList.remove('d-none');
    } else {
      this.#clearFieldError(input);
    }
  }

  #clearFieldError(input) {
    input.classList.remove('input-error');
    input.removeAttribute('aria-invalid');
    const group = input.closest('.form-group') || input.parentElement;
    const errorEl = group.querySelector('.form-error-msg');
    if (errorEl) {
      errorEl.classList.add('d-none');
      errorEl.textContent = '';
    }
  }

  showGlobalError(message) {
    this.#errorContainer.textContent = message;
    this.#errorContainer.classList.remove('d-none');
  }

  clearGlobalError() {
    this.#errorContainer.textContent = '';
    this.#errorContainer.classList.add('d-none');
  }

  // ── State Management ───────────────────────────────────────────

  setLoading(isLoading) {
    if (!this.#submitBtn) return;
    
    if (isLoading) {
      this.#submitBtn.disabled = true;
      this.#submitBtn.classList.add('btn-loading');
      // Disable all inputs
      const inputs = this.#formEl.querySelectorAll('input, select, textarea');
      inputs.forEach(i => i.disabled = true);
    } else {
      this.#submitBtn.disabled = false;
      this.#submitBtn.classList.remove('btn-loading');
      // Re-enable inputs
      const inputs = this.#formEl.querySelectorAll('input, select, textarea');
      inputs.forEach(i => i.disabled = false);
    }
  }

  // ── Submit Handler ─────────────────────────────────────────────

  async #handleSubmit(e) {
    e.preventDefault();
    this.clearGlobalError();

    if (!this.#validateForm()) {
      // Focus first invalid element
      const firstInvalid = this.#formEl.querySelector('.input-error');
      if (firstInvalid) firstInvalid.focus();
      return;
    }

    if (!this.#opts.onSubmit) return;

    // Collect data using FormData
    const formData = new FormData(this.#formEl);
    const data = Object.fromEntries(formData.entries());
    
    // Sanitize data before passing to handler
    const sanitizedData = {};
    for (const [key, value] of Object.entries(data)) {
        sanitizedData[key] = Validators.sanitize(value);
    }

    this.setLoading(true);
    
    try {
      await this.#opts.onSubmit(sanitizedData, e);
      if (this.#opts.clearOnSubmit) {
        this.#formEl.reset();
      }
      if (this.#opts.onSuccess) {
        this.#opts.onSuccess(sanitizedData);
      }
    } catch (err) {
      this.showGlobalError(err.message || 'An error occurred submitting the form.');
      if (this.#opts.onError) {
        this.#opts.onError(err);
      }
    } finally {
      this.setLoading(false);
    }
  }
}
