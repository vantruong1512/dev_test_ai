import api from './axios';

export const sendMessage = (payload) => 
  api.post('/chat/message', payload).then(r => r.data);

export const getChatHistory = (sessionId) => 
  api.get(`/chat/history/${sessionId}`).then(r => r.data);

export const getChatSessions = () => 
  api.get('/chat/sessions').then(r => r.data);

export const health = () => 
  api.get('/chat/health').then(r => r.data);
