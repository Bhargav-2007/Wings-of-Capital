// Global error handler
window.addEventListener('error', function(e) {
  // Log error, show fallback UI if needed
  console.error('Global error:', e.error || e.message);
});
