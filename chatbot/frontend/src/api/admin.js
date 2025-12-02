import api from './axios';

// Chat Mode Management
export const getChatMode = () => 
  api.get('/admin/settings/chat-mode').then(r => r.data);

export const setChatMode = (mode) => 
  api.post('/admin/settings/chat-mode', { mode }).then(r => r.data);

// User Management
export const getUsers = () => 
  api.get('/admin/users').then(r => r.data.users || r.data);

export const getUserBySession = (sessionId) => 
  api.get(`/admin/users/${sessionId}`).then(r => r.data);

export const getUserHistoryBySession = (sessionId) => 
  api.get(`/admin/users/${sessionId}/history`).then(r => r.data);

export const getUserHistoryByEmail = (email) => 
  api.get(`/admin/users/email/${email}/history`).then(r => r.data);

// Admin Chat - Send message as admin to user
export const sendAdminMessage = (sessionId, message) => 
  api.post('/admin/reply', { 
    session_id: sessionId, 
    message,
    role: 'assistant'
  }).then(r => r.data);

export const replyToUser = (sessionId, message) => 
  api.post('/admin/reply', { 
    session_id: sessionId, 
    message,
    role: 'assistant'
  }).then(r => r.data);

// Get active chat sessions (users waiting for response in HUMAN_ONLINE mode)
export const getActiveSessions = () => 
  api.get('/admin/chat/active-sessions').then(r => r.data);

// Mark session as responded
export const markSessionResponded = (sessionId) => 
  api.post(`/admin/chat/sessions/${sessionId}/respond`).then(r => r.data);

// Statistics
export const getStatistics = () => 
  api.get('/admin/statistics').then(r => r.data);
