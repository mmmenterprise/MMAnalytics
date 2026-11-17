const API_BASE = 'https://mmanalyticsnow.com';
const token = localStorage.getItem('mma_token');

if (!token) {
  window.location.href = 'index.html';
}

document.getElementById('user-email').textContent = localStorage.getItem('mma_email') || '';

document.getElementById('logout-btn').addEventListener('click', () => {
  localStorage.removeItem('mma_token');
  localStorage.removeItem('mma_email');
  window.location.href = 'index.html';
});

async function loadDashboard() {
  try {
    const res = await fetch(`${API_BASE}/dashboard/summary`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Failed to load summary');
    const data = await res.json();

    document.getElementById('total-sales').textContent = data.total_sales ?? '—';
    document.getElementById('units-sold').textContent = data.units_sold ?? '—';
    document.getElementById('stockout-risks').textContent = data.stockout_risks ?? '—';
    document.getElementById('excess-inventory').textContent = data.excess_inventory ?? '—';
  } catch (err) {
    console.error(err);
  }
}

async function loadRecommendations() {
  const tbody = document.querySelector('#recommendations-table tbody');
  try {
    const res = await fetch(`${API_BASE}/dashboard/recommendations`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Failed to load recommendations');
    const items = await res.json();

    if (!items.length) {
      tbody.innerHTML = '<tr><td colspan="5" class="empty">No recommendations at this time</td></tr>';
      return;
    }

    tbody.innerHTML = items.map(item => `
      <tr>
        <td>${item.description || item.sid}</td>
        <td>${item.store_name || item.storesid}</td>
        <td>${item.on_hand}</td>
        <td>${item.on_order ?? 0}</td>
        <td><button class="btn-secondary btn-sm">Details</button></td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty">Unable to load recommendations</td></tr>';
  }
}

loadDashboard();
loadRecommendations();
