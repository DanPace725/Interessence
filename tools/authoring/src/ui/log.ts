const logEl = document.getElementById('log');

export function log(message: string) {
  if (!logEl) return;
  const ts = new Date().toISOString();
  const line = document.createElement('div');
  line.textContent = `[${ts}] ${message}`;
  logEl.appendChild(line);
  logEl.scrollTop = logEl.scrollHeight;
}

export function logError(message: string) {
  log(`ERROR: ${message}`);
}
