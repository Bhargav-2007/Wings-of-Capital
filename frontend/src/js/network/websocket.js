// WebSocket with heartbeat and auto-reconnect
window.WOC_WS = function(url, onMsg) {
  let ws;
  let timer;
  function connect() {
    ws = new WebSocket(url);
    ws.onopen = () => { timer = setInterval(() => ws.send('ping'), 30000); };
    ws.onmessage = (e) => { if (onMsg) onMsg(e.data); };
    ws.onclose = () => { clearInterval(timer); setTimeout(connect, 2000); };
    ws.onerror = () => ws.close();
  }
  connect();
  return { close: () => ws && ws.close() };
};
