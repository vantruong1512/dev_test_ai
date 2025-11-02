# Chatbot AI with Image Generation

Một dự án chatbot thông minh sử dụng ChatGPT API kết hợp với khả năng tạo hình ảnh bằng Diffusion Pipeline.

## Tính năng

- 💬 Chat với AI sử dụng GPT-4o-mini
- 🎨 Tự động tạo hình ảnh dựa trên yêu cầu
- 🌐 Giao diện web thân thiện với Gradio
- 🚀 Hỗ trợ GPU (CUDA, MPS) và CPU

## Yêu cầu

- Python 3.8+
- CUDA 11.8+ (nếu sử dụng GPU NVIDIA)
- 6GB+ VRAM (khuyến nghị cho GPU)

## Cài đặt

1. Clone dự án:
```bash
git clone <your-repo-url>
cd calling_funcion_ai
```

2. Tạo virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

4. Cấu hình API Key:
   - Mở file `config.py`
   - Thay `sk-proj-XXX` bằng API key từ [OpenAI Platform](https://platform.openai.com/api-keys)

## Sử dụng

Chạy ứng dụng:
```bash
python funcion_calling.py
```

Ứng dụng sẽ chạy tại `http://localhost:7860`

## Cách hoạt động

1. **Chat Input**: Nhập tin nhắn của bạn
2. **AI Processing**: ChatGPT xử lý tin nhắn
3. **Image Generation**: Nếu cần vẽ hình, bot sẽ gọi hàm `generate_image()`
4. **Display**: Hình ảnh được hiển thị trong chat

## Cấu trúc dự án

```
calling_funcion_ai/
├── funcion_calling.py      # File chính của ứng dụng
├── config.py               # Cấu hình ứng dụng
├── requirements.txt        # Dependencies
└── README.md              # File này
```

## Lưu ý

- ⚠️ **API Key**: Không commit API key lên GitHub. Sử dụng environment variables thay vào đó
- 💰 **Chi phí**: Sử dụng OpenAI API sẽ tính phí. Theo dõi sử dụng của bạn
- 🖼️ **Hình ảnh**: Hình ảnh được lưu dưới tên `image_<timestamp>.png`

## Troubleshooting

### Lỗi "Import could not be resolved"
- Đảm bảo virtual environment được activate
- Chạy `pip install -r requirements.txt`

### Lỗi CUDA
- Cài đặt CUDA 11.8+ từ NVIDIA website
- Hoặc sử dụng CPU bằng cách để device = "cpu"

### Lỗi API Key
- Kiểm tra API key từ https://platform.openai.com/api-keys
- Đảm bảo không có khoảng trắng thừa

## Tác giả

Được phát triển bởi AI Copilot

## License

MIT
