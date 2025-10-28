// ...existing code...
const out = document.getElementById('messages');
const input = document.getElementById('msg');
const btn = document.getElementById('send');

// image element to show game result
let resultImg = document.getElementById('result-img');
if (!resultImg) {
  resultImg = document.createElement('img');
  resultImg.id = 'result-img';
  resultImg.style.maxWidth = '300px';
  resultImg.style.display = 'block';
  resultImg.style.marginTop = '10px';
  document.body.insertBefore(resultImg, out.nextSibling);
}

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
  ws.addEventListener('message', (ev) => {
    const text = ev.data;
    append('Received: ' + text);
    // try to match: Game 1 Score is 68578, Game 2 Score is 0
    const m = /Game\s*1\s*Score\s*is\s*(\d+)\D+Game\s*2\s*Score\s*is\s*(\d+)/i.exec(text);
    if (m) {
      const g1 = parseInt(m[1], 10);
      const g2 = parseInt(m[2], 10);
      // if either score below threshold show image3 (assumption)
      const THRESH = 1000;
      if (g1 < THRESH || g2 < THRESH) {
        // image3
        resultImg.src = 'pictures/game3.png';
        //append(`Displaying image3 (score below ${THRESH}): g1=${g1}, g2=${g2}`);
      } else if (g1 > g2) {
        resultImg.src = 'pictures/game1.png';
        //append(`Displaying image1 (g1>g2): g1=${g1}, g2=${g2}`);
      } else if (g2 > g1) {
        resultImg.src = 'pictures/game2.png';
        //append(`Displaying image2 (g2>g1): g1=${g1}, g2=${g2}`);
      } 
    }
  });
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