// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

/**
 * Wings of Capital — Reusable Table Component
 * Sortable, filterable, paginated — DOM-based, no innerHTML with user data.
 *
 * Usage:
 *   const tbl = new WocTable({
 *     container: '#my-table',
 *     columns: [
 *       { key: 'name',   label: 'Name',   sortable: true },
 *       { key: 'amount', label: 'Amount', sortable: true, formatter: Fmt.currency },
 *       { key: 'status', label: 'Status', render: row => BadgeEl(row.status) },
 *     ],
 *     data: [...],
 *     pageSize: 10,
 *   });
 */

'use strict';

class WocTable {
  #opts;
  #data;
  #filtered;
  #page;
  #sortKey;
  #sortDir;
  #container;

  constructor(opts = {}) {
    this.#opts     = opts;
    this.#data     = opts.data || [];
    this.#filtered = [...this.#data];
    this.#page     = 1;
    this.#sortKey  = opts.defaultSort || null;
    this.#sortDir  = opts.defaultSortDir || 'asc';

    const target = typeof opts.container === 'string'
      ? document.querySelector(opts.container)
      : opts.container;

    if (!target) { console.warn('[WocTable] Container not found:', opts.container); return; }
    this.#container = target;
    this.#render();
  }

  // ── Public API ───────────────────────────────────────────────

  setData(data) {
    this.#data     = data || [];
    this.#filtered = [...this.#data];
    this.#page     = 1;
    this.#applySort();
    this.#render();
  }

  refresh() { this.#render(); }

  // ── Internal helpers ─────────────────────────────────────────

  #el(tag, cls, attrs = {}) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    Object.entries(attrs).forEach(([k, v]) => n.setAttribute(k, v));
    return n;
  }

  #txt(str) { return document.createTextNode(String(str ?? '')); }

  get #pageSize() { return this.#opts.pageSize || 10; }

  get #pageCount() { return Math.max(1, Math.ceil(this.#filtered.length / this.#pageSize)); }

  get #pageData() {
    const start = (this.#page - 1) * this.#pageSize;
    return this.#filtered.slice(start, start + this.#pageSize);
  }

  #applySort() {
    if (!this.#sortKey) return;
    const dir = this.#sortDir === 'asc' ? 1 : -1;
    this.#filtered.sort((a, b) => {
      const av = a[this.#sortKey]; const bv = b[this.#sortKey];
      if (av == null) return dir;
      if (bv == null) return -dir;
      return typeof av === 'number' ? (av - bv) * dir : String(av).localeCompare(String(bv)) * dir;
    });
  }

  #applyFilter(query) {
    const q = query.toLowerCase();
    this.#filtered = q
      ? this.#data.filter(row =>
          Object.values(row).some(v => String(v ?? '').toLowerCase().includes(q))
        )
      : [...this.#data];
    this.#page = 1;
    this.#applySort();
    this.#renderBody();
    this.#renderPagination();
  }

  // ── Render ───────────────────────────────────────────────────

  #render() {
    this.#container.innerHTML = '';

    if (this.#opts.searchable !== false) {
      this.#container.appendChild(this.#buildSearch());
    }

    const wrap = this.#el('div', 'overflow-x-auto');
    const table = this.#el('table', '', { role: 'grid', 'aria-label': this.#opts.label || 'Data table' });

    table.appendChild(this.#buildHead());
    this.#tbody = table.appendChild(document.createElement('tbody'));
    this.#renderBody();

    wrap.appendChild(table);
    this.#container.appendChild(wrap);
    this.#paginationEl = this.#el('div', 'table-pagination');
    this.#container.appendChild(this.#paginationEl);
    this.#renderPagination();
  }

  #buildSearch() {
    const wrap  = this.#el('div', 'd-flex items-center gap-3', { style: 'margin-bottom: var(--space-4)' });
    const input = this.#el('input', '', {
      type:        'search',
      placeholder: 'Search…',
      'aria-label':'Search table',
      style:       'max-width: 280px;',
    });
    input.addEventListener('input', e => this.#applyFilter(e.target.value));

    const countEl = this.#el('span', 'text-sm text-tertiary');
    countEl.textContent = `${this.#data.length} records`;
    this.#countEl = countEl;

    wrap.append(input, countEl);
    return wrap;
  }

  #buildHead() {
    const thead = document.createElement('thead');
    const tr    = document.createElement('tr');

    this.#opts.columns.forEach(col => {
      const th = document.createElement('th');
      th.scope = 'col';

      const inner = this.#el('div', 'd-flex items-center gap-2', { style: 'cursor: pointer; user-select: none;' });
      inner.appendChild(this.#txt(col.label));

      if (col.sortable !== false) {
        const icon = this.#el('span', 'sort-icon');
        icon.textContent = this.#sortKey === col.key
          ? (this.#sortDir === 'asc' ? '↑' : '↓')
          : '↕';
        icon.style.opacity = this.#sortKey === col.key ? '1' : '0.4';
        inner.appendChild(icon);

        th.addEventListener('click', () => {
          if (this.#sortKey === col.key) {
            this.#sortDir = this.#sortDir === 'asc' ? 'desc' : 'asc';
          } else {
            this.#sortKey = col.key;
            this.#sortDir = 'asc';
          }
          this.#applySort();
          this.#render();
        });
      }

      th.appendChild(inner);
      if (col.width) th.style.width = col.width;
      tr.appendChild(th);
    });

    thead.appendChild(tr);
    return thead;
  }

  #renderBody() {
    if (!this.#tbody) return;
    this.#tbody.innerHTML = '';

    const rows = this.#pageData;

    if (!rows.length) {
      const tr = document.createElement('tr');
      const td = document.createElement('td');
      td.colSpan = this.#opts.columns.length;
      td.style.textAlign = 'center';
      td.style.padding   = 'var(--space-8)';
      td.style.color     = 'var(--color-text-tertiary)';
      td.textContent     = this.#opts.emptyMessage || 'No data available';
      tr.appendChild(td);
      this.#tbody.appendChild(tr);
      return;
    }

    rows.forEach((row, ri) => {
      const tr = document.createElement('tr');
      tr.setAttribute('aria-rowindex', (this.#page - 1) * this.#pageSize + ri + 1);

      if (this.#opts.onRowClick) {
        tr.style.cursor = 'pointer';
        tr.addEventListener('click', () => this.#opts.onRowClick(row));
      }

      this.#opts.columns.forEach(col => {
        const td = document.createElement('td');

        if (col.render) {
          // col.render must return a DOM element
          const node = col.render(row, ri);
          if (node instanceof Node) td.appendChild(node);
          else td.textContent = String(node ?? '');
        } else {
          const val = row[col.key];
          td.textContent = col.formatter ? col.formatter(val, row) : String(val ?? '—');
        }

        if (col.align) td.style.textAlign = col.align;
        tr.appendChild(td);
      });

      this.#tbody.appendChild(tr);
    });

    if (this.#countEl) {
      this.#countEl.textContent = `${this.#filtered.length} records`;
    }
  }

  #renderPagination() {
    if (!this.#paginationEl) return;
    this.#paginationEl.innerHTML = '';

    if (this.#pageCount <= 1 && this.#opts.hidePaginationOnSingle !== false) return;

    const wrap = this.#el('div', 'd-flex items-center justify-between', {
      style: 'margin-top: var(--space-4); font-size: var(--text-sm);',
    });

    const info = this.#el('span', 'text-tertiary');
    const start = (this.#page - 1) * this.#pageSize + 1;
    const end   = Math.min(this.#page * this.#pageSize, this.#filtered.length);
    info.textContent = `Showing ${start}–${end} of ${this.#filtered.length}`;

    const btns = this.#el('div', 'd-flex gap-2');

    const prev = this.#el('button', 'btn btn-ghost btn-sm');
    prev.textContent = '← Prev';
    prev.disabled    = this.#page === 1;
    prev.addEventListener('click', () => { this.#page--; this.#renderBody(); this.#renderPagination(); });

    const next = this.#el('button', 'btn btn-ghost btn-sm');
    next.textContent = 'Next →';
    next.disabled    = this.#page >= this.#pageCount;
    next.addEventListener('click', () => { this.#page++; this.#renderBody(); this.#renderPagination(); });

    const pageInfo = this.#el('span', 'text-tertiary', { style: 'padding: 0 var(--space-2); align-self: center;' });
    pageInfo.textContent = `${this.#page} / ${this.#pageCount}`;

    btns.append(prev, pageInfo, next);
    wrap.append(info, btns);
    this.#paginationEl.appendChild(wrap);
  }
}
