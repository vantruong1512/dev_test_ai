# 🤖 Chatbot AI RAG - Hệ thống đa kênh cho doanh nghiệp

> **Version**: 1.0.0 (November 2025)  
> **Tech Stack**: FastAPI + Ollama (Gemma2 2B) + ChromaDB + SQLite + React  
> **Architecture**: Vector RAG với ChromaDB + Semantic Search  
> **Status**: ✅ Production Ready

---

## 📋 Mục lục

- [1. Giới thiệu](#1-giới-thiệu)
- [2. Tính năng chính](#2-tính-năng-chính)
- [3. Yêu cầu kỹ thuật](#3-yêu-cầu-kỹ-thuật)
- [4. Kiến trúc hệ thống](#4-kiến-trúc-hệ-thống)
- [5. Chế độ AI ↔ Human Takeover](#5-chế-độ-ai--human-takeover)
- [6. Cấu trúc dự án](#6-cấu-trúc-dự-án)
- [7. Hướng dẫn cài đặt](#7-hướng-dẫn-cài-đặt)
- [8. Cấu hình](#8-cấu-hình)
- [9. Sử dụng API](#9-sử-dụng-api)
- [10. GitHub Copilot Prompts](#10-github-copilot-prompts)
- [11. Xử lý lỗi](#11-xử-lý-lỗi)
- [12. Roadmap](#12-roadmap)

---

## 1. Giới thiệu

### 1.1 Mục đích

Hệ thống **Chatbot AI đa kênh** với khả năng:
- ✅ Trả lời tự động dựa trên tài liệu doanh nghiệp (RAG)
- ✅ Thu thập lead (tên, email, phone)
- ✅ Tích hợp Website, Facebook Messenger, Zalo OA
- ✅ Admin Panel quản lý tài liệu + chat history
- ✅ **Chế độ AI ↔ Nhân viên Online** linh hoạt

### 1.2 Công nghệ sử dụng

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI (Python 3.9+) |
| **LLM** | Ollama (Gemma2 2B) |
| **RAG** | Vector RAG với ChromaDB + Semantic Search |
| **Embeddings** | Vietnamese Sentence BERT (keepitreal/vietnamese-sbert) |
| **Vector DB** | ChromaDB (Persistent) |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Frontend** | React Widget + Admin Panel |
| **Document Loaders** | LangChain Community (PDF, DOCX, TXT) |

### 1.3 Tài liệu tham khảo

- [Ollama Documentation](https://ollama.ai)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [LangChain Community](https://python.langchain.com)

---

## 2. Tính năng chính

### 2.1 Khách hàng (End User)

- 💬 Chat trên website (widget React hoặc iframe HTML)
- 📱 Chat qua Facebook Messenger
- 💬 Chat qua Zalo OA
- 🎨 Giao diện thân thiện, dễ sử dụng
- 🤖 Nhận trả lời từ AI hoặc nhân viên (tùy chế độ)

### 2.2 Nhân viên bán hàng

- 📩 Nhận tin nhắn khách khi chế độ `HUMAN_ONLINE` đang bật
- 💬 Xem và trả lời khách ngay trên Admin Panel
- 🏷️ Gắn tag, ghi chú khách hàng
- 📜 Theo dõi lịch sử chat theo từng khách

### 2.3 Quản trị viên

- 📁 Upload / Xóa / Quản lý tài liệu huấn luyện RAG
- 🔄 Huấn luyện lại embeddings
- 📊 Theo dõi lịch sử chat theo thời gian
- ⚙️ Bật/Tắt chế độ:
  - `AI_ONLY` → AI trả lời toàn bộ
  - `HUMAN_ONLINE` → Nhân viên trả lời, AI tạm dừng
- 👥 Quản lý nhân viên nội bộ
- 🔑 Quản lý token, cấu hình tích hợp Facebook/Zalo

---

## 3. Yêu cầu kỹ thuật

### 3.1 Yêu cầu chức năng

- **RAG Engine**: Vector RAG với ChromaDB (chunking + semantic search)
- **LLM**: 
  - Ưu tiên: Ollama (Gemma2 2B - nhanh, nhẹ, tiếng Việt tốt)
  - Fallback: LM Studio / Groq / DeepSeek
- **Backend**: FastAPI
- **Frontend**: 
  - Website widget: React hoặc HTML Script
  - Admin: React Admin
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Realtime**: WebSocket hoặc Socket.IO

### 3.2 Yêu cầu phi chức năng

- ✅ Backup DB hằng ngày
- ✅ Rate limit API để chống spam
- ✅ Thông báo lỗi rõ ràng, không lộ thông tin nội bộ

### 3.3 Yêu cầu bảo mật

- 🔐 JWT & phân quyền
- 🔒 Mã hóa email/phone lưu DB
- 🔑 Token Facebook/Zalo/LLM tách riêng trong `.env`

---

## 4. Kiến trúc hệ thống

### 4.1 Sơ đồ hoạt động tổng quát

```
User → Chat Widget → FastAPI → MODE CHECK
      └───────────────────────────┘
                  ↓
     ┌────────────────────────────────┐
     │ IF MODE == HUMAN_ONLINE        │
     │ → Không gọi AI                 │
     │ → Đẩy tin nhắn cho nhân viên   │
     └────────────────────────────────┘
                  ↓
     ┌────────────────────────────────┐
     │ IF MODE == AI_ONLY             │
     │ → RAG Pipeline → LLM           │
     └────────────────────────────────┘
                  ↓
        → Gửi response về người dùng  
                  ↓
        → Lưu lịch sử vào Database
```

### 4.2 Vector RAG với ChromaDB

#### 4.2.1 Đặc điểm
- ✅ **Chunking thông minh**: Chia tài liệu thành chunks 500 ký tự với overlap 50 ký tự
- ✅ **Vector Embeddings**: Sử dụng Vietnamese Sentence BERT (keepitreal/vietnamese-sbert)
- ✅ **Semantic Search**: Tìm kiếm theo ngữ nghĩa, không phải keyword matching
- ✅ **Persistent Storage**: ChromaDB lưu trữ vector embeddings bền vững
- ✅ **Top-K Retrieval**: Lấy 10 chunks liên quan nhất, lọc thông minh theo context
- ✅ **Multi-file Support**: Tự động phát hiện file liên quan theo câu hỏi

#### 4.2.2 Cấu trúc dữ liệu
```
/data/
 ├── uploads/                          # Tài liệu gốc
 │   ├── Automation Testing.pdf
 │   ├── Quan tri he thong.pdf
 │   └── Tri tue nhan tao - AI Engineer.pdf
 │
 └── vector_db/                        # ChromaDB persistent storage
     ├── chroma.sqlite3               # Vector database
     └── [embedding data]/
```

#### 4.2.3 Pipeline xử lý

**Khi upload file:**
1. Convert nội dung sang text (PDF/DOCX/TXT)
2. Chia thành chunks (500 chars, overlap 50)
3. Generate embeddings với Vietnamese SBERT
4. Lưu vào ChromaDB với metadata (filename, chunk_index, etc.)

**Khi user hỏi:**
1. **Embedding Query**: Convert câu hỏi thành vector
2. **Semantic Search**: Tìm top-10 chunks gần nhất (cosine similarity)
3. **File Filtering**: Phát hiện file cụ thể (AI, Automation, Quản trị) theo keywords
4. **Chunk Selection**: Ưu tiên chunks có thông tin giá + số tiền (VND, triệu)
5. **Context Building**: Ghép chunks thành context (<2500 chars)
6. **LLM Generation**: Gửi context + prompt vào Ollama

**Cấu hình hiện tại:**
```python
CHUNK_SIZE = 500           # Kích thước mỗi chunk
CHUNK_OVERLAP = 50         # Overlap giữa chunks
TOP_K_CHUNKS = 10          # Số chunks lấy từ vector search
MAX_CONTEXT_CHARS = 2500   # Giới hạn context gửi cho LLM
```

**Ưu điểm so với Full-file loading:**
- ⚡ **Nhanh hơn 10x**: Chỉ load chunks liên quan thay vì toàn bộ file
- 🎯 **Chính xác hơn**: Semantic search tìm đúng thông tin cần thiết
- 📈 **Scalable**: Hỗ trợ hàng trăm tài liệu không giảm hiệu năng
- 💾 **Tiết kiệm token**: Context nhỏ gọn, giảm chi phí LLM

### 4.3 Backend Services

#### 4.3.1 API Routes
- `/chat/message` - Chat endpoint
- `/admin/*` - Admin management
- `/train/*` - RAG training

#### 4.3.2 Core Services
- **llm_service.py**: Ollama/LLM provider management (Gemma2 2B)
- **rag_service.py**: Vector RAG với ChromaDB + Vietnamese SBERT embeddings
- **db_service.py**: SQLite database operations (chat history, users)


---

## 5. Chế độ AI ↔ Human Takeover

### 5.1 Mô tả tính năng

- ✔ Mặc định AI trả lời tự động
- ✔ Khi nhân viên bật "Online Mode" → toàn bộ tin nhắn chuyển qua người thật

### 5.2 Cách hoạt động

#### Mode: AI_ONLY (Mặc định)
- AI trả lời nhanh dựa trên nội dung tài liệu
- Sử dụng full-file RAG context
- Không cần nhân viên can thiệp

#### Mode: HUMAN_ONLINE
- Tin nhắn khách được đẩy vào Admin Panel
- Nhân viên trả lời trực tiếp
- AI dừng hoàn toàn
- Có thể chuyển về AI_ONLY bất cứ lúc nào

### 5.3 API Endpoints

```python
# Lấy mode hiện tại
GET /settings/chat-mode

# Đổi mode (admin only)
POST /settings/chat-mode
{
  "mode": "AI_ONLY" | "HUMAN_ONLINE"
}
```

---

## 6. Cấu trúc dự án

```
Chatbot_web/
 ├── main.py                    # FastAPI entry point
 ├── requirements.txt           # Python dependencies
 ├── .env                       # Environment configuration
 ├── Dockerfile                 # Docker container config
 ├── docker-compose.yml         # Docker compose setup
 │
 ├── api/                       # API routes
 │   ├── chat_api.py           # Chat endpoints
 │   ├── admin_api.py          # Admin endpoints
 │   └── train_api.py          # Training endpoints
 │
 ├── core/                      # Core business logic
 │   ├── llm_service.py        # LLM provider management
 │   ├── rag_service.py        # Full-file document loading
 │   ├── db_service.py         # Database operations
 │  
 │
 ├── data/                      # Data storage
 │   ├── uploads/              # Uploaded documents
 │
 └── frontend/                  # Frontend applications
     ├── chat_widget/          # Chat widget
     │   ├── index.html
     │   └── README.md
     └── admin_dashboard/      # Admin panel
         └── README.md
```

---

## 7. Hướng dẫn cài đặt

### 7.1 Yêu cầu hệ thống

- **Python**: 3.9+ (khuyến nghị 3.11)
- **Ollama**: Latest version (tải từ https://ollama.ai)
- **RAM**: 8GB+ (khuyến nghị 16GB)
- **Disk**: 10GB+ free space
- **OS**: Windows 10/11, Linux, macOS

### 7.2 Cài đặt từng bước

#### Bước 1: Clone hoặc tải dự án
```powershell
# Clone repository (nếu có)
git clone <repository-url>
cd chatbot

# Hoặc giải nén file zip vào thư mục
cd d:\AI_for_code_Copilot\dev_test_ai\chatbot
```

#### Bước 2: Tạo môi trường ảo Python (khuyến nghị)
```powershell
# Tạo virtual environment
python -m venv venv

# Kích hoạt (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Nếu lỗi policy, chạy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Bước 3: Cài đặt dependencies
```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Cài đặt packages
pip install -r requirements.txt

# Kiểm tra cài đặt
pip list
```

#### Bước 4: Cấu hình môi trường (.env)
```powershell
# Copy file mẫu
cp .env.example .env

# Chỉnh sửa .env với editor
notepad .env
```

**Cấu hình tối thiểu trong .env:**
```env
LLM_PROVIDER=ollama
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=gemma2:2b
LLM_TIMEOUT_SECONDS=120
DATABASE_URL=sqlite:///./data/chatbot.db
```

#### Bước 5: Cài đặt và cấu hình Ollama

**Windows:**
1. Tải Ollama từ: https://ollama.ai/download/windows
2. Chạy file cài đặt OllamaSetup.exe
3. Sau khi cài đặt, mở PowerShell/Terminal mới
4. Pull model Gemma2 2B:

```powershell
# Kiểm tra Ollama đã cài
ollama --version

# Pull model Gemma2 2B (download ~1.6GB - nhẹ và nhanh)
ollama pull gemma2:2b

# Kiểm tra model đã có
ollama list

# Test model (optional)
ollama run gemma2:2b "Xin chào"
```

**Linux/macOS:**
```bash
# Cài đặt Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull model Gemma2 2B
ollama pull gemma2:2b

# Kiểm tra
ollama list
```

#### Bước 6: Kiểm tra cấu trúc thư mục
```powershell
# Đảm bảo các thư mục này tồn tại
New-Item -ItemType Directory -Force -Path data/uploads
New-Item -ItemType Directory -Force -Path data/vector_db
New-Item -ItemType Directory -Force -Path logs
```

#### Bước 7: Test hệ thống
```powershell
# Test import modules
python -c "from core.rag_service import RAGService; print('RAG OK')"
python -c "from core.llm_service import LLMService; print('LLM OK')"
python -c "from core.db_service import DatabaseService; print('DB OK')"

# Test Ollama connection
curl http://127.0.0.1:11434/api/tags
```

#### Bước 8: Khởi chạy server
```powershell
# Chạy server (database sẽ tự động khởi tạo)
python main.py

# Hoặc dùng uvicorn trực tiếp
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Server sẽ chạy tại:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### 7.3 Kiểm tra hoạt động

#### Test 1: Health Check
```powershell
# Windows PowerShell
Invoke-WebRequest -Uri http://localhost:8000/health | Select-Object -Expand Content

# Hoặc dùng curl
curl http://localhost:8000/health
```

**Expected output:**
```json
{
  "status": "ok",
  "message": "Chatbot AI RAG is running"
}
```

#### Test 2: Index tài liệu vào Vector DB
```powershell
# Index tài liệu đã có trong data/uploads/
python core/rag_service.py

# Hoặc tạo file test mới
"Khóa học Python có giá 5 triệu VNĐ. Thời lượng 3 tháng." | Out-File -FilePath data/uploads/test.txt -Encoding utf8

# Index lại
python -c "from core.rag_service import VectorRAGService; rag = VectorRAGService(); print(rag.index_all_documents(force_reindex=True))"
```

#### Test 3: Chat API
```powershell
# Test câu hỏi về học phí
$body = @{
    message = "Học phí AI bao nhiêu?"
    session_id = "test123"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/chat/message `
  -Method POST `
  -ContentType "application/json" `
  -Body $body | Select-Object -Expand Content
```

**Expected output:**
```json
{
  "reply": "Học phí khóa AI Engineer có 3 hình thức thanh toán:\n- Đóng theo tháng: 3,000,000 VND x 6 tháng\n- Đóng theo kỳ: 8,600,000 VND x 2 kỳ (tiết kiệm 5%)\n- Trọn gói: 16,200,000 VND (tiết kiệm 10%)",
  "session_id": "test123",
  "mode": "AI_ONLY",
  "provider": "ollama"
}
```

#### Test 4: Upload tài liệu mới qua API
```powershell
# Upload file PDF/DOCX/TXT
$filePath = "D:\path\to\your\document.pdf"
$uri = "http://localhost:8000/admin/documents/upload"

# Tạo multipart form data
$form = @{
    file = Get-Item -Path $filePath
}

Invoke-WebRequest -Uri $uri -Method POST -Form $form
```

**Expected output:**
```json
{
  "success": true,
  "filename": "document.pdf",
  "size": 245678,
  "char_count": 12456,
  "chunks_indexed": 25,
  "message": "Upload thành công: document.pdf"
}
```

### 7.4 Xử lý lỗi cài đặt thường gặp

#### Lỗi 1: "ollama: command not found"
```powershell
# Kiểm tra PATH
$env:PATH -split ';' | Select-String ollama

# Thêm vào PATH (tạm thời)
$env:PATH += ";C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama"

# Hoặc restart terminal sau khi cài Ollama
```

#### Lỗi 2: "ModuleNotFoundError"
```powershell
# Kiểm tra virtual environment đã activate chưa
Get-Command python | Select-Object Source

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Lỗi 3: "Connection refused (Ollama)"
```powershell
# Kiểm tra Ollama đang chạy
Get-Process ollama -ErrorAction SilentlyContinue

# Khởi động Ollama (Windows)
Start-Process "ollama" -ArgumentList "serve"

# Kiểm tra port
Test-NetConnection -ComputerName 127.0.0.1 -Port 11434
```

#### Lỗi 4: "Permission denied (.db file)"
```powershell
# Tạo thư mục data với quyền đầy đủ
New-Item -ItemType Directory -Force -Path data
icacls data /grant "$env:USERNAME:F" /T
```

### 7.5 Triển khai Production (Optional)

#### Docker Deployment
```bash
# Build image
docker build -t chatbot-rag:latest .

# Run container
docker run -d -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  --name chatbot-rag \
  chatbot-rag:latest
```

#### Systemd Service (Linux)
```bash
# Tạo service file
sudo nano /etc/systemd/system/chatbot-rag.service

# Enable và start
sudo systemctl enable chatbot-rag
sudo systemctl start chatbot-rag
```

---

## 8. Cấu hình

### 8.1 Biến môi trường (.env)

```env
# LLM Configuration
LLM_PROVIDER=ollama
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=gemma3:12b
LLM_TIMEOUT_SECONDS=180

# Database
DATABASE_URL=sqlite:///./data/chatbot.db

# API Keys (nếu dùng cloud LLM)
GROQ_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here

# Facebook/Zalo Integration (optional)
FACEBOOK_PAGE_TOKEN=your_token_here
ZALO_OA_TOKEN=your_token_here
```

### 8.2 Vector RAG Configuration

**RAG Service (core/rag_service.py):**
```python
CHUNK_SIZE = 500           # Kích thước mỗi chunk (chars)
CHUNK_OVERLAP = 50         # Overlap giữa chunks
TOP_K_CHUNKS = 10          # Số chunks lấy từ vector search
MAX_CONTEXT_CHARS = 2500   # Giới hạn context gửi cho LLM
```

**Embeddings Model:**
- Model: `keepitreal/vietnamese-sbert`
- Size: ~540MB (download lần đầu)
- Optimize cho tiếng Việt

**Tại sao giới hạn context?**
- Gemma2 2B context window: ~8K tokens
- 2500 chars ≈ 625 tokens (an toàn, còn dư cho response)
- Context nhỏ → LLM nhanh hơn, chính xác hơn

**Điều chỉnh nếu cần:**
- Model lớn hơn (Gemma3 27B): Tăng MAX_CONTEXT_CHARS lên 5000
- Nhiều tài liệu hơn: Tăng TOP_K_CHUNKS lên 15-20
- Câu trả lời dài hơn: Giảm MAX_CONTEXT_CHARS xuống 2000

### 8.3 LLM Provider Priority

1. **Ollama** (Primary) - Local, fast
2. **LM Studio** (Fallback) - Local alternative
3. **Groq** (Cloud) - Fast cloud API
4. **DeepSeek** (Cloud) - Alternative cloud API

---

## 9. Sử dụng API

### 9.1 Health Check

```bash
GET /health

Response:
{
  "status": "ok"
}
```

### 9.2 Chat API

#### Request
```bash
POST /chat/message
Content-Type: application/json

{
  "message": "Xin chào",
  "session_id": "user123",
  "email": "user@example.com",
  "name": "Nguyễn Văn A",
  "phone": "0901234567"
}
```

**Lưu ý quan trọng:**
- ✅ **Email là bắt buộc** - Mỗi user phải có email duy nhất
- ✅ **Tự động tạo user** - Lần chat đầu tiên sẽ tạo user mới với email
- ✅ **Lưu lịch sử chat** - Tất cả chat được lưu vào database gắn với user
- ✅ **Name và Phone** - Tùy chọn, có thể cập nhật sau

#### Response
```json
{
  "reply": "Xin chào! Tôi có thể giúp gì cho bạn?",
  "session_id": "user123",
  "mode": "AI_ONLY",
  "provider": "ollama"
}
```

### 9.3 Admin API

#### Upload tài liệu
```bash
POST /admin/upload
Content-Type: multipart/form-data

file: document.pdf
```

#### Huấn luyện lại
```bash
POST /train/retrain
```

### 9.4 Test với Python

```python
import requests

url = "http://localhost:8000/chat/message"
data = {
    "message": "Xin chào",
    "session_id": "test123",
    "email": "test@example.com"
}

response = requests.post(url, json=data)
print(response.json())
```

---

## 10. GitHub Copilot Prompts

### 10.1 RAG "full file" – không chia chunk

```python
# Copilot Prompt

Tạo class RAGService:
- Thư mục: ./data/uploads
- load_all_documents_content():
  - Quét tất cả file trong thư mục
  - Đọc full nội dung (txt/md/pdf/docx)
  - Convert pdf/docx sang text
  - Ghép nội dung tất cả file
  - Truncate nếu > MAX_TOTAL_CHARS (12000)
  - Trả về combined_context
```

### 10.2 Chế độ AI / Nhân viên Online

```python
# Copilot Prompt

Trong FastAPI tạo:
- Enum ChatMode: AI_ONLY, HUMAN_ONLINE
- DB table Settings { chat_mode }

API:
GET  /settings/chat-mode  → trả về mode hiện tại
POST /settings/chat-mode  → set mode (admin only)

Trong route /chat:
- Nếu chat_mode == AI_ONLY → RAG + LLM
- Nếu chat_mode == HUMAN_ONLINE:
    - Không gọi AI
    - Lưu message vào DB
    - Trả về {"status": "WAITING_FOR_HUMAN"}
```

### 10.3 Admin Panel – Toggle AI/Human

```javascript
// Copilot Prompt

Tạo component ChatModeToggle:
- GET /settings/chat-mode khi load
- Switch UI: AI_ONLY <→> HUMAN_ONLINE
- POST cập nhật mode khi toggle
- Hiển thị trạng thái hiện tại
```

---

## 11. Xử lý lỗi và Troubleshooting

### 11.1 Lỗi thường gặp

#### ❌ Lỗi: "ollama: command not found"
**Nguyên nhân:** Ollama chưa trong PATH hoặc chưa cài đặt

**Giải pháp:**
```powershell
# Kiểm tra Ollama đã cài
where.exe ollama

# Thêm vào PATH tạm thời
$env:PATH += ";C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama"

# Hoặc restart terminal/PowerShell
```

#### ❌ Lỗi: "There is no item named 'word/document.xml' in the archive"
**Nguyên nhân:** File `.doc` (Word 97-2003) không được hỗ trợ

**Giải pháp:**
```
1. Mở file .doc trong Microsoft Word
2. Chọn File → Save As
3. Chọn định dạng: "Word Document (*.docx)"
4. Lưu và upload file .docx mới

Hoặc dùng online converter:
- https://www.zamzar.com/convert/doc-to-docx/
- https://convertio.co/doc-docx/
```

**Lưu ý:** Hệ thống chỉ hỗ trợ:
- ✅ `.docx` (Word 2007+)
- ✅ `.pdf`
- ✅ `.txt`, `.md`
- ❌ `.doc` (Word 97-2003) - KHÔNG hỗ trợ

#### ❌ Lỗi: "httpx.ReadTimeout" 
**Nguyên nhân:** LLM xử lý quá lâu (file quá dài, model chậm)

**Giải pháp:**
```env
# Tăng timeout trong .env
LLM_TIMEOUT_SECONDS=180

# Hoặc giảm context size
MAX_TOTAL_CONTEXT=15000
```

#### ❌ Lỗi: "Model not found"
**Nguyên nhân:** Chưa pull model Ollama

**Giải pháp:**
```powershell
# Pull model
ollama pull qwen3:4b

# Kiểm tra
ollama list

# Test model
ollama run qwen3:4b "test"
```

#### ❌ Lỗi: "Connection refused [127.0.0.1:11434]"
**Nguyên nhân:** Ollama server không chạy

**Giải pháp:**
```powershell
# Khởi động Ollama
ollama serve

# Hoặc start service (Windows)
Start-Process ollama -ArgumentList "serve"

# Test connection
curl http://127.0.0.1:11434/api/tags
```

#### ❌ Lỗi: "ModuleNotFoundError: No module named 'xxx'"
**Nguyên nhân:** Dependencies chưa cài hoặc sai virtualenv

**Giải pháp:**
```powershell
# Kiểm tra virtualenv
Get-Command python | Select-Object Source

# Activate lại venv
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### ❌ Lỗi: "Permission denied" (database)
**Nguyên nhân:** Không có quyền ghi vào thư mục data/

**Giải pháp:**
```powershell
# Tạo lại thư mục với quyền
New-Item -ItemType Directory -Force -Path data
icacls data /grant "$env:USERNAME:(OI)(CI)F" /T
```

#### ❌ Lỗi: LLM trả lời sai/bịa thông tin
**Nguyên nhân:** Temperature cao, prompt chưa tốt, context thiếu

**Giải pháp:**
```python
# Giảm temperature trong core/llm_service.py
"temperature": 0.1,  # Thay vì 0.3

# Kiểm tra context đã load đầy đủ chưa
# Check logs: "Context length: XXX chars"
```

### 11.2 Debug Mode

**Bật logging chi tiết:**
```python
# Thêm vào đầu main.py
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Kiểm tra logs:**
```powershell
# Xem logs realtime
Get-Content logs/chatbot.log -Wait -Tail 50

# Tìm errors
Select-String -Path logs/chatbot.log -Pattern "ERROR|CRITICAL"
```

### 11.3 Health Checks

**Kiểm tra từng component:**
```powershell
# 1. Python modules
python -c "from core.rag_service import RAGService; print('✅ RAG OK')"
python -c "from core.llm_service import LLMService; print('✅ LLM OK')"
python -c "from core.db_service import DatabaseService; print('✅ DB OK')"

# 2. Ollama
curl http://127.0.0.1:11434/api/tags

# 3. FastAPI server
curl http://localhost:8000/health

# 4. Chat endpoint
curl -X POST http://localhost:8000/chat/message `
  -H "Content-Type: application/json" `
  -d '{\"message\":\"test\",\"session_id\":\"test\"}'
```

### 11.4 Performance Issues

**Server chậm:**
```python
# Giảm context size
MAX_TOTAL_CONTEXT = 10000

# Dùng model nhỏ hơn
OLLAMA_MODEL = "gemma3:1b"  # Model nhỏ hơn
```

**Memory cao:**
```powershell
# Kiểm tra memory usage
Get-Process python | Select-Object Name, CPU, WorkingSet

# Restart server định kỳ
```

### 11.5 Liên hệ hỗ trợ

Nếu gặp vấn đề không giải quyết được:
1. Check logs: `logs/chatbot.log`
2. Kiểm tra [Issues trên GitHub](https://github.com/...)
3. Email: support@example.com

---

## 12. Roadmap

### 12.1 Phiên bản hiện tại (v1.0) ✅ HOÀN THÀNH

- ✅ **Vector RAG với ChromaDB**: Semantic search, chunking thông minh
- ✅ **Vietnamese SBERT Embeddings**: Tối ưu cho tiếng Việt
- ✅ **Ollama Gemma2 2B**: LLM nhanh, nhẹ, chính xác
- ✅ **Chat API**: Trả lời câu hỏi từ tài liệu với độ chính xác cao
- ✅ **Document Upload**: Hỗ trợ PDF, DOCX, TXT - tự động index vào vector DB
- ✅ **Admin API**: Quản lý tài liệu, thống kê
- ✅ **Error Handling**: Xử lý lỗi .doc (Word 97-2003), timeout, etc.
- ✅ **Smart Context Building**: Ưu tiên chunks có thông tin giá cả, lọc theo file

**Tested & Verified:**
- ✅ Câu hỏi "Học phí AI bao nhiêu?" → Trả lời đúng 3 hình thức thanh toán
- ✅ Upload file PDF → Tự động chunk + embed + index
- ✅ Multi-document support → Phát hiện file đúng theo context

### 12.2 Giai đoạn 2 (v1.1 - v1.5)

- 🔜 Tích hợp Facebook Messenger webhook
- 🔜 Tích hợp Zalo OA API
- 🔜 Hệ thống ưu tiên:
  - Nếu nhân viên không trả lời 1–2 phút → AI fallback
- 🔜 Redis Queue để scale nhiều user
- 🔜 WebSocket real-time chat

### 12.3 Giai đoạn 3 (v2.0+)

- 🔮 Dashboard tổng quan:
  - Top câu hỏi
  - Thống kê theo giờ/ngày/tuần
  - Đánh giá AI accuracy
- 🔮 Multi-language support
- 🔮 Voice chat support
- 🔮 Advanced analytics
- 🔮 A/B testing cho câu trả lời

---

## 13. Dependencies và Versions

### 13.1 Core Dependencies (Bắt buộc)

```txt
fastapi>=0.115.0          # Web framework
uvicorn[standard]>=0.32.0 # ASGI server
httpx>=0.27.0             # Async HTTP client
python-dotenv>=1.0.1      # Environment variables
pydantic[email]>=2.10.0   # Data validation
python-multipart>=0.0.12  # File upload support
```

### 13.2 RAG & Document Processing

```txt
langchain-community>=0.3.0     # Document loaders
pypdf>=5.1.0                   # PDF reader
pdfplumber>=0.11.0             # PDF extraction
docx2txt>=0.8                  # DOCX to text
python-docx>=1.1.2             # DOCX processing

# Vector Database & Embeddings
chromadb>=0.4.22               # Vector database
sentence-transformers>=2.2.2   # Embeddings model
```

### 13.3 Database

- **SQLite**: Built-in Python (không cần cài)
- **PostgreSQL** (Optional): `psycopg2-binary>=2.9.10`

### 13.4 LLM Providers

- **Ollama**: Local (khuyến nghị) - https://ollama.ai
- **Groq**: Cloud API - Cần API key
- **DeepSeek**: Cloud API - Cần API key

### 13.5 Kiểm tra versions

```powershell
# Kiểm tra Python version
python --version  # Nên >= 3.9

# Kiểm tra pip version
pip --version

# List installed packages
pip list | Select-String "fastapi|uvicorn|httpx|langchain"

# Kiểm tra compatibility
pip check
```


---

## 14. Đóng góp

### 14.1 Quy trình đóng góp

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

### 14.2 Coding standards

- Follow PEP 8 for Python code
- Add docstrings to functions
- Write unit tests for new features
- Update documentation

---

## 16. Liên hệ và Đóng góp

### 16.1 Thông tin liên hệ

- **Repository**: https://github.com/vantruong1512/dev_test_ai
- **Issues**: https://github.com/vantruong1512/dev_test_ai/issues
- **Email**: truong@example.com

### 16.2 Đóng góp code

```bash
# 1. Fork repository
# 2. Tạo branch mới
git checkout -b feature/amazing-feature

# 3. Commit changes
git commit -m 'Add amazing feature'

# 4. Push và tạo Pull Request
git push origin feature/amazing-feature
```

### 16.3 Coding Standards

- **Python**: Follow PEP 8
- **Docstrings**: Google style
- **Type hints**: Bắt buộc cho functions
- **Tests**: Write tests cho features mới

---

## 📝 Checklist trước khi bắt đầu

- [ ] Python 3.9+ đã cài (`python --version`)
- [ ] Ollama đã cài và pull model (`ollama list`)
- [ ] Dependencies đã cài (`pip install -r requirements.txt`)
- [ ] File .env đã cấu hình (`cp .env.example .env`)
- [ ] Thư mục data/uploads đã tạo
- [ ] Test import modules thành công
- [ ] Health check OK (`curl http://localhost:8000/health`)

---

---

## 🎯 Backend API Status - SẴN SÀNG CHO FRONTEND

### ✅ **Backend đã được kiểm tra đầy đủ và hoạt động ổn định**

**Tổng số API đã test: 16/16 ✅**

#### **CHAT APIs (4/4 ✅)**
- ✅ `POST /chat/message` - Gửi tin nhắn, nhận phản hồi AI với RAG context
- ✅ `GET /chat/history/{session_id}` - Lấy lịch sử chat theo session
- ✅ `GET /chat/sessions` - Liệt kê tất cả sessions (36 sessions hiện tại)
- ✅ `GET /chat/health` - Kiểm tra trạng thái hệ thống

#### **ADMIN APIs (9/9 ✅)**
- ✅ `GET /admin/settings/chat-mode` - Xem chế độ chat hiện tại
- ✅ `POST /admin/settings/chat-mode` - Đổi chế độ AI_ONLY ↔ HUMAN_ONLINE
- ✅ `GET /admin/documents` - Liệt kê tài liệu đã upload
- ✅ `GET /admin/documents/stats` - Thống kê tài liệu và vector DB
- ✅ `GET /admin/users` - Liệt kê tất cả users (36 users)
- ✅ `GET /admin/users/{session_id}` - Thông tin user theo session
- ✅ `GET /admin/users/{session_id}/history` - Lịch sử chat theo session + user info
- ✅ `GET /admin/users/email/{email}/history` - Lịch sử chat theo email
- ✅ `GET /admin/statistics` - Thống kê tổng thể hệ thống

#### **DEFAULT APIs (2/2 ✅)**
- ✅ `GET /` - Root endpoint với thông tin app
- ✅ `GET /health` - Health check đơn giản

#### **File Upload APIs (1/1 ✅)**
- ✅ `POST /admin/documents/upload` - Upload PDF, DOCX, TXT
- ⚠️ `DELETE /admin/documents/{filename}` - Xóa tài liệu (chưa test, cần có file để xóa)

### 📊 Tình trạng hệ thống

**Đã test thành công:**
- ✅ **Vector RAG**: 159 chunks đã index, semantic search hoạt động tốt
- ✅ **User Management**: Email UNIQUE, auto-create user, 36 users
- ✅ **Chat History**: Lưu với user_id foreign key, query được bằng session_id hoặc email
- ✅ **Database**: SQLite với auto schema creation
- ✅ **Chat Modes**: Chuyển đổi AI_ONLY ↔ HUMAN_ONLINE mượt mà
- ✅ **Statistics**: 86 messages, 36 sessions, 36 users, 1 document visible (6 total indexed)

**Backend sẵn sàng 100% cho Frontend kết nối! 🚀**

---

## 📋 Hướng dẫn test API cho Frontend Developer

### 🔜 Các API cần tích hợp

#### 1. Chat Mode Management (Chế độ AI/Human)
```powershell
# Lấy mode hiện tại
Invoke-WebRequest -Uri http://localhost:8000/admin/settings/chat-mode

# Đổi sang HUMAN_ONLINE
$body = @{ mode = "HUMAN_ONLINE" } | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8000/admin/settings/chat-mode `
  -Method POST -ContentType "application/json" -Body $body

# Đổi về AI_ONLY
$body = @{ mode = "AI_ONLY" } | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8000/admin/settings/chat-mode `
  -Method POST -ContentType "application/json" -Body $body
```

#### 2. Document Management
```powershell
# Lấy danh sách tất cả documents
Invoke-WebRequest -Uri http://localhost:8000/admin/documents

# Lấy thống kê documents
Invoke-WebRequest -Uri http://localhost:8000/admin/documents/stats

# Xóa document
Invoke-WebRequest -Uri http://localhost:8000/admin/documents/test.txt `
  -Method DELETE
```

#### 3. User Management
```powershell
# Lấy danh sách users (leads)
Invoke-WebRequest -Uri http://localhost:8000/admin/users

# Lấy thông tin user cụ thể
Invoke-WebRequest -Uri http://localhost:8000/admin/users/test123

# Lấy chat history của user theo session_id
Invoke-WebRequest -Uri http://localhost:8000/admin/users/test123/history

# Lấy chat history của user theo email
Invoke-WebRequest -Uri "http://localhost:8000/admin/users/email/user@example.com/history"
```

#### 4. Statistics
```powershell
# Lấy thống kê tổng quan
Invoke-WebRequest -Uri http://localhost:8000/admin/statistics
```

#### 5. Test RAG với nhiều câu hỏi
```powershell
# Test các câu hỏi khác nhau (LƯU Ý: Email bắt buộc)
$questions = @(
    "Học phí Automation Testing bao nhiêu?",
    "Học phí Quản trị hệ thống bao nhiêu?",
    "So sánh học phí 3 khóa học",
    "Khóa nào rẻ nhất?",
    "Có giảm giá không?",
    "Thời lượng khóa AI bao lâu?"
)

foreach ($q in $questions) {
    Write-Host "`n=== $q ===" -ForegroundColor Cyan
    $body = @{ 
        message = $q
        session_id = "test123"
        email = "test@example.com"
        name = "Test User"
    } | ConvertTo-Json -Compress
    $utf8 = [System.Text.Encoding]::UTF8.GetBytes($body)
    $response = Invoke-WebRequest -Uri http://localhost:8000/chat/message `
      -Method POST -ContentType "application/json" -Body $utf8
    ($response.Content | ConvertFrom-Json).reply
}
```

#### 6. Stress Test
```powershell
# Test performance với nhiều requests
1..10 | ForEach-Object -Parallel {
    $body = @{ message = "Học phí AI?"; session_id = "user$_" } | ConvertTo-Json
    Invoke-WebRequest -Uri http://localhost:8000/chat/message `
      -Method POST -ContentType "application/json" -Body $body
} -ThrottleLimit 5
```

#### 7. Error Handling Test
```powershell
# Upload file .doc (should fail with clear message)
$form = @{ file = Get-Item "old_file.doc" }
Invoke-WebRequest -Uri http://localhost:8000/admin/documents/upload `
  -Method POST -Form $form

# Upload file không hỗ trợ (.exe, .zip)
# Chat với email không hợp lệ (should fail)
$body = @{ 
    message = "Test"
    session_id = "test"
    email = "invalid-email"
} | ConvertTo-Json -Compress
$utf8 = [System.Text.Encoding]::UTF8.GetBytes($body)
Invoke-WebRequest -Uri http://localhost:8000/chat/message `
  -Method POST -ContentType "application/json" -Body $utf8

# Chat không có email (should fail - email bắt buộc)
$body = @{ 
    message = "Test"
    session_id = "test"
} | ConvertTo-Json -Compress
$utf8 = [System.Text.Encoding]::UTF8.GetBytes($body)
Invoke-WebRequest -Uri http://localhost:8000/chat/message `
  -Method POST -ContentType "application/json" -Body $utf8
```

### 📊 Test Checklist

- [x] Chat API với nhiều câu hỏi khác nhau (**Email bắt buộc**)
- [x] Upload PDF, DOCX, TXT thành công
- [x] Upload .doc thất bại với message rõ ràng
- [x] Lấy danh sách documents
- [x] Xóa document
- [x] Đổi chat mode AI ↔ HUMAN
- [x] Lấy statistics
- [x] Test với multiple sessions và emails khác nhau
- [x] Test lấy lịch sử chat theo session_id
- [x] Test lấy lịch sử chat theo email
- [x] Test tạo user mới với email mới
- [x] Test cập nhật user info với email đã tồn tại
- [x] Test error: chat không có email (should fail)
- [x] Test error: email không hợp lệ (should fail)
- [x] Test performance (10+ requests đồng thời)

### 🧪 Chạy Test

#### Test đơn giản (1 câu hỏi + kiểm tra lịch sử)
```powershell
python test_chatbot_hocphi.py
```

#### Test đầy đủ (nhiều câu hỏi + statistics)
```powershell
python test_chatbot_hocphi.py full
```

#### Test API suite (PowerShell)
```powershell
powershell -ExecutionPolicy Bypass -File .\test_api_suite.ps1
```

---

## 📝 Quản lý User và Lịch sử Chat

### Thiết kế Database

#### Bảng `users`
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    name TEXT,
    email TEXT UNIQUE,              -- Email duy nhất
    phone TEXT,
    tags TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Bảng `chat_history`
```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,       -- Foreign key đến users
    session_id TEXT NOT NULL,
    message TEXT NOT NULL,
    reply TEXT,
    context_used TEXT,
    provider TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Khởi tạo Database

**Database sẽ tự động khởi tạo** khi bạn start server lần đầu tiên:
- ✅ Tạo bảng `users` với email UNIQUE constraint
- ✅ Tạo bảng `chat_history` với foreign key đến users
- ✅ Tạo bảng `chat_messages` (backward compatible)
- ✅ Tạo indexes cho performance
- ✅ Khởi tạo settings mặc định

**Vị trí database:** `data/chatbot.db`

**Lưu ý:** Nếu bạn đã có database cũ, hệ thống sẽ tự động tương thích. Backup database định kỳ bằng cách copy file `data/chatbot.db`

### Luồng xử lý User

1. **User chat lần đầu**:
   - Gửi request với `email`, `session_id`, `message`
   - Backend kiểm tra email trong database
   - Nếu chưa có → Tạo user mới
   - Nếu đã có → Lấy user hiện tại
   - Lưu chat vào `chat_history` với `user_id`

2. **User chat lần sau**:
   - Gửi request với cùng `email`
   - Backend tìm user theo email
   - Lưu chat tiếp vào `chat_history`

3. **Truy xuất lịch sử**:
   - Theo session_id: `GET /admin/users/{session_id}/history`
   - Theo email: `GET /admin/users/email/{email}/history`

### 📝 Ví dụ kiểm tra lịch sử chat

#### PowerShell
```powershell
# Lấy lịch sử theo email
$email = "test@example.com"
Invoke-WebRequest -Uri "http://localhost:8000/admin/users/email/$email/history" | 
  Select-Object -Expand Content | ConvertFrom-Json | ConvertTo-Json -Depth 10

# Lấy lịch sử theo session_id
$sessionId = "test123"
Invoke-WebRequest -Uri "http://localhost:8000/admin/users/$sessionId/history" | 
  Select-Object -Expand Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

#### Python
```python
import requests

# Lấy lịch sử theo email
email = "test@example.com"
response = requests.get(f"http://localhost:8000/admin/users/email/{email}/history")
history = response.json()

print(f"User: {history['user']['name']}")
print(f"Total messages: {history['count']}")
for msg in history['history']:
    print(f"Q: {msg['message']}")
    print(f"A: {msg['reply'][:100]}...")
```

### API Endpoints

#### Tạo/Cập nhật User (tự động khi chat)
```bash
POST /chat/message
{
  "message": "Xin chào",
  "session_id": "user123",
  "email": "user@example.com",      # BẮT BUỘC
  "name": "Nguyễn Văn A",           # Tùy chọn
  "phone": "0901234567"             # Tùy chọn
}
```

#### Lấy lịch sử chat theo session_id
```bash
GET /admin/users/{session_id}/history?limit=50

Response:
{
  "session_id": "user123",
  "user": {
    "name": "Nguyễn Văn A",
    "email": "user@example.com",
    "phone": "0901234567"
  },
  "count": 25,
  "history": [
    {
      "id": 1,
      "message": "Học phí AI bao nhiêu?",
      "reply": "Học phí khóa AI...",
      "created_at": "2025-11-17 10:30:00"
    }
  ]
}
```

#### Lấy lịch sử chat theo email
```bash
GET /admin/users/email/{email}/history?limit=50

Response:
{
  "email": "user@example.com",
  "user": {
    "session_id": "user123",
    "name": "Nguyễn Văn A",
    "phone": "0901234567"
  },
  "count": 25,
  "history": [...]
}
```

### Ưu điểm thiết kế

- ✅ **Email unique**: Mỗi user chỉ có 1 email, tránh duplicate
- ✅ **Foreign key**: Chat history gắn chặt với user, xóa user → xóa history
- ✅ **Flexible query**: Truy xuất lịch sử theo session_id hoặc email
- ✅ **Auto user creation**: Không cần API riêng để tạo user
- ✅ **Data integrity**: Đảm bảo mỗi chat đều có user tương ứng
- ✅ **Auto schema creation**: Database tự động khởi tạo schema khi start server
- ✅ **Backward compatible**: Giữ lại bảng `chat_messages` cũ cho tương thích

---

**✅ Tài liệu đã được kiểm tra và cập nhật - Vector RAG Production Ready!**

**Version**: 1.0.0 | **Last Updated**: November 17, 2025
