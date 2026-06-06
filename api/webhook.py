from http.server import BaseHTTPRequestHandler
import json
import requests

# این تابع پاسخ رو با متد POST به تلگرام می‌فرسته
def send_telegram_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

# این تابع پیام رو به هوش مصنوعی Gemini می‌فرسته
def get_gemini_response(api_key, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        # استخراج متن پاسخ از ساختار جیسون جمینای
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return "شرمنده، یه مشکلی توی پردازش هوش مصنوعی پیش اومد."

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            update = json.loads(post_data.decode('utf-8'))
            
            # بررسی اینکه آیا پیام متنی فرستاده شده یا نه
            if "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                user_text = update["message"]["text"]
                
                # توکن‌ها رو از محیط وی‌ان‌وی ورسل می‌خونیم (امن‌تره)
                # یا می‌تونی موقتاً مستقیم همینجا جایگزین کنی
                import os
                TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "اینجا_توکن_تلگرام")
                GEMINI_KEY = os.environ.get("GEMINI_KEY", "اینجا_ای_پی_ای_جمینای")
                
                if user_text == "/start":
                    reply = "سلام! من ربات هوش مصنوعی تو هستم روی ورسل. هر چی بخوای بنویس تا جواب بدم. 🚀"
                else:
                    reply = get_gemini_response(GEMINI_KEY, user_text)
                
                send_telegram_message(TELEGRAM_TOKEN, chat_id, reply)
                
        except Exception as e:
            print(f"Error: {e}")

        # اعلام وضعیت ۲۰۰ به تلگرام که بفهمه پیام رسیده
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
