import gradio as gr
import random

def chat_logic(message, chat_history):
    '''
    message: Tin nhắn của user (string)
    chat_history: Lịch sử chat (list gồm nhiều tin nhắn, mỗi tin nhắn là một list [message, bot_message])
    '''
    bot_message = random.choice(["Chào bạn!", "Bạn cần giúp gì?", "Tôi không hiểu bạn nói gì?"])

    chat_history.append([message, bot_message])
    return "", chat_history

with gr.Blocks() as demo:
    gr.Markdown("# Chatbot bằng ChatGPT")
    message = gr.Textbox(label="Nhập tin nhắn của bạn:")
    chatbot = gr.Chatbot(label="Chat Bot siêu thông minh")

    # Khi user nhập tin nhắn, gọi hàm chat_logic
    message.submit(chat_logic, [message, chatbot], [message, chatbot])

demo.launch()