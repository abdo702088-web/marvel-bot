import requests
import time
import random
import re
import json

TOKEN = "8830217007:AAHmVJQjqnJq1GFc8pXK6Dxy0Wv3Wne9oUM"
API = f"https://api.telegram.org/bot{TOKEN}/"

offset = 0
user_state = {}

tips = [
    "🛡️ فعل التحقق بخطوتين.",
    "🔐 استخدم كلمة مرور مختلفة لكل موقع.",
    "⚠️ لا تضغط على الروابط المجهولة.",
    "📧 تحقق من اسم الموقع قبل تسجيل الدخول."
]

def send(chat_id, text, keyboard=None):
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = keyboard
    requests.post(API + "sendMessage", json=data)

def main_menu():
    return {
        "keyboard": [
            [{"text": "🔍 فحص رابط"}],
            [{"text": "🤖 المساعد"}, {"text": "🛡️ نصائح الحماية"}],
            [{"text": "🔐 فحص كلمة مرور"}],
            [{"text": "👤 عن MARVEL"}, {"text": "⚙️ الإعدادات"}]
        ],
        "resize_keyboard": True
    }

def back_menu():
    return {
        "keyboard": [[{"text": "🏠 الرئيسية"}]],
        "resize_keyboard": True
    }

def scan_link(url):
    score = 100
    notes = []

    if not url.startswith("http"):
        return "🔴 الرابط غير صالح."

    if not url.startswith("https://"):
        score -= 25
        notes.append("HTTPS غير موجود")

    for w in ["login","verify","password","free","gift"]:
        if w in url.lower():
            score -= 15
            notes.append(f"كلمة مشبوهة: {w}")

    if score >= 80:
        status = "🟢 يبدو طبيعياً"
    elif score >= 50:
        status = "🟡 يحتاج حذر"
    else:
        status = "🔴 مشبوه"

    return f"🔍 نتيجة الفحص\\n\\n{status}\\nالتقييم: {score}/100\\n\\n" + ("\\n".join(notes) if notes else "لا توجد مؤشرات واضحة.")

def password_strength(p):
    score = 0
    if len(p) >= 8: score += 1
    if re.search(r"[A-Z]", p): score += 1
    if re.search(r"[a-z]", p): score += 1
    if re.search(r"\\d", p): score += 1
    if re.search(r"[^A-Za-z0-9]", p): score += 1

    levels = ["ضعيفة جداً","ضعيفة","متوسطة","جيدة","قوية","قوية جداً"]
    return "🔐 قوة كلمة المرور: " + levels[score]

print("MARVEL V2 RUNNING...")

while True:
    try:
        r = requests.get(API + "getUpdates",
                         params={"offset": offset, "timeout": 30},
                         timeout=35).json()

        for upd in r.get("result", []):
            offset = upd["update_id"] + 1

            if "message" not in upd:
                continue

            msg = upd["message"]
            chat_id = msg["chat"]["id"]
            text = msg.get("text", "")

            state = user_state.get(chat_id)

            if state == "link":
                user_state.pop(chat_id, None)
                send(chat_id, scan_link(text), main_menu())
                continue

            if state == "password":
                user_state.pop(chat_id, None)
                send(chat_id, password_strength(text), main_menu())
                continue

            if text == "/start" or text == "🏠 الرئيسية":
                send(chat_id,
                     "💀 MARVEL\n\nاختر من القائمة 👇",
                     main_menu())

            elif text == "🔍 فحص رابط":
                user_state[chat_id] = "link"
                send(chat_id, "📩 أرسل الرابط الآن.", back_menu())

            elif text == "🔐 فحص كلمة مرور":
                user_state[chat_id] = "password"
                send(chat_id, "📩 أرسل كلمة المرور لتقييمها.", back_menu())

            elif text == "🤖 المساعد":
                send(chat_id,
                     "🤖 MARVEL\n\nاسأل عن الحماية أو التصيد الإلكتروني أو كلمات المرور.",
                     back_menu())

            elif text == "🛡️ نصائح الحماية":
                send(chat_id, random.choice(tips), back_menu())

            elif text == "👤 عن MARVEL":
                send(chat_id,
                     "💀 MARVEL\n\nمساعد عربي لفحص الروابط وتقديم نصائح الحماية.",
                     back_menu())

            elif text == "⚙️ الإعدادات":
                send(chat_id,
                     "⚙️ الإعدادات\n\nلا توجد إعدادات متقدمة حالياً.",
                     back_menu())

            else:
                send(chat_id,
                     "🤖 MARVEL\nاستخدم الأزرار للتنقل.",
                     main_menu())

        time.sleep(1)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(5)
