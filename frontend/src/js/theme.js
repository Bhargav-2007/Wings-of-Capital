// Theme toggle logic for Wings of Capital
(function() {
  function setTheme(dark) {
    if (dark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }
  // On load, set theme from preference
  const userPref = window.WOC_DATA?.user?.theme_preference;
  const stored = localStorage.getItem('theme');
  if (stored) setTheme(stored === 'dark');
  else if (userPref) setTheme(userPref === 'dark');

  window.toggleTheme = function() {
    setTheme(!document.documentElement.classList.contains('dark'));
  };
})();
