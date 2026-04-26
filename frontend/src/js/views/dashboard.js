// Dashboard view logic (fetches real data from backend)
(async function() {
  try {
    const data = await window.WOC_API.getDashboard();
    // Use the same DOM update logic as in app.js, but with real data
    // Example: update balance
    document.querySelectorAll('.widget-value').forEach((el, idx) => {
      if (idx === 0 && data.metrics && data.metrics.balance) {
        el.textContent = '$' + data.metrics.balance.current.toLocaleString(undefined, {minimumFractionDigits:2});
      }
    });
    // ...update other widgets as needed
  } catch (e) {
    console.error('Failed to load dashboard data from backend:', e);
  }
})();
