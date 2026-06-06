from http.server import BaseHTTPRequestHandler
import json
import requests

TELEGRAM_BOT_TOKEN = "8975706157:AAFsAJfYZdHWUeXK_btpXKvW2j5EjRspQOo"
# کلید رسمی چت‌جی‌پتی شما مستقیم اینجا قرار گرفت 👇
OPENAI_API_KEY = "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"

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

def get_chatgpt_response(prompt):
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system", 
                "content": "شما ربات هوش مصنوعی رسمی ChatGPT مسلط به زبان فارسی هستید. به تمام سوالات با لحنی کاملاً طبیعی، روان و صمیمی پاسخ دهید."
            },
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        result = response.json()
        
        if 'error' in result:
            return f"خطای اپن‌آی‌ای: {result['error'].get('message', 'خطای ناشناخته')}"
            
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
                    reply = "سلام! ربات چت‌جی‌پتی اصلی شما روی تلگرام با موفقیت فعال شد. 🦾 هر چیزی می‌خوای بپرس تا با کیفیت درجه‌یک جوابت رو بدم!"
                else:
                    reply = get_chatgpt_response(user_text)
                
                send_telegram_message(chat_id, reply)
                
        except Exception as e:
            print(f"Error: {e}")

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
