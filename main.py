import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from threading import Thread
from flask import Flask

# ==================== إعداداتك ====================
API_ID = 35366951
API_HASH = 'd079f23211d239c1ebb67eac4dc5095e'

# المعرف الكبير (الجلسة)
SESSION_STRING = '1BJWap1wBu53EJ3RIGEHqeRYAlQsMY41xT_-hlDi4kinI4Xxrg9GTgXKww_Je2C7wqShw3f4MJAlnBNYnmwg10FRISV_sXGCWeaPNQawIrjR3UnFZoQczd43jd83iLjmaFEascAZ9y_clju0kddGaKW9qd1ayf3E1rIzB41K5npbwuydaVBBUecc9TWRcmGaw5l-4b2fzywYBTZ5AYAfulbfYyGS2Lv8HeR3_zpTGEhN3crph1Eo_hL6Jd9O7b3zaRv-ZmfLKQrLCCfJv5VhIuh-DM1LydsnxQfuTPu4_2L-Jtv25jke0KzSJmrho8aAF-077hEHU5yVbsr4DN6tGFB3HlvI-TBo='

# معرف القناة (الكبير)
TARGET_CHANNEL = -1003948605081
# =================================================

# ========== الكلمات المفتاحية (كاملة) ==========
KEYWORDS = {
    'ابي حد','ابي احد','احتاج احد','احتاج شخص','ابي شخص',
    'حد يعرف','من يعرف','مين يعرف','احد يعرف','في احد يعرف',
    'في حد يعرف','من يسوي','مين يسوي','حد يسوي','احد يسوي',
    'من يقدر','مين يقدر','يساعدني','مساعدة','محتاج مساعدة',
    'ابي مساعدة','احتاج مساعدة','دلوني','دلوني على احد',
    'عندكم احد','تعرفون احد','تعرفوا احد','ابي احد يساعدني',
    'احتاج من يسوي','من يتعامل','مين يتعامل','ابغى حد',
    'ابي حل','احتاج حل','محتاج حل','ابغى حل','يسوي لي',
    'سوي لي','يسوون لي','يسووا لي',
    
    'حل اختبار','حل اختبارات','ابي حل اختبار','ابي احد يحل اختبار',
    'من يحل اختبار','مين يحل اختبار','اختبار اونلاين','اختبار الكتروني',
    'امتحان','امتحانات','كويز','كويزات','quiz','quizzes',
    'ميد','فاينل','اختبار نهائي','اختبار نصفي','ميدترم','فاينال',
    'حل امتحان','حل كويز','ابي حل امتحان','ابي حل كويز',
    'mid','final','exam','exams','test','tests',
    
    'حل واجب','حل واجبات','واجب','واجبات','تكليف','تكاليف',
    'اسايمنت','assignment','assignments','حل اسايمنت',
    'حل تكليف','نشاط','انشطة','حل نشاط','حل تكاليف',
    'homework','hw','solution','solutions','solve',
    
    'مشروع','مشاريع','مشروع تخرج','تخرج','مشروع مادة',
    'حل مشروع','سوي لي مشروع','ابي مشروع','احتاج مشروع',
    'project','projects','graduation project','senior project',
    
    'بحث','بحوث','بحث علمي','ورقة بحثية','تقرير','تقارير',
    'رسالة ماجستير','رسالة دكتوراه','سوي لي بحث','سوي لي تقرير',
    'research','paper','report','thesis','dissertation',
    
    'تلخيص','ملخص','ملخصات','تلخيص كتاب','تلخيص محاضرات',
    'تلخيص مقرر','ملخص كتاب','ملخص محاضرات','summary',
    'summarize','notes',
    
    'ترجمة','مترجم','ترجمة بحث','ترجمة ملف','ترجمة pdf',
    'ترجمة انجليزي','ترجمة عربي','ترجمة من انجليزي',
    'translate','translation','translator','ترجمه',
    
    'بوربوينت','باوربوينت','powerpoint','ppt','عرض تقديمي',
    'برزنتيشن','presentation','سلايدات','شرائح','slides',
    'سوي لي بوربوينت','سوي لي عرض','ابي بوربوينت',
    
    'تصميم','مصمم','تصميم احترافي','تصميم اعلان','تصميم بوستر',
    'تصميم شعار','تصميم لوجو','انفوجرافيك','بروشور','logo',
    'design','designer','poster','infographic','brochure',
    
    'سيرة ذاتية','cv','سي في','تصميم cv','كتابة cv','تعديل cv',
    'السيرة الذاتية','resume','curriculum vitae','سوي لي cv',
    
    'وورد','word','اكسل','excel','pdf','بي دي اف',
    'برمجة','موقع','مواقع','تطبيق','تطبيقات','كود','اكواد',
    'مشروع برمجي','مشروع تخرج برمجة','برمج','programming',
    'code','coding','website','app','application','developer',
    
    'خدمات طلابية','خدمة طلابية','مساعدة طلابية','مساعدة طالب',
    'مساعدة طالبة','خدمة طالب','خدمة طالبة','student services',
    
    'يسوي سكليف','sick leave','اجازة مرضية','صحتي','اجازة',
    'sick','medical leave','leave','استراحة مرضية',
}

# ========== تصنيفات ==========
CATEGORIES = {
    'اختبار': {'اختبار','امتحان','كويز','quiz','ميد','فاينل','mid','final','exam','test'},
    'واجب': {'واجب','تكليف','اسايمنت','assignment','homework','hw'},
    'مشروع': {'مشروع','تخرج','project','graduation'},
    'بحث': {'بحث','تقرير','research','report','thesis'},
    'تلخيص': {'تلخيص','ملخص','summary'},
    'ترجمة': {'ترجمة','translate','translation'},
    'بوربوينت': {'بوربوينت','powerpoint','presentation','عرض'},
    'تصميم': {'تصميم','design','logo','مصمم'},
    'cv': {'cv','سيرة ذاتية','resume'},
    'برمجة': {'برمجة','برمج','programming','code','موقع','تطبيق'},
    'سكليف': {'سكليف','sick leave','اجازة مرضية','sick'},
}

CATEGORY_COLORS = {
    'اختبار': '🔴', 'واجب': '🟢', 'مشروع': '🔵',
    'بحث': '🟣', 'تلخيص': '🟡', 'ترجمة': '🟠',
    'بوربوينت': '⚫', 'تصميم': '🔘', 'cv': '🟤',
    'برمجة': '⚪', 'سكليف': '🩺', 'عام': '📌',
}

# ========== إعدادات ==========
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

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
        'جامعة الامام محمد بن سعود': ['جامعة الامام', 'جامعة الإمام'],
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
    except:
        pass
    return None

# ========== البوت ==========
async def main():
    print("🚀 البوت بدأ العمل...")
    await client.start()
    print("✅ تم تسجيل الدخول!")

    @client.on(events.NewMessage)
    async def handler(event):
        chat = await event.get_chat()
        
        # تجاهل القناة الهدف
        if hasattr(chat, 'id') and chat.id == TARGET_CHANNEL:
            return
        
        # فقط المجموعات
        if not event.is_group:
            return
        
        text = event.raw_text or ""
        if not text:
            return
        
        # البحث عن الكلمات
        keyword = None
        for kw in KEYWORDS:
            if kw.lower() in text.lower():
                keyword = kw
                break
        
        if keyword:
            sender = await event.get_sender()
            group_name = getattr(chat, 'title', 'مجموعة غير معروفة')
            group_link = await get_group_link(chat)
            
            first = getattr(sender, 'first_name', '') or ''
            last = getattr(sender, 'last_name', '') or ''
            full_name = (first + ' ' + last).strip() or 'مجهول'
            username = sender.username
            user_id = sender.id
            
            # رابط المستخدم
            user_display = "[" + full_name + "](tg://user?id=" + str(user_id) + ")"
            
            # رابط المجموعة
            if group_link:
                group_display = "[" + group_name + "](" + group_link + ")"
            else:
                group_display = group_name
            
            university = get_university(text)
            category = get_category(keyword)
            color = CATEGORY_COLORS.get(category, '📌')
            
            # بناء الرسالة
            msg = ""
            msg += color + " **طلب جديد - " + category + "**\n\n"
            msg += "📌 **الكلمة المفتاحية:** `" + keyword + "`\n"
            msg += "📂 **التصنيف:** " + category + "\n\n"
            msg += "👤 **المرسل:** " + user_display + "\n"
            
            if username:
                msg += "🔹 **اليوزر:** @" + username + "\n"
            else:
                msg += "🔹 **اليوزر:** لا يوجد\n"
                
            msg += "🆔 **الايدي:** `" + str(user_id) + "`\n\n"
            msg += "🏫 **الجامعة:** " + university + "\n"
            msg += "💬 **المجموعة:** " + group_display + "\n\n"
            msg += "📝 **الرسالة:**\n```\n"
            
            if len(text) > 500:
                msg += text[:500] + "..."
            else:
                msg += text
                
            msg += "\n```\n\n"
            msg += "⏰ **الوقت:** " + str(event.date.strftime('%Y-%m-%d %H:%M:%S'))
            
            try:
                await client.send_message(TARGET_CHANNEL, msg, link_preview=False)
                print("✅ [" + category + "] " + full_name + " | " + keyword)
            except Exception as e:
                print("❌ خطأ: " + str(e))

    await client.run_until_disconnected()

# ========== سيرفر الويب ==========
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 البوت يعمل بكفاءة 24/7!"

def run_web_server():
    app.run(host='0.0.0.0', port=10000)

# ========== التشغيل ==========
if __name__ == '__main__':
    Thread(target=run_web_server).start()
    asyncio.run(main())
