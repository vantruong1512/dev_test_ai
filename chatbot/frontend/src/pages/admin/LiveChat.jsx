import { useEffect, useState, useRef, useCallback } from 'react';
import { useAdminStore } from '../../store/useAdminStore';
import { sendAdminMessage, getActiveSessions, getUserHistoryBySession } from '../../api/admin';
import MessageBubble from '../../components/MessageBubble';
import { Send, RefreshCw, MessageSquare, User } from 'lucide-react';
import { useAdminWebSocket } from '../../hooks/useWebSocket';

export default function LiveChat() {
  const { mode } = useAdminStore();
  const [activeSessions, setActiveSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);
  const selectedSessionRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // ⚠️ QUAN TRỌNG: Sync selectedSessionRef để WebSocket handler có thể dùng
  useEffect(() => {
    selectedSessionRef.current = selectedSession;
  }, [selectedSession]);

  const loadActiveSessions = async () => {
    try {
      setLoading(true);
      const sessions = await getActiveSessions();
      setActiveSessions(sessions || []);
    } catch (err) {
      console.error('Failed to load sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async (sessionId) => {
    try {
      const response = await getUserHistoryBySession(sessionId);
      // Extract the history array from the response object
      setMessages(response?.history || []);
    } catch (err) {
      console.error('Failed to load messages:', err);
    }
  };

  // ========== WEBSOCKET HANDLER ==========
  // 🔑 QUAN TRỌNG: Handler này KHÔNG phụ thuộc vào selectedSession
  // Để tránh reconnect WebSocket mỗi khi selectedSession thay đổi
  const handleWebSocketMessage = useCallback((data) => {
    console.log('📨 [WS EVENT]', data.type, 'session_id:', data.session_id);
    
    // ✅ Filter pong/system messages
    if (data.type === 'pong' || data.type === 'connected') {
      console.log('  ↳ System message, ignore');
      return;
    }
    
    // B1: Kiểm tra type của event
    if (data.type === 'new_user_message' || data.type === 'new_message') {
      console.log('  ↳ User gửi message mới');
      // B1a: Kiểm tra nếu là message từ selected session → reload message luôn
      if (selectedSessionRef.current?.session_id === data.session_id) {
        console.log('  ↳ Là message từ session hiện tại → reload messages');
        loadMessages(data.session_id);
      } else {
        console.log('  ↳ Là message từ session khác → reload sessions');
        loadActiveSessions();
      }
    } else if (data.type === 'message_sent') {
      console.log('  ↳ Admin gửi reply');
      // B2a: Kiểm tra nếu là reply cho selected session → reload message
      if (selectedSessionRef.current?.session_id === data.session_id) {
        console.log('  ↳ Là reply cho session hiện tại → reload messages');
        loadMessages(data.session_id);
      } else {
        console.log('  ↳ Là reply cho session khác → reload sessions');
        loadActiveSessions();
      }
    } else if (data.type === 'user_connected') {
      console.log('  ↳ User kết nối → reload sessions');
      loadActiveSessions();
    } else if (data.type === 'typing') {
      console.log('  ↳ User đang typing');
    }
  }, []); // ⚠️ KHÔNG có dependency -> Handler không thay đổi

  // Connect WebSocket - sẽ chỉ connect 1 lần, không reconnect
  const { sendTyping } = useAdminWebSocket(handleWebSocketMessage);

  // ========== EFFECT: Load active sessions + polling ==========
  useEffect(() => {
    console.log('🚀 [LIVECHAT MOUNT] loadActiveSessions');
    loadActiveSessions();
    // Polling sessions mỗi 60s
    const interval = setInterval(() => {
      console.log('🔄 [POLLING] loadActiveSessions');
      loadActiveSessions();
    }, 60000);
    return () => {
      console.log('🚀 [LIVECHAT UNMOUNT] clear interval');
      clearInterval(interval);
    };
  }, []); // Empty dependency - chỉ chạy 1 lần khi mount

  // ========== EFFECT: Khi selectedSession thay đổi -> reload history ==========
  useEffect(() => {
    if (selectedSession) {
      console.log('📋 [EFFECT] selectedSession thay đổi →', selectedSession.session_id, '-> loadMessages');
      loadMessages(selectedSession.session_id);
    }
  }, [selectedSession]); // Phụ thuộc selectedSession

  const handleSend = async () => {
    if (!input.trim() || !selectedSession || sending) {
      console.warn('⚠️ Cannot send: empty input or already sending');
      return;
    }

    const messageText = input.trim();
    setInput(''); // Clear input ngay

    try {
      setSending(true);
      console.log('📤 Sending admin message:', messageText);
      
      // Thêm message vào UI ngay (optimistic update)
      const optimisticMsg = {
        role: 'assistant',
        text: messageText,
        ts: new Date().toISOString(),
        provider: 'admin'
      };
      setMessages(prev => [...prev, optimisticMsg]);
      
      // Gửi API - chỉ 1 request duy nhất
      await sendAdminMessage(selectedSession.session_id, messageText);
      console.log('✅ Message sent successfully');
    } catch (err) {
      console.error('❌ Failed to send message:', err);
      alert('Không thể gửi tin nhắn: ' + err.message);
      // Reload để sync lại
      await loadMessages(selectedSession.session_id);
    } finally {
      setSending(false);
    }
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
    // Send typing indicator
    if (selectedSession && sendTyping) {
      sendTyping(selectedSession.session_id, e.target.value.length > 0);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Live Chat</h1>
            <p className="text-gray-600 mt-2">Chat trực tiếp với người dùng</p>
          </div>
          {mode !== 'HUMAN_ONLINE' && (
            <div className="bg-yellow-100 border border-yellow-300 text-yellow-800 px-4 py-2 rounded-lg">
              ⚠️ Chat mode hiện tại: <strong>{mode}</strong>. Chuyển sang HUMAN_ONLINE để chat trực tiếp.
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sessions List */}
          <div className="lg:col-span-1 bg-white rounded-lg shadow">
            <div className="p-4 border-b border-gray-200 flex items-center justify-between">
              <h2 className="font-semibold text-gray-900 flex items-center gap-2">
                <MessageSquare className="w-5 h-5" />
                Active Sessions ({activeSessions.length})
              </h2>
              <button
                onClick={loadActiveSessions}
                disabled={loading}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>

            <div className="overflow-y-auto" style={{ maxHeight: '600px' }}>
              {activeSessions.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <MessageSquare className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                  <p className="text-sm">Không có session nào đang chờ</p>
                </div>
              ) : (
                activeSessions.map((session) => (
                  <button
                    key={session.session_id}
                    onClick={() => setSelectedSession(session)}
                    className={`w-full p-4 border-b border-gray-100 hover:bg-blue-50 transition-colors text-left ${
                      selectedSession?.session_id === session.session_id ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                        <User className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">{session.email || 'Unknown User'}</p>
                        <p className="text-xs text-gray-500 truncate">{session.name || 'N/A'}</p>
                        <p className="text-xs text-gray-400 mt-1">
                          {session.message_count || 0} messages
                        </p>
                      </div>
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>

          {/* Chat Window */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow flex flex-col" style={{ height: '680px' }}>
            {selectedSession ? (
              <>
                {/* Chat Header */}
                <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-blue-600 to-purple-600">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center">
                      <User className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-white">{selectedSession.email}</h3>
                      <p className="text-sm text-blue-100">{selectedSession.name || 'N/A'} • {selectedSession.phone || 'N/A'}</p>
                    </div>
                  </div>
                </div>

                {/* Messages Area */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-blue-50 to-purple-50">
                  {messages.length === 0 ? (
                    <div className="text-center py-12 text-gray-500">
                      <MessageSquare className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                      <p>Chưa có tin nhắn nào</p>
                    </div>
                  ) : (
                    messages.map((msg, idx) => (
                      <MessageBubble key={idx} message={msg} />
                    ))
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-4 border-t border-gray-200">
                  <div className="flex gap-2">
                    <textarea
                      value={input}
                      onChange={handleInputChange}
                      onKeyPress={handleKeyPress}
                      placeholder="Nhập tin nhắn để trả lời user..."
                      disabled={sending}
                      rows={2}
                      className="flex-1 resize-none border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 disabled:bg-gray-100"
                    />
                    <button
                      onClick={handleSend}
                      disabled={sending || !input.trim()}
                      className="px-6 py-2 bg-gradient-to-br from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 disabled:from-gray-300 disabled:to-gray-400 transition-all shadow-md hover:shadow-lg flex items-center gap-2"
                    >
                      <Send className="w-5 h-5" />
                      {sending ? 'Đang gửi...' : 'Gửi'}
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    💡 Tip: Nhấn Enter để gửi, Shift + Enter để xuống dòng
                  </p>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-400">
                <div className="text-center">
                  <MessageSquare className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                  <p className="text-lg">Chọn một session để bắt đầu chat</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}