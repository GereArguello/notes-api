let lastMessage = "";
let lastShownAt = 0;

const DEDUPE_WINDOW_MS = 1200;

export function showAlertOnce(message) {
  const now = Date.now();

  if (message === lastMessage && now - lastShownAt < DEDUPE_WINDOW_MS) {
    return;
  }

  lastMessage = message;
  lastShownAt = now;
  window.alert(message);
}
