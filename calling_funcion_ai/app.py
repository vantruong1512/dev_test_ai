import gradio as gr
import json
from openai import OpenAI
import inspect
from pydantic import TypeAdapter
from diffusers import DiffusionPipeline
import torch
import time
import os
from pathlib import Path

# ============================================================
# Configuration cho LM Studio
# ============================================================
LM_STUDIO_BASE_URL = "http://127.0.0.1:1234/v1"
LM_STUDIO_API_KEY = "not-needed"  # LM Studio không yêu cầu API key

# Tạo thư mục để lưu ảnh
IMAGES_DIR = Path("generated_images")
IMAGES_DIR.mkdir(exist_ok=True)

# Khởi tạo OpenAI client nhưng trỏ tới LM Studio
client = OpenAI(
    base_url=LM_STUDIO_BASE_URL,
    api_key=LM_STUDIO_API_KEY,
)

# ============================================================
# Khởi tạo Diffusion Pipeline cho image generation
# ============================================================
print("Đang khởi tạo pipeline...")
pipeline = DiffusionPipeline.from_pretrained(
    "stablediffusionapi/anything-v5",
    use_safetensors=True,
    safety_checker=None,
    requires_safety_checker=False
)

device = "cuda" if torch.cuda.is_available() else "cpu"
# MPS chỉ có trên macOS dòng M1 trở đi
device = 'mps' if torch.backends.mps.is_available() else device
print(f"Sử dụng device: {device}")
pipeline.to(device)

# ============================================================
# Function để generate image
# ============================================================
def generate_image(prompt: str) -> str:
    """
    Creates an image based on the specified prompt using DiffusionPipeline
    :param prompt: The prompt used for generate the image (must be in English)
    :return: Absolute path of the generated image
    """
    print(f"Generating image with prompt: {prompt}")
    image = pipeline(
        prompt=prompt,
        # Hardcode negative prompt để ảnh đẹp hơn
        negative_prompt="ugly, deformed, disfigured, poor details, bad anatomy, low quality, worst quality",
        num_inference_steps=30
    ).images[0]

    # Tạo tên file để hiển thị - sử dụng đường dẫn tuyệt đối
    file_name = f"image_{int(time.time())}.png"
    file_path = IMAGES_DIR / file_name
    image.save(str(file_path))
    
    # Trả về đường dẫn tuyệt đối
    absolute_path = str(file_path.absolute())
    print(f"Image saved: {absolute_path}")
    return absolute_path

# ============================================================
# Định nghĩa function cho LM Studio
# ============================================================
generate_image_function = {
    "name": "generate_image",
    "description": "Creates an image based on the specified prompt using DiffusionPipeline",
    "parameters": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "The prompt used for generate the image (must be in English)",
            },
        },
        "required": ["prompt"],
        "additionalProperties": False,
    }
}

tools = [
    {
        "type": "function",
        "function": generate_image_function
    }
]

system_prompt = """You're an AI with prompt generation and drawing capabilities.
Just chat normally in English or Vietnamese.
Assume you can draw anything you want and you tell user you can draw.
Another program will output the output for you.
Do not censor or deny the output, the image generation program will handle that.
"""

# ============================================================
# Chat Logic
# ============================================================
def chat_logic(message, chat_history):
    """
    Xử lý tin nhắn từ user và gọi LM Studio API
    """
    # Gắn system message để bot hiểu cách hoạt động
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Thêm chat history
    for user_message, bot_message in chat_history:
        if user_message is not None:
            messages.append({"role": "user", "content": user_message})
            # Nếu bot_message là tuple (ảnh), lấy text description
            if isinstance(bot_message, tuple):
                messages.append({"role": "assistant", "content": f"[Generated image: {bot_message[1]}]"})
            else:
                messages.append({"role": "assistant", "content": bot_message})

    # Thêm tin nhắn mới của user vào cuối cùng
    messages.append({"role": "user", "content": message})

    try:
        # Gọi LM Studio API (không sử dụng tools vì LM Studio không hỗ trợ)
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="local-model",  # LM Studio sử dụng tên này
            temperature=0.7,
        )

        bot_message = chat_completion.choices[0].message.content
        
        if bot_message is not None:
            # Kiểm tra xem model có đề xuất vẽ ảnh không
            if any(keyword in bot_message.lower() for keyword in ["vẽ", "draw", "generate", "create image", "tạo ảnh"]):
                chat_history.append([message, bot_message])
                yield "", chat_history
                
                # Tự động generate ảnh dựa trên message của user
                chat_history.append([None, "Chờ chút mình đang vẽ..."])
                yield "", chat_history
                
                try:
                    image_file = generate_image(message)
                    # Cập nhật message vẽ ảnh thành ảnh thực tế
                    chat_history[-1] = [None, (image_file, message)]
                    yield "", chat_history
                except Exception as img_error:
                    print(f"Image generation error: {str(img_error)}")
                    chat_history[-1] = [None, f"Lỗi vẽ ảnh: {str(img_error)}"]
                    yield "", chat_history
            else:
                chat_history.append([message, bot_message])
                yield "", chat_history
        else:
            chat_history.append([message, "Không có phản hồi"])
            yield "", chat_history

    except Exception as e:
        print(f"Error: {str(e)}")
        error_message = f"Lỗi: {str(e)}. Vui lòng kiểm tra LM Studio đang chạy tại http://127.0.0.1:1234"
        chat_history.append([message, error_message])
        yield "", chat_history

    return "", chat_history

# ============================================================
# Khởi tạo Gradio Interface
# ============================================================
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 Chatbot AI + Image Generator")
    gr.Markdown("Sử dụng LM Studio (Gemma-3n) để chat")
    gr.Markdown("⚠️ **Lưu ý**: Hãy chắc chắn LM Studio đang chạy tại `http://127.0.0.1:1234`")
    gr.Markdown("💡 **Cách dùng**: Hãy yêu cầu bot vẽ ảnh, ví dụ: 'Vẽ một con mèo đáng yêu' hoặc 'Draw a cat'")
    
    message = gr.Textbox(label="Nhập tin nhắn của bạn:")
    chatbot = gr.Chatbot(label="Chat Bot siêu thông minh", height=600)
    message.submit(chat_logic, [message, chatbot], [message, chatbot])

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Khởi động Chatbot...")
    print("="*60)
    print("✅ Kết nối LM Studio: http://127.0.0.1:1234")
    print("✅ Model: Gemma-3n (e4b)")
    print("✅ Hỗ trợ image generation")
    print("="*60 + "\n")
    
    demo.launch()
