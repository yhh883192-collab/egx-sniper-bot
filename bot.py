import os
import requests
import pandas as pd
import yfinance as yf

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

WATCHLIST = ["COMI.CA", "HRHO.CA", "HELI.CA", "MNHD.CA", "EMFD.CA", "ABUK.CA"]

def fetch_market_data():
    print("جاري جلب بيانات الأسهم الحالية...")
    data_summary = ""
    for ticker in WATCHLIST:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="5d", interval="15m")
            if not df.empty:
                current_price = df['Close'].iloc[-1]
                prev_price = df['Close'].iloc[-2]
                change = ((current_price - prev_price) / prev_price) * 100
                volume = df['Volume'].iloc[-1]
                
                data_summary += f"السهم: {ticker} | السعر: {current_price:.2f} | التغير: {change:.2f}% | الفوليوم: {volume}\n"
        except Exception as e:
            print(f"خطأ في سحب بيانات {ticker}: {e}")
    return data_summary

def analyze_with_three_personas(market_data):
    print("الشخصيات الثلاثة (القناص، البروفسور، المحلل) يبدأون النقاش...")
    
    prompt = f"""
    أنت نظام ذكاء اصطناعي يتكون من 3 شخصيات استثمارية محترفة للمضاربة السريعة في البورصة المصرية:
    1. **القناص (Sniper):** يركز على الزخم، التغير السريع في الأسعار، وحجم التداول (Volume).
    2. **البروفسور (Professor):** يركز على تحليل السيولة اللحظية ودفتر الأوامر والمنطق الحسابي للصفقة.
    3. **المحلل (Analyst):** يركز على الاتجاه العام والسياق الإخباري والقطاعي.
    
    إليك بيانات الأسهم الحالية المستخرجة من السوق:
    {market_data}
    
    المطلوب:
    قم بعمل "جلسة نقاش" سريعة بين الشخصيات الثلاثة على أفضل سهم مرشح للمضاربة الآن.
    هل اتفق الثلاثة على فرصة شراء حقيقية؟ ولماذا اختلفوا أو اتفقوا؟
    وفي النهاية، أعطنا التوصية النهائية بوضوح: (شراء مؤكد / مراقبة / امتناع) مع تحديد السهم البديل لو وجد.
    اجعل الإجابة باللغة العربية، منظمة، ومباشرة ومناسبة لتنبيه سريع على التيليجرام.
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        try:
            return result['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            return "خطأ في قراءة رد الذكاء الاصطناعي."
    else:
        return f"فشل الاتصال بـ API: {response.text}"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    data = fetch_market_data()
    if data:
        analysis_result = analyze_with_three_personas(data)
        final_message = f"🚨 **تقرير بوت المضاربة اللحظي (EGX)** 🚨\n\n{analysis_result}"
        send_telegram_message(final_message)
        print("تم إرسال التقرير إلى تيليجرام بنجاح!")
    else:
        print("لم يتم العثور على بيانات كافية.")
