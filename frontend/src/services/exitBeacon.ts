import { API_BASE_URL } from './api';

// Simple session id stored for the lifetime of the tab
function getSessionId(): string {
  const key = 'agentteam.sessionId';
  let sid = sessionStorage.getItem(key);
  if (!sid) {
    sid = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
    sessionStorage.setItem(key, sid);
  }
  return sid;
}

function sendExitBeacon(reason: string) {
  try {
    const payload = {
      session_id: getSessionId(),
      page: window.location.href,
      reason,
      timestamp: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
    const url = `${API_BASE_URL}/api/client-exit`;
    if (navigator.sendBeacon) {
      navigator.sendBeacon(url, blob);
    } else {
      // Fallback for older browsers
      fetch(url, { method: 'POST', body: JSON.stringify(payload), headers: { 'Content-Type': 'application/json' }, keepalive: true as any }).catch(() => {});
    }
  } catch {}
}

export function installExitBeacon() {
  let sent = false;

  const once = (reason: string) => {
    if (!sent) {
      sent = true;
      sendExitBeacon(reason);
    }
  };
  const reset = () => {
    // When the page becomes visible again or is shown from bfcache, allow sending again
    sent = false;
  };

  // pagehide is the most reliable for Safari/iOS
  window.addEventListener('pagehide', () => once('pagehide'));

  // visibilitychange catches cases where the tab is closed or app backgrounded
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      once('visibilitychange');
    } else if (document.visibilityState === 'visible') {
      reset();
    }
  });

  // pageshow fires when coming back (including bfcache restore)
  window.addEventListener('pageshow', () => reset());

  // also reset on focus just in case
  window.addEventListener('focus', () => reset());

  // beforeunload as a final fallback
  window.addEventListener('beforeunload', () => once('beforeunload'));
}
