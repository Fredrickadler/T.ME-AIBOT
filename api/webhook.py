from http.server import BaseHTTPRequestHandler
import json
import requests

TELEGRAM_BOT_TOKEN = "8975706157:AAFsAJfYZdHWUeXK_btpXKvW2j5EjRspQOo"
# کلید جدیدی که از سایت DeepInfra گرفتی رو بذار اینجا 👇
DEEPINFRA_API_KEY = "اینجا_ای_پی_ای_کی_دیپ_اینفرا_رو_بذار"

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

def get_ai_response(prompt):
    url = "https://api.deepinfra.com/v1/openai/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {DEEPINFRA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # استفاده از مدل فوق‌العاده قوی ۷۰ میلیاردی با پشتیبانی عالی از زبان فارسی
    payload = {
        "model": "meta-llama/Meta-Llama-3-70B-Instruct",
        "messages": [
            {
                "role": "system", 
                "content": "شما یک دستیار هوش مصنوعی بسیار هوشمند، مهربان و مسلط به زبان فارسی هستید. تمام پاسخ‌های خود را به زبان فارسی روان، طبیعی و بدون غلط املایی بنویسید."
            },
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        result = response.json()
        
        if 'error' in result:
            return f"خطای سرور: {result['error'].get('message', 'خطای ناشناخته')}"
            
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
                    reply = "سلام! من ربات هوش مصنوعی جدید تو هستم. حالا با خیال راحت هر چی می‌خوای به فارسی روان بنویس تا جوابت رو بدم! 🤖🌸"
                else:
                    reply = get_ai_response(user_text)
                
                send_telegram_message(chat_id, reply)
                
        except Exception as e:
            print(f"Error: {e}")

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
