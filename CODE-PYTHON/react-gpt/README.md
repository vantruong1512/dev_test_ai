# ChatGPT React App 🤖

Ứng dụng chatbot đơn giản được xây dựng bằng **React**, **Vite**, **TailwindCSS** và **OpenAI API**.

## 🌟 Tính năng

- ✅ Giao diện chat đẹp mắt với TailwindCSS
- ✅ Tích hợp OpenAI GPT-4o-mini
- ✅ Lưu API key vào localStorage (không cần nhập lại)
- ✅ Lưu lịch sử chat
- ✅ Xóa chat history
- ✅ Đổi API key dễ dàng
- ✅ Auto-scroll xuống tin nhắn mới
- ✅ Xử lý lỗi API

## 📋 Yêu cầu

- **Node.js** phiên bản 18+ (khuyến nghị Node 20+)
- **npm** hoặc **yarn**
- **OpenAI API Key** (lấy tại [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys))

## 🚀 Cài đặt và chạy

### Bước 1: Di chuyển vào thư mục dự án

```powershell
Set-Location 'd:\AI_for_code_Copilot\dev_test_ai\CODE-PYTHON\react-gpt'
```

### Bước 2: Cài đặt dependencies

```powershell
npm install
```

### Bước 3: Chạy ứng dụng

```powershell
npm run dev
```

Ứng dụng sẽ chạy tại: **http://localhost:5173**

## 🔑 Cấu hình API Key

1. Khi chạy lần đầu, ứng dụng sẽ yêu cầu bạn nhập **OpenAI API Key**
2. Lấy API key tại: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
3. Nhập key vào form và nhấn "Lưu API Key"
4. Key sẽ được lưu vào localStorage, không cần nhập lại lần sau

⚠️ **CẢNH BÁO BẢO MẬT:**
- **KHÔNG BAO GIỜ** commit API key vào Git
- **KHÔNG BAO GIỜ** deploy app với API key hardcode
- Nên sử dụng backend để xử lý API key an toàn hơn
- Key lưu trong localStorage chỉ dùng cho môi trường dev/test

## 📁 Cấu trúc dự án

```
react-gpt/
├── index.html              # HTML chính (có TailwindCSS CDN)
├── package.json            # Dependencies và scripts
├── vite.config.js          # Cấu hình Vite
├── .gitignore              # Ignore node_modules, dist
├── README.md               # File này
└── src/
    ├── main.jsx            # Entry point React
    └── App.jsx             # Component chatbot chính
```

## 🎨 Công nghệ sử dụng

- **React 18** - UI framework
- **Vite** - Build tool nhanh
- **TailwindCSS** - CSS framework (via CDN)
- **OpenAI SDK** - Gọi API ChatGPT
- **LocalStorage** - Lưu API key và history

## 📝 Sử dụng

1. Nhập API key lần đầu
2. Gõ tin nhắn vào ô input và nhấn "Gửi tin nhắn" hoặc Enter
3. Bot sẽ trả lời sau vài giây
4. Sử dụng nút "Xóa Chat" để xóa lịch sử
5. Sử dụng nút "Đổi API Key" để thay đổi key

## 🛠️ Build cho production

```powershell
npm run build
```

Build output sẽ nằm trong thư mục `dist/`.

Xem preview:
```powershell
npm run preview
```

## 🐛 Xử lý lỗi thường gặp

### Lỗi: "Module not found: openai"
```powershell
npm install openai
```

### Lỗi: "Invalid API key"
- Kiểm tra lại API key tại [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Xóa key cũ và nhập key mới

### Lỗi: "Network error"
- Kiểm tra kết nối mạng
- Kiểm tra firewall/proxy

## 📚 Tài liệu tham khảo

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [TailwindCSS Documentation](https://tailwindcss.com)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [OpenAI Node.js SDK](https://www.npmjs.com/package/openai)

## 📝 Bài tập mở rộng

1. ✅ **Đã hoàn thành:** Yêu cầu người dùng nhập API key thay vì hardcode
2. ✅ **Đã hoàn thành:** Lưu API key vào localStorage
3. ✅ **Đã hoàn thành:** Chức năng clear chat history
4. ⭐ **Bài tập thêm:**
   - Thêm streaming response (hiển thị từng chữ)
   - Lưu nhiều cuộc hội thoại khác nhau
   - Thêm chức năng export chat history
   - Tích hợp backend API
   - Dark mode toggle

## 📄 License

MIT License - Tự do sử dụng cho mục đích học tập và phát triển.

---

**Tạo bởi:** Hướng dẫn từ HocCodeAI  
**Ngày tạo:** 2025-10-29
