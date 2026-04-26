// Initial loader: checks auth, loads theme
(function() {
  // Example: check for token, set theme
  if (localStorage.getItem('token')) {
    document.body.classList.add('authed');
  }
  // Theme is loaded by theme.js
})();
