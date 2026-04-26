// Wings of Capital - Main App Logic
(function() {
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);
  const data = window.WOC_DATA;
  const charts = window.WOC_Charts;

  // Format currency
  function fmt(amount) {
    return '$' + amount.toLocaleString(undefined, {minimumFractionDigits:2});
  }

  // Sidebar navigation links
  const navLinks = [
    { name: 'Dashboard', icon: '🏠', href: '#', active: true },
    { name: 'Neuro AI', icon: '🧠', href: '#', active: false },
    { name: 'Accounts', icon: '💳', href: '#', active: false },
    { name: 'Transactions', icon: '🔄', href: '#', active: false },
    { name: 'Reports', icon: '📊', href: '#', active: false },
    { name: 'Investments', icon: '📈', href: '#', active: false },
    { name: 'Loans', icon: '💰', href: '#', active: false },
    { name: 'Taxes', icon: '🧾', href: '#', active: false }
  ];

  // Build sidebar
  function renderSidebar() {
    return `
      <aside class="sidebar">
        <div>
          <div class="brand">
            <div class="brand-logo">W</div>
            <span class="brand-title">Wings of Capital</span>
          </div>
          <div class="user-card">
            <div class="user-row">
              <span class="user-date">MONDAY, MARCH 24</span>
              <button class="theme-toggle" aria-label="Toggle theme" onclick="toggleTheme()">${document.documentElement.classList.contains('dark') ? '🌙' : '☀️'}</button>
            </div>
            <div class="user-greeting">Welcome back, ${data.user.name}!</div>
          </div>
          <nav>
            ${navLinks.map(link => `
              <a href="${link.href}" target="_blank" class="${link.active ? 'active' : ''}">
                <span>${link.icon}</span> ${link.name}
              </a>
            `).join('')}
          </nav>
        </div>
        <div class="promo">
          <div class="promo-title">Activate NeuroBank Pro</div>
          <div class="promo-desc">Elevate finances with AI</div>
          <button class="promo-btn">Upgrade Now</button>
        </div>
      </aside>
    `;
  }

  // Build top action bar
  function renderTopbar() {
    return `
      <div class="topbar">
        <div class="topbar-left">
          <button class="dropdown"><span>📅</span> This Month</button>
        </div>
        <div class="actions">
          <button class="ghost-btn">Manage Widgets</button>
          <button class="primary-btn">+ Add new Widget</button>
        </div>
      </div>
    `;
  }

  // Build widget grid
  function renderWidgets() {
    return `
      <div class="widget-grid">
        <div class="widget ai">
          <div class="widget-title">AI Insights</div>
          <div class="widget-value" style="font-size:1.1rem;">${data.metrics.ai_insight}</div>
          <button class="widget-action" title="Open AI Insights"><span>↗️</span></button>
        </div>
        <div class="widget balance">
          <div class="widget-title">Balance Overview</div>
          <div class="widget-value">${fmt(data.metrics.balance.current)}</div>
          <div class="widget-indicator">↑ ${data.metrics.balance.delta_percentage}% From last month</div>
          <div class="widget-pills">
            <span class="pill">${data.metrics.balance.total_transactions} transactions</span>
            <span class="pill alt">${data.metrics.balance.categories} categories</span>
          </div>
          <canvas class="chart-canvas" id="balanceChart"></canvas>
        </div>
        <div class="widget earnings">
          <div class="widget-title">Earnings</div>
          <div class="widget-value">${fmt(data.metrics.earnings.current)}</div>
          <div class="widget-indicator">↑ ${data.metrics.earnings.delta_percentage}% From last month</div>
          <div class="chart-canvas"><canvas id="earningsChart"></canvas></div>
          <div class="legend">
            <span><span class="legend-dot current"></span> Current</span>
            <span><span class="legend-dot goal"></span> Month goal</span>
          </div>
        </div>
        <div class="widget transactions">
          <div class="widget-title">Recent Transactions</div>
          <table>
            <thead>
              <tr>
                <th>Merchant</th>
                <th>Card</th>
                <th>Date & Time</th>
                <th>Amount</th>
              </tr>
            </thead>
            <tbody id="txnRows"></tbody>
          </table>
        </div>
        <div class="widget spending">
          <div class="widget-title">Spending</div>
          <div class="widget-value">${fmt(data.metrics.spending.current)}</div>
          <div class="widget-indicator negative">↓ ${Math.abs(data.metrics.spending.delta_percentage)}% From last month</div>
          <canvas class="chart-canvas" id="spendingChart"></canvas>
        </div>
      </div>
    `;
  }

  // Render all
  function renderApp() {
    $('#app').innerHTML = renderSidebar() + '<main class="main">' + renderTopbar() + renderWidgets() + '</main>';
    // Transactions
    const txns = data.recent_transactions;
    const rows = txns.map(txn => `
      <tr>
        <td><span style="display:inline-block;width:28px;height:28px;border-radius:50%;background:#e0e7ff;color:#6366f1;font-weight:bold;text-align:center;line-height:28px;">${txn.merchant[0]}</span> ${txn.merchant}</td>
        <td>**** ${txn.card_last_four}</td>
        <td>${txn.timestamp}</td>
        <td class="amount ${txn.amount > 0 ? 'positive' : 'negative'}">${txn.amount > 0 ? '+' : ''}${fmt(Math.abs(txn.amount))}</td>
      </tr>
    `).join('');
    $('#txnRows').innerHTML = rows;
    // Charts
    setTimeout(() => {
      charts.renderBalanceChart($('#balanceChart').getContext('2d'), data.metrics.balance.timeseries);
      charts.renderEarningsChart($('#earningsChart').getContext('2d'), data.metrics.earnings.goal_percentage);
      charts.renderSpendingChart($('#spendingChart').getContext('2d'), data.metrics.spending.categories);
    }, 0);
  }

  // Initial render
  document.addEventListener('DOMContentLoaded', renderApp);
  // Theme toggle re-render
  window.toggleTheme = function() {
    if (document.documentElement.classList.contains('dark')) {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    } else {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    }
    renderApp();
  };
})();
