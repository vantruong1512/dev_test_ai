# Hướng dẫn chạy Chatbot AI + Image Generator với LM Studio

## 📋 Yêu cầu
- Python 3.8+
- LM Studio chạy trên `http://127.0.0.1:1234`
- GPU (khuyến nghị) hoặc CPU

## 🔧 Bước 1: Cài đặt LM Studio

1. Tải LM Studio từ [https://lmstudio.ai/](https://lmstudio.ai/)
2. Mở LM Studio
3. Tìm kiếm model `google/gemma-3n-e4b` hoặc model khác
4. Download model
5. Chọn "Local Server" tab
6. Chọn model và click "Start Server"
7. Xác nhận server chạy tại `http://127.0.0.1:1234`

## 📦 Bước 2: Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

Hoặc cài từng cái:
```bash
pip install gradio openai pillow diffusers torchvision torch accelerate pydantic
```

## 🚀 Bước 3: Chạy ứng dụng

```bash
python app.py
```

## 📝 Ghi chú

- **LM Studio URL**: `http://127.0.0.1:1234/v1`
- **API Key**: Không cần (LM Studio chạy local)
- **Model**: Gemma-3n (hoặc model khác được load trong LM Studio)
- **Image Generation**: Sử dụng Stable Diffusion v5

## ⚠️ Lỗi thường gặp

### "Connection refused"
- Kiểm tra LM Studio đang chạy
- Đảm bảo server local đang hoạt động trên port 1234

### "Model not found"
- Tải model từ LM Studio model library
- Khởi động server trong LM Studio

### Memory Error (CUDA/GPU)
- Giảm `num_inference_steps` trong `generate_image()` function
- Sử dụng device khác (CPU/MPS)

## 💡 Tùy chỉnh

### Đổi model trong LM Studio
1. Mở LM Studio
2. Chọn model khác từ "Local Server"
3. Click "Start Server"

### Đổi prompt cho image generation
Sửa trong hàm `generate_image()`:
```python
negative_prompt="ugly, deformed, disfigured, poor details, bad anatomy, low quality, worst quality"
```

### Đổi số bước inference
```python
num_inference_steps=30  # Tăng để ảnh đẹp hơn, nhưng chậm hơn
```
