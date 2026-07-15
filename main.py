import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import Channel
from threading import Thread
from flask import Flask

# --- تشغيل سيرفر ويب وهمي لتخطي نظام Render المجاني ---
web_app = Flask('')

@web_app.route('/')
def home():
    return "Scraper is running successfully!"

def run_web_server():
    # Render يمرر رقم المنفذ تلقائياً عبر متغير PORT
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web_server)
    t.start()
# ----------------------------------------------------

# قراءة المتغيرات الأساسية بأمان من إعدادات الاستضافة
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
PHONE = os.getenv("PHONE", "")
TARGET_CHANNEL = int(os.getenv("TARGET_CHANNEL", "0"))

# استيراد الإعدادات الأخرى من ملف config.py إذا كان موجوداً
try:
    from config import KEYWORDS_SET, CATEGORIES, CATEGORY_COLORS
except ImportError:
    # إعدادات افتراضية في حال عدم وجود ملف config لضمان عدم توقف الكود
    KEYWORDS_SET = {"حل واجب", "بحث تخرج", "جامعة", "assignment", "مشروع"}
    CATEGORIES = {
        'واجبات': ['واجب', 'حل', 'assignment'],
        'أبحاث': ['بحث', 'تخرج', 'صياغة'],
        'برمجة': ['كود', 'جاڤا', 'java', 'python']
    }
    CATEGORY_COLORS = {'واجبات': '📚', 'أبحاث': '🔬', 'برمجة': '💻', 'عام': '📌'}

SESSION = os.getenv("SESSION_STRING", "session")
client = TelegramClient(SESSION, API_ID, API_HASH)

def check_keywords(text):
    if not text:
        return None
    text_lower = text.lower()
    for kw in KEYWORDS_SET:
        if kw.lower() in text_lower:
            return kw
    return None

def get_category(keyword):
    kw_lower = keyword.lower()
    for cat, words in CATEGORIES.items():
        for w in words:
            if w.lower() in kw_lower:
                return cat
    return 'عام'

def get_university(text):
    if not text:
        return "غير معروف"
    text = text.lower()
    unis = {
        'جامعة الملك سعود': ['جامعة الملك سعود', 'ksu'],
        'جامعة الامام': ['جامعة الامام', 'جامعة الإمام'],
        'جامعة الملك عبدالعزيز': ['جامعة الملك عبدالعزيز', 'kau'],
        'جامعة القصيم': ['جامعة القصيم', 'qu'],
        'جامعة تبوك': ['جامعة تبوك'],
        'جامعة الدمام': ['جامعة الدمام'],
        'جامعة جدة': ['جامعة جدة'],
        'جامعة الطائف': ['جامعة الطائف'],
        'جامعة حائل': ['جامعة حائل'],
        'جامعة جازان': ['جامعة جازان'],
    }
    for uni_name, aliases in unis.items():
        for alias in aliases:
            if alias in text:
                return uni_name
    return "غير معروف"

async def get_group_link(chat):
    try:
        if hasattr(chat, 'username') and chat.username:
            return "https://t.me/" + str(chat.username)
    except Exception:
        pass
    return None

@client.on(events.NewMessage)
async def handler(event):
    try:
        chat = await event.get_chat()
        
        if isinstance(chat, Channel) and chat.id == TARGET_CHANNEL:
            return
        
        if not event.is_group:
            return
        
        text = event.raw_text or ""
        keyword = check_keywords(text)
        
        if keyword:
            sender = await event.get_sender()
            group_name = getattr(chat, 'title', 'مجموعة غير معروفة')
            group_link = await get_group_link(chat)
            first = getattr(sender, 'first_name', '') or ''
            last = getattr(sender, 'last_name', '') or ''
            full_name = (first + ' ' + last).strip() or 'مجهول'
            username = getattr(sender, 'username', None)
            user_id = getattr(sender, 'id', 0)
            university = get_university(text)
            category = get_category(keyword)
            color = CATEGORY_COLORS.get(category, '📌')
            
            user_display = f"[{full_name}](tg://user?id={user_id})"
            group_display = f"[{group_name}]({group_link})" if group_link else group_name
            
            msg_lines = [
                f"{color} **طلب جديد - {category}**\n",
                f"📌 **الكلمة المفتاحية:** `{keyword}`",
                f"📂 **التصنيف:** {category}\n",
                f"👤 **المرسل:** {user_display}",
                f"🔹 **اليوزر:** @{username}" if username else "🔹 **اليوزر:** لا يوجد",
                f"🆔 **الايدي:** `{user_id}`\n",
                f"🏫 **الجامعة:** {university}",
                f"💬 **المجموعة:** {group_display}\n",
                "📝 **الرسالة:**",
                "```"
            ]
            
            if len(text) > 500:
                msg_lines.append(text[:500] + "...")
            else:
                msg_lines.append(text)
            msg_lines.append("```\n")
            msg_lines.append(f"⏰ **الوقت:** {event.date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            msg = "\n".join(msg_lines)
            
            await client.send_message(TARGET_CHANNEL, msg, link_preview=False)
            print(f"✅ [{category}] {full_name} | {keyword}")
            
    except Exception as e:
        print(f"❌ خطأ في معالجة الرسالة: {e}")

async def main():
    await client.start(phone=PHONE)
    me = await client.get_me()
    print("=" * 50)
    print(f"🤖 حساب السكرايبر يعمل بنجاح: {me.first_name}")
    print(f"📡 القناة الهدف الموجه لها: {TARGET_CHANNEL}")
    print(f"🔑 عدد الكلمات المراقبة: {len(KEYWORDS_SET)}")
    print("=" * 50)
    print("⏳ بانتظار رصد الطلبات في المجموعات...")
    await client.run_until_disconnected()

# بدلاً من تشغيل السكرايبر فقط، سنستخدم Thread ليتم تشغيله مع سيرفر الويب في نفس الوقت

if __name__ == '__main__':
    # 1. تشغيل السكرايبر في مسار منفصل (Thread)
    scraper_thread = Thread(target=lambda: asyncio.run(main()))
    scraper_thread.start()
    
    # 2. تشغيل سيرفر الويب الوهمي (ليظل الرندر مستيقظاً)
    run_web_server()
