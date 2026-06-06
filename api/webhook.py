from http.server import BaseHTTPRequestHandler
import json
import requests

TELEGRAM_BOT_TOKEN = "8975706157:AAFsAJfYZdHWUeXK_btpXKvW2j5EjRspQOo"

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

def get_free_ai_response(prompt):
    # استفاده از ای‌پ‌آی لایه باز و پایدار DuckDuckGo AI Hub بدون محدودیت رایج
    url = "https://nexra.aryahcr.cc/api/chat/duckduckgo"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "model": "llama-3", # مدل فوق‌العاده هوشمند
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=25)
        
        # هندل کردن پاسخ‌های مختلف سرور واسط
        if response.status_code == 200:
            result = response.json()
            # استخراج متن پاسخ از ساختار جیسون نکسرا
            if 'gpt' in result:
                return result['gpt']
            elif 'id' in result: # ساختار جایگزین
                return result.get('text', 'پاسخی دریافت نشد.')
            else:
                return response.text
        else:
            return f"خطای موقت سیستم (کد {response.status_code})، لطفاً یک بار دیگر پیام بفرستید."
            
    except Exception as e:
        return f"خطا در پردازش اطلاعات: {str(e)}"

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
                    reply = "سلام! ربات هوش مصنوعی جدید، رایگان و بدون محدودیت شما فعال شد. 🚀 هر چه می‌خواهی بپرس تا پاسخ دهم!"
                else:
                    reply = get_free_ai_response(user_text)
                
                send_telegram_message(chat_id, reply)
                
        except Exception as e:
            print(f"Error: {e}")

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
