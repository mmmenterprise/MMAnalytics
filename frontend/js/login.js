const API_BASE = 'https://api.mmanalyticsnow.com';

document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const errorEl = document.getElementById('error-message');
  errorEl.hidden = true;

  try {
    const res = await fetch(`${API_BASE}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.message || 'Login failed');
    }

    const data = await res.json();
    localStorage.setItem('mma_token', data.token);
    localStorage.setItem('mma_email', email);
    window.location.href = 'dashboard.html';
  } catch (err) {
    errorEl.textContent = err.message || 'Unable to sign in';
    errorEl.hidden = false;
  }
});
