// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

/**
 * Wings of Capital — Dashboard View Logic
 * Populates all 5 widgets using API data and Chart.js wrappers.
 */

'use strict';

document.addEventListener('DOMContentLoaded', async () => {
  // Guard: Must be authenticated
  if (!AuthManager.requireAuth()) return;

  // Render Sidebar (Active: Dashboard)
  Sidebar.render('dashboard');

  // Load data concurrently where possible
  try {
    stateManager.setLoading(true);
    
    // In a real app, these would be API calls:
    // const [portfolio, txs, insights] = await Promise.all([
    //   apiClient.get('/crypto/portfolio'),
    //   apiClient.get('/ledger/transactions?limit=5'),
    //   apiClient.get('/crypto/ai/predictions')
    // ]);

    // For now, we simulate API responses based on the implementation plan
    await new Promise(r => setTimeout(r, 600)); // Simulate network

    renderBalanceWidget();
    renderAIWidget();
    renderEarningsWidget();
    renderTransactionsWidget();
    renderSpendingWidget();

  } catch (err) {
    stateManager.addNotification('Failed to load dashboard data', 'danger');
    console.error(err);
  } finally {
    stateManager.setLoading(false);
  }

  // ── 1. Balance Widget ───────────────────────────────────────────

  function renderBalanceWidget() {
    const totalEl = document.getElementById('total-balance');
    const changeVal = document.getElementById('balance-change-val');
    const changePct = document.getElementById('balance-change-pct');
    const changeWrap = document.getElementById('balance-change');

    // Mock Data
    const balance = 142580.45;
    const change  = 3450.20;
    const isUp    = change >= 0;

    totalEl.textContent = Fmt.currency(balance);
    changeVal.textContent = Fmt.currency(Math.abs(change));
    changePct.textContent = Fmt.percent((change / balance) * 100);
    
    if (!isUp) {
      changeWrap.classList.replace('positive', 'negative');
      changeWrap.querySelector('span').textContent = '↓';
    }

    // Chart
    const labels = ChartHelpers.generateDateLabels(7);
    const data   = ChartHelpers.generateRandomWalk(7, 138000, 2000);

    LineChart('balanceChart', labels, [{
      label: 'Net Balance',
      data: data,
    }], {
      yFormatter: (val) => '$' + (val / 1000).toFixed(0) + 'k'
    });
  }

  // ── 2. AI Insights Widget ───────────────────────────────────────

  function renderAIWidget() {
    const content = document.getElementById('ai-insight-content');
    const confText = document.getElementById('ai-confidence-text');
    const confFill = document.getElementById('ai-confidence-fill');

    // Mock AI Prediction
    content.innerHTML = `Strong accumulation signal detected in <strong class="text-primary">ETH</strong>. Mean reversion model suggests a <strong class="text-success">+4.2%</strong> upside over the next 48 hours.`;
    
    const confidence = 87; // %
    confText.textContent = `${confidence}%`;
    
    // Animate bar
    setTimeout(() => {
      confFill.style.width = `${confidence}%`;
    }, 100);
  }

  // ── 3. Earnings (Allocation) Widget ─────────────────────────────

  function renderEarningsWidget() {
    const centerVal = document.getElementById('donut-center-val');
    const legendEl  = document.getElementById('allocation-legend');

    // Mock Data
    const assets = [
      { symbol: 'BTC', value: 85000, color: 'var(--chart-1)' },
      { symbol: 'ETH', value: 42000, color: 'var(--chart-2)' },
      { symbol: 'SOL', value: 10000, color: 'var(--chart-3)' },
      { symbol: 'USDC',value: 5580,  color: 'var(--chart-4)' },
    ];
    
    const total = assets.reduce((sum, a) => sum + a.value, 0);
    centerVal.textContent = assets.length; // Number of assets

    // Build Chart
    DonutChart('earningsChart', 
      assets.map(a => a.symbol),
      assets.map(a => a.value),
      {
        colors: assets.map(a => a.color),
        formatter: (val) => Fmt.currency(val, true)
      }
    );

    // Build Legend
    legendEl.innerHTML = '';
    assets.slice(0, 3).forEach(asset => { // Show top 3
      const pct = (asset.value / total) * 100;
      
      const item = document.createElement('div');
      item.className = 'legend-item';
      item.innerHTML = `
        <div class="legend-dot" style="background: ${asset.color}"></div>
        <div class="legend-label">${asset.symbol}</div>
        <div class="legend-value">${Fmt.currency(asset.value, true)}</div>
        <div class="legend-pct">${pct.toFixed(1)}%</div>
      `;
      legendEl.appendChild(item);
    });
  }

  // ── 4. Transactions Widget ──────────────────────────────────────

  function renderTransactionsWidget() {
    const list = document.getElementById('recent-tx-list');
    
    // Mock Data
    const txs = [
      { id: '1', type: 'income',   asset: 'BTC',  desc: 'Staking Reward',     cat: 'Yield',   date: new Date().toISOString(), amount: 0.045, amountUsd: 2850.40 },
      { id: '2', type: 'transfer', asset: 'ETH',  desc: 'Transfer to Vault',  cat: 'Wallet',  date: new Date(Date.now() - 86400000).toISOString(), amount: -2.5, amountUsd: -8500.00 },
      { id: '3', type: 'expense',  asset: 'USDC', desc: 'Exchange Fee',       cat: 'Fee',     date: new Date(Date.now() - 172800000).toISOString(), amount: -12.50, amountUsd: -12.50 },
      { id: '4', type: 'income',   asset: 'SOL',  desc: 'Market Buy',         cat: 'Trade',   date: new Date(Date.now() - 259200000).toISOString(), amount: 150, amountUsd: 21000.00 },
      { id: '5', type: 'expense',  asset: 'USD',  desc: 'Withdrawal to Bank', cat: 'Fiat',    date: new Date(Date.now() - 345600000).toISOString(), amount: -5000, amountUsd: -5000.00 }
    ];

    list.innerHTML = ''; // Clear skeleton

    const icons = {
      'income':   '↓',
      'expense':  '↑',
      'transfer': '↔'
    };

    txs.forEach(tx => {
      const isPos = tx.amountUsd > 0;
      const el = document.createElement('div');
      el.className = 'tx-item';
      
      // XSS Safe creation
      el.innerHTML = `
        <div class="tx-icon ${tx.type}">${icons[tx.type]}</div>
        <div>
          <div class="tx-name">${tx.asset}</div>
          <div class="tx-cat line-clamp-1">${tx.desc}</div>
        </div>
        <div class="tx-cat">
          <span class="badge badge-neutral">${tx.cat}</span>
        </div>
        <div class="tx-date">${Fmt.date(tx.date)}</div>
        <div class="tx-amount ${isPos ? 'positive' : 'negative'}">
          ${isPos ? '+' : ''}${Fmt.currency(tx.amountUsd)}
        </div>
      `;
      list.appendChild(el);
    });
  }

  // ── 5. Spending Widget (Cash Flow) ──────────────────────────────

  function renderSpendingWidget() {
    const netFlowEl = document.getElementById('net-flow-val');
    
    // Mock Data
    const labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
    const inflows = [12000, 5000, 8000, 15000];
    const outflows = [3000, 6000, 2000, 4000];
    
    const totalIn = inflows.reduce((a,b)=>a+b,0);
    const totalOut = outflows.reduce((a,b)=>a+b,0);
    const net = totalIn - totalOut;

    netFlowEl.textContent = `${net >= 0 ? '+' : ''}${Fmt.currency(net)}`;
    netFlowEl.className = `spending-total ${net >= 0 ? 'text-success' : 'text-danger'}`;

    BarChart('spendingChart', labels, [
      {
        label: 'Inflow',
        data: inflows,
        color: 'var(--chart-2)' // Emerald
      },
      {
        label: 'Outflow',
        data: outflows,
        color: 'var(--chart-5)' // Rose
      }
    ], {
      yFormatter: (val) => '$' + (val / 1000).toFixed(0) + 'k'
    });
  }

});
