// Authentication UI logic
window.WOC_Login = {
  login: async function(username, password) {
    const res = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (!res.ok) throw new Error('Login failed');
    const data = await res.json();
    if (data.token) localStorage.setItem('token', data.token);
    return data;
  }
};
