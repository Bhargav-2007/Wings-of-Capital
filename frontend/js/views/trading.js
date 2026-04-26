// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

/**
 * Wings of Capital — Trading View Logic
 * Handles the trading chart, order book rendering, and order submission.
 */

'use strict';

document.addEventListener('DOMContentLoaded', async () => {
  if (!AuthManager.requireAuth()) return;

  Sidebar.render('trading');

  let currentSide = 'buy'; // 'buy' or 'sell'

  try {
    stateManager.setLoading(true);
    await new Promise(r => setTimeout(r, 500)); // Simulate API

    renderChart();
    renderOrderBook();
    renderOpenOrders();
    setupOrderEntry();

  } catch (err) {
    stateManager.addNotification('Failed to load trading data', 'danger');
  } finally {
    stateManager.setLoading(false);
  }

  // ── 1. Chart ─────────────────────────────────────────────────────

  function renderChart() {
    const labels = ChartHelpers.generateDateLabels(48); // 48 hours
    const data   = ChartHelpers.generateRandomWalk(48, 65000, 500);

    LineChart('tradingChart', labels, [{
      label: 'BTC/USD',
      data: data,
      color: 'var(--brand-500)'
    }], {
      yFormatter: (val) => '$' + Fmt.number(val),
      beginAtZero: false,
      extra: {
        interaction: { mode: 'nearest', axis: 'x', intersect: false },
      }
    });

    document.getElementById('ticker-price').textContent = Fmt.currency(data[data.length-1]);
  }

  // ── 2. Order Book ────────────────────────────────────────────────

  function renderOrderBook() {
    const asksEl = document.getElementById('ob-asks');
    const bidsEl = document.getElementById('ob-bids');

    // Mock Data
    let basePrice = 65400.00;
    
    // Generate asks (going up from base price)
    let askHtml = '';
    let askTotal = 0;
    for(let i=0; i<8; i++) {
        const price = basePrice + (Math.random() * 10) + (i * 5);
        const amount = Math.random() * 2;
        askTotal += amount;
        const depth = Math.min((askTotal / 15) * 100, 100);
        
        askHtml += `
          <div class="ob-row ask" style="--depth-pct: ${depth}%">
            <span class="ob-price">${Fmt.number(price)}</span>
            <span class="ob-amount">${amount.toFixed(4)}</span>
            <span class="ob-total">${askTotal.toFixed(4)}</span>
          </div>
        `;
    }
    asksEl.innerHTML = askHtml;

    // Generate bids (going down from base price)
    let bidHtml = '';
    let bidTotal = 0;
    for(let i=0; i<8; i++) {
        const price = basePrice - (Math.random() * 10) - (i * 5);
        const amount = Math.random() * 2;
        bidTotal += amount;
        const depth = Math.min((bidTotal / 15) * 100, 100);
        
        bidHtml += `
          <div class="ob-row bid" style="--depth-pct: ${depth}%">
            <span class="ob-price">${Fmt.number(price)}</span>
            <span class="ob-amount">${amount.toFixed(4)}</span>
            <span class="ob-total">${bidTotal.toFixed(4)}</span>
          </div>
        `;
    }
    bidsEl.innerHTML = bidHtml;
  }

  // ── 3. Open Orders Table ─────────────────────────────────────────

  function renderOpenOrders() {
    const orders = [
      { id: 'O-1', pair: 'BTC-USD', side: 'buy',  type: 'limit', price: 62000.00, amount: 0.5, filled: 0, date: new Date().toISOString() },
      { id: 'O-2', pair: 'ETH-USD', side: 'sell', type: 'limit', price: 3800.00,  amount: 10.0, filled: 2.5, date: new Date(Date.now()-86400000).toISOString() },
    ];

    new WocTable({
      container: '#orders-table-container',
      data: orders,
      hidePaginationOnSingle: true,
      columns: [
        { key: 'date', label: 'Date', formatter: Fmt.dateTime },
        { key: 'pair', label: 'Pair', sortable: true },
        { 
          key: 'side', 
          label: 'Side', 
          render: (row) => {
            const el = document.createElement('span');
            el.className = row.side === 'buy' ? 'text-success font-bold uppercase' : 'text-danger font-bold uppercase';
            el.textContent = row.side;
            return el;
          }
        },
        { key: 'price', label: 'Price', align: 'right', formatter: Fmt.currency },
        { 
          key: 'amount', 
          label: 'Amount', 
          align: 'right',
          render: (row) => {
            const el = document.createElement('div');
            el.innerHTML = `<div>${row.amount}</div><div class="text-xs text-tertiary">${row.filled} filled</div>`;
            return el;
          }
        },
        {
          key: 'action',
          label: 'Action',
          align: 'center',
          render: (row) => {
            const btn = document.createElement('button');
            btn.className = 'btn btn-ghost btn-xs text-danger';
            btn.textContent = 'Cancel';
            btn.onclick = (e) => {
              e.stopPropagation();
              stateManager.addNotification(`Order ${row.id} cancelled.`, 'info');
            };
            return btn;
          }
        }
      ]
    });
  }

  // ── 4. Order Entry Logic ─────────────────────────────────────────

  function setupOrderEntry() {
    const tabBuy = document.getElementById('tab-buy');
    const tabSell = document.getElementById('tab-sell');
    const btnSubmit = document.getElementById('submit-order-btn');
    const inputPrice = document.getElementById('order-price');
    const inputAmt = document.getElementById('order-amount');
    const totalEl = document.getElementById('order-total');

    // Tab Switching
    function setSide(side) {
      currentSide = side;
      if(side === 'buy') {
        tabBuy.style.borderBottom = '2px solid var(--color-success)';
        tabBuy.className = 'flex-1 py-2 text-sm font-semi text-success';
        tabSell.style.borderBottom = 'none';
        tabSell.className = 'flex-1 py-2 text-sm font-medium text-tertiary hover:text-danger transition-base';
        
        btnSubmit.className = 'btn btn-success btn-block btn-lg mt-2';
        btnSubmit.textContent = 'Buy BTC';
      } else {
        tabSell.style.borderBottom = '2px solid var(--color-danger)';
        tabSell.className = 'flex-1 py-2 text-sm font-semi text-danger';
        tabBuy.style.borderBottom = 'none';
        tabBuy.className = 'flex-1 py-2 text-sm font-medium text-tertiary hover:text-success transition-base';
        
        btnSubmit.className = 'btn btn-danger btn-block btn-lg mt-2';
        btnSubmit.textContent = 'Sell BTC';
      }
    }

    tabBuy.addEventListener('click', () => setSide('buy'));
    tabSell.addEventListener('click', () => setSide('sell'));

    // Calc Total
    function calcTotal() {
      const p = parseFloat(inputPrice.value) || 0;
      const a = parseFloat(inputAmt.value) || 0;
      totalEl.textContent = Fmt.currency(p * a);
    }

    inputPrice.addEventListener('input', calcTotal);
    inputAmt.addEventListener('input', calcTotal);

    // Form Submission
    document.getElementById('order-form').addEventListener('submit', (e) => {
      e.preventDefault();
      const amt = parseFloat(inputAmt.value);
      if(!amt || amt <= 0) {
        stateManager.addNotification('Please enter a valid amount.', 'warning');
        return;
      }
      
      // Simulate submission
      stateManager.setLoading(true);
      btnSubmit.classList.add('btn-loading');
      
      setTimeout(() => {
        stateManager.setLoading(false);
        btnSubmit.classList.remove('btn-loading');
        stateManager.addNotification(`Successfully placed ${currentSide} order for ${amt} BTC.`, 'success');
        inputAmt.value = '';
        calcTotal();
      }, 800);
    });
  }

});
