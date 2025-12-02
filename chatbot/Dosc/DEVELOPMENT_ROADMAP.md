# 📋 DEVELOPMENT ROADMAP - MULTI-CHANNEL RAG SYSTEM

**Dự án:** Chatbot AI RAG đa kênh (Web + Facebook + Zalo + Telegram)  
**Ngày:** 2025-11-30  
**Trạng thái:** Giai đoạn 1 (✅ 100%) + Giai đoạn 2 - Facebook (✅ HOÀN THÀNH - 100%)

---

## 📊 PHÂN TÍCH TÌNH TRẠNG HIỆN TẠI

### ✅ ĐÃ HOÀN THÀNH (Giai đoạn 1 - WEB + ADMIN)

#### Frontend (React + Tailwind)
- ✅ LeadGate: Form nhập email/phone/name
- ✅ ChatPage: Chat widget với WebSocket real-time
- ✅ Session handling: localStorage + UUID
- ✅ Admin Dashboard: 5 trang hoàn chỉnh
  - Users List (/admin/users)
  - User Detail (/admin/users/:sessionId)
  - Documents Management (/admin/documents)
  - Statistics (/admin/statistics)
  - Settings (mode toggle)
- ✅ Components: ChatWindow, MessageBubble, ChatInput, FileUploader, Table, DataCard
- ✅ Zustand store: useChatStore, useAdminStore
- ✅ Axios API client: chat.js, admin.js, documents.js

#### Backend (FastAPI + SQLite)
- ✅ API endpoints:
  - POST /chat/message - gửi tin nhắn
  - GET /chat/history/{session_id} - lịch sử
  - GET /admin/users - danh sách users
  - GET /admin/users/{session_id} - chi tiết user
  - GET /admin/users/{session_id}/history - history
  - POST /admin/documents/upload - upload file
  - GET /admin/documents - danh sách file
  - DELETE /admin/documents/{filename} - xóa file
  - GET /admin/statistics - thống kê
  - POST /admin/settings/chat-mode - toggle mode
- ✅ WebSocket: /ws/chat/{session_id} (user), /ws/stream/admin (admin)
- ✅ Database: users, chat_messages, chat_history, documents, settings
- ✅ RAG pipeline: Chroma vector DB + LLM
- ✅ Session handling: UUID, email/phone validation

---

## 🔄 LỘ TRÌNH PHÁT TRIỂN ĐA KÊNH

### **GIAI ĐOẠN 1 - WEB + ADMIN (✅ HOÀN THÀNH - 100%)**

**Trạng thái:** ✅ ALL DONE

Công việc hoàn tất:
1. ✅ Frontend: LeadGate, ChatPage, Admin Dashboard (5 pages)
2. ✅ Backend: All API endpoints, WebSocket, RAG pipeline
3. ✅ Database: Multi-table schema, chat history
4. ✅ Session handling: UUID-based, no data mixing
5. ✅ Admin features: Users, Documents, Statistics

**Timeline:** Completed

---

### **GIAI ĐOẠN 2 - FACEBOOK INTEGRATION (✅ HOÀN THÀNH - 100%)**

**Trạng thái:** ✅ ALL DONE - Full end-to-end Facebook Messenger integration working

---

#### ✅ HOÀN THÀNH

**Backend Services:**
- ✅ `core/channel_router.py` (150 lines) - Normalize messages from all channels
- ✅ `core/facebook_send.py` (240 lines) - Send via Facebook Send API
- ✅ `core/send_router.py` (200 lines) - Route to correct channel output
- ✅ `api/facebook_webhook.py` (280 lines) - Webhook receive + verify signature
- ✅ `core/db_service.py` (updated) - Multi-channel schema (channel, metadata columns)
- ✅ `main.py` (updated) - Register facebook_router

**Frontend:**
- ✅ `frontend/src/pages/admin/Users.jsx` (updated) - Channel column + icons + filter

**Total code:** ~1,270 lines new

---

#### 2.1 ENVIRONMENT SETUP (YÊU CẦU NGAY BÂY GIỜ)

Tạo file `.env` trong folder backend:
```env
# Facebook Configuration
FACEBOOK_PAGE_ACCESS_TOKEN=your_page_access_token_here
FACEBOOK_VERIFY_TOKEN=my_chatbot_verify_token_12345
FACEBOOK_APP_SECRET=your_app_secret_here

# Other
API_BASE_URL=http://localhost:8000
LLM_MODEL=mistral
CHROMA_PATH=./data/vector_db
```

**Hướng dẫn lấy tokens:**
1. Truy cập: https://developers.facebook.com/
2. Tạo App (loại Business)
3. Thêm product "Messenger"
4. Tạo/chọn Facebook Page
5. Lấy: **App ID**, **App Secret**, **Page Access Token**
6. Tạo **Verify Token** (chuỗi bất kỳ, 20-30 ký tự)

---

#### 2.2 SETUP NGROK (LOCAL TESTING)

```bash
# 1. Download: https://ngrok.com/download
# 2. Extract to C:\ngrok

cd C:\ngrok
ngrok http 8000

# Output sẽ hiển thị:
# Forwarding: https://abc123def.ngrok.io -> http://localhost:8000
# Copy URL này: https://abc123def.ngrok.io
```

---

#### 2.3 CHẠY BACKEND

```bash
cd d:\AI_for_code_Copilot\dev_test_ai\chatbot

# Cài dependencies
pip install httpx

# Chạy server
python main.py
```

**Expected output:**
```
✅ Database khởi tạo
📚 Docs available at: http://localhost:8000/docs
🚀 Starting Chatbot AI RAG server...
```

---

#### 2.4 CẤU HÌNH FACEBOOK WEBHOOK

**Trên Facebook App Dashboard:**

1. Vào **Messenger → Settings**
2. Tìm mục **Webhook**
3. Nhập:
   - **Callback URL:** `https://abc123def.ngrok.io/webhook/facebook`
   - **Verify Token:** `my_chatbot_verify_token_12345`
4. Nhấn "Verify and Save"
5. Subscribe to events: ✅ messages, ✅ message_echoes, ✅ messaging_postbacks

---

#### 2.5 TEST VERIFY TOKEN

```bash
# PowerShell
$url = "http://localhost:8000/webhook/facebook?hub_mode=subscribe&hub_verify_token=my_chatbot_verify_token_12345&hub_challenge=test123"
Invoke-WebRequest -Uri $url -Method GET

# Expected response: 123
```

---

#### 2.6 TEST SEND MESSAGE

**Từ Facebook Messenger:**
1. Mở Facebook Page vừa tạo
2. Nhấn "Send Message"
3. Gửi một tin nhắn test

**Kiểm tra logs backend:**
```
📨 FB message from 123456789: Hello
✅ FB message sent to 123456789: message_id_abc123
```

**Kiểm tra Database:**
```bash
sqlite3 ./data/chatbot.db

SELECT * FROM users WHERE channel='facebook';
SELECT * FROM chat_messages WHERE channel='facebook' ORDER BY created_at DESC LIMIT 5;
```

---

#### 2.7 WORKFLOW LUỒNG

```
📱 User gửi tin nhắn trên Facebook Messenger
   ↓
🔔 Facebook gọi POST /webhook/facebook
   ↓
✅ Backend verify signature (HMAC-SHA1) + verify token
   ↓
📥 Extract { psid, text, timestamp }
   ↓
🔑 Tạo session_id = f"fb_{psid}"
   ↓
📤 channel_router.process_message()
   ├─ Save message vào DB (channel='facebook')
   ├─ Gọi RAG pipeline (Chroma + LLM)
   └─ Generate reply text
   ↓
🔀 send_router.send_to_channel()
   ├─ Detect channel = 'facebook'
   ├─ Extract PSID từ session_id
   └─ Gọi facebook_send.send_text_message()
   ↓
📤 Facebook Send API gửi reply
   ↓
📡 Broadcast /ws/stream/admin
   └─ Admin dashboard thấy message real-time
   ↓
✅ User thấy reply trên Messenger
```

---

#### 2.8 DATABASE SCHEMA (CẬP NHẬT)

**users table:**
```sql
-- NEW columns
channel TEXT DEFAULT 'web'      -- web|facebook|zalo|telegram
metadata TEXT                    -- JSON {psid, zalo_user_id, telegram_chat_id}
```

**chat_messages table:**
```sql
-- NEW columns
channel TEXT DEFAULT 'web'      -- channel name
sender TEXT                      -- user|ai|admin
metadata TEXT                    -- channel-specific data
```

---

#### 2.9 FILES & STRUCTURE

**Created:**
```
core/
  ├─ channel_router.py     # Normalize from all channels
  ├─ facebook_send.py      # Send via FB Send API
  └─ send_router.py        # Route to output channels

api/
  └─ facebook_webhook.py   # Webhook receive + verify

frontend/src/pages/admin/
  └─ Users.jsx (updated)   # Channel column + filter
```

**Modified:**
```
core/db_service.py         # Schema + save_user_info()
main.py                    # Register facebook_router
```

---

#### 2.10 TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| ❌ "Invalid verify token" | Kiểm tra FACEBOOK_VERIFY_TOKEN trong .env khớp Facebook App |
| ❌ "Signature verification failed" | Kiểm tra FACEBOOK_APP_SECRET đúng |
| ❌ "HTTP 400: Missing required parameter" | Kiểm tra FACEBOOK_PAGE_ACCESS_TOKEN hợp lệ |
| ❌ ngrok bị ngắt | Restart ngrok, copy URL mới, update Webhook URL trên Facebook |
| ❌ "Connection refused" | Backend không chạy, restart `python main.py` |

---

#### 2.11 CHECKLIST LOCAL TESTING

- [x] .env file cấu hình đúng (3 tokens: access_token, verify_token, app_secret)
- [x] ngrok running (`ngrok http 8000`) - URL: https://eliz-subangulated-piercingly.ngrok-free.dev
- [x] Backend running (`python main.py`)
- [x] Facebook webhook URL cấu hình (`https://ngrok-url/webhook/facebook`)
- [x] Verify token test pass (endpoint trả về hub_challenge)
- [x] Send message test từ Messenger
- [x] Backend logs hiển thị "📨 FB message" + "✅ FB message sent"
- [x] Admin dashboard hiển thị message với channel='facebook'
- [x] Database có row mới trong chat_messages với channel='facebook'
- [x] RAG pipeline hoạt động với Facebook messages
- [x] HUMAN_ONLINE mode working (AI skips when enabled)
- [x] Admin can reply to Facebook users via Send API
- [x] Multi-channel support in admin panel (Users page shows channel icons)
- [x] All admin endpoints support both web and Facebook sessions

**Timeline:** 1-2 tuần  
**Độ phức tạp:** Trung bình

---

### **GIAI ĐOẠN 3 - ZALO INTEGRATION**

#### 3.1 Chuẩn bị
- [ ] Đăng ký Zalo OA (Official Account)
- [ ] Lấy Zalo Server Key
- [ ] Cấu hình Webhook URL
- [ ] Test webhook connection

#### 3.2 Backend module
**Tạo file:** `backend/api/zalo_webhook.py`
```python
# POST /webhook/zalo
# Verify webhook (signature check)
# Receive message: user_id + text
# session_id = f"zalo_{user_id}"
# Gọi channel_router
```

**Tạo file:** `backend/services/zalo_send.py`
```python
# Gửi message qua Zalo OA API
```

#### 3.3 Database
**Thêm column:**
- zalo_user_id: (for Zalo)

#### 3.4 Luồng xử lý Zalo
- Giống Facebook nhưng dùng Zalo API
- session_id = f"zalo_{user_id}"
- Webhook signature verify khác

**Timeline:** 1-2 tuần  
**Độ phức tạp:** Trung bình (tương tự Facebook)

---

### **GIAI ĐOẠN 4 - TELEGRAM INTEGRATION**

#### 4.1 Chuẩn bị
- [ ] Tạo Telegram Bot (BotFather)
- [ ] Lấy Bot Token
- [ ] Set Webhook URL

#### 4.2 Backend module
**Tạo file:** `backend/api/telegram_webhook.py`
```python
# POST /webhook/telegram
# Receive message: chat_id + text
# session_id = f"tg_{chat_id}"
# Gọi channel_router
```

**Tạo file:** `backend/services/telegram_send.py`
```python
# Gửi message qua Telegram Bot API
# https://api.telegram.org/bot{TOKEN}/sendMessage
```

#### 4.3 Database
**Thêm column:**
- telegram_chat_id: (for Telegram)

#### 4.4 Luồng xử lý Telegram
- Giống FB/Zalo
- session_id = f"tg_{chat_id}"
- Webhook verify khác

**Timeline:** 1 tuần  
**Độ phức tạp:** Dễ (API đơn giản nhất)

---

### **GIAI ĐOẠN 5 - FRONTEND ADMIN UPDATE**

#### 5.1 Cập nhật Users page
**File:** `frontend/src/pages/admin/Users.jsx`
- Thêm column "Channel" để hiển thị kênh (web/facebook/zalo/telegram)
- Hiển thị icon kênh: 🌐 web, 📱 facebook, 💬 zalo, ✈️ telegram
- Filter theo kênh

#### 5.2 Cập nhật User Detail page
**File:** `frontend/src/pages/admin/UserDetail.jsx`
- Hiển thị thông tin kênh
- Nếu Facebook: hiển thị PSID
- Nếu Zalo: hiển thị Zalo User ID
- Nếu Telegram: hiển thị Chat ID

#### 5.3 API update
**File:** `frontend/src/api/admin.js`
- Không cần thay đổi gì (vẫn dùng session_id)

**Timeline:** 3-5 ngày  
**Độ phức tạp:** Dễ

---

### **GIAI ĐOẠN 6 - OPTIMIZATION & ENHANCEMENT**

#### 6.1 Performance
- [ ] Streaming response cho Web
- [ ] Message queue (Redis)
- [ ] Cache user session
- [ ] Rate limiting per channel

#### 6.2 Features
- [ ] Admin reply to any channel
- [ ] Broadcast message to all channels
- [ ] Channel analytics dashboard
- [ ] A/B testing per channel

#### 6.3 Reliability
- [ ] Retry logic webhook fail
- [ ] Message deduplication
- [ ] Webhook signature verification
- [ ] Circuit breaker

**Timeline:** 2-4 tuần  
**Độ phức tạp:** Cao

---

## 🏗️ KIẾN TRÚC HỆ THỐNG CUỐI CÙNG

```
┌─────────────────────────────────────────────────────────────────┐
│                    USERS (MULTI-CHANNEL)                        │
│  Web User    Facebook User    Zalo User    Telegram User       │
└──────────────┬──────────────────┬──────────────┬────────────────┘
               │                  │              │
        ┌──────▼──────────────────▼──────────────▼──────┐
        │          FASTAPI BACKEND (1 domain)          │
        └──────┬───────────────────────────────────────┘
               │
        ┌──────▼──────────────────────────────────────┐
        │     API ROUTERS (webhook + REST)            │
        │ ├─ web_chat.py                              │
        │ ├─ facebook_webhook.py                      │
        │ ├─ zalo_webhook.py                          │
        │ ├─ telegram_webhook.py                      │
        │ └─ admin.py                                 │
        └──────┬───────────────────────────────────────┘
               │
        ┌──────▼──────────────────────────────────────┐
        │      CHANNEL ROUTER (normalize)             │
        │ ├─ Detect channel (web/fb/zalo/tg)         │
        │ ├─ Extract session_id + metadata           │
        │ ├─ Normalize message format                 │
        │ └─ Route to RAG pipeline                    │
        └──────┬───────────────────────────────────────┘
               │
        ┌──────▼──────────────────────────────────────┐
        │      RAG PIPELINE (shared)                  │
        │ ├─ Save message to DB                       │
        │ ├─ Embedding + Vector search                │
        │ ├─ LLM generate reply                       │
        │ └─ Save reply to DB                         │
        └──────┬───────────────────────────────────────┘
               │
        ┌──────▼──────────────────────────────────────┐
        │      SEND ROUTER (channel-specific)         │
        │ ├─ Web: WebSocket /ws/chat/{session_id}    │
        │ ├─ Facebook: FB Send API                    │
        │ ├─ Zalo: Zalo OA API                        │
        │ └─ Telegram: Telegram Bot API               │
        └──────┬───────────────────────────────────────┘
               │
        ┌──────▼──────────────────────────────────────┐
        │    ADMIN BROADCAST (WebSocket)              │
        │    /ws/stream/admin (all channels)          │
        └──────────────────────────────────────────────┘
               │
        ┌──────▼──────────────────────────────────────┐
        │       SHARED DATABASE (SQLite)              │
        │ ├─ users (channel, session_id, metadata)   │
        │ ├─ messages (session_id, text, channel)    │
        │ ├─ documents (RAG)                          │
        │ └─ settings (mode, etc)                     │
        └──────────────────────────────────────────────┘
```

---

## 📝 DATABASE SCHEMA (CẬP NHẬT)

### users table
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  session_id TEXT UNIQUE NOT NULL,
  channel TEXT DEFAULT 'web',  -- NEW: web|facebook|zalo|telegram
  email TEXT,
  phone TEXT,
  name TEXT,
  metadata TEXT,  -- NEW: JSON {psid, zalo_user_id, telegram_chat_id}
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### messages table
```sql
CREATE TABLE messages (
  id INTEGER PRIMARY KEY,
  session_id TEXT NOT NULL,
  channel TEXT,  -- NEW: detect from session_id prefix
  sender TEXT,  -- user|ai|admin
  text TEXT,
  metadata TEXT,  -- NEW: channel-specific metadata
  created_at TIMESTAMP
);
```

---

## 🎯 CHECKLIST IMPLEMENTATION

### GIAI ĐOẠN 2 - FACEBOOK

**Backend:**
- [x] Tạo `api/facebook_webhook.py` (340 lines)
- [x] Implement webhook verify logic (HMAC-SHA1 signature)
- [x] Implement receive message handler (with HUMAN_ONLINE mode support)
- [x] Create `core/facebook_send.py` (304 lines)
- [x] Create `core/channel_router.py` (138 lines)
- [x] Update database schema (channel + metadata columns)
- [x] Test Facebook webhook locally (ngrok)
- [x] Integrate RAG pipeline for AI responses
- [x] Update all admin endpoints for multi-channel support

**Frontend:**
- [x] Add "Channel" column to Users page
- [x] Add channel icons (🌐 web, 📱 facebook, 💬 zalo, ✈️ telegram)
- [x] Add channel filter (all/web/facebook/zalo/telegram)
- [x] Real-time updates via WebSocket for Facebook messages
- [x] User detail page supports Facebook sessions

**Testing:**
- [x] Test webhook verify token
- [x] Send test message from FB
- [x] Verify message appears in DB (chat_messages table)
- [x] Verify admin sees message realtime (WebSocket broadcast)
- [x] Verify reply sent back to FB (Send API working)
- [x] Test AI response with RAG (retrieves 23 chunks, generates accurate answers)
- [x] Test HUMAN_ONLINE mode (AI skips, admin takes over)
- [x] Test admin reply to Facebook user

---

### GIAI ĐOẠN 3 - ZALO

**Backend:**
- [ ] Tạo `api/zalo_webhook.py`
- [ ] Implement webhook signature verify
- [ ] Implement receive message handler
- [ ] Create `services/zalo_send.py`
- [ ] Update database schema (add zalo_user_id)
- [ ] Test Zalo webhook

**Frontend:**
- [ ] (Reuse từ Giai đoạn 2)

**Testing:**
- [ ] Similar to Facebook

---

### GIAI ĐOẠN 4 - TELEGRAM

**Backend:**
- [ ] Tạo `api/telegram_webhook.py`
- [ ] Implement webhook handler
- [ ] Create `services/telegram_send.py`
- [ ] Update database schema (add telegram_chat_id)

**Frontend:**
- [ ] (Reuse từ Giai đoạn 2)

---

## 🚀 NEXT STEPS (ĐỐI VỚI BẠN NGAY BÂY GIỜ)

### ⏱️ HÔM NAY (Quick Start)

**Bước 1: Setup Environment**
```bash
# Tạo .env file
cat > .env << EOF
FACEBOOK_PAGE_ACCESS_TOKEN=your_token_here
FACEBOOK_VERIFY_TOKEN=my_chatbot_verify_token_12345
FACEBOOK_APP_SECRET=your_app_secret_here
API_BASE_URL=http://localhost:8000
EOF
```

**Bước 2: Lấy Facebook Tokens**
- Vào https://developers.facebook.com/
- Tạo App → Loại "Business"
- Thêm Product: "Messenger"
- Tạo/chọn Facebook Page
- Copy: App ID, App Secret, Page Access Token
- Tạo: Verify Token (chuỗi bất kỳ)

**Bước 3: Start ngrok + Backend**
```bash
# Terminal 1: ngrok
ngrok http 8000

# Terminal 2: Backend
python main.py
```

**Bước 4: Configure Facebook Webhook**
- Vào Facebook App → Messenger → Settings
- Webhook:
  - URL: `https://ngrok-url/webhook/facebook`
  - Verify Token: `my_chatbot_verify_token_12345`
- Subscribe to: messages

**Bước 5: Test**
- Gửi message từ Messenger
- Kiểm tra backend logs
- Xác nhận reply được gửi lại

### 📅 TUẦN NÀY

1. ✅ Code base Facebook (DONE)
2. ⏳ Local testing & bug fixing
3. ⏳ Deploy backend lên production
4. ⏳ Test trên production Facebook

### 📅 TUẦN SAU (Giai đoạn 3-4)

1. Giai đoạn 3: Zalo Integration (copy pattern Facebook)
2. Giai đoạn 4: Telegram Integration (copy pattern Facebook)
3. Frontend: Channel filter updates (already done)

---

## 📊 SUMMARY - GIAI ĐOẠN 2 FACEBOOK INTEGRATION

| Item | Status | Details |
|------|--------|---------|
| Backend Services | ✅ Done | channel_router, facebook_send, send_router |
| Webhook API | ✅ Done | facebook_webhook.py with signature verify |
| Database Schema | ✅ Done | channel + metadata columns |
| Frontend UI | ✅ Done | Channel column + filter + icons |
| Documentation | ✅ Done | Full config guide in this file |
| Local Testing | ✅ Done | All tests passed with ngrok |
| RAG Integration | ✅ Done | Full pipeline working with Facebook |
| HUMAN_ONLINE Mode | ✅ Done | Chat mode switching implemented |
| Admin Reply | ✅ Done | Admin can reply via Send API |
| Multi-channel Support | ✅ Done | All endpoints support web + Facebook |
| Production Deploy | ⏳ Optional | Can deploy to production when needed |

**Total code:** ~1,500 lines new  
**Features implemented:**
- ✅ Full webhook receive/send flow
- ✅ RAG-based AI responses (23 chunks, accurate answers)
- ✅ Signature verification (HMAC-SHA1)
- ✅ HUMAN_ONLINE mode (admin takeover)
- ✅ Real-time admin dashboard updates
- ✅ Multi-channel database schema
- ✅ Admin reply functionality

---

## 📞 SUPPORT & REFERENCES

- **Webhook docs:** https://developers.facebook.com/docs/messenger-platform/webhooks
- **Send API:** https://developers.facebook.com/docs/messenger-platform/reference/send-api
- **ngrok docs:** https://ngrok.com/docs
- **Issues:** Check backend logs for error messages

---

**Lần cập nhật cuối:** 2025-11-30 (Giai đoạn 2 - Facebook - 100% HOÀN THÀNH)  
**Status:** ✅ Production Ready - All features working end-to-end
