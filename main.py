import asyncio
import os
import re
import json
from datetime import datetime
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from threading import Thread
from flask import Flask

# ==================== إعدادات المتغيرات ====================
API_ID = int(os.environ.get('API_ID', 35366951))
API_HASH = os.environ.get('API_HASH', 'd079f23211d239c1ebb67eac4dc5095e')
SESSION_STRING = os.environ.get('SESSION_STRING', '1BJWap1sBuzFdEendO9uUi4XQdIAT_85hA-sevAZWtrkxUR4ICdyOli_26gpn0VKbY5A1WE-kxLYMuc1yCs3-VBac7FaDS4g9nofFRvLJZT1-aZ0jMkI7himMW8GIi4YoNalinqW7mtjwuH-zZJBQ5eQ3WQh8h1So9mkIY2gBv2zTjwuBz87lWFG1OIDfEsAIMhvOrkRwA-V9Tz3shK5nJvlemzjIW0ZMSs1exMY5mhPuQd81LCi79EM1PVu9-KC6t5DW2DlWyaY5iOdwrJV4kUXmJ1bZzCyrQxTloMGwYQva3DHy92xhGzd8z0neRGq0migff0GBc0Kgo6X_ANrtSE8Ubtnsa0A=')
TARGET_CHANNEL = int(os.environ.get('TARGET_CHANNEL', -1003948605081))
ADMIN_ID = int(os.environ.get('ADMIN_ID', 0))
DEVELOPER = "العباد الشدادي"
PORT = int(os.environ.get('PORT', 10000))
# =========================================================

BOT_STATUS = {
    'running': True,
    'monitoring': True,
    'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'total_requests': 0,
    'total_ads_blocked': 0,
    'total_groups': 0,
    'last_request': None
}

MONITORED_GROUPS = set()

# ========== فلتر الإعلانات الكبيرة والأنماط ==========
AD_PATTERNS = [
    r'للبيع', r'بيع', r'اشتري', r'سعر', r'خصم', r'عرض\s+محدود',
    r'تخفيض', r'متجر', r'متاح\s+الآن', r'توصيل', r'شحن', r'مجاني',
    r'وكيل', r'موزع', r'دعاية', r'اعلان', r'إعلان', r'تسويق',
    r'كوبون', r'خصومات', r'تخفيضات', r'تنزيلات', r'اشترك', r'فولو',
    r'معلن', r'معلنين', r'اعلانات', r'إعلانات', r'مدفوع', r'برعاية',
    r'عرض\s+خاص', r'لفترة\s+محدودة', r'الكمية\s+محدودة', r'اطلب\s+الآن',
    r'wa\.me', r'api\.whatsapp\.com', r'whatsapp', r'واتساب', r'تواصل\s+واتس',
    r'رقم\s+التواصل', r'للتواصل\s+عبر', r'قناة\s+التيليجرام', r'انضم\s+إلينا',
    r'خدماتنا\s+الرسمية', r'اعتماد', r'مرخص', r'ضمانات\s+قوية', r'ضمان\s+الدرجة',
    r'نقدم\s+لكم', r'نوفر\s+لكم', r'فريق\s+مختص', r'نخبة\s+من', r'كادر\s+تعليمي',
    r'أسعارنا\s+منافسة', r'لإنجاز\s+مهامكم', r'خدمة\s+العملاء', r'فريقنا',
    r'خدمات\s+البحث\s+العلمي', r'الدراسات\s+العليا', r'للطلب\s+والاستفسار',
    r'خبراء\s+أكاديميين', r'جودة\nعالية', r'سرية\s+تامة', r'دكاترة\s+متخصصين',
    r'دخل\s+يومي', r'تركت\s+وظيفتي', r'اقسم\s+برب', r'من\s+نفس\s+جوالي',
    r'مشروع\s+ربحي', r'ارباح\s+يومية', r'أرباح\s+يومية', r'عمل\s+من\s+المنزل'
]

MARKETING_WORDS = [
    'خدمات', 'فريق', 'دكتور', 'دكاترة', 'ماجستير', 'دكتوراه', 'تحليل', 
    'تنسيق', 'ترجمة', 'توفير', 'المراجع', 'التواصل', 'جودة', 'ضمان', 'خبرة'
]

# ========== الكلمات المفتاحية ==========
KEYWORDS_SET = {
    'بنات تعرفون حد يسوي بحوث تخرج', 'بنات تعرفون حد يسوي مشاريع', 'بنات تعرفون حد يسوي سكليف', 
    'بنات تعرفون حد يسوي عرض', 'بنات تعرفون حد يسوي برزنتيشن', 'بنات تعرفون أحد يسوي بحوث', 
    'بنات تعرفون أحد يسوي مشروع', 'بنات تعرفون أحد يسوي واجبات', 'بنات تعرفون أحد يسوي تقارير', 
    'بنات تعرفون أحد يسوي عروض', 'بنات تعرفون أحد يسوي برزنتيشن', 'بنات بغيت حد فاهم في البحوث', 
    'بنات محتاجة حد يسوي لي الواجب', 'بنات ساعدوني أبي خدمات طلابية', 'تعرفون أحد يسوي بحوث', 
    'تعرفون أحد يسوي مشروع', 'تعرفون أحد يسوي واجبات', 'تعرفون أحد يسوي سكليف', 
    'تعرفون أحد يسوي برزنتيشن', 'تعرفون أحد يسوي عروض بوربوينت', 'تعرفون أحد يسوي كل التكاليف', 
    'تعرفون أحد مضمون', 'من يعرف حد يسوي واجبات', 'من يعرف حد يسوي مشاريع', 'من يعرف حد يسوي بحوث', 
    'من يعرف حد يسوي تقارير', 'من يعرف حد يسوي عروض', 'من يعرف حد يسوي برزنتيشن', 
    'من يعرف حد يسوي سكليف', 'من تعرف وحدة تسوي تكاليف', 'من تعرف وحدة ممتازة', 
    'من يسوي واجبات', 'من يسوي مشاريع', 'من يسوي بحوث', 'من يسوي تقارير', 'من يسوي تلخيص', 
    'من يسوي اختبارات', 'من يسوي تقرير تدريب', 'من يسوي مشروع تخرج', 'من يسوي عروض احترافية', 
    'من يسوي Excel', 'من يسوي اكسل', 'من يسوي Access', 'من يسوي اكسس', 'من يسوي APA', 
    'من عنده شخص ثقة للخدمات الطلابية', 'حد عنده حد ثقة يسوي واجبات', 'حد عنده حد ثقة يسوي مشاريع', 
    'أبي حد يسوي واجبات', 'أبي حد يسوي مشاريع', 'أبي حد يسوي بحث', 'أبي حد يسوي سكليف', 
    'أبي حد يسوي تقرير', 'أبي حد يسوي عرض بوربوينت', 'أبي حد يسوي برزنتيشن', 
    'أبي أحد يسوي مشروع تخرج', 'أبي أحد يخلص لي الواجب', 'أبي أحد يحل الكويز',
    'محتاج حد يسوي لي واجبات', 'محتاجة حد يسوي لي الواجب', 'محتاجة حد يسوي لي مشروع',
    'يعيال من يعرف أحد يسوي واجبات', 'ابغي حد يسوي بحوث', 'ابغي حد يسوي برزنتيشن',
    'من يسوي cv', 'من يسوي سيفي', 'مين يسوي cv', 'مين يحل اختبار', 'ابي حل اختبار'
}

CATEGORIES = {
    'اختبار': {'اختبار','امتحان','كويز','quiz','ميد','فاينل','mid','final','exam','test'},
    'واجب': {'واجب','تكليف','اسايمنت','assignment','homework'},
    'مشروع': {'مشروع','تخرج','project','graduation'},
    'بحث': {'بحث','تقرير','research','report'},
    'تلخيص': {'تلخيص','ملخص','summary'},
    'ترجمة': {'ترجمة','translate','translation'},
    'بوربوينت': {'بوربوينت','powerpoint','presentation','عرض'},
    'تصميم': {'تصميم','design','logo','مصمم','فيديو'},
    'cv': {'cv','سيرة ذاتية','resume','سي في'},
    'برمجة': {'برمجة','code','موقع','تطبيق'},
    'سكليف': {'سكليف','sick leave','اجازة مرضية'},
    'عام': set(),
}

CATEGORY_COLORS = {
    'اختبار': '🔴', 'واجب': '🟢', 'مشروع': '🔵',
    'بحث': '🟣', 'تلخيص': '🟡', 'ترجمة': '🟠',
    'بوربوينت': '⚫', 'تصميم': '🔘', 'cv': '🟤',
    'برمجة': '⚪', 'سكليف': '🩺', 'عام': '📌',
}

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

def is_ad(text):
    if not text:
        return False
    text_lower = text.lower()
    for pattern in AD_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    if "wa.me/" in text_lower or "t.me/" in text_lower or "chat.whatsapp.com" in text_lower:
        return True
    marketing_count = sum(1 for word in MARKETING_WORDS if word in text_lower)
    if marketing_count >= 3:
        return True
    return False

def check_keywords_fast(text):
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
        if cat == 'عام': continue
        for w in words:
            if w.lower() in kw_lower:
                return cat
    return 'عام'

def build_main_menu():
    msg = f"""
🤖 **بوت الخدمات الطلابية الذكي**
👑 المطور: **{DEVELOPER}**
──────────────────
⚙️ **أوامر المراقبة:**
• `/monitor` - تشغيل المراقبة
• `/stopmonitor` - إيقاف المراقبة
• `/status` - حالة البوت
• `/reset` - تصفير الإحصائيات

📌 **أوامر الكلمات المفتاحية:**
• `/addkw` - إضافة كلمة
• `/delkw` - حذف كلمة
• `/listkw` - عرض الكلمات

🛡 **أوامر الإعلانات:**
• `/addad` - إضافة نمط إعلان
• `/delad` - حذف نمط إعلان
• `/listad` - عرض أنماط الإعلانات

📊 **أوامر عامة:**
• `/help` - عرض هذا الدليل
"""
    buttons = [
        [Button.inline("📊 حالة البوت", data=b"status"), Button.inline("⚙️ تشغيل/إيقاف", data=b"toggle_monitor")],
        [Button.inline("📋 الكلمات المفتاحية", data=b"listkw"), Button.inline("🛡 فلاتر الإعلانات", data=b"listad")],
        [Button.inline("🔄 تصفير الإحصائيات", data=b"reset")]
    ]
    return msg, buttons

async def start_bot():
    print(f"🚀 جاري تشغيل البوت | المطور: {DEVELOPER}")
    await client.start()

    @client.on(events.CallbackQuery)
    async def callback_handler(event):
        data = event.data.decode('utf-8')
        if data == "status":
            await event.respond(f"📊 **الطلبات:** {BOT_STATUS['total_requests']} | 🛡 **الإعلانات المحظورة:** {BOT_STATUS['total_ads_blocked']}\n👑 {DEVELOPER}")
        elif data == "toggle_monitor":
            BOT_STATUS['monitoring'] = not BOT_STATUS['monitoring']
            state = "✅ تم التشغيل" if BOT_STATUS['monitoring'] else "⛔ تم الإيقاف"
            await event.respond(f"{state}\n👑 المطور: {DEVELOPER}")
        elif data == "listkw":
            kw_list = "\n".join([f"• `{kw}`" for kw in sorted(KEYWORDS_SET)])
            if len(kw_list) > 4000: kw_list = kw_list[:4000] + "\n..."
            await event.respond(f"📋 **الكلمات ({len(KEYWORDS_SET)}):**\n{kw_list}")
        elif data == "listad":
            ad_list = "\n".join([f"• `{ad}`" for ad in AD_PATTERNS])
            if len(ad_list) > 4000: ad_list = ad_list[:4000] + "\n..."
            await event.respond(f"🛡 **أنماط الحظر ({len(AD_PATTERNS)}):**\n{ad_list}")
        elif data == "reset":
            BOT_STATUS['total_requests'] = 0
            BOT_STATUS['total_ads_blocked'] = 0
            BOT_STATUS['total_groups'] = 0
            BOT_STATUS['last_request'] = None
            BOT_STATUS['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            await event.respond(f"🔄 **تم تصفير الإحصائيات بنجاح**\n👑 {DEVELOPER}")

    @client.on(events.NewMessage)
    async def handler(event):
        chat = await event.get_chat()
        sender = await event.get_sender()
        sender_id = getattr(sender, 'id', None)
        text = event.raw_text or ""

        is_target_channel = hasattr(chat, 'id') and chat.id == TARGET_CHANNEL
        is_private_msg = event.is_private

        if (is_target_channel or is_private_msg) and text.startswith('/'):
            parts = text.split(' ', 1)
            command = parts[0].lower()
            argument = parts[1] if len(parts) > 1 else ""
            reply_target = event.chat_id

            if command == '/status':
                uptime = datetime.now() - datetime.strptime(BOT_STATUS['start_time'], '%Y-%m-%d %H:%M:%S')
                hours, remainder = divmod(uptime.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                msg = f"🟢 **حالة البوت**\n👑 المطور: **{DEVELOPER}**\n⏱ التشغيل: **{hours}h {minutes}m {seconds}s**\n📊 المراقبة: **{'✅ نشطة' if BOT_STATUS['monitoring'] else '⛔ متوقفة'}**\n📨 الطلبات: **{BOT_STATUS['total_requests']}**\n🛡 الإعلانات المحظورة: **{BOT_STATUS['total_ads_blocked']}**"
                await client.send_message(reply_target, msg)
                return
            elif command == '/monitor':
                BOT_STATUS['monitoring'] = True
                await client.send_message(reply_target, f"✅ **تم تشغيل المراقبة**\n👑 {DEVELOPER}")
                return
            elif command == '/stopmonitor':
                BOT_STATUS['monitoring'] = False
                await client.send_message(reply_target, f"⛔ **تم إيقاف المراقبة**\n👑 {DEVELOPER}")
                return
            elif command == '/addkw' and argument:
                KEYWORDS_SET.add(argument)
                await client.send_message(reply_target, f"✅ **تمت إضافة الكلمة:** `{argument}`\n👑 {DEVELOPER}")
                return
            elif command == '/delkw' and argument:
                KEYWORDS_SET.discard(argument)
                await client.send_message(reply_target, f"🗑 **تم حذف الكلمة:** `{argument}`\n👑 {DEVELOPER}")
                return
            elif command == '/listkw':
                kw_list = "\n".join([f"• `{kw}`" for kw in sorted(KEYWORDS_SET)])
                await client.send_message(reply_target, f"📋 **الكلمات:**\n{kw_list[:4000]}")
                return
            elif command == '/addad' and argument:
                AD_PATTERNS.append(argument)
                await client.send_message(reply_target, f"✅ **تمت إضافة النمط:** `{argument}`\n👑 {DEVELOPER}")
                return
            elif command == '/delad' and argument:
                if argument in AD_PATTERNS: AD_PATTERNS.remove(argument)
                await client.send_message(reply_target, f"🗑 **تم حذف النمط:** `{argument}`\n👑 {DEVELOPER}")
                return
            elif command == '/listad':
                ad_list = "\n".join([f"• `{ad}`" for ad in AD_PATTERNS])
                await client.send_message(reply_target, f"🛡 **أنماط الإعلانات:**\n{ad_list[:4000]}")
                return
            elif command == '/reset':
                BOT_STATUS['total_requests'] = 0
                BOT_STATUS['total_ads_blocked'] = 0
                await client.send_message(reply_target, f"🔄 **تم تصفير الإحصائيات**\n👑 {DEVELOPER}")
                return
            elif command in ['/help', '/start']:
                help_msg, buttons = build_main_menu()
                await client.send_message(reply_target, help_msg, buttons=buttons)
                return

        if BOT_STATUS['monitoring'] and event.is_group:
            if is_ad(text):
                BOT_STATUS['total_ads_blocked'] += 1
                return

            keyword = check_keywords_fast(text)
            if keyword:
                BOT_STATUS['total_requests'] += 1
                BOT_STATUS['last_request'] = datetime.now().strftime('%H:%M:%S')
                
                user_id = getattr(sender, 'id', 0)
                first_name = getattr(sender, 'first_name', '') or ''
                username = getattr(sender, 'username', None)
                category = get_category(keyword)
                color = CATEGORY_COLORS.get(category, '📌')

                msg = f"{color} **طلب جديد - {category}**\n\n"
                msg += f"📌 **الكلمة:** `{keyword}`\n"
                msg += f"👤 **المرسل:** [{first_name}](tg://user?id={user_id})\n"
                msg += f"🔹 **اليوزر:** @{username if username else 'لا يوجد'}\n\n"
                msg += f"📝 **الرسالة:**\n```\n{text[:300]}\n```\n\n"
                msg += f"👑 المطور: {DEVELOPER}"

                try:
                    await client.send_message(TARGET_CHANNEL, msg, link_preview=False)
                except Exception as e:
                    print(f"Error: {e}")

    await client.run_until_disconnected()

# ========== سيرفر الويب Flask ==========
app = Flask(__name__)

@app.route('/')
def home():
    return f"🤖 البوت يعمل بنجاح 24/7 | 👑 {DEVELOPER}"

def run_telethon():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

if __name__ == '__main__':
    t = Thread(target=run_telethon)
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', port=PORT)
