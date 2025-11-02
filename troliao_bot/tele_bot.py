import os
import time
import logging
import json
from dotenv import load_dotenv
import requests

# === TELEGRAM BOT POLLING ===
# Bot simple sử dụng polling (getUpdates) - tránh lỗi Updater
# Hỗ trợ gọi LM Studio (OpenAI-compatible) hoặc echo messages

# Load biến môi trường từ .env
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_API_BASE = os.getenv('OPENAI_API_BASE')  # e.g. http://127.0.0.1:1234
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
MODEL_NAME = os.getenv('OPENAI_MODEL', 'gemma-3n-e4b')

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


# === Gửi tin nhắn tới user ===     
def send_message(chat_id: int, text: str):
    try:
        r = requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text})
        r.raise_for_status()
    except Exception as e:
        logging.exception("Failed to send message to %s: %s", chat_id, e)


# === Gọi LM Studio (OpenAI-compatible API) ===
# Nếu OPENAI_API_BASE không cấu hình, trả về thông báo lỗi
def call_lm(prompt: str) -> str:
    if not OPENAI_API_BASE:
        return "ERROR: LM not configured."
    url = OPENAI_API_BASE.rstrip('/') + '/v1/chat/completions'
    headers = {"Content-Type": "application/json"}
    if OPENAI_API_KEY:
        headers['Authorization'] = f"Bearer {OPENAI_API_KEY}"
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512,
        "temperature": 0.7,
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # standard OpenAI-compatible shape
        if isinstance(data, dict) and data.get('choices'):
            choice = data['choices'][0]
            if isinstance(choice, dict):
                if 'message' in choice and isinstance(choice['message'], dict) and 'content' in choice['message']:
                    return choice['message']['content'].strip()
                if 'text' in choice:
                    return choice['text'].strip()
        return json.dumps(data)[:1000]
    except Exception as e:
        logging.exception('LM call failed')
        return f"ERROR contacting LM: {e}"


# === Kiểm tra token Telegram hợp lệ ===
def check_token():
    try:
        r = requests.post(f"{TELEGRAM_API}/getMe", timeout=10)
        r.raise_for_status()
        data = r.json()
        if not data.get('ok'):
            logging.error('Telegram getMe not ok: %s', data)
            return None
        return data.get('result', {})
    except Exception as e:
        logging.exception('Failed to call getMe')
        return None


# === Vòng lặp polling chính ===
# Lấy updates từ Telegram API theo định kỳ
def main():
    if not BOT_TOKEN:
        print('ERROR: BOT_TOKEN missing in .env')
        return

    info = check_token()
    if not info:
        print('ERROR: token invalid or cannot reach Telegram API')
        return

    logging.info('Bot running as @%s (id=%s)', info.get('username'), info.get('id'))

    offset = None
    backoff = 1
    while True:
        try:
            params = {"timeout": 30}
            if offset:
                params['offset'] = offset
            resp = requests.get(f"{TELEGRAM_API}/getUpdates", params=params, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            if not data.get('ok'):
                logging.error('getUpdates returned not ok: %s', data)
                time.sleep(2)
                continue
            updates = data.get('result', [])
            if updates:
                for upd in updates:
                    offset = upd['update_id'] + 1
                    # handle only messages with text
                    msg = upd.get('message') or upd.get('edited_message')
                    if not msg:
                        continue
                    chat = msg.get('chat')
                    if not chat:
                        continue
                    chat_id = chat.get('id')
                    text = msg.get('text')
                    if not text:
                        continue
                    logging.info('Received message from %s: %s', chat_id, text)
                    if text.strip().lower().startswith('/start'):
                        send_message(chat_id, 'Mình là bot, bạn có câu hỏi gì không!')
                        continue
                    # if LM configured, call it, otherwise echo
                    if OPENAI_API_BASE:
                        reply = call_lm(text)
                    else:
                        reply = f"Đã nhận: {text}"
                    send_message(chat_id, reply)
            backoff = 1
        except requests.exceptions.ReadTimeout:
            # normal long-poll timeout
            continue
        except Exception as e:
            logging.exception('Polling loop error')
            time.sleep(backoff)
            backoff = min(60, backoff * 2)


if __name__ == '__main__':
    main()