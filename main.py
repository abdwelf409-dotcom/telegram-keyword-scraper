import asyncio
import os
import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from threading import Thread
from flask import Flask

# ==================== إعدادات ====================
API_ID = int(os.environ.get('API_ID', 35366951))
API_HASH = os.environ.get('API_HASH', 'd079f23211d239c1ebb67eac4dc5095e')
SESSION_STRING = '1BJWap1sBuzFdEendO9uUi4XQdIAT_85hA-sevAZWtrkxUR4ICdyOli_26gpn0VKbY5A1WE-kxLYMuc1yCs3-VBac7FaDS4g9nofFRvLJZT1-aZ0jMkI7himMW8GIi4YoNalinqW7mtjwuH-zZJBQ5eQ3WQh8h1So9mkIY2gBv2zTjwuBz87lWFG1OIDfEsAIMhvOrkRwA-V9Tz3shK5nJvlemzjIW0ZMSs1exMY5mhPuQd81LCi79EM1PVu9-KC6t5DW2DlWyaY5iOdwrJV4kUXmJ1bZzCyrQxTloMGwYQva3DHy92xhGzd8z0neRGq0migff0GBc0Kgo6X_ANrtSE8Ubtnsa0A='
TARGET_CHANNEL = int(os.environ.get('TARGET_CHANNEL', -1003948605081))
DEVELOPER = "العباد الشدادي"
DEVELOPER_ID = None
# =================================================

# ========== فلتر الإعلانات المتطور (لحظر إعلانات المكاتب الكبيرة والشركات) ==========
AD_PATTERNS = [
    r'للبيع', r'بيع', r'اشتري', r'سعر', r'خصم', r'عرض\s+محدود',
    r'تخفيض', r'متجر', r'متاح\s+الآن', r'توصيل', r'شحن', r'مجاني',
    r'وكيل', r'موزع', r'دعاية', r'اعلان', r'إعلان', r'تسويق',
    r'كوبون', r'خصومات', r'تخفيضات', r'تنزيلات',
    r'اشترك', r'فولو', r'تابعني', r'حسابي', r'تبادل',
    r'معلن', r'معلنين', r'اعلانات', r'إعلانات', r'مدفوع', r'برعاية',
    r'عرض\s+خاص', r'لفترة\s+محدودة', r'الكمية\s+محدودة',
    r'اطلب\s+الآن', r'تواصل\s+واتس', r'رقم\s+التواصل',
    r'للتواصل\s+عبر', r'قناة\s+التيليجرام', r'انضم\s+إلينا',
    r'خدماتنا\s+الرسمية', r'اعتماد', r'مرخص', r'ضمانات\s+قوية',
    r'نقدم\s+لكم', r'نوفر\s+لكم', r'فريق\s+مختص', r'نخبة\s+من',
    r'أسعارنا\s+منافسة', r'لإنجاز\s+مهامكم', r'خدمة\s+العملاء',
    r'خدمات\s+البحث\s+العلمي', r'الدراسات\s+العليا', r'للطلب\s+والاستفسار',
    r'wa\.me', r'لخدمات', r'فريقنا', r'خبراء\s+أكاديميين',
    r'🔥', r'💥', r'⚡️\s+عرض', r'🎉\s+تخفيض', r'📌\s+إعلان', r'💢'
]

# قائمة الإعلانات المتعلمة (يتعلمها البوت تلقائياً)
LEARNED_AD_PATTERNS = []

# ========== الكلمات المفتاحية للطلبات ==========
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
    'من عندها رقم خدمات طلابية', 'من عندها شخص مجرب', 'من عنده شخص ثقة للخدمات الطلابية', 
    'حد عنده حد ثقة يسوي واجبات', 'حد عنده حد ثقة يسوي مشاريع', 'حد عنده حد ثقة يسوي بحوث', 
    'حد عنده حد ثقة يسوي سكليف', 'حد عنده حد ثقة يسوي تقارير', 'حد عنده مصمم فيديو', 
    'حد عنده مصمم دعوات', 'حد يعرف أحد يحل واجبات', 'حد يعرف أحد يحل اختبارات', 
    'حد يعرف أحد يسوي مشاريع', 'حد يعرف أحد يسوي بحوث', 'حد يعرف أحد يسوي عروض', 
    'حد يعرف أحد يصمم فيديو', 'حد يعرف أحد يصمم دعوة زواج', 'أحد يعرف خدمات طلابية', 
    'أحد عنده خدمات طلابية', 'أحد عنده رقم وحدة تسوي بحوث', 'أحد مجرب خدمات طلابية', 
    'أحد يسوي واجبات', 'أحد يسوي Word', 'أحد يضمن الدرجة', 'أحد متفرغ اليوم', 
    'أبي حد يسوي واجبات', 'أبي حد يسوي مشاريع', 'أبي حد يسوي بحث', 'أبي حد يسوي سكليف', 
    'أبي حد يسوي تقرير', 'أبي حد يسوي عرض بوربوينت', 'أبي حد يسوي برزنتيشن', 
    'أبي حد يسوي تكليف', 'أبي أحد يسوي مشروع', 'أبي أحد يسوي مشروع تخرج', 
    'أبي أحد يسوي واجبات', 'أبي أحد يسوي بحث', 'أبي أحد يكتب بحث كامل', 
    'أبي أحد يسوي برزنتيشن', 'أبي أحد يسوي عرض بوربوينت', 'أبي أحد يسوي سكليف', 
    'أبي أحد يسوي تقرير', 'أبي أحد يسوي مشاريع الجامعة', 'أبي أحد يخلص المشروع كامل', 
    'أبي أحد يخلص الأبحاث', 'أبي أحد يخلص التكليف', 'أبي أحد يخلص واجبات الجامعة', 
    'أبي أحد يخلص لي الواجب', 'أبي أحد يخلص لي المشروع', 'أبي أحد يخلص لي البحث', 
    'أبي أحد يخلص لي كل موادي', 'أبي أحد يحل الكويز', 'أبي أحد يحل الاختبار', 
    'أبي أحد ينجز اليوم', 'أبي أحد يخلص قبل الموعد', 'أبي أحد شغله احترافي', 
    'أبي أحد شغله مضمون', 'أبي أحد أسعاره مناسبة', 'أبي شخص ثقة', 'أبي شخص مضمون', 
    'أبي شغل مرتب وسريع', 'أبي خدمات جامعية كاملة', 'أبي تنسيق بحث', 'أبي تدقيق لغوي', 
    'محتاج حد يسوي لي واجبات', 'محتاجة حد يسوي لي الواجب', 'محتاجة حد يسوي لي مشروع', 
    'محتاجة حد يسوي لي بحث', 'محتاجة أحد يسوي بحث', 'محتاجة أحد يخلص التكليف', 
    'يعيال حد عنده أحد ثقة', 'يعيال من يعرف أحد يسوي واجبات', 'يعيال من يعرف أحد يسوي مشاريع', 
    'يعيال من يعرف أحد يسوي بحوث', 'ابغي حد يسوي بحوث', 'ابغي حد يسوي برزنتيشن', 
    'ابغي حد يسوي بوربوينت', 'ابغي حد يسوي تقرير', 'ابغي حد يسوي مشروع', 
    'ابغي حد يسوي واجبات', 'ابغي حد يسوي تكاليف', 'ابغي حد يسوي سكليف', 
    'ابغي حد يسوي عرض', 'بغيت حد فاهم في البحوث', 'بغيت حد فاهم في المشاريع', 
    'بغيت حد فاهم في التقارير', 'بغيت حد ثقة', 'ابي حد يصمم لي فيديو', 
    'ابي حد يسوي مونتاج', 'ابي حد يصمم لي مونتاج', 'ابي حد يصمم لي دعوة زواج', 
    'ابي حد يصمم لي دعوة', 'ابي حد يصمم اعلان', 'ابي حد يصمم بوستر', 
    'ابي حد يصمم شعار', 'ابي حد يصمم لوجو', 'ابي حد يصمم هوية بصرية', 
    'ابي حد يصمم انفوجرافيك', 'ابي حد يصمم سيرة ذاتية', 'ابي حد يصمم برزنتيشن', 
    'ابي حد يسوي تصميم احترافي', 'ابي حد يمنتج فيديو', 'ابي حد يسوي موشن جرافيك', 
    'ابي حد يصمم ريلز', 'ابي حد يصمم سناب', 'ابي حد يصمم منشورات', 
    'ابي حد يصمم بطاقة دعوة', 'من يعرف مصمم فيديو', 'من يعرف مصمم دعوات', 
    'من يعرف مصمم ثقة', 'بنات تعرفون مصمم فيديو', 'بنات تعرفون أحد يصمم دعوات', 
    'من يسوي اكسل', 'أبي أحد يسوي اكسل', 'أبي أحد يسوي Excel', 'ابغي حد يسوي اكسل', 
    'من يعرف أحد يسوي اكسل', 'تعرفون أحد يسوي اكسل', 'من يسوي باوربوينت', 'من يسوي بوربوينت', 
    'أبي أحد يسوي باوربوينت', 'ابغي حد يسوي باوربوينت', 'من يعرف أحد يسوي باوربوينت', 
    'تعرفون أحد يسوي باوربوينت', 'من يسوي وورد', 'من يسوي Word', 'أبي أحد يسوي وورد', 
    'ابغي حد يسوي وورد', 'من يعرف أحد يسوي وورد', 'تعرفون أحد يسوي وورد', 
    'من يعرف أحد يسوي اكسس', 'تعرفون أحد يسوي اكسس', 'من يسوي برزنتيشن احترافي', 
    'من يسوي بوربوينت احترافي', 'أبي أحد يسوي سيرة ذاتية', 'من يسوي CV', 'من يسوي سيفي', 
    'أبي أحد يسوي CV', 'أبي أحد يسوي سيفي', 'بنات احد يعرف يسوي cv بنظام ats بسعر كويس', 
    'مين يسوي cv', 'مين يسوي سي في', 'مين يسوي سيرة ذاتية', 'مين يسوي cv ats', 
    'مين يعرف يسوي cv', 'مين يعرف يسوي سي في', 'مين يعرف يسوي سيرة ذاتية', 
    'مين يعرف حد يسوي cv', 'مين يعرف احد يسوي سي في', 'مين يضبط لي cv', 
    'مين يسملي cv', 'مين يدلني على حد يسوي cv', 'مين يقدر يسوي لي', 
    'حد يعرف أحد', 'أحد يعرف', 'تعرفون أحد', 'تعرفوا أحد', 'فيه أحد', 
    'مين يعرف', 'مين يدلني', 'أبي أحد', 'أبي شخص', 'أبي رقم', 'أبي مكتب', 
    'أبي خدمات', 'أبي ثقة', 'أبي مضمون', 'أبي سريع', 'أبي اليوم', 'أبي خلال ساعات', 
    'أبي يخلصه اليوم', 'أبي أحد يسويه', 'أبي أحد ينجزه', 'أبي أحد يحله', 
    'أبي أحد يكتبه', 'أبي أحد يصممه', 'أبي أحد يرتبه', 'أبي أحد يراجعه', 
    'أبي أحد يترجمه', 'أبي أحد يدققه', 'أبي أحد يساعدني', 'مين يسوي', 'مين يحل', 
    'مين يكتب', 'مين يصمم', 'مين ينجز', 'مين يترجم', 'مين يدقق', 'مين يخلص', 
    'حد يسوي', 'حد يحل', 'حد يكتب', 'حد يصمم', 'حد ينجز', 'حد يترجم', 'حد يدقق', 'حد يخلص',
    'ابي', 'ابغي', 'ابغى', 'محتاج', 'محتاجه', 'محتاجة', 'بغيت', 'اريد',
    'من يحل', 'من يصمم', 'يساعدني', 'مساعدة', 'خدمات طلابية', 'خدمة طلابية',
    'حل اختبار', 'حل اختبارات', 'ابي حل اختبار', 'ابي احد يحل اختبار',
    'من يحل اختبار', 'مين يحل اختبار', 'اختبار اونلاين', 'اختبار الكتروني',
    'امتحان', 'امتحانات', 'كويز', 'كويزات', 'quiz', 'quizzes', 'mid', 'ميد',
    'final', 'فاينل', 'اختبار نهائي', 'اختبار نصفي', 'حل واجب', 'حل واجبات',
    'واجب', 'واجبات', 'تكليف', 'تكاليف', 'اسايمنت', 'assignment', 'assignments',
    'نشاط', 'انشطة', 'مشروع مادة', 'مشروع', 'مشاريع', 'مشروع تخرج', 'تخرج',
    'بحث', 'بحوث', 'بحث علمي', 'ورقة بحثية', 'تقرير', 'تقارير', 'رسالة ماجستير',
    'رسالة دكتوراه', 'تلخيص', 'ملخص', 'ملخصات', 'تلخيص كتاب', 'تلخيص محاضرات',
    'تلخيص مقرر', 'ترجمة', 'مترجم', 'ترجمة بحث', 'ترجمة ملف', 'ترجمة pdf',
    'ترجمة انجليزي', 'ترجمة عربي', 'بوربوينت', 'باوربوينت', 'powerpoint', 'ppt',
    'عرض تقديمي', 'برزنتيشن', 'presentation', 'سلايدات', 'شرائح', 'تصميم', 'مصمم',
    'تصميم احترافي', 'تصميم اعلان', 'تصميم بوستر', 'تصميم شعار', 'تصميم لوجو',
    'انفوجرافيك', 'بروشور', 'سيرة ذاتية', 'cv', 'سي في', 'تصميم cv', 'كتابة cv',
    'تعديل cv', 'السيرة الذاتية', 'وورد', 'word', 'اكسل', 'excel', 'pdf',
    'بي دي اف', 'برمجة', 'موقع', 'مواقع', 'تطبيق', 'تطبيقات', 'كود', 'اكواد',
    'مشروع برمجي', 'مشروع تخرج برمجة', 'حل اسايمنت', 'حل تكليف', 'حل نشاط',
    'حل مشروع', 'سوي لي مشروع', 'سوي لي بحث', 'سوي لي تقرير', 'سوي لي واجب',
    'سوي لي عرض', 'سوي لي بوربوينت', 'سوي لي cv', 'ابغى حل', 'ابي حل',
    'احتاج حل', 'محتاج حل', 'ابي احد يساعدني', 'احتاج من يسوي', 'من تتعامل',
    'مين تتعامل', 'دلوني', 'دلوني على احد', 'عندكم احد', 'تعرفون احد', 'تعرفوا احد',
    'يسوي سكليف', 'سكليف', 'sick leave', 'اجازة مرضية', 'صحتي', 'حد يعرف',
    'من يعرف', 'مين يعرف', 'احد يعرف', 'في احد يعرف', 'في حد يعرف', 'من يسوي',
    'مين يسوي', 'حد يسوي', 'احد يسوي', 'من يقدر', 'مين يقدر',
}

# ========== قاموس تصحيح الأخطاء الإملائية ==========
SPELLING_FIX = {
    'بربوينت': 'بوربوينت', 'بوربينت': 'بوربوينت', 'بوربوينت': 'بوربوينت', 'باوربونت': 'بوربوينت',
    'وجب': 'واجب', 'وجبات': 'واجبات', 'واجب': 'واجب',
    'بحت': 'بحث', 'بحوث': 'بحوث', 'بحث': 'بحث',
    'مشروع': 'مشروع', 'مشاريع': 'مشاريع', 'مشروع': 'مشروع',
    'تقارير': 'تقارير', 'تقرير': 'تقرير', 'تقارير': 'تقارير',
    'اكسل': 'اكسل', 'اكسيل': 'اكسل', 'excel': 'excel',
    'سيره': 'سيرة', 'سيفي': 'سي في', 'cv': 'cv',
    'بوربوينت': 'بوربوينت', 'برزنتيشن': 'برزنتيشن', 'برسنتيشن': 'برزنتيشن',
    'سكليف': 'سكليف', 'سكلبف': 'سكليف', 'sick': 'sick',
    'مونتج': 'مونتاج', 'مونتاج': 'مونتاج', 'مونتاچ': 'مونتاج',
    'تصميم': 'تصميم', 'تصمام': 'تصميم', 'تصمم': 'تصميم',
}

# ========== مرادفات الطلب ==========
REQUEST_SYNONYMS = [
    'ابي', 'ابغى', 'ابغي', 'أبي', 'أبغى', 'أبغي', 'اريد', 'أريد',
    'احتاج', 'أحتاج', 'محتاج', 'محتاجة', 'محتاجه', 'بغيت', 'بغيت',
    'اللي', 'اللي عنده', 'اللي تعرف', 'اللي يعرف', 'من عنده',
    'من يعرف', 'من تعرف', 'مين يعرف', 'مين تعرف', 'مين عنده',
    'حد يعرف', 'حد عنده', 'أحد يعرف', 'أحد عنده', 'فيه أحد',
    'في احد', 'فيه حد', 'عندكم', 'عندك', 'تدلوني', 'يدلني',
]

# ========== تصنيفات الرسائل ==========
CATEGORIES = {
    'اختبار': {'اختبار','امتحان','كويز','quiz','ميد','فاينل','mid','final','exam','test'},
    'واجب': {'واجب','تكليف','اسايمنت','assignment','homework','hw'},
    'مشروع': {'مشروع','تخرج','project','graduation'},
    'بحث': {'بحث','تقرير','research','report','thesis'},
    'تلخيص': {'تلخيص','ملخص','summary'},
    'ترجمة': {'ترجمة','translate','translation'},
    'بوربوينت': {'بوربوينت','powerpoint','presentation','عرض'},
    'تصميم': {'تصميم','design','logo','مصمم','فيديو','مونتاج'},
    'cv': {'cv','سيرة ذاتية','resume','سي في'},
    'برمجة': {'برمجة','برمج','programming','code','موقع','تطبيق'},
    'سكليف': {'سكليف','sick leave','اجازة مرضية','sick','تقرير طبي'},
    'عام': set(),
}

CATEGORY_COLORS = {
    'اختبار': '🔴', 'واجب': '🟢', 'مشروع': '🔵',
    'بحث': '🟣', 'تلخيص': '🟡', 'ترجمة': '🟠',
    'بوربوينت': '⚫', 'تصميم': '🔘', 'cv': '🟤',
    'برمجة': '⚪', 'سكليف': '🩺', 'عام': '📌',
}

# ========== إعدادات البوت ==========
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

def is_developer(user_id):
    if DEVELOPER_ID and user_id == DEVELOPER_ID:
        return True
    return False

def normalize_text(text):
    """تطبيع النص: توحيد الحروف العربية/الإنجليزية"""
    if not text:
        return ""
    text = text.lower()
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    text = text.replace('ة', 'ه')
    text = text.replace('ى', 'ي')
    return text

def fix_spelling(text):
    """تصحيح الأخطاء الإملائية الشائعة"""
    words = text.split()
    fixed_words = []
    for word in words:
        word_lower = word.lower()
        if word_lower in SPELLING_FIX:
            fixed_words.append(SPELLING_FIX[word_lower])
        else:
            fixed_words.append(word)
    return ' '.join(fixed_words)

def detect_intent(text):
    """
    كشف نية الرسالة - تحليل ذكي
    يرجع: ('request', confidence) أو ('ad', confidence) أو ('question', confidence)
    """
    text_normalized = normalize_text(text)
    
    # مؤشرات الطلب
    request_score = 0
    for syn in REQUEST_SYNONYMS:
        if normalize_text(syn) in text_normalized:
            request_score += 1
    
    # مؤشرات الإعلان
    ad_score = 0
    ad_indicators = ['للتواصل', 'واتساب', 'wa.me', 'للطلب', 'نوفر', 'نقدم', 'خصم', 'تخفيض', 'لفترة محدودة', 'الكمية محدودة']
    for ind in ad_indicators:
        if normalize_text(ind) in text_normalized:
            ad_score += 1
    
    # مؤشرات الخدمات الطلابية
    service_keywords = ['واجب', 'بحث', 'مشروع', 'اختبار', 'بوربوينت', 'برزنتيشن', 'تلخيص', 'ترجمة', 'تصميم', 'سكليف']
    service_score = 0
    for kw in service_keywords:
        if kw in text_normalized:
            service_score += 1
    
    # تحليل النية النهائي
    if ad_score > request_score and len(text) > 150:
        return ('ad', 0.8)
    elif request_score >= 1 and service_score >= 1:
        return ('request', 0.9)
    elif request_score >= 1:
        return ('request', 0.6)
    elif service_score >= 1:
        return ('request', 0.5)
    elif '?' in text or 'سؤال' in text or 'استفسار' in text:
        return ('question', 0.7)
    else:
        return ('unknown', 0.3)

def is_ad(text):
    """فلتر ذكي للإعلانات"""
    if not text:
        return False
    
    text_lower = text.lower()
    intent, confidence = detect_intent(text)
    
    # إذا كان إعلان بثقة عالية
    if intent == 'ad' and confidence >= 0.7:
        return True
    
    # فحص الأنماط المعروفة
    for pattern in AD_PATTERNS + LEARNED_AD_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    
    # فحص الرسائل الطويلة جداً (غالباً إعلانات)
    if len(text) > 300:
        promo_words = ['خدمات', 'فريق', 'دكتور', 'رسائل', 'الماجستير', 'الدكتوراه', 'تحليل', 'تنسيق', 'ترجمه', 'توفير', 'المراجع', 'التواصل', 'خبرة', 'متخصص', 'محترف']
        promo_count = sum(1 for word in promo_words if word in text_lower)
        if promo_count >= 3:
            return True
    
    return False

def get_category(keyword):
    kw_lower = keyword.lower()
    for cat, words in CATEGORIES.items():
        if cat == 'عام':
            continue
        for w in words:
            if w.lower() in kw_lower:
                return cat
    return 'عام'

def check_keywords_fast(text):
    """
    بحث ذكي مع تصحيح إملائي وفهم السياق
    """
    if not text:
        return None
    
    # تصحيح الأخطاء الإملائية
    fixed_text = fix_spelling(text)
    text_lower = fixed_text.lower()
    
    # البحث في الكلمات المفتاحية
    for kw in KEYWORDS_SET:
        if kw.lower() in text_lower:
            return kw
    
    # بحث ذكي: لو ما لقى تطابق كامل، يدور على كلمات مفتاحية أصغر
    smart_keywords = ['ابي', 'ابغى', 'محتاج', 'احتاج', 'بغيت', 'اريد', 'من يسوي', 'مين يسوي', 'حد يسوي']
    for kw in smart_keywords:
        if kw.lower() in text_lower:
            # تأكد إن فيه طلب خدمة حقيقي
            intent, confidence = detect_intent(text)
            if intent == 'request' and confidence >= 0.5:
                return kw
    
    return None

async def get_group_link(chat):
    try:
        if hasattr(chat, 'username') and chat.username:
            return "https://t.me/" + str(chat.username)
    except:
        pass
    return None

# ========== الحدث الرئيسي للبوت ==========
async def main():
    print("🚀 البوت الذكي يعمل والفلتر المتطور للإعلانات نشط...")
    print(f"👑 المطور: {DEVELOPER}")
    await client.start()
    print("✅ تم تسجيل الدخول بنجاح!")

    @client.on(events.NewMessage)
    async def handler(event):
        chat = await event.get_chat()
        
        # ========== نظام الأوامر في القناة الخاصة ==========
        if hasattr(chat, 'id') and chat.id == TARGET_CHANNEL:
            text = event.raw_text or ""
            sender = await event.get_sender()
            user_id = sender.id
            
            if text.startswith('/'):
                parts = text.split(' ', 1)
                command = parts[0].lower()
                argument = parts[1] if len(parts) > 1 else ""
                
                if command == '/status':
                    msg = f"""
🤖 **حالة البوت الذكي**
👑 المطور: **{DEVELOPER}**
📊 الكلمات المفتاحية: **{len(KEYWORDS_SET)}**
🛡 أنماط حظر الإعلانات: **{len(AD_PATTERNS)}**
🧠 أنماط متعلمة: **{len(LEARNED_AD_PATTERNS)}**
✅ البوت يعمل بكفاءة
                    """
                    await client.send_message(TARGET_CHANNEL, msg)
                    return
                
                elif command == '/addkw' and argument:
                    if argument not in KEYWORDS_SET:
                        KEYWORDS_SET.add(argument)
                        await client.send_message(TARGET_CHANNEL, f"✅ **تمت إضافة الكلمة:** `{argument}`\n👑 بواسطة: {DEVELOPER}")
                    else:
                        await client.send_message(TARGET_CHANNEL, f"⚠️ الكلمة `{argument}` موجودة مسبقاً")
                    return
                
                elif command == '/delkw' and argument:
                    if argument in KEYWORDS_SET:
                        KEYWORDS_SET.remove(argument)
                        await client.send_message(TARGET_CHANNEL, f"🗑 **تم حذف الكلمة:** `{argument}`\n👑 بواسطة: {DEVELOPER}")
                    else:
                        await client.send_message(TARGET_CHANNEL, f"⚠️ الكلمة `{argument}` غير موجودة")
                    return
                
                elif command == '/listkw':
                    kw_list = "\n".join([f"• `{kw}`" for kw in sorted(KEYWORDS_SET)])
                    if len(kw_list) > 4000:
                        kw_list = kw_list[:4000] + "\n... (تم الاختصار)"
                    await client.send_message(TARGET_CHANNEL, f"📋 **الكلمات المفتاحية ({len(KEYWORDS_SET)}):**\n{kw_list}\n\n👑 المطور: {DEVELOPER}")
                    return
                
                elif command == '/addad' and argument:
                    if argument not in AD_PATTERNS:
                        AD_PATTERNS.append(argument)
                        await client.send_message(TARGET_CHANNEL, f"✅ **تمت إضافة نمط إعلان:** `{argument}`\n👑 بواسطة: {DEVELOPER}")
                    else:
                        await client.send_message(TARGET_CHANNEL, f"⚠️ النمط `{argument}` موجود مسبقاً")
                    return
                
                elif command == '/delad' and argument:
                    if argument in AD_PATTERNS:
                        AD_PATTERNS.remove(argument)
                        await client.send_message(TARGET_CHANNEL, f"🗑 **تم حذف نمط إعلان:** `{argument}`\n👑 بواسطة: {DEVELOPER}")
                    elif argument in LEARNED_AD_PATTERNS:
                        LEARNED_AD_PATTERNS.remove(argument)
                        await client.send_message(TARGET_CHANNEL, f"🗑 **تم حذف نمط متعلم:** `{argument}`\n👑 بواسطة: {DEVELOPER}")
                    else:
                        await client.send_message(TARGET_CHANNEL, f"⚠️ النمط `{argument}` غير موجود")
                    return
                
                elif command == '/listad':
                    ad_list = "\n".join([f"• `{ad}`" for ad in AD_PATTERNS])
                    learned_list = "\n".join([f"🧠 `{ad}`" for ad in LEARNED_AD_PATTERNS])
                    msg = f"🛡 **أنماط حظر الإعلانات ({len(AD_PATTERNS)}):**\n{ad_list}"
                    if LEARNED_AD_PATTERNS:
                        msg += f"\n\n🧠 **أنماط متعلمة ({len(LEARNED_AD_PATTERNS)}):**\n{learned_list}"
                    msg += f"\n\n👑 المطور: {DEVELOPER}"
                    await client.send_message(TARGET_CHANNEL, msg)
                    return
                
                elif command == '/analyze' and argument:
                    intent, confidence = detect_intent(argument)
                    await client.send_message(TARGET_CHANNEL, f"🔍 **تحليل النص:**\n📝 النص: `{argument}`\n🎯 النية: **{intent}**\n📊 الثقة: **{confidence*100:.0f}%**")
                    return
                
                elif command == '/help' or command == '/start':
                    help_msg = f"""
🤖 **أوامر تحكم البوت الذكي** - 👑 {DEVELOPER}

📌 **إدارة الكلمات المفتاحية:**
`/addkw كلمة` - إضافة كلمة مفتاحية
`/delkw كلمة` - حذف كلمة مفتاحية
`/listkw` - عرض كل الكلمات

🛡 **إدارة فلتر الإعلانات:**
`/addad نمط` - إضافة نمط إعلان
`/delad نمط` - حذف نمط إعلان
`/listad` - عرض أنماط الحظر

🧠 **أوامر الذكاء:**
`/analyze نص` - تحليل نية النص

⚙️ **أوامر عامة:**
`/status` - حالة البوت
`/help` - هذه القائمة
                    """
                    await client.send_message(TARGET_CHANNEL, help_msg)
                    return                
                return
        
        # ========== نظام التقاط الطلبات من المجموعات ==========
        if not event.is_group:
            return
        
        text = event.raw_text or ""
        if not text:
            return
        
        # تحليل النية
        intent, confidence = detect_intent(text)
        
        # حظر الإعلانات
        if is_ad(text):
            # تعلم نمط جديد لو كان إعلان غير معروف
            if intent == 'ad' and confidence >= 0.8:
                # استخراج كلمات مفتاحية من الإعلان
                words = text.lower().split()
                for i in range(len(words)-2):
                    phrase = ' '.join(words[i:i+3])
                    if len(phrase) > 15 and phrase not in AD_PATTERNS and phrase not in LEARNED_AD_PATTERNS:
                        if any(ad_word in phrase for ad_word in ['خصم', 'تخفيض', 'عرض', 'تواصل', 'خدماتنا', 'فريقنا']):
                            LEARNED_AD_PATTERNS.append(phrase)
                            print(f"🧠 تعلمت نمط إعلان جديد: {phrase}")
                            break
            return
        
        # لا تلتقط الأسئلة العامة
        if intent == 'question':
            return
        
        # لا تلتقط لو الثقة منخفضة جداً
        if intent == 'unknown' and confidence < 0.5:
            return
        
        # البحث عن الكلمات المفتاحية
        keyword = check_keywords_fast(text)
        
        if keyword:
            sender = await event.get_sender()
            group_name = getattr(chat, 'title', 'مجموعة غير معروفة')
            group_link = await get_group_link(chat)
            
            first = getattr(sender, 'first_name', '') or ''
            last = getattr(sender, 'last_name', '') or ''
            full_name = (first + ' ' + last).strip() or 'مجهول'
            username = sender.username
            user_id = sender.id
            
            user_display = "[" + full_name + "](tg://user?id=" + str(user_id) + ")"
            
            if group_link:
                group_display = "[" + group_name + "](" + group_link + ")"
            else:
                group_display = group_name
            
            category = get_category(keyword)
            color = CATEGORY_COLORS.get(category, '📌')
            
            if len(text) > 400:
                short_text = text[:400] + "\n... (تم اختصار الرسالة)"
            else:
                short_text = text
            
            msg = ""
            msg += color + " **طلب جديد - " + category + "**\n\n"
            msg += "📌 **الكلمة المفتاحية:** `" + keyword + "`\n"
            msg += "📂 **التصنيف:** " + category + "\n"
            msg += "🎯 **نية الرسالة:** طلب خدمة\n\n"
            msg += "👤 **المرسل:** " + user_display + "\n"
            
            if username:
                msg += "🔹 **اليوزر:** @" + username + "\n"
            else:
                msg += "🔹 **اليوزر:** لا يوجد\n"
                
            msg += "🆔 **الايدي:** `" + str(user_id) + "`\n\n"
            msg += "💬 **المجموعة:** " + group_display + "\n\n"
            msg += "📝 **الرسالة:**\n```\n"
            msg += short_text
            msg += "\n```\n\n"
            msg += "⏰ **الوقت:** " + str(event.date.strftime('%Y-%m-%d %H:%M:%S'))
            msg += f"\n\n👑 المطور: {DEVELOPER}"
            
            try:
                await client.send_message(TARGET_CHANNEL, msg, link_preview=False)
                print("✅ [طلب طالب حقيقي] " + full_name + " | " + keyword)
            except Exception as e:
                print("❌ خطأ: " + str(e))

    await client.run_until_disconnected()

# ========== سيرفر الويب للبقاء على قيد الحياة ==========
app = Flask(__name__)

@app.route('/')
def home():
    return f"🤖 البوت الذكي يعمل بكفاءة 24/7! | 👑 المطور: {DEVELOPER}"

def run_web_server():
    app.run(host='0.0.0.0', port=10000)

# ========== التشغيل المباشر ==========
if __name__ == '__main__':
    Thread(target=run_web_server).start()
    asyncio.run(main())
