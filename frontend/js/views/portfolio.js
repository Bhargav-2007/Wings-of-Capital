// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

/**
 * Wings of Capital — Portfolio View Logic
 * Handles KPI data, performance chart, and the asset holdings table.
 */

'use strict';

document.addEventListener('DOMContentLoaded', async () => {
  // Guard: Must be authenticated
  if (!AuthManager.requireAuth()) return;

  // Render Sidebar (Active: Portfolio)
  Sidebar.render('portfolio');

  try {
    stateManager.setLoading(true);

    // Simulate API fetch
    await new Promise(r => setTimeout(r, 600));

    renderKPIs();
    renderPerformanceChart();
    renderAssetsTable();

  } catch (err) {
    stateManager.addNotification('Failed to load portfolio data', 'danger');
    console.error(err);
  } finally {
    stateManager.setLoading(false);
  }

  // ── 1. Top KPIs ──────────────────────────────────────────────────

  function renderKPIs() {
    const totalEl = document.getElementById('portfolio-total');
    const changeVal = document.querySelector('#portfolio-change span:nth-child(2)');
    const stakedEl = document.getElementById('portfolio-staked');
    const pnlEl = document.getElementById('portfolio-pnl');
    const pnlPct = document.getElementById('portfolio-pnl-pct');

    // Mock Data
    const total = 142580.45;
    const change24h = 3450.20;
    const staked = 45000.00;
    const pnl = 28400.15;
    const pnlPercent = 24.5;

    totalEl.textContent = Fmt.currency(total);
    changeVal.textContent = Fmt.currency(Math.abs(change24h));
    stakedEl.textContent = Fmt.currency(staked);
    pnlEl.textContent = Fmt.currency(pnl);
    pnlPct.textContent = Fmt.percent(pnlPercent, false); // false means don't divide by 100
  }

  // ── 2. Performance Chart ─────────────────────────────────────────

  function renderPerformanceChart() {
    const labels = ChartHelpers.generateDateLabels(30);
    const data   = ChartHelpers.generateRandomWalk(30, 110000, 3000);

    LineChart('performanceChart', labels, [{
      label: 'Portfolio Value',
      data: data,
      color: 'var(--brand-500)'
    }], {
      yFormatter: (val) => '$' + (val / 1000).toFixed(0) + 'k'
    });
  }

  // ── 3. Assets Table ──────────────────────────────────────────────

  function renderAssetsTable() {
    // Mock Data
    const assets = [
      { id: 'btc',  symbol: 'BTC',  name: 'Bitcoin',  balance: 1.245, price: 65400.00, value: 81423.00, change24h: 2.4,  allocation: 57.1 },
      { id: 'eth',  symbol: 'ETH',  name: 'Ethereum', balance: 14.5,  price: 3450.00,  value: 50025.00, change24h: 4.1,  allocation: 35.1 },
      { id: 'sol',  symbol: 'SOL',  name: 'Solana',   balance: 65.2,  price: 145.20,   value: 9467.04,  change24h: -1.2, allocation: 6.6 },
      { id: 'usdc', symbol: 'USDC', name: 'USD Coin', balance: 1665.41,price: 1.00,    value: 1665.41,  change24h: 0.0,  allocation: 1.2 },
    ];

    new WocTable({
      container: '#assets-table-container',
      data: assets,
      defaultSort: 'value',
      defaultSortDir: 'desc',
      columns: [
        {
          key: 'symbol',
          label: 'Asset',
          sortable: true,
          render: (row) => {
            const wrap = document.createElement('div');
            wrap.className = 'd-flex items-center gap-3';
            
            // Generate a deterministic color based on symbol
            const hue = row.symbol.split('').reduce((a, b) => a + b.charCodeAt(0), 0) * 137 % 360;
            
            wrap.innerHTML = `
              <div style="width:32px; height:32px; border-radius:var(--radius-full); background:hsl(${hue}, 70%, 50%); display:flex; align-items:center; justify-content:center; color:#fff; font-size:12px; font-weight:bold;">
                ${row.symbol[0]}
              </div>
              <div>
                <div class="font-semi text-primary">${row.symbol}</div>
                <div class="text-xs text-tertiary">${row.name}</div>
              </div>
            `;
            return wrap;
          }
        },
        { key: 'price', label: 'Price', sortable: true, align: 'right', formatter: Fmt.currency },
        {
          key: 'balance',
          label: 'Balance',
          sortable: true,
          align: 'right',
          render: (row) => {
            const wrap = document.createElement('div');
            wrap.innerHTML = `
              <div class="font-mono text-primary">${Fmt.number(row.balance)}</div>
              <div class="text-xs text-tertiary">${row.symbol}</div>
            `;
            return wrap;
          }
        },
        { key: 'value', label: 'Value (USD)', sortable: true, align: 'right', formatter: Fmt.currency },
        {
          key: 'change24h',
          label: '24h Change',
          sortable: true,
          align: 'right',
          render: (row) => {
            const el = document.createElement('div');
            const isPos = row.change24h > 0;
            const isZero = row.change24h === 0;
            
            el.className = isZero ? 'text-tertiary' : (isPos ? 'text-success' : 'text-danger');
            el.textContent = isZero ? '0.00%' : `${isPos ? '+' : ''}${row.change24h.toFixed(2)}%`;
            return el;
          }
        },
        {
          key: 'allocation',
          label: 'Allocation',
          sortable: true,
          align: 'right',
          render: (row) => {
            const wrap = document.createElement('div');
            wrap.style.display = 'flex';
            wrap.style.alignItems = 'center';
            wrap.style.gap = 'var(--space-2)';
            wrap.style.justifyContent = 'flex-end';

            wrap.innerHTML = `
              <span class="text-sm">${row.allocation.toFixed(1)}%</span>
              <div class="progress" style="width: 60px; height: 4px;">
                <div class="progress-bar" style="width: ${row.allocation}%; background: var(--brand-500)"></div>
              </div>
            `;
            return wrap;
          }
        }
      ]
    });
  }

});
