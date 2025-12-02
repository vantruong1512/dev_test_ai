# Chatbot AI RAG - Frontend

Frontend cho hệ thống Chatbot AI RAG với React + Vite + TailwindCSS.

## Cài đặt

```bash
# Copy file .env
cp .env.example .env

# Cài đặt dependencies
npm install

# Chạy dev server
npm run dev

# Build production
npm run build

# Preview production build
npm run preview
```

## Cấu trúc thư mục

```
src/
├── api/              # API client (axios, chat, admin, documents)
├── components/       # UI components
├── pages/           # Page components (widget, admin)
├── routes/          # Router configuration
├── store/           # Zustand state management
├── styles/          # Tailwind CSS
└── utils/           # Utilities (session, validators)
```

## Scripts

- `npm run dev` - Chạy development server
- `npm run build` - Build production
- `npm run preview` - Preview production build
- `npm run lint` - Chạy ESLint

## Công nghệ

- React 18
- Vite
- TailwindCSS
- Zustand (state management)
- React Router v6
- Axios
- date-fns
- Lucide React (icons)

## Tính năng

### Widget (Public)
- Form lead capture (email, phone, name)
- Chat interface với AI
- Lưu session_id vào localStorage
- Hiển thị lịch sử chat
- Hỗ trợ chế độ AI_ONLY / HUMAN_ONLINE

### Admin
- Dashboard tổng quan
- Quản lý users/leads
- Xem chi tiết user và lịch sử chat
- Quản lý documents (upload, delete, stats)
- Thống kê hệ thống
- Toggle chat mode (AI ↔ Human)

## Môi trường

Tạo file `.env` từ `.env.example`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WIDGET_TITLE=Chatbot AI
VITE_BRAND_PRIMARY=#1e293b
```

## Development

Đảm bảo backend đang chạy tại `http://localhost:8000` trước khi chạy frontend.

## Build & Deploy

```bash
# Build
npm run build

# Output: dist/

# Deploy tĩnh (Nginx, Vercel, Netlify)
```

Nginx config:
```nginx
location / {
  try_files $uri /index.html;
}
```
