import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession  # <--- هذا السطر هو الذي كان ناقصاً
from threading import Thread
from flask import Flask

# --- إعدادات الحساب (لا تغيرها إلا إذا استخرجت جلسة جديدة) ---
API_ID = 35366951
API_HASH = 'd079f23211d239c1ebb67eac4dc5095e'
SESSION_STRING = '1BJWap1wBu53EJ3RIGEHqeRYAlQsMY41xT_-hlDi4kinI4Xxrg9GTgXKww_Je2C7wqShw3f4MJAlnBNYnmwg10FRISV_sXGCWeaPNQawIrjR3UnFZoQczd43jd83iLjmaFEascAZ9y_clju0kddGaKW9qd1ayf3E1rIzB41K5npbwuydaVBBUecc9TWRcmGaw5l-4b2fzywYBTZ5AYAfulbfYyGS2Lv8HeR3_zpTGEhN3crph1Eo_hL6Jd9O7b3zaRv-ZmfLKQrLCCfJv5VhIuh-DM1LydsnxQfuTPu4_2L-Jtv25jke0KzSJmrho8aAF-077hEHU5yVbsr4DN6tGFB3HlvI-TBo='

# --- إعدادات القناة والكلمات ---
TARGET_CHANNEL = -1003948605081 # تأكد من وجود الـ -100 في البداية
KEYWORDS = {
    "واجب", "حل", "مساعدة", "مطلوب", "تكليف", "أسئلة", "اختبار", "كويز",
    "بحث", "تقرير", "تلخيص", "تحليل", "صياغة", "تدقيق", "مراجعة", "تنسيق", "مراجع", "توثيق",
    "كود", "برمجة", "java", "python", "c++", "بروجكت", "مشروع", "تطوير", "موقع", "تطبيق", "sql",
    "ترجمة", "شرح", "سلايدات", "ملخص", "دراسة", "سمنار", "خطة بحث", "ماجستير", "دكتوراه",
    "تصميم", "بوربوينت", "عرض", "presentation", "فوتوشوب", "مونتاج"
}

# --- إعداد السكرايبر ---
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

async def main():
    print("🚀 البوت بدأ العمل الآن...")
    await client.start()
    print("✅ تم تسجيل الدخول بنجاح! البوت يراقب الآن...")

    @client.on(events.NewMessage)
    async def handler(event):
        if event.raw_text:
            text = event.raw_text.lower()
            # فحص إذا كانت الرسالة تحتوي على أي من الكلمات المفتاحية
            if any(keyword in text for keyword in KEYWORDS):
                print(f"📩 تم صيد رسالة: {text[:40]}...")
                # إرسال الرسالة للقناة الهدف
                msg = f"✨ رسالة جديدة تم صيدها:\n\n{event.raw_text}"
                await client.send_message(TARGET_CHANNEL, msg)

    await client.run_until_disconnected()

# --- إعداد سيرفر الويب (لإبقاء الخدمة تعمل) ---
app = Flask(__name__)
@app.route('/')
def home():
    return "البوت يعمل بكفاءة 24/7!"

def run_web_server():
    app.run(host='0.0.0.0', port=10000)

# --- التشغيل الأساسي ---
if __name__ == '__main__':
    # تشغيل السيرفر والسكرايبر معاً
    Thread(target=run_web_server).start()
    asyncio.run(main())
