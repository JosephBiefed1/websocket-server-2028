// ...existing code...
const out = document.getElementById('messages');
const input = document.getElementById('msg');
const btn = document.getElementById('send');

const wsUrl = `ws://${location.hostname}:2028/`;
let ws = null;

function append(text) {
  const el = document.createElement('div');
  el.textContent = text;
  out.appendChild(el);
  out.scrollTop = out.scrollHeight;
}

function connect() {
  ws = new WebSocket(wsUrl);

  ws.addEventListener('open', () => append('WebSocket connected to ' + wsUrl));
  ws.addEventListener('close', () => append('WebSocket disconnected'));
  ws.addEventListener('error', () => append('WebSocket error'));
  ws.addEventListener('message', (ev) => append('Received: ' + ev.data));
}

function send() {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    append('Not connected');
    return;
  }
  const v = input.value.trim();
  if (!v) return;
  ws.send(v);
  append('Sent: ' + v);
  input.value = '';
}

btn.addEventListener('click', send);
input.addEventListener('keydown', (e) => { if (e.key === 'Enter') send(); });

window.addEventListener('DOMContentLoaded', () => {
  connect();
});
// ...existing code...