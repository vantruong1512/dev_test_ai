import { create } from 'zustand';
import { sendMessage, getChatHistory } from '../api/chat';
import { getChatMode } from '../api/admin';
import { getOrCreateSessionId } from '../utils/session';

export const useChatStore = create((set, get) => ({
  sessionId: getOrCreateSessionId(),
  mode: 'AI_ONLY',
  user: { email: '', name: '', phone: '' },
  messages: [], // {role:'user'|'assistant'|'system', text, ts}
  loading: false,
  error: null,

  setSessionId: (newSessionId) => set({ sessionId: newSessionId }),

  setUser: (userData) => set((state) => ({ 
    user: { ...state.user, ...userData } 
  })),

  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),

  loadMode: async () => {
    try {
      const { mode } = await getChatMode();
      set({ mode });
    } catch (error) {
      console.error('Failed to load chat mode:', error);
    }
  },

  loadHistory: async () => {
    try {
      const sessionId = get().sessionId;
      const data = await getChatHistory(sessionId);
      set({ messages: data.history || [] });
    } catch (error) {
      console.error('Failed to load history:', error);
      set({ error: error.message });
    }
  },

  send: async (text) => {
    const { mode, sessionId, user } = get();
    
    // ✅ Validate email required
    if (!user.email || user.email.trim() === '') {
      set({ error: 'Vui lòng nhập email trước khi chat' });
      return;
    }
    
    console.log('📤 Sending message:', { text, mode, sessionId, user });
    
    // Add user message
    set((state) => ({ 
      messages: [...state.messages, { role: 'user', text, ts: Date.now() }],
      loading: true,
      error: null
    }));

    try {
      if (mode === 'HUMAN_ONLINE') {
        console.log('🔄 HUMAN_ONLINE mode - sending to API...');
        // Gửi message để trigger WebSocket broadcast
        const res = await sendMessage({ 
          message: text, 
          session_id: sessionId, 
          ...user 
        });
        
        console.log('✅ HUMAN_ONLINE response:', res);
        
        // ✅ Update sessionId từ backend response
        if (res?.session_id && res.session_id !== sessionId) {
          console.log('🔄 Session ID updated:', sessionId, '→', res.session_id);
          const { updateSessionId } = require('../utils/session');
          updateSessionId(res.session_id);
          set({ sessionId: res.session_id });
        }
        
        set((state) => ({ 
          messages: [...state.messages, { 
            role: 'system', 
            text: res?.reply || 'Tin nhắn của bạn đã được ghi nhận. Nhân viên sẽ phản hồi sớm nhất có thể.', 
            ts: Date.now() 
          }],
          loading: false
        }));
        return { status: 'WAITING_FOR_HUMAN', ...res };
      }

      console.log('🤖 AI_ONLY mode - sending to API...');
      const res = await sendMessage({ 
        message: text, 
        session_id: sessionId, 
        ...user 
      });
      
      console.log('✅ AI_ONLY response:', res);
      
      // ✅ Update sessionId từ backend response
      if (res?.session_id && res.session_id !== sessionId) {
        console.log('🔄 Session ID updated:', sessionId, '→', res.session_id);
        const { updateSessionId } = require('../utils/session');
        updateSessionId(res.session_id);
        set({ sessionId: res.session_id });
      }
      
      const reply = res?.reply || 'Xin lỗi, hiện không có phản hồi.';
      set((state) => ({ 
        messages: [...state.messages, { 
          role: 'assistant', 
          text: reply, 
          ts: Date.now() 
        }],
        loading: false
      }));
      
      return res;
    } catch (error) {
      set({ 
        loading: false, 
        error: error.message 
      });
      throw error;
    }
  },

  clearError: () => set({ error: null }),
}));
