// Simple CSRF token handling (stub)
window.WOC_CSRF = {
  getToken: function() {
    return localStorage.getItem('csrf_token') || '';
  },
  setToken: function(token) {
    localStorage.setItem('csrf_token', token);
  }
};
