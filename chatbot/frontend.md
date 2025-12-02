# Phân cấp phát triển frontend dự án Chatbot AI RAG
# không tạo thêm các file hướng dẫn , tạo thêm các file tóm tawtss và document,khi sữa hay cập nhật trực tiếp vào frontend.md
## 1. Mục tiêu & phạm vi
- Chat Widget React + Tailwind, bắt buộc email trước khi chat.
- Admin Dashboard: quản lý mode, users/leads, chat history, documents, statistics.
- Tích hợp đầy đủ API backend đã liệt kê.

## 2. Tính năng frontend
- End-user: Form lead, chat real-time, lưu session_id, xem lịch sử.
- Admin: Toggle mode, danh sách users/leads, chat history, quản lý documents, xem statistics, health check.

## 3. Kiến trúc & flow
- [Widget UI] → [Zustand store] → [Axios API] → FastAPI
- localStorage lưu session_id
- Mode flow: loadChatMode → AI_ONLY/HUMAN_ONLINE → gọi API phù hợp

## 4. Cấu trúc thư mục
```
frontend/
├─ package.json
├─ tailwind.config.js
├─ postcss.config.js
├─ index.html
├─ .env.example
├─ src/
│  ├─ main.jsx
│  ├─ App.jsx
│  ├─ styles/tailwind.css
│  ├─ routes/
│  │   ├─ router.jsx
│  │   └─ ProtectedRoute.jsx
│  ├─ pages/
│  │   ├─ widget/ChatPage.jsx
│  │   ├─ widget/LeadGate.jsx
│  │   ├─ admin/Dashboard.jsx
│  │   ├─ admin/Users.jsx
│  │   ├─ admin/UserDetail.jsx
│  │   ├─ admin/Documents.jsx
│  │   ├─ admin/Statistics.jsx
│  │   └─ admin/Settings.jsx
│  ├─ components/
│  │   ├─ ChatWindow.jsx
│  │   ├─ MessageBubble.jsx
│  │   ├─ ChatInput.jsx
│  │   ├─ ModeBadge.jsx
│  │   ├─ FileUploader.jsx
│  │   ├─ DataCard.jsx
│  │   └─ Table.jsx
│  ├─ store/
│  │   ├─ useChatStore.js
│  │   └─ useAdminStore.js
│  ├─ api/
│  │   ├─ axios.js
│  │   ├─ chat.js
│  │   ├─ admin.js
│  │   └─ documents.js
│  └─ utils/
│      ├─ session.js
│      └─ validators.js
└─ public/
   └─ widget.js
```

## 5. Cài đặt & chạy
- cd frontend
- npm i
- npm run dev / build / preview

## 6. Cấu hình .env
- VITE_API_BASE_URL, VITE_WIDGET_TITLE, VITE_BRAND_PRIMARY

## 7. Router & trang
- / → Widget (LeadGate → ChatPage)
- /admin → Dashboard
- /admin/users → Users
- /admin/users/:sessionId → UserDetail + history
- /admin/documents → Documents + stats
- /admin/statistics → Statistics
- /admin/settings → Settings (mode toggle)
- ProtectedRoute cho admin nếu cần login

## 8. State management (Zustand)
- useChatStore.js: sessionId, mode, user, messages, setUser, loadMode, loadHistory, send
- useAdminStore.js: mode, users, stats, documents, docStats, refreshMode, toggleMode, loadUsers, loadUserDetail, loadUserHistory, loadDocuments, loadDocStats, uploadDoc, removeDoc, loadStatistics

## 9. API client (Axios)
- axios.js: config baseURL, interceptors
- chat.js: sendMessage, getChatHistory, getChatSessions, health
- admin.js: getChatMode, setChatMode, getUsers, getUserBySession, getUserHistoryBySession, getUserHistoryByEmail, getStatistics
- documents.js: listDocuments, getDocumentStats, uploadDocument, deleteDocument

## 10. UI Components (Tailwind)
- ChatWindow, MessageBubble, ChatInput, ModeBadge, FileUploader, DataCard, Table
- LeadGate: form email/name/phone
- FileUploader: drag & drop, upload
- DataCard/Table: thống kê, danh sách

## 11. Chat Widget nhúng Website
- Build widget.js (UMD/IIFE), nhúng vào website ngoài
- Mount bubble cố định, mở panel chat

## 12. Xử lý chế độ AI ↔ HUMAN
- GET /admin/settings/chat-mode
- AI_ONLY: gọi /chat/message
- HUMAN_ONLINE: không gọi AI, hiển thị notice
- Admin toggle mode, badge đổi màu real-time

## 13. Upload tài liệu & RAG stats
- Trang Documents: bảng files, upload, delete, stats

## 14. Lỗi & fallback
- Toast/error banner, hướng dẫn convert .docx, timeout LLM, validate email

## 15. Build & deploy
- Widget: build widget.js, CDN
- Admin: build SPA, deploy Nginx/static hosting
- Nginx: try_files $uri /index.html

## 16. Copilot Prompts (JS + React)
- ChatWindow, store chat, Admin Documents page, Mode toggle, Users & History

## 17. Roadmap UI
- Streaming, emoji, file attachment, lọc users, dark mode, i18n

## 18. Checklist QA
- Validate email, lưu session_id, HUMAN_ONLINE không call /chat/message, upload file đúng, delete cập nhật list, users/history load đúng, mode toggle hoạt động, API base URL từ .env, UI responsive.

> Phân cấp này bám sát toàn bộ nội dung file, giúp phát triển frontend đầy đủ, rõ ràng, dễ mở rộng.

## 28. HOÀN THÀNH: Trang Users List (/admin/users)

### Cập nhật Users.jsx
- Gọi `useAdminStore()` lấy: users, loading, error, loadUsers
- loadUsers() gọi API getUsers() từ admin.js
- Mount trang: gọi loadUsers()
- Render bảng danh sách:
    - STT, Email, Name, Phone, Session ID, Last Message, Messages
    - Click row → navigate `/admin/users/:sessionId`
- Tìm kiếm client-side: filter email/phone/name
- UI: Tailwind admin style, rounded-xl, shadow-sm, bg-white

### Cập nhật Table.jsx
- Hỗ trợ columns: header, accessor, render(row, idx)
- render() nhận row và rowIndex, trả JSX để render cell
- onRowClick: điều hướng khi click hàng
- Hover effect khi onRowClick có giá trị

### API sẵn có
- getUsers() → trả danh sách users từ /admin/users
- Mỗi user có: email, name, phone, session_id, message_count, last_message_time

## 29. FIX: Session Handling khi User submit LeadGate (Tránh merge dữ liệu cũ)

### Vấn đề cũ
- Khi user nhập email/sdt mới trong LeadGate → Backend vẫn merge với session cũ
- Admin nhận được dữ liệu lẫn lộn (email cũ + tin nhắn mới, etc.)

### Giải pháp mới
**Frontend (LeadGate.jsx):**
1. Khi user submit form:
   - Xóa session cũ: `clearSession()` (xóa localStorage)
   - Tạo session_id mới: `crypto.randomUUID()` → lưu vào localStorage
   - Gọi `setSessionId(newSessionId)` (Zustand action)
   - Gọi `setUser(formData)` (Zustand action)
   - Navigate sang `/chat` (ChatPage sẽ connect WebSocket với sessionId mới)

**Backend (db_service.py - save_user_info):**
1. Luồng đơn giản hóa:
   - Check nếu session_id tồn tại → UPDATE user info
   - Nếu session_id mới → INSERT user mới
   - Nếu email tồn tại với session khác → Xóa bản ghi cũ trước khi INSERT
   - ✅ Không merge hay update session lại

**Luồng hoàn chỉnh:**
```
LeadGate (user nhập email mới)
  ↓
clearSession() → xóa session cũ
  ↓
generateNewSessionId() → tạo UUID mới
  ↓
setSessionId(newSessionId) → update Zustand
  ↓
Navigate /chat → ChatPage mount
  ↓
ChatPage: connect WebSocket với sessionId mới
  ↓
Gửi tin nhắn: API /chat/message + sessionId mới
  ↓
Backend: save_user_info(sessionId mới) → INSERT user mới
  ↓
Admin nhận thông tin user mới chính xác ✅
```

**Thay đổi code:**
- LeadGate.jsx: Thêm clearSession() + generateNewSessionId()
- useChatStore.js: Thêm action setSessionId()
- db_service.py: Đơn giản hóa save_user_info() logic

## 30. HOÀN THÀNH: Trang Documents Management (/admin/documents)

### Cấu trúc trang
**Layout:** 2 cột (left: upload + table, right: stats)
- **Trái (col-span-2):** Upload section + Documents Table
- **Phải (col-span-1):** File details & RAG stats (sticky)

### Upload Section (FileUploader.jsx)
- Hỗ trợ drag-drop + click to select
- Loading state với spinner
- Message: "Đang upload..." khi đang xử lý

### Documents Table (Table + data từ listDocuments())
- Columns: filename, file_size, char_count, extension, uploaded_at, actions
- Row click → select file → hiển thị stats bên phải
- Delete button → confirm → removeDoc() → reload

### File Details Panel (bên phải)
- Hiển thị khi select file
- Thông tin: filename, extension, file_size, char_count, uploaded_at
- RAG stats: total_chunks, embedding_dim (từ docStats)
- Delete button (hoàn toàn)
- Sticky position

### API & Store
- **useAdminStore:** documents, docStats, loadDocuments(), loadDocStats(), uploadDoc(), removeDoc()
- **documents.js:** listDocuments(), getDocumentStats(), uploadDocument(), deleteDocument()
- **FileUploader.jsx:** onUpload callback, loading prop

### Thay đổi code
- Documents.jsx: Layout 2 cột, row click handler, file stats panel
- FileUploader.jsx: Drag-drop support, loading state, lucide icons
- useAdminStore.js: Actions đã sẵn có ✅
- documents.js: APIs đã sẵn có ✅
- Table.jsx: onRowClick support ✅

## 31. HOÀN THÀNH: Trang Statistics (/admin/statistics)

### Dữ liệu từ Backend
API: GET /admin/statistics
Response:
```json
{
  "total_users": number,
  "total_messages": number,
  "total_ai_messages": number,
  "total_human_messages": number,
  "total_documents": number,
  "active_sessions": number,
  "top_documents": [
    { "filename": "...", "used": number }
  ],
  "daily_messages": [
    { "date": "2025-01-01", "count": 12 }
  ]
}
```

### Layout
- Grid cards: total_users, total_messages, total_ai_messages, total_human_messages, total_documents
- Active sessions card (dạng số lớn)
- Top documents table (STT, filename, used)
- Daily messages table + bar chart (width % dựa trên count)

### API & Store
- **useAdminStore:** stats, loadStatistics() ✅
- **admin.js:** getStatistics() ✅

### Thay đổi code
- Statistics.jsx: Layout cards + 2 tables, dữ liệu từ backend không tính toán lại
- DataCard.jsx: Hỗ trợ icon prop ✅
- Table.jsx: Render prop ✅


## 19. Thư viện cần cài đặt
- react@18.x
- react-dom@18.x
- react-router-dom@6.x
- zustand@4.x
- axios@1.x
- tailwindcss@3.x
- postcss@8.x
- autoprefixer@10.x
- @headlessui/react (modal, dialog)
- lucide-react (icon)
- react-hook-form (form validation)
- date-fns (date utils)
- react-i18next (đa ngôn ngữ, optional)
- jest, @testing-library/react (kiểm thử)

## 20. Hướng dẫn build widget.js
1. Tạo file `src/widget/WidgetRoot.jsx` (hoặc ChatWidget.jsx)
2. Cấu hình Vite/webpack output dạng UMD/IIFE:
    - Vite: `build.lib.entry`, `build.lib.formats = ['umd']`
    - Webpack: `output.libraryTarget = 'umd'`
3. Build ra `public/widget.js`, nhúng vào website ngoài như hướng dẫn ở trên.

## 21. Mẫu cấu hình .env.example
```
VITE_API_BASE_URL=http://localhost:8000
VITE_WIDGET_TITLE=Chatbot AI
VITE_BRAND_PRIMARY=#1e293b
```

## 22. Mẫu code component chính
### ChatWindow.jsx
```jsx
import React from 'react';
export default function ChatWindow({ messages, onSend, mode }) {
   // ...render header, messages, input
}
```
### LeadGate.jsx
```jsx
import React from 'react';
export default function LeadGate({ onSubmit }) {
   // ...form email, name, phone
}
```
### FileUploader.jsx
```jsx
import React from 'react';
export default function FileUploader({ onUpload }) {
   // ...drag & drop, button upload
}
```

## 23. Hướng dẫn kiểm thử
- Sử dụng Jest, React Testing Library cho unit/integration test.
- Viết test cho store, API, component chính.

## 24. CI/CD
- Đề xuất dùng GitHub Actions, Vercel, Netlify để build/deploy frontend tự động.
- Workflow: push code → build → deploy lên static hosting/CDN.

## 25. Phân quyền admin
- Nếu cần đăng nhập: dùng JWT, lưu token vào localStorage, tạo ProtectedRoute.jsx cho các trang /admin/*.
- API xác thực: /admin/login, /admin/logout (tùy backend).

## 26. Hướng dẫn i18n
- Dùng react-i18next, tạo thư mục `src/locales/` chứa file dịch.
- Thêm hook chuyển đổi ngôn ngữ vào UI.

## 27. Responsive/mobile
- Sử dụng Tailwind breakpoint (`sm`, `md`, `lg`, `xl`).
- Ưu tiên mobile-first, test UI trên nhiều thiết bị.

## 32. HOÀN THÀNH: Multi-Channel Support (Facebook Integration)

### Backend Integration
- ✅ `api/facebook_webhook.py` (340 lines) - Webhook receive/verify
- ✅ `core/facebook_send.py` (304 lines) - Send API integration
- ✅ `core/channel_router.py` (138 lines) - Multi-channel message routing
- ✅ Database schema: channel, metadata columns
- ✅ RAG pipeline: Works with all channels (web, facebook, zalo, telegram)
- ✅ HUMAN_ONLINE mode: AI skips when admin is online

### Frontend Updates (Users.jsx)
- ✅ Channel column với icons: 🌐 web, 📱 facebook, 💬 zalo, ✈️ telegram
- ✅ Filter theo channel (all/web/facebook/zalo/telegram)
- ✅ Real-time updates qua WebSocket cho Facebook messages
- ✅ User detail page hỗ trợ Facebook sessions (fb_ prefix)

### Flow hoàn chỉnh
```
Facebook Messenger → Webhook → Channel Router → RAG → LLM → Send API → Facebook User
                                      ↓
                              Admin Dashboard (real-time via WebSocket)
```

### API Endpoints
- POST /webhook/facebook - Nhận messages từ Facebook
- GET /webhook/facebook - Verify webhook token
- GET /admin/users - Danh sách users (bao gồm Facebook)
- GET /admin/users/{session_id} - Chi tiết user (hỗ trợ fb_ sessions)
- POST /admin/reply - Admin reply (gửi qua Send API nếu Facebook)

### Configuration (.env.local)
```env
FACEBOOK_PAGE_ACCESS_TOKEN=EAAWODn...(real token)
FACEBOOK_VERIFY_TOKEN=my_chatbot_verify_token_12345
FACEBOOK_APP_SECRET=302fa086b42db61e0b154ce5aef33fdb
```

### Testing Results
- ✅ Webhook verification: 200 OK
- ✅ Message reception: Messages saved to DB
- ✅ AI responses: RAG retrieves 23 chunks, generates accurate answers
- ✅ Send API: Messages delivered to Facebook users
- ✅ Admin dashboard: Real-time updates, channel filter working
- ✅ Chat mode: HUMAN_ONLINE skips AI, AI_ONLY uses RAG
- ✅ Admin reply: Successfully sends via Facebook Send API

**Trạng thái:** ✅ Production Ready
**Ngày hoàn thành:** 2025-11-30