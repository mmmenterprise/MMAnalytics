const API_BASE = 'https://api.mmanalyticsnow.com';
const token = localStorage.getItem('mma_token');

const panel = document.getElementById('chat-panel');
const toggle = document.getElementById('ask-ai-toggle');
const closeBtn = document.getElementById('close-chat');
const form = document.getElementById('chat-form');
const input = document.getElementById('chat-input');
const messages = document.getElementById('chat-messages');

toggle.addEventListener('click', () => {
  panel.classList.remove('hidden');
  input.focus();
});

closeBtn.addEventListener('click', () => {
  panel.classList.add('hidden');
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const question = input.value.trim();
  if (!question) return;

  addMessage(question, 'user');
  input.value = '';
  addMessage('Thinking…', 'ai', true);

  try {
    const res = await fetch(`${API_BASE}/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ question })
    });

    const thinking = messages.querySelector('.thinking');
    if (thinking) thinking.remove();

    if (!res.ok) throw new Error('Request failed');
    const data = await res.json();
    addMessage(data.answer || 'No response', 'ai');
  } catch (err) {
    const thinking = messages.querySelector('.thinking');
    if (thinking) thinking.remove();
    addMessage('Sorry, something went wrong. Please try again.', 'ai');
  }
});

function addMessage(text, role, isThinking = false) {
  const div = document.createElement('div');
  div.className = `message ${role}${isThinking ? ' thinking' : ''}`;
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}
