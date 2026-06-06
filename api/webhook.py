from http.server import BaseHTTPRequestHandler
import json
import requests
import urllib.parse

TELEGRAM_BOT_TOKEN = "8975706157:AAFsAJfYZdHWUeXK_btpXKvW2j5EjRspQOo"

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

def get_free_ai_response(prompt):
    # استفاده از سیستم رایگان، بدون کلید و فوق‌العاده پایدار Pollinations
    # یک سیستم پروکسی برای هدایت متن به مدل‌های پیشرفته هوش مصنوعی با زبان فارسی روان
    system_prompt = "شما یک دستیار هوش مصنوعی هوشمند و مسلط به زبان فارسی هستید. به تمام سوالات با لحنی کاملاً روان، طبیعی و صمیمی پاسخ دهید."
    
    # ترکیب پرامپت سیستمی و متن کاربر برای بهترین بازدهی
    full_prompt = f"{system_prompt}\n\nکاربر: {prompt}"
    encoded_prompt = urllib.parse.quote(full_prompt)
    
    # استفاده از مدل باکیفیت و باز openai (بدون تحریم و کاملاً رایگان)
    url = f"https://text.pollinations.ai/{encoded_prompt}?model=openai"
    
    try:
        response = requests.get(url, timeout=25)
        if response.status_code == 200:
            return response.text
        else:
            return f"خطای سرور واسط (کد {response.status_code}): لطفا دوباره تلاش کنید."
    except Exception as e:
        return f"خطا در سیستم پشتیبان: {str(e)}"

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
                    reply = "سلام! ربات هوش مصنوعی رایگان و بدون تحریم شما فعال شد. 🚀 بدون هیچ مشکلی هر چی می‌خوای بپرس تا به فارسی روان جوابت رو بدم!"
                else:
                    reply = get_free_ai_response(user_text)
                
                send_telegram_message(chat_id, reply)
                
        except Exception as e:
            print(f"Error: {e}")

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
