// Generate or retrieve session ID from localStorage
export function getOrCreateSessionId() {
  let sessionId = localStorage.getItem('chatbot_session_id');
  if (!sessionId) {
    sessionId = generateUUID();
    localStorage.setItem('chatbot_session_id', sessionId);
  }
  return sessionId;
}

// Update session ID (used when server returns canonical session)
export function updateSessionId(newSessionId) {
  if (newSessionId) {
    localStorage.setItem('chatbot_session_id', newSessionId);
    console.log('💾 Session ID updated in localStorage:', newSessionId);
  }
}

// Generate UUID v4
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// Clear session
export function clearSession() {
  localStorage.removeItem('chatbot_session_id');
}
