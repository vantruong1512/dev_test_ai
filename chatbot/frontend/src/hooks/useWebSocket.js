import { useEffect, useRef, useCallback } from 'react';

/**
 * Hook để connect WebSocket cho admin
 * Admin nhận tất cả events từ hệ thống (global channel)
 */
export function useAdminWebSocket(onMessage) {
  const ws = useRef(null);
  const reconnectTimeout = useRef(null);
  const isIntentionalClose = useRef(false);
  const onMessageRef = useRef(onMessage); // 🔑 Store onMessage in ref, không dùng trong dependency

  // ⚠️ Update ref khi onMessage thay đổi, nhưng không reconnect
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      console.log('✅ WebSocket already connected');
      return; // Already connected
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:8000/ws/stream/admin`;

    console.log('🔌 Connecting to admin WebSocket:', wsUrl);
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('✅ Admin WebSocket connected');
      // Send ping every 30s to keep alive
      const pingInterval = setInterval(() => {
        if (ws.current?.readyState === WebSocket.OPEN) {
          ws.current.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30000);
      ws.current.pingInterval = pingInterval;
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📨 Admin received message:', data.type, data);
        
        // ✅ Filter pong/system messages
        if (data.type === 'pong' || data.type === 'connected') {
          console.log('  ↳ System message, ignore');
          return;
        }
        
        // 🔑 Gửi callback từ ref, không reconnect
        if (onMessageRef.current) {
          onMessageRef.current(data);
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.current.onerror = (error) => {
      console.error('❌ Admin WebSocket error:', error);
    };

    ws.current.onclose = (event) => {
      console.log('🔌 Admin WebSocket closed:', event.code, event.reason);
      if (ws.current?.pingInterval) {
        clearInterval(ws.current.pingInterval);
      }
      
      // Auto reconnect after 3s if not intentional close
      if (!isIntentionalClose.current) {
        reconnectTimeout.current = setTimeout(() => {
          console.log('🔄 Reconnecting admin WebSocket...');
          connect();
        }, 3000);
      }
    };
  }, []); // ⚠️ Không phụ thuộc onMessage!

  const disconnect = useCallback(() => {
    isIntentionalClose.current = true;
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
    }
    if (ws.current?.pingInterval) {
      clearInterval(ws.current.pingInterval);
    }
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
  }, []);

  const sendMessage = useCallback((message) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      console.warn('⚠️ WebSocket not connected, cannot send message');
    }
  }, []);

  const sendTyping = useCallback((sessionId, isTyping) => {
    sendMessage({
      type: 'typing',
      session_id: sessionId,
      is_typing: isTyping
    });
  }, [sendMessage]);

  useEffect(() => {
    console.log('🔌 useAdminWebSocket: Mounting, connecting...');
    connect();
    return () => {
      console.log('🔌 useAdminWebSocket: Unmounting, disconnecting...');
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    sendMessage,
    sendTyping,
    isConnected: ws.current?.readyState === WebSocket.OPEN
  };
}

/**
 * Hook để connect WebSocket cho user
 * User chỉ nhận messages của session mình
 */
export function useUserWebSocket(sessionId, onMessage) {
  const ws = useRef(null);
  const reconnectTimeout = useRef(null);
  const isIntentionalClose = useRef(false);
  const onMessageRef = useRef(onMessage); // 🔑 Store onMessage in ref

  // ⚠️ Update ref khi onMessage thay đổi, nhưng không reconnect
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  const connect = useCallback(() => {
    if (!sessionId) {
      console.warn('⚠️ No sessionId provided, skipping WebSocket connection');
      return;
    }
    
    if (ws.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:8000/ws/chat/${sessionId}`;

    console.log('🔌 Connecting to user WebSocket:', wsUrl);
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('✅ User WebSocket connected');
      // Send ping every 30s to keep alive
      const pingInterval = setInterval(() => {
        if (ws.current?.readyState === WebSocket.OPEN) {
          ws.current.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30000);
      ws.current.pingInterval = pingInterval;
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📨 User received:', data);
        
        // ✅ Filter pong/system messages before callback
        if (data.type === 'pong' || data.type === 'connected') {
          console.log('  ↳ System message, ignore');
          return;
        }
        
        // 🔑 Gửi callback từ ref, không reconnect
        if (onMessageRef.current) {
          onMessageRef.current(data);
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.current.onerror = (error) => {
      console.error('❌ User WebSocket error:', error);
    };

    ws.current.onclose = (event) => {
      console.log('🔌 User WebSocket closed:', event.code, event.reason);
      if (ws.current?.pingInterval) {
        clearInterval(ws.current.pingInterval);
      }
      
      // Auto reconnect after 3s if not intentional close
      if (!isIntentionalClose.current) {
        reconnectTimeout.current = setTimeout(() => {
          console.log('🔄 Reconnecting user WebSocket...');
          connect();
        }, 3000);
      }
    };
  }, [sessionId]); // 🔑 Chỉ phụ thuộc sessionId, không phụ thuộc onMessage

  const disconnect = useCallback(() => {
    isIntentionalClose.current = true;
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
    }
    if (ws.current?.pingInterval) {
      clearInterval(ws.current.pingInterval);
    }
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
  }, []);

  const sendMessage = useCallback((message) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }, []);

  const sendTyping = useCallback((isTyping) => {
    sendMessage({
      type: 'typing',
      is_typing: isTyping
    });
  }, [sendMessage]);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    sendMessage,
    sendTyping,
    isConnected: ws.current?.readyState === WebSocket.OPEN
  };
}
