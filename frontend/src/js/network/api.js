// API integration for Wings of Capital
window.WOC_API = {
  getDashboard: async function() {
    const res = await window.WOC_HTTP('/api/dashboard', { method: 'GET' });
    return res.json();
  },
  getUser: async function() {
    const res = await window.WOC_HTTP('/api/v1/auth/me', { method: 'GET' });
    return res.json();
  },
  getPortfolio: async function() {
    const res = await window.WOC_HTTP('/api/v1/crypto/portfolio', { method: 'GET' });
    return res.json();
  },
  getTransactions: async function() {
    const res = await window.WOC_HTTP('/api/v1/ledger/transactions', { method: 'GET' });
    return res.json();
  },
  // Add more endpoints as needed
};
