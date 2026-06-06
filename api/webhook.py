from http.server import BaseHTTPRequestHandler
import json
import requests

TELEGRAM_BOT_TOKEN = "8975706157:AAFsAJfYZdHWUeXK_btpXKvW2j5EjRspQOo"
GEMINI_API_KEY = "AIzaSyBEubFM7eV6cwK3uuNKMR2d6_lFFzmgfoM"

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

def get_gemini_response(prompt):
    # استفاده از نسخه پایدارتر API گوگل
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # اضافه کردن User-Agent برای اینکه سرور ورسل شبیه مرورگر به نظر برسه و بلاک نشه
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        result = response.json()
        
        # اگر گوگل ارور فرستاده باشه اینجا مشخص میشه
        if 'error' in result:
            return f"خطای گوگل: {result['error'].get('message', 'خطای ناشناخته')}"
            
        return result['candidates'][0]['content']['parts'][0]['text']
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
                    reply = "سلام! من ربات هوش مصنوعی تو هستم روی ورسل. هر چی بخوای بنویس تا جواب بدم. 🚀"
                else:
                    reply = get_gemini_response(user_text)
                
                send_telegram_message(chat_id, reply)
                
        except Exception as e:
            print(f"Error: {e}")

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
