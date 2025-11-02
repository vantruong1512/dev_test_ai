# chatbot.py
import os
from openai import OpenAI

# ✅ Kết nối đến LM Studio Local server
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="not-needed"  # LM Studio không yêu cầu API key
)

# Lưu lịch sử hội thoại toàn cục
messages = [
    {"role": "system", "content": "Bạn là một trợ lý AI thân thiện, nói ngắn gọn và dễ hiểu."}
]

def ask_bot(user_input):
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="google/gemma-3n-e4b",
        messages=messages,
        max_tokens=800
    )

    answer = response.choices[0].message.content
    messages.append({"role": "assistant", "content": answer})
    return answer
