from http.server import BaseHTTPRequestHandler
import json
import requests

TELEGRAM_BOT_TOKEN = "8975706157:AAFsAJfYZdHWUeXK_btpXKvW2j5EjRspQOo"
GROQ_API_KEY = "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"

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

def get_ai_response(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # استفاده از مدل جدید و فعال llama-3.1-8b-instant
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Always reply in the same language the user speaks to you."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        result = response.json()
        
        if 'error' in result:
            return f"خطای سرور هوش مصنوعی: {result['error'].get('message', 'خطای ناشناخته')}"
            
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"خطا در ارتباط: {str(e)}"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            update = json.loads(post_data.decode('utf-8'))
            
            if "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                user_text = update["message"]["text"]
                
                if user_text == "/start":
                    reply = "سلام! من ربات هوش مصنوعی تو هستم روی ورسل. هر چی بخوای بنویس تا با سرعت نور جواب بدم! ⚡🚀"
                else:
                    reply = get_ai_response(user_text)
                
                send_telegram_message(chat_id, reply)
                
        except Exception as e:
            print(f"Error: {e}")

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
