// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

/**
 * Wings of Capital — Formatting Utilities
 * Handles numbers, currencies, dates, and percentages consistently.
 */

'use strict';

const Fmt = (() => {

  const _currencyFormatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  const _compactCurrencyFormatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    notation: 'compact',
    compactDisplay: 'short',
    maximumFractionDigits: 1,
  });

  const _numberFormatter = new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 8, // For crypto
  });

  const _percentFormatter = new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
    signDisplay: 'exceptZero', // Shows + for positive
  });
  
  const _dateFormatter = new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
  });

  const _timeFormatter = new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
  });

  // ── API ────────────────────────────────────────────────────────

  function currency(val, compact = false) {
    if (val == null || isNaN(val)) return '—';
    return compact ? _compactCurrencyFormatter.format(val) : _currencyFormatter.format(val);
  }

  function number(val) {
    if (val == null || isNaN(val)) return '—';
    return _numberFormatter.format(val);
  }

  function percent(val, rawDecimal = false) {
    if (val == null || isNaN(val)) return '—';
    // If rawDecimal is true, assume val is 0.05 for 5%. Otherwise assume 5 is 5%.
    const v = rawDecimal ? val : val / 100;
    return _percentFormatter.format(v);
  }

  function date(dateString) {
    if (!dateString) return '—';
    try {
      const d = new Date(dateString);
      if (isNaN(d.getTime())) return '—';
      return _dateFormatter.format(d);
    } catch {
      return '—';
    }
  }

  function time(dateString) {
      if (!dateString) return '—';
      try {
        const d = new Date(dateString);
        if (isNaN(d.getTime())) return '—';
        return _timeFormatter.format(d);
      } catch {
        return '—';
      }
  }

  function dateTime(dateString) {
      if (!dateString) return '—';
      return `${date(dateString)} ${time(dateString)}`;
  }

  /** Truncate a crypto address or hash */
  function truncateAddress(address, chars = 6) {
    if (!address || typeof address !== 'string') return '';
    if (address.length <= chars * 2) return address;
    return `${address.slice(0, chars + 2)}...${address.slice(-chars)}`;
  }

  return Object.freeze({
    currency,
    number,
    percent,
    date,
    time,
    dateTime,
    truncateAddress,
  });
})();
