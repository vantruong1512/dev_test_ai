import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChatStore } from '../../store/useChatStore';
import { getChatMode } from '../../api/admin';
import ChatWindow from '../../components/ChatWindow';
import { MessageCircle, X } from 'lucide-react';
import { useUserWebSocket } from '../../hooks/useWebSocket';

export default function ChatPage() {
  const navigate = useNavigate();
  const { user, sessionId, messages, loadMode, loadHistory, addMessage } = useChatStore();
  const [isOpen, setIsOpen] = useState(false);

  // WebSocket message handler
  const handleWebSocketMessage = useCallback((data) => {
    console.log('User WS received:', data);
    
    // ✅ Filter out pong/system messages
    if (data.type === 'pong' || data.type === 'connected') {
      console.log('  ↳ System message, ignore');
      return;
    }
    
    if (data.type === 'new_message') {
      // Admin gửi message mới
      const newMsg = {
        role: data.role,
        text: data.text,
        ts: data.timestamp,
        provider: data.provider
      };
      addMessage(newMsg);
      
      // Auto open chat window nếu đang đóng
      setIsOpen(true);
    }
  }, [addMessage]); // Removed isOpen dependency

  // Connect WebSocket with sessionId from store
  const { sendTyping } = useUserWebSocket(sessionId, handleWebSocketMessage);
  
  // ✅ Poll mode every 60s to detect admin mode changes
  useEffect(() => {
    if (!user.email) return;
    
    const pollMode = async () => {
      try {
        const result = await getChatMode();
        const currentMode = useChatStore.getState().mode;
        if (result.mode && result.mode !== currentMode) {
          console.log('🔄 Mode changed:', currentMode, '→', result.mode);
          useChatStore.setState({ mode: result.mode });
        }
      } catch (err) {
        console.error('Failed to poll mode:', err);
      }
    };
    
    // Poll every 60s
    const interval = setInterval(pollMode, 60000);
    return () => clearInterval(interval);
  }, [user.email]); // Only depend on user.email
  
  // Debug: Log sessionId changes
  useEffect(() => {
    console.log('📌 ChatPage sessionId changed:', sessionId);
  }, [sessionId]);

  useEffect(() => {
    // Redirect if no user email
    if (!user.email) {
      navigate('/');
      return;
    }

    // Load chat mode and history (only once on mount)
    const loadInitial = async () => {
      try {
        await loadMode();
        await loadHistory();
      } catch (err) {
        console.error('Failed to load initial data:', err);
      }
    };
    
    loadInitial();
  }, [user.email, navigate]);

  if (!user.email) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Floating Chat Widget */}
      <div className="fixed bottom-6 right-6 z-50">
        {/* Chat Window */}
        {isOpen && (
          <div className="mb-4 shadow-2xl rounded-2xl overflow-hidden bg-white" 
               style={{ width: '380px', height: '600px' }}>
            <ChatWindow onClose={() => setIsOpen(false)} />
          </div>
        )}

        {/* Toggle Button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="ml-auto block w-16 h-16 rounded-full shadow-2xl bg-gradient-to-br from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white transition-all duration-300 hover:scale-110 focus:outline-none focus:ring-4 focus:ring-blue-300"
        >
          {isOpen ? (
            <X className="w-8 h-8 mx-auto" />
          ) : (
            <MessageCircle className="w-8 h-8 mx-auto" />
          )}
        </button>
      </div>
    </div>
  );
}
