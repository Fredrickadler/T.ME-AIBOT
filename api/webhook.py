from http.server import BaseHTTPRequestHandler
import json
import requests

TELEGRAM_BOT_TOKEN = "8975706157:AAFsAJfYZdHWUeXK_btpXKvW2j5EjRspQOo"
# توکن رایگان Hugging Face شما مستقیم اینجا قرار گرفت 👇
HF_API_KEY = "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"

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

def get_ai_response(prompt):
    # استفاده از مدل فوق‌العاده قدرتمند ۷۰ میلیاردی لاما ۳ با کیفیت عالی در زبان فارسی
    url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-70B-Instruct/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "meta-llama/Meta-Llama-3-70B-Instruct",
        "messages": [
            {
                "role": "system", 
                "content": "شما یک دستیار هوش مصنوعی هوشمند و مسلط به زبان فارسی هستید. به تمام سوالات با لحنی کاملاً روان، طبیعی و صمیمی پاسخ دهید."
            },
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        result = response.json()
        
        if 'error' in result:
            return f"خطای سرور رایگان: {result['error'] if isinstance(result['error'], str) else result['error'].get('message', 'خطا')}"
            
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
                    reply = "سلام! ربات هوش مصنوعی رایگان و پرقدرت شما فعال شد. 🚀 هر چی می‌خوای بپرس تا به فارسی روان جوابت رو بدم!"
                else:
                    reply = get_ai_response(user_text)
                
                send_telegram_message(chat_id, reply)
                
        except Exception as e:
            print(f"Error: {e}")

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
