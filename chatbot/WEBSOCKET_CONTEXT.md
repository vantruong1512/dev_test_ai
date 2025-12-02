# WebSocket Real-time 2-Way Architecture

## Flow Diagram
```
User FE ──POST /chat/message──▶ FastAPI
   ▲             │
   │   (AI_ONLY) │ RAG→LLM→save DB→push WS
   │             ▼
WS /ws/chat/{sid} ◀─ AI reply / Admin reply
   │
   └─ (HUMAN_ONLY: save DB→broadcast to admins via WS)

Admin FE ◀──WS /ws/stream/admin (global: nhận mọi user event)
   │
   └──POST /admin/reply──▶ FastAPI ──save DB──push WS──▶ User
                                              └──▶ Admins (echo)
```

## Endpoints

**WebSocket:**
- `/ws/stream/admin` - Admin global stream (nhận all events)
- `/ws/chat/{session_id}` - User chat channel (nhận AI/admin replies)

**REST API:**
- `POST /chat/message` - User gửi tin nhắn
- `POST /admin/reply` - Admin reply to user
- `GET /admin/chat/active-sessions` - List waiting sessions

## Message Flow

**User → Admin (HUMAN_ONLINE mode):**
1. User: POST /chat/message {message, session_id, email}
2. Backend: Save DB (provider="human_pending")
3. Backend: ws_manager.broadcast_new_message(from_admin=False)
4. Admin: Nhận qua WS /ws/stream/admin → event "new_user_message"

**Admin → User:**
1. Admin: POST /admin/reply {session_id, message}
2. Backend: Save DB (provider="admin")
3. Backend: ws_manager.broadcast_new_message(from_admin=True)
4. User: Nhận qua WS /ws/chat/{sid} → event "new_message"
5. Admins: Nhận qua WS /ws/stream/admin → event "message_sent" (echo)

**AI → User (AI_ONLY mode):**
1. User: POST /chat/message
2. Backend: RAG→LLM→generate reply
3. Backend: Save DB (provider="openai"/"gemini")
4. Backend: Optional WS push (if needed)
5. User: Nhận reply trong HTTP response

## Events

**Admin receives (WS /ws/stream/admin):**
- `new_user_message` - User gửi message mới (HUMAN_ONLINE)
- `message_sent` - Admin khác đã reply (multi-tab sync)
- `user_connected` - User kết nối WebSocket
- `user_typing` - User đang typing

**User receives (WS /ws/chat/{sid}):**
- `new_message` - Admin/AI reply
- `typing` - Admin đang typing
- `connected` - Connection success

## Files

**Backend:**
- core/websocket_service.py - WebSocketManager
- api/websocket_api.py - WS endpoints
- api/chat_api.py - POST /chat/message + WS broadcast
- api/admin_api.py - POST /admin/reply + WS broadcast
- api/facebook_webhook.py - Facebook webhook + WS broadcast (NEW)
- core/channel_router.py - Multi-channel routing (NEW)
- core/facebook_send.py - Send API for Facebook (NEW)

**Frontend:**
- hooks/useWebSocket.js - useAdminWebSocket, useUserWebSocket
- pages/admin/LiveChat.jsx - Admin UI + WS
- pages/widget/ChatPage.jsx - User UI + WS
- pages/admin/Users.jsx - Channel filter + multi-channel display (UPDATED)
- api/admin.js - replyToUser()
- store/useChatStore.js - addMessage()

## Multi-Channel Support (UPDATED 2025-11-30)

**Channels supported:**
- ✅ Web (original)
- ✅ Facebook Messenger (NEW)
- ⏳ Zalo (planned)
- ⏳ Telegram (planned)

**Session ID format:**
- Web: UUID (e.g., `a1b2c3d4-...`)
- Facebook: `fb_{psid}` (e.g., `fb_4068042279978116`)
- Zalo: `zalo_{user_id}` (planned)
- Telegram: `tg_{chat_id}` (planned)

**WebSocket events include channel info:**
```json
{
  "type": "new_message",
  "session_id": "fb_4068042279978116",
  "channel": "facebook",
  "message": "...",
  "sender": "user|ai|admin"
}
```

**Admin dashboard:**
- Real-time updates for ALL channels via `/ws/stream/admin`
- Channel filter: all, web, facebook, zalo, telegram
- Channel icons: 🌐 📱 💬 ✈️
