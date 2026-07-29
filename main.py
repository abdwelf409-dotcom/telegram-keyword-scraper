const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason,
    fetchLatestBaileysVersion
} = require('@whiskeysockets/baileys');
const { Boom } = require('@hapi/boom');
const P = require('pino');
const fs = require('fs-extra');
const path = require('path');

// ==================== إعدادات الملفات ====================
const configPath = './config.json';
const sessionsPath = './sessions.json';
const groupsPath = './groups.json';

// ==================== إعدادات الحسابات والأدمن ====================
const SOLE_ADMIN_NUMBER = "967771048364"; // الأدمن الرئيسي للتحكم بالأوامر
const ALL_BOT_ACCOUNTS = [
    "967771048364",
    "966552725737",
  
]; // الحسابات النشطة للبوت

// متغير عام للتحكم في إيقاف الإعلانات أثناء إرسالها
let isAdvertisingActive = false;

// ==================== قائمة الكلمات المفتاحية للالتقاط (المرحلة الأولى) ====================
const defaultKeywords = [
    // طلبات بحوث ومشاريع وأكاديمية
    "بنات تعرفون حد يسوي بحوث تخرج", "بنات تعرفون حد يسوي مشاريع", "بنات تعرفون حد يسوي سكليف", "بنات تعرفون حد يسوي عرض",
    "بنات تعرفون حد يسوي برزنتيشن", "بنات تعرفون أحد يسوي بحوث", "بنات تعرفون أحد يسوي مشروع", "بنات تعرفون أحد يسوي واجبات",
    "بنات تعرفون أحد يسوي تقارير", "بنات تعرفون أحد يسوي عروض", "بنات تعرفون أحد يسوي برزنتيشن", "بنات بغيت حد فاهم في البحوث",
    "بنات محتاجة حد يسوي لي الواجب", "بنات ساعدوني أبي خدمات طلابية", "تعرفون أحد يسوي بحوث", "تعرفون أحد يسوي مشروع",
    "تعرفون أحد يسوي واجبات", "تعرفون أحد يسوي سكليف", "تعرفون أحد يسوي برزنتيشن", "تعرفون أحد يسوي عروض بوربوينت",
    "تعرفون أحد يسوي كل التكاليف", "تعرفون أحد مضمون", "من يعرف حد يسوي واجبات", "من يعرف حد يسوي مشاريع",
    "من يعرف حد يسوي بحوث", "من يعرف حد يسوي تقارير", "من يعرف حد يسوي عروض", "من يعرف حد يسوي برزنتيشن",
    "من يعرف حد يسوي سكليف", "من تعرف وحدة تسوي تكاليف", "من تعرف وحدة ممتازة", "من يسوي واجبات", "من يسوي مشاريع",
    "من يسوي بحوث", "من يسوي تقارير", "من يسوي تلخيص", "من يسوي اختبارات", "من يسوي تقرير تدريب", "من يسوي مشروع تخرج",
    "من يسوي عروض احترافية", "من يسوي Excel", "من يسوي Access", "من يسوي APA", "من عندها رقم خدمات طلابية",
    "من عندها شخص مجرب", "من عنده شخص ثقة للخدمات الطلابية", "حد عنده حد ثقة يسوي واجبات", "حد عنده حد ثقة يسوي مشاريع",
    "حد عنده حد ثقة يسوي بحوث", "حد عنده حد ثقة يسوي سكليف", "حد عنده حد ثقة يسوي تقارير", "حد عنده مصمم فيديو",
    "حد عنده مصمم دعوات", "حد يعرف أحد يحل واجبات", "حد يعرف أحد يحل اختبارات", "حد يعرف أحد يسوي مشاريع",
    "حد يعرف أحد يسوي بحوث", "حد يعرف أحد يسوي عروض", "حد يعرف أحد يصمم فيديو", "حد يعرف أحد يصمم دعوة زواج",
    "أحد يعرف خدمات طلابية", "أحد عنده خدمات طلابية", "أحد عنده رقم وحدة تسوي بحوث", "أحد مجرب خدمات طلابية",
    "أحد يسوي واجبات", "أحد يسوي Word", "أحد يضمن الدرجة", "أحد متفرغ اليوم", "أبي حد يسوي واجبات", "أبي حد يسوي مشاريع",
    "أبي حد يسوي بحث", "أبي حد يسوي سكليف", "أبي حد يسوي تقرير", "أبي حد يسوي عرض بوربوينت", "أبي حد يسوي برزنتيشن",
    "أبي حد يسوي تكليف", "أبي أحد يسوي مشروع", "أبي أحد يسوي مشروع تخرج", "أبي أحد يسوي واجبات", "أبي أحد يسوي بحث",
    "أبي أحد يكتب بحث كامل", "أبي أحد يسوي برزنتيشن", "أبي أحد يسوي عرض بوربوينت", "أبي أحد يسوي سكليف",
    "أبي أحد يسوي تقرير", "أبي أحد يسوي مشاريع الجامعة", "أبي أحد يخلص المشروع كامل", "أبي أحد يخلص الأبحاث",
    "أبي أحد يخلص التكليف", "أبي أحد يخلص واجبات الجامعة", "أبي أحد يخلص لي الواجب", "أبي أحد يخلص لي المشروع",
    "أبي أحد يخلص لي البحث", "أبي أحد يخلص لي كل موادي", "أبي أحد يحل الكويز", "أبي أحد يحل الاختبار",
    "أبي أحد ينجز اليوم", "أبي أحد يخلص قبل الموعد", "أبي أحد شغله احترافي", "أبي أحد شغله مضمون",
    "أبي أحد أسعاره مناسبة", "أبي شخص ثقة", "أبي شخص مضمون", "أبي شغل مرتب وسريع", "أبي خدمات جامعية كاملة",
    "أبي تنسيق بحث", "أبي تدقيق لغوي", "محتاج حد يسوي لي واجبات", "محتاجة حد يسوي لي الواجب", "محتاجة حد يسوي لي مشروع",
    "محتاجة حد يسوي لي بحث", "محتاجة أحد يسوي بحث", "محتاجة أحد يخلص التكليف", "يعيال حد عنده أحد ثقة",
    "يعيال من يعرف أحد يسوي واجبات", "يعيال من يعرف أحد يسوي مشاريع", "يعيال من يعرف أحد يسوي بحوث",
    "ابغي حد يسوي بحوث", "ابغي حد يسوي برزنتيشن", "ابغي حد يسوي بوربوينت", "ابغي حد يسوي تقرير",
    "ابغي حد يسوي مشروع", "ابغي حد يسوي واجبات", "ابغي حد يسوي تكاليف", "ابغي حد يسوي سكليف",
    "ابغي حد يسوي عرض", "بغيت حد فاهم في البحوث", "بغيت حد فاهم في المشاريع", "بغيت حد فاهم في التقارير",
    "بغيت حد ثقة", "ابي حد", "ابي احد", "احتاج احد", "احتاج شخص", "ابي شخص", "حد يعرف", "من يعرف", "مين يعرف", 
    "احد يعرف", "في احد يعرف", "في حد يعرف", "من يسوي", "مين يسوي", "حد يسوي", "احد يسوي", "من يقدر", 
    "مين يقدر", "يساعدني", "مساعدة", "خدمات طلابية", "خدمة طلابية", "حل اختبار", "حل اختبارات", 
    "ابي حل اختبار", "ابي احد يحل اختبار", "من يحل اختبار", "مين يحل اختبار", "اختبار اونلاين", 
    "اختبار الكتروني", "امتحان", "امتحانات", "كويز", "كويزات", "quiz", "quizzes", "mid", "ميد", 
    "final", "فاينل", "اختبار نهائي", "اختبار نصفي", "حل واجب", "حل واجبات", "واجب", "واجبات", 
    "تكليف", "تكاليف", "اسايمنت", "assignment", "assignments", "نشاط", "انشطة", "مشروع مادة", 
    "مشروع", "مشاريع", "مشروع تخرج", "تخرج", "بحث", "بحوث", "بحث علمي", "ورقة بحثية", "تقرير", 
    "تقارير", "رسالة ماجستير", "رسالة دكتوراه", "تلخيص", "ملخص", "ملخصات", "تلخيص كتاب", 
    "تلخيص محاضرات", "تلخيص مقرر", "ترجمة", "مترجم", "ترجمة بحث", "ترجمة ملف", "ترجمة pdf", 
    "ترجمة انجليزي", "ترجمة عربي", "بوربوينت", "باوربوينت", "powerpoint", "ppt", "عرض تقديمي", 
    "برزنتيشن", "presentation", "سلايدات", "شرائح", "تصميم", "مصمم", "تصميم احترافي", "تصميم اعلان", 
    "تصميم بوستر", "تصميم شعار", "تصميم لوجو", "انفوجرافيك", "بروشور", "سيرة ذاتية", "cv", "سي في", 
    "تصميم cv", "كتابة cv", "تعديل cv", "السيرة الذاتية", "وورد", "word", "اكسل", "excel", "pdf", 
    "بي دي اف", "برمجة", "موقع", "م مواقع", "تطبيق", "تطبيقات", "كود", "اكواد", "مشروع برمجي", 
    "مشروع تخرج برمجة", "حل اسايمنت", "حل تكليف", "حل نشاط", "حل مشروع", "سوي لي مشروع", 
    "سوي لي بحث", "سوي لي تقرير", "سوي لي واجب", "سوي لي عرض", "سوي لي بوربوينت", "سوي لي cv", 
    "ابغى حل", "ابي حل", "احتاج حل", "محتاج حل", "ابي احد يساعدني", "احتاج من يسوي", "من تتعامل", 
    "مين تتعامل", "دلوني", "دلوني على احد", "عندكم احد", "تعرفون احد", "تعرفوا احد", "يسوي سكليف", 
    "سكليف", "sick leave", "اجازة مرضية", "صحتي",

    // تصميم ومونتاج وشعارات
    "ابي حد يصمم لي فيديو", "ابي حد يسوي مونتاج", "ابي حد يصمم لي مونتاج", "ابي حد يصمم لي دعوة زواج",
    "ابي حد يصمم لي دعوة", "ابي حد يصمم اعلان", "ابي حد يصمم بوستر", "ابي حد يصمم شعار", "ابي حد يصمم لوجو",
    "ابي حد يصمم هوية بصرية", "ابي حد يصمم انفوجرافيك", "ابي حد يصمم سيرة ذاتية", "ابي حد يصمم برزنتيشن",
    "ابي حد يسوي تصميم احترافي", "ابي حد يمنتج فيديو", "ابي حد يسوي موشن جرافيك", "ابي حد يصمم ريلز",
    "ابي حد يصمم سناب", "ابي حد يصمم منشورات", "ابي حد يصمم بطاقة دعوة", "من يعرف مصمم فيديو",
    "من يعرف مصمم دعوات", "من يعرف مصمم ثقة", "بنات تعرفون مصمم فيديو", "بنات تعرفون أحد يصمم دعوات",

    // البرامج البرمجية والمكتبية
    "من يسوي اكسل", "من يسوي Excel", "أبي أحد يسوي اكسل", "أبي أحد يسوي Excel", "أبي حد يسوي اكسل",
    "أبي حد يسوي Excel", "ابغي حد يسوي اكسل", "ابغي حد يسوي Excel", "من يعرف أحد يسوي اكسل",
    "من يعرف أحد يسوي Excel", "تعرفون أحد يسوي اكسل", "تعرفون أحد يسوي Excel", "حد يسوي اكسل",
    "حد يسوي Excel", "أحد يسوي اكسل", "أحد يسوي Excel", "محتاج أحد يسوي اكسل", "محتاجة أحد يسوي اكسل",
    "بنات تعرفون أحد يسوي اكسل", "يعيال من يسوي اكسل", "من يسوي باوربوينت", "من يسوي بوربوينت",
    "أبي أحد يسوي باوربوينت", "أبي أحد يسوي بوربوينت", "ابغي حد يسوي باوربوينت", "ابغي حد يسوي بوربوينت",
    "من يعرف أحد يسوي باوربوينت", "من يعرف أحد يسوي بوربوينت", "تعرفون أحد يسوي باوربوينت",
    "تعرفون أحد يسوي بوربوينت", "من يسوي وورد", "من يسوي Word", "أبي أحد يسوي وورد", "أبي أحد يسوي Word",
    "ابغي حد يسوي وورد", "ابغي حد يسوي Word", "من يعرف أحد يسوي وورد", "تعرفون أحد يسوي وورد",
    "من يسوي اكسس", "من يسوي Access", "أبي أحد يسوي اكسس", "ابغي حد يسوي اكسس", "من يعرف أحد يسوي اكسس",
    "تعرفون أحد يسوي اكسس", "من يسوي برزنتيشن احترافي", "من يسوي بوربوينت احترافي",

    // السيرة الذاتية CV
    "أبي أحد يسوي سيرة ذاتية", "من يسوي CV", "من يسوي سيفي", "أبي أحد يسوي CV", "أبي أحد يسوي سيفي",

    // أدوات الطلب المباشرة
    "ابي", "ابغي", "ابغى", "محتاج", "محتاجه", "محتاجة", "بغيت", "اريد", "من يسوي", "مين يسوي", "حد يسوي", "احد يسوي", "من يحل", "من يصمم"
];

// ==================== قائمة مؤشرات الإعلانات والتوصيات (للاستبعاد الصارم) ====================
const adIndicators = [
    "نوفر لكم", "نقدم لكم", "نعلن عن", "خصم", "خصومات", "عرض خاص", "عرض حصري", 
    "تواصل معنا", "للتواصل واتساب", "رابط الجروب", "اشترك الان", "خدماتنا", "فريقنا",
    "اسعار منافسة", "بأرخص الأسعار", "بارخص الاسعار", "ضمان النجاح", "للتواصل على", "تابعونا", "سارع بالحجز",
    "نحن متخصصون", "نحن متخصصي", "متخصصون في", "متخصصي", "للتواصل خاص", "للتواصل ع الخاص", "للتواصل عالخاص",
    "خاص للتواصل", "واتساب للتواصل", "عن تجربه", "عن تجربة", "عن تجريبه", "تجربه موثوقه", "تجربة موثوقة",
    "ذي تحل", "هذي تحل", "هذا يحل", "ذا يحل", "الدفع بعد التسليم", "السعر مناسب", "اسعار مناسبة", "أسعار مناسبة",
    "رقمها", "رقمها بالخاص", "رقم المكتب", "تواصلو معها", "تواصلوا معها", "تواصلو معه", "تواصلوا معه", "تواصل عبر الرابط"
];

// ==================== قاعدة بيانات الرسائل المباشرة المعروفة (المرحلة الثانية) ====================
const KNOWN_DIRECT_MESSAGES = [
    "بنات تعرفون حد يسوي بحوث تخرج", "بنات تعرفون حد يسوي مشاريع", "بنات تعرفون حد يسوي سكليف", "بنات تعرفون حد يسوي عرض",
    "بنات تعرفون حد يسوي برزنتيشن", "بنات تعرفون أحد يسوي بحوث", "بنات تعرفون أحد يسوي مشروع", "بنات تعرفون أحد يسوي واجبات",
    "بنات تعرفون أحد يسوي تقارير", "بنات تعرفون أحد يسوي عروض", "بنات تعرفون أحد يسوي برزنتيشن", "بنات بغيت حد فاهم في البحوث",
    "بنات محتاجة حد يسوي لي الواجب", "بنات ساعدوني أبي خدمات طلابية", "تعرفون أحد يسوي بحوث", "تعرفون أحد يسوي مشروع",
    "تعرفون أحد يسوي واجبات", "تعرفون أحد يسوي سكليف", "تعرفون أحد يسوي برزنتيشن", "تعرفون أحد يسوي عروض بوربوينت",
    "تعرفون أحد يسوي كل التكاليف", "تعرفون أحد مضمون", "من يعرف حد يسوي واجبات", "من يعرف حد يسوي مشاريع",
    "من يعرف حد يسوي بحوث", "من يعرف حد يسوي تقارير", "من يعرف حد يسوي عروض", "من يعرف حد يسوي برزنتيشن",
    "من يعرف حد يسوي سكليف", "من تعرف وحدة تسوي تكاليف", "من تعرف وحدة ممتازة", "من يسوي واجبات", "من يسوي مشاريع",
    "من يسوي بحوث", "من يسوي تقارير", "من يسوي تلخيص", "من يسوي اختبارات", "من يسوي تقرير تدريب", "من يسوي مشروع تخرج",
    "من يسوي عروض احترافية", "من يسوي Excel", "من يسوي Access", "من يسوي APA", "من عندها رقم خدمات طلابية",
    "من عندها شخص مجرب", "من عنده شخص ثقة للخدمات الطلابية", "حد عنده حد ثقة يسوي واجبات", "حد عنده حد ثقة يسوي مشاريع",
    "حد عنده حد ثقة يسوي بحوث", "حد عنده حد ثقة يسوي سكليف", "حد عنده حد ثقة يسوي تقارير", "حد عنده مصمم فيديو",
    "حد عنده مصمم دعوات", "حد يعرف أحد يحل واجبات", "حد يعرف أحد يحل اختبارات", "حد يعرف أحد يسوي مشاريع",
    "حد يعرف أحد يسوي بحوث", "حد يعرف أحد يسوي عروض", "حد يعرف أحد يصمم فيديو", "حد يعرف أحد يصمم دعوة زواج",
    "أحد يعرف خدمات طلابية", "أحد عنده خدمات طلابية", "أحد عنده رقم وحدة تسوي بحوث", "أحد مجرب خدمات طلابية",
    "أحد يسوي واجبات", "أحد يسوي Word", "أحد يضمن الدرجة", "أحد متفرغ اليوم", "أبي حد يسوي واجبات", "أبي حد يسوي مشاريع",
    "أبي حد يسوي بحث", "أبي حد يسوي سكليف", "أبي حد يسوي تقرير", "أبي حد يسوي عرض بوربوينت", "أبي حد يسوي برزنتيشن",
    "أبي حد يسوي تكليف", "أبي أحد يسوي مشروع", "أبي أحد يسوي مشروع تخرج", "أبي أحد يسوي واجبات", "أبي أحد يسوي بحث",
    "أبي أحد يكتب بحث كامل", "أبي أحد يسوي برزنتيشن", "أبي أحد يسوي عرض بوربوينت", "أبي أحد يسوي سكليف",
    "أبي أحد يسوي تقرير", "أبي أحد يسوي مشاريع الجامعة", "أبي أحد يخلص المشروع كامل", "أبي أحد يخلص الأبحاث",
    "أبي أحد يخلص التكليف", "أبي أحد يخلص واجبات الجامعة", "أبي أحد يخلص لي الواجب", "أبي أحد يخلص لي المشروع",
    "أبي أحد يخلص لي البحث", "أبي أحد يخلص لي كل موادي", "أبي أحد يحل الكويز", "أبي أحد يحل الاختبار",
    "أبي أحد ينجز اليوم", "أبي أحد يخلص قبل الموعد", "أبي أحد شغله احترافي", "أبي أحد شغله مضمون",
    "أبي أحد أسعاره مناسبة", "أبي شخص ثقة", "أبي شخص مضمون", "أبي شغل مرتب وسريع", "أبي خدمات جامعية كاملة",
    "أبي تنسيق بحث", "أبي تدقيق لغوي", "محتاج حد يسوي لي واجبات", "محتاجة حد يسوي لي الواجب", "محتاجة حد يسوي لي مشروع",
    "محتاجة حد يسوي لي بحث", "محتاجة أحد يسوي بحث", "محتاجة أحد يخلص التكليف", "يعيال حد عنده أحد ثقة",
    "يعيال من يعرف أحد يسوي واجبات", "يعيال من يعرف أحد يسوي مشاريع", "يعيال من يعرف أحد يسوي بحوث",
    "ابغي حد يسوي بحوث", "ابغي حد يسوي برزنتيشن", "ابغي حد يسوي بوربوينت", "ابغي حد يسوي تقرير",
    "ابغي حد يسوي مشروع", "ابغي حد يسوي واجبات", "ابغي حد يسوي تكاليف", "ابغي حد يسوي سكليف",
    "ابغي حد يسوي عرض", "بغيت حد فاهم في البحوث", "بغيت حد فاهم في المشاريع", "بغيت حد فاهم في التقارير",
    "بغيت حد ثقة", "ابي حد يصمم لي فيديو", "ابي حد يسوي مونتاج", "ابي حد يصمم لي مونتاج", "ابي حد يصمم لي دعوة زواج",
    "ابي حد يصمم لي دعوة", "ابي حد يصمم اعلان", "ابي حد يصمم بوستر", "ابي حد يصمم شعار", "ابي حد يصمم لوجو",
    "ابي حد يصمم هوية بصرية", "ابي حد يصمم انفوجرافيك", "ابي حد يصمم بروشور", "ابي حد يصمم سيرة ذاتية",
    "ابي حد يصمم برزنتيشن", "ابي حد يسوي تصميم احترافي", "ابي حد يمنتج فيديو", "ابي حد يسوي موشن جرافيك",
    "ابي حد يصمم ريلز", "ابي حد يصمم سناب", "ابي حد يصمم منشورات", "ابي حد يصمم بطاقة دعوة",
    "من يعرف مصمم فيديو", "من يعرف مصمم دعوات", "من يعرف مصمم ثقة", "بنات تعرفون مصمم فيديو",
    "بنات تعرفون أحد يصمم دعوات", "من يسوي اكسل", "من يسوي Excel", "أبي أحد يسوي اكسل",
    "أبي أحد يسوي Excel", "أبي حد يسوي اكسل", "أبي حد يسوي Excel", "ابغي حد يسوي اكسل",
    "ابغي حد يسوي Excel", "من يعرف أحد يسوي اكسل", "من يعرف أحد يسوي Excel", "تعرفون أحد يسوي اكسل",
    "تعرفون أحد يسوي اكسل", "حد يسوي اكسل", "حد يسوي Excel", "أحد يسوي اكسل", "أحد يسوي Excel",
    "محتاج أحد يسوي اكسل", "محتاجة أحد يسوي اكسل", "بنات تعرفون أحد يسوي اكسل", "يعيال من يسوي اكسل",
    "من يسوي باوربوينت", "من يسوي بوربوينت", "أبي أحد يسوي باوربوينت", "أبي أحد يسوي بوربوينت",
    "ابغي حد يسوي باوربوينت", "ابغي حد يسوي بوربوينت", "من يعرف أحد يسوي باوربوينت",
    "من يعرف أحد يسوي بوربوينت", "تعرفون أحد يسوي باوربوينت", "تعرفون أحد يسوي بوربوينت",
    "من يسوي وورد", "من يسوي Word", "أبي أحد يسوي وورد", "أبي أحد يسوي Word", "ابغي حد يسوي وورد",
    "ابغي حد يسوي Word", "من يعرف أحد يسوي وورد", "تعرفون أحد يسوي وورد", "من يسوي اكسس",
    "من يسوي Access", "أبي أحد يسوي اكسس", "ابغي حد يسوي اكسس", "من يعرف أحد يسوي اكسس",
    "تعرفون أحد يسوي اكسس", "من يسوي برزنتيشن احترافي", "من يسوي بوربوينت احترافي", "أبي أحد يسوي سيرة ذاتية",
    "من يسوي CV", "من يسوي سيفي", "أبي أحد يسوي CV", "أبي أحد يسوي سيفي"
];

// ==================== تهيئة الملفات والإعدادات ====================
if (!fs.existsSync(configPath)) {
    fs.writeJsonSync(configPath, {
        targetGroup: "",
        monitoringEnabled: true,
        adsEnabled: true,
        autoReplyEnabled: false,
        autoReplyText: "*مرحباً بك!*\n\nتواصل معنا مباشرة عبر الواتساب لتلبية طلبك بسرعة وسهولة 📥:\nhttps://wa.me/966593341070",
        keywords: defaultKeywords,
        ownerNumbers: [SOLE_ADMIN_NUMBER, "967734691582", "967739172238", "966593341070"],
        smartFilter: true,
        adDelay: 2000
    });
} else {
    let cfg = fs.readJsonSync(configPath);
    if (!cfg.ownerNumbers) cfg.ownerNumbers = [SOLE_ADMIN_NUMBER, "967734691582", "967739172238", "966593341070"];
    if (!cfg.ownerNumbers.includes(SOLE_ADMIN_NUMBER)) cfg.ownerNumbers.push(SOLE_ADMIN_NUMBER);
    fs.writeJsonSync(configPath, cfg, { spaces: 2 });
}

if (!fs.existsSync(sessionsPath)) {
    fs.writeJsonSync(sessionsPath, ALL_BOT_ACCOUNTS);
}

if (!fs.existsSync(groupsPath)) {
    fs.writeJsonSync(groupsPath, {
        targetGroups: [],
        excludedGroups: [],
        monitoredGroups: []
    });
}

let config = fs.readJsonSync(configPath);
let activeSessions = fs.readJsonSync(sessionsPath);
let groupsConfig = fs.readJsonSync(groupsPath);

function saveConfig() { fs.writeJsonSync(configPath, config, { spaces: 2 }); }
function saveSessions() { fs.writeJsonSync(sessionsPath, activeSessions, { spaces: 2 }); }
function saveGroups() { fs.writeJsonSync(groupsPath, groupsConfig, { spaces: 2 }); }

const logger = P({ level: 'silent' });
const socks = new Map();

// ==================== 🧹 دالة تنظيف وتوحيد النص (Normalization) ====================
function normalizeText(text) {
    if (!text) return "";
    return text.toLowerCase()
        .replace(/https?:\/\/\S+|www\.\S+|wa\.me\/\S+|t\.me\/\S+/g, '')
        .replace(/@\w+/g, '')
        .replace(/[أإآءئؤ]/g, 'ا')
        .replace(/[ىىىى]/g, 'ي')
        .replace(/ة/g, 'ه')
        .replace(/[\u0300-\u036f\u064b-\u0652]/g, '')
        .replace(/(.)\1{2,}/g, '$1')
        .replace(/[^\w\s\u0600-\u06FF]/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
}

// ==================== 🧠 المرحلة الثالثة: تحليل الأنماط والسياق الذكي NLP ====================
function stage3_NLPCheck(cleanText) {
    const intentVerbs = [
        'ابي', 'ابغي', 'ابغى', 'محتاج', 'محتاجه', 'بغيت', 'اريد', 'درت', 'ادور', 'ابحث',
        'من', 'حد', 'احد', 'مين', 'في حد', 'في احد', 'هل في', 'هل فيه',
        'تعرفون', 'تعرفو', 'تعرف', 'تعرفين', 'عندكم', 'عندك', 'منو',
        'يوجد', 'موجود', 'تكفون', 'ساعدوني', 'يحل', 'يسوي', 'يعمل', 'يكتب', 'يجهز', 'يخلص'
    ].join('|');

    const academicServices = [
        'بحوث', 'بحث', 'بحوثات', 'تخرج', 'مشروع', 'مشاريع', 'تكليف', 'تكاليف', 
        'واجب', 'واجبات', 'تقرير', 'تقارير', 'كويز', 'كويزات', 'اختبار', 'اختبارات', 'ميد', 'فاينل',
        'امتحان', 'امتحانات', 'اسايمنت', 'assignment', 'homework', 'quiz', 'exam',
        'سكليف', 'عذر', 'اعذار', 'عذر طبي', 'سك ليف', 'sick leave',
        'عرض', 'عروض', 'برزنتيشن', 'بوربوينت', 'powerpoint', 'presentation',
        'وورد', 'word', 'اكسل', 'excel', 'اكسس', 'access', 'سيفي', 'cv', 'سيره ذاتيه',
        'تلخيص', 'ملخص', 'ملخصات', 'تدقيق', 'ترجمه', 'صياغه', 'apa', 'تنسيق',
        'خدمات طلابيه', 'خدمه طلابيه', 'خدمات جامعيه',
        'كود', 'برمجه', 'مشروع تخرج', 'قاعده بيانات', 'داتا بيز', 'شبكات', 'امن سيبراني'
    ].join('|');

    const creativeServices = [
        'تصميم', 'مصمم', 'مصممه', 'فيديو', 'مونتاج', 'شعار', 'لوجو', 'logo',
        'دعوه', 'دعوات', 'دعوه زواج', 'انفوجرافيك', 'هويه بصريه',
        'بوستر', 'إعلان', 'اعلان', 'ريلز', 'سناب', 'بطاقه'
    ].join('|');

    const patternDirect = new RegExp(`(${intentVerbs}).{0,35}(${academicServices}|${creativeServices})`, 'i');
    const patternReverse = new RegExp(`(${academicServices}|${creativeServices}).{0,35}(${intentVerbs})`, 'i');
    const patternExplicit = new RegExp(`(خدمات طلابيه|خدمات جامعيه|رقم خدمات|ارقام خدمات|حد ثقه|شخص ثقه)`, 'i');

    return patternDirect.test(cleanText) || patternReverse.test(cleanText) || patternExplicit.test(cleanText);
}

// ==================== ⚙️ خط أنبوب الفلترة المتقدم (Pipeline Filter) ====================
function processMessageThroughPipeline(rawText) {
    if (!rawText || typeof rawText !== 'string') return false;

    // 1. استبعاد النصوص الطويلة جداً
    if (rawText.length > 180) return false;

    // 2. فحص الروابط
    const urlPattern = /https?:\/\/\S+|www\.\S+|wa\.me\/\S+|t\.me\/\S+|chat\.whatsapp\.com\/\S+/i;
    if (urlPattern.test(rawText)) return false;

    // 3. فحص أرقام الهواتف (استبعاد الإعلانات التي تحتوي أرقام التواصل)
    const phonePattern = /(\+?\d{1,4}[\s-]?)?\(?\d{2,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}|\b05\d{8}\b|\b966\d{9}\b|\b967\d{8,9}\b|\b\d{8,14}\b/;
    if (phonePattern.test(rawText)) return false;

    const lowerText = rawText.toLowerCase().trim();

    // 4. استبعاد الإعلانات والتوصيات عبر المؤشرات
    const isAd = adIndicators.some(adWord => lowerText.includes(adWord.toLowerCase()));
    if (isAd) return false;

    // 5. فحص المرحلة الأولى: وجود كلمة مفتاحية
    const activeKeywords = config.keywords || defaultKeywords;
    const hasKeyword = activeKeywords.some(kw => lowerText.includes(kw.toLowerCase()));
    if (!hasKeyword) return false;

    const cleanText = normalizeText(rawText);
    if (!cleanText || cleanText.length < 5) return false;

    // 6. فحص المرحلة الثانية: المطابقة المباشرة مع الجمل المخزنة
    const isDirectMatch = KNOWN_DIRECT_MESSAGES.some(dbMsg => {
        const cleanDbMsg = normalizeText(dbMsg);
        return cleanText.includes(cleanDbMsg) || cleanDbMsg.includes(cleanText);
    });

    if (isDirectMatch) return true;

    // 7. فحص المرحلة الثالثة: تحليل NLP للأنماط والسياق (إذا كانت الفلترة الذكية مفعلة)
    if (!config.smartFilter) return false;
    return stage3_NLPCheck(cleanText);
}

// ==================== الحصول على اسم المجموعة ====================
async function getGroupName(sock, jid) {
    try {
        const metadata = await sock.groupMetadata(jid);
        return metadata.subject || "غير معروف";
    } catch (e) {
        return "غير معروف";
    }
}

// ==================== تنسيق التنبيه ====================
function formatAlert(groupName, pushName, senderSection, phone, messageContent) {
    return `📢 *تنبيه طلب جديد*\n\n` +
           `👥 *المجموعة:* ${groupName}\n` +
           `👤 *الاسم:* ${pushName}\n` +
           `${senderSection}\n` +
           `🤖 *عبر حساب:* ${phone}\n\n` +
           `📝 *الرسالة:* \n${messageContent}`;
}

// ==================== بدء تشغيل الحساب ====================
async function startAccount(phone) {
    if (socks.has(phone)) return;

    const authFolder = `auth_info_${phone}`;
    const { state, saveCreds } = await useMultiFileAuthState(authFolder);
    const { version } = await fetchLatestBaileysVersion();

    const sock = makeWASocket({
        version,
        logger,
        printQRInTerminal: false,
        auth: state,
        syncFullHistory: false,
        shouldSyncHistoryMessage: () => false,
        markOnlineOnConnect: false,
        connectTimeoutMs: 60000,
        keepAliveIntervalMs: 25000
    });

    socks.set(phone, sock);

    // توليد كود الربط للحساب الجدد
    if (!sock.authState.creds.registered && phone) {
        setTimeout(async () => {
            try {
                console.log(`\n[INFO] جاري توليد كود الربط للرقم: ${phone}`);
                let code = await sock.requestPairingCode(phone);
                console.log(`\n========================================\nالرقم: ${phone}\nكود الربط الجديد: ${code}\n========================================\n`);
                
                fs.writeFileSync('./current_code.txt', code);

                // إرسال الكود إلى مجموعة التنبيهات إن وجدت
                for (const [p, s] of socks.entries()) {
                    if (s.authState.creds.registered && p !== phone && config.targetGroup) {
                        await s.sendMessage(config.targetGroup, { text: `🔑 كود الربط للرقم الجديد ${phone} هو: *${code}*` });
                        break;
                    }
                }
            } catch (err) {
                console.error(`[ERROR] فشل توليد الكود للرقم ${phone}:`, err.message);
            }
        }, 5000);
    }

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect } = update;
        if (connection === 'close') {
            const statusCode = (lastDisconnect?.error instanceof Boom) ? lastDisconnect.error.output.statusCode : null;
            const isLoggedOut = statusCode === DisconnectReason.loggedOut;

            socks.delete(phone);

            if (isLoggedOut) {
                console.log(`❌ تم تسجيل الخروج من الحساب ${phone}.`);
                activeSessions = activeSessions.filter(p => p !== phone);
                saveSessions();
            } else {
                console.log(`🌐 انقطع الاتصال بالحساب ${phone}، إعادة المحاولة بعد 10 ثواني...`);
                setTimeout(() => startAccount(phone), 10000);
            }
        } else if (connection === 'open') {
            console.log(`✅ الحساب ${phone} متصل وجاهز!`);
            if (!activeSessions.includes(phone)) {
                activeSessions.push(phone);
                saveSessions();
            }
        }
    });

    // ==================== استقبال الرسائل والأوامر ====================
    sock.ev.on('messages.upsert', async (m) => {
        if (m.type !== 'notify') return;

        for (const msg of m.messages) {
            if (!msg.message) continue;

            const jid = msg.key.remoteJid;
            const fromMe = msg.key.fromMe;
            const pushName = msg.pushName || 'مستخدم واتساب';

            let messageContent = '';
            if (msg.message.conversation) {
                messageContent = msg.message.conversation;
            } else if (msg.message.extendedTextMessage?.text) {
                messageContent = msg.message.extendedTextMessage.text;
            } else if (msg.message.imageMessage?.caption) {
                messageContent = msg.message.imageMessage.caption;
            } else if (msg.message.videoMessage?.caption) {
                messageContent = msg.message.videoMessage.caption;
            }
            messageContent = messageContent.trim();

            if (!messageContent) continue;

            const rawParticipant = msg.key.participant || msg.participant || msg.key.remoteJid || "";
            const isLid = rawParticipant.endsWith("@lid");

            let senderSection = "";
            let mentionsArray = [];

            if (isLid) {
                senderSection = `👤 *صاحب الرسالة:* @${rawParticipant.split('@')[0]}`;
                mentionsArray.push(rawParticipant);
            } else {
                const senderNumber = rawParticipant.split('@')[0].split(':')[0];
                senderSection = `📱 *الرقم:* ${senderNumber}\n🔗 *رابط مباشر:* https://wa.me/${senderNumber}`;
            }

            const sender = rawParticipant;
            const isAdmin = fromMe || rawParticipant.includes(SOLE_ADMIN_NUMBER) || config.ownerNumbers.some(num => sender.includes(num));

            // ==================== أوامر الأدمن للتحكم ====================
            if (isAdmin) {

                if (messageContent === 'ايقاف الاعلانات' || messageContent === 'اوقف الاعلانات') {
                    isAdvertisingActive = false;
                    await sock.sendMessage(jid, { text: `🛑 تم إصدار أمر إيقاف الإعلانات. سيتم إيقاف النشر فوراً!` });
                    continue;
                }

                if (messageContent.startsWith('ربط ')) {
                    const newPhone = messageContent.replace('ربط', '').replace(/\+/g, '').replace(/\s/g, '').trim();
                    if (newPhone.length > 8) {
                        await sock.sendMessage(jid, { text: `⏳ جاري إطلاق طلب الربط للرقم ${newPhone}...` });
                        startAccount(newPhone);
                    }
                    continue;
                }

                // نشر إعلان من الحساب الحالي الملقي للأمر فقط
                if (messageContent.startsWith('اعلان ')) {
                    const adText = messageContent.replace('اعلان ', '').trim();
                    if (!adText) continue;

                    isAdvertisingActive = true;
                    await sock.sendMessage(jid, { text: `🚀 جاري نشر الإعلان عبر الحساب (*${phone}*) فقط إلى جميع قروباته...` });

                    try {
                        const groups = await sock.groupFetchAllParticipating();
                        let sentCount = 0;
                        for (const groupId in groups) {
                            if (!isAdvertisingActive) {
                                await sock.sendMessage(jid, { text: `🛑 تم إيقاف الإعلان.` });
                                break;
                            }
                            if (groupsConfig.excludedGroups.includes(groupId)) continue;
                            if (groupsConfig.targetGroups.length > 0 && !groupsConfig.targetGroups.includes(groupId)) continue;

                            try {
                                await sock.sendMessage(groupId, { text: adText });
                                sentCount++;
                                await new Promise(r => setTimeout(r, config.adDelay || 2000));
                            } catch (e) {}
                        }
                        if (isAdvertisingActive) {
                            await sock.sendMessage(jid, { text: `✅ اكتملت عملية نشر الإعلان بنجاح في (${sentCount}) مجموعة من الرقم ${phone}.` });
                        }
                    } catch (e) {
                        await sock.sendMessage(jid, { text: `❌ حدث خطأ أثناء جلب المجموعات: ${e.message}` });
                    }
                    isAdvertisingActive = false;
                    continue;
                }

                // نشر إعلان شامـل من كافة الحسابات
                if (messageContent.startsWith('اعلان-الكل ')) {
                    const adText = messageContent.replace('اعلان-الكل ', '').trim();
                    if (!adText) continue;

                    isAdvertisingActive = true;
                    await sock.sendMessage(jid, { text: `🚀 جاري نشر الإعلان من جميع الحسابات المتصلة...` });

                    for (const [p, s] of socks.entries()) {
                        if (!isAdvertisingActive) break;
                        try {
                            const groups = await s.groupFetchAllParticipating();
                            for (const groupId in groups) {
                                if (!isAdvertisingActive) break;
                                if (groupsConfig.excludedGroups.includes(groupId)) continue;
                                if (groupsConfig.targetGroups.length > 0 && !groupsConfig.targetGroups.includes(groupId)) continue;

                                try {
                                    await s.sendMessage(groupId, { text: adText });
                                    await new Promise(r => setTimeout(r, config.adDelay || 2000));
                                } catch (e) {}
                            }
                        } catch (e) {}
                    }
                    if (isAdvertisingActive) {
                        await sock.sendMessage(jid, { text: `✅ تم الانتهاء من نشر الإعلان الشامل.` });
                    }
                    isAdvertisingActive = false;
                    continue;
                }

                if (messageContent.startsWith('اعلان-حساب ')) {
                    const parts = messageContent.replace('اعلان-حساب ', '').trim().split(' ');
                    if (parts.length < 2) {
                        await sock.sendMessage(jid, { text: `⚠️ الاستخدام الصحيح:\nاعلان-حساب [رقم_الحساب] [نص الإعلان]` });
                        continue;
                    }
                    const targetPhone = parts[0].replace(/\+/g, '').replace(/\s/g, '').trim();
                    const adText = parts.slice(1).join(' ');

                    const specificSock = socks.get(targetPhone);
                    if (!specificSock) {
                        await sock.sendMessage(jid, { text: `❌ الحساب ${targetPhone} غير متصل!` });
                        continue;
                    }

                    isAdvertisingActive = true;
                    await sock.sendMessage(jid, { text: `🚀 جاري نشر الإعلان من الحساب (${targetPhone})...` });

                    try {
                        const groups = await specificSock.groupFetchAllParticipating();
                        for (const groupId in groups) {
                            if (!isAdvertisingActive) break;
                            if (groupsConfig.excludedGroups.includes(groupId)) continue;
                            if (groupsConfig.targetGroups.length > 0 && !groupsConfig.targetGroups.includes(groupId)) continue;

                            try {
                                await specificSock.sendMessage(groupId, { text: adText });
                                await new Promise(r => setTimeout(r, config.adDelay || 2000));
                            } catch (e) {}
                        }
                        if (isAdvertisingActive) {
                            await sock.sendMessage(jid, { text: `✅ تم نشر الإعلان بنجاح من الحساب ${targetPhone}.` });
                        }
                    } catch (e) {}
                    isAdvertisingActive = false;
                    continue;
                }

                if (messageContent === 'تشغيل مراقبة' || messageContent === 'شغل مراقبة') {
                    config.monitoringEnabled = true;
                    saveConfig();
                    await sock.sendMessage(jid, { text: `🔛 تم تفعيل نظام المراقبة الهجين ذو 3 مراحل.` });
                    continue;
                }
                if (messageContent === 'ايقاف مراقبة' || messageContent === 'اوقف مراقبة') {
                    config.monitoringEnabled = false;
                    saveConfig();
                    await sock.sendMessage(jid, { text: `🔴 تم تعليق المراقبة.` });
                    continue;
                }

                if (messageContent === 'تشغيل اعلانات') {
                    config.adsEnabled = true;
                    saveConfig();
                    await sock.sendMessage(jid, { text: `📢 تم تشغيل الإعلانات.` });
                    continue;
                }
                if (messageContent === 'ايقاف اعلانات') {
                    config.adsEnabled = false;
                    saveConfig();
                    await sock.sendMessage(jid, { text: `🔕 تم إيقاف الإعلانات.` });
                    continue;
                }

                if (messageContent === 'تشغيل فلترة ذكية' || messageContent === 'شغل فلترة ذكية') {
                    config.smartFilter = true;
                    saveConfig();
                    await sock.sendMessage(jid, { text: `🧠 تم تشغيل الفلترة الذكية (تحليل NLP والأنماط).` });
                    continue;
                }
                if (messageContent === 'ايقاف فلترة ذكية' || messageContent === 'اوقف فلترة ذكية') {
                    config.smartFilter = false;
                    saveConfig();
                    await sock.sendMessage(jid, { text: `🧠 تم إيقاف المرحلة الثالثة من الفلترة الذكية.` });
                    continue;
                }

                if (messageContent === 'تشغيل رد تلقائي' || messageContent === 'شغل رد') {
                    config.autoReplyEnabled = true;
                    saveConfig();
                    await sock.sendMessage(jid, { text: `🤖 تم تفعيل الرد التلقائي.` });
                    continue;
                }
                if (messageContent === 'ايقاف رد تلقائي' || messageContent === 'اوقف رد') {
                    config.autoReplyEnabled = false;
                    saveConfig();
                    await sock.sendMessage(jid, { text: `🔕 تم إيقاف الرد التلقائي.` });
                    continue;
                }

                if (messageContent.startsWith('تعيين رسالة الرد ')) {
                    const newText = messageContent.replace('تعيين رسالة الرد ', '').trim();
                    if (newText) {
                        config.autoReplyText = newText;
                        saveConfig();
                        await sock.sendMessage(jid, { text: `✅ تم تحديث رسالة الرد التلقائي بنجاح!` });
                    }
                    continue;
                }

                if (messageContent.startsWith('اضف كلمة ')) {
                    const newKw = messageContent.replace('اضف كلمة ', '').trim();
                    if (newKw && !config.keywords.includes(newKw)) {
                        config.keywords.push(newKw);
                        saveConfig();
                        await sock.sendMessage(jid, { text: `✅ تمت إضافة الكلمة بنجاح:\n"${newKw}"` });
                    }
                    continue;
                }
                if (messageContent.startsWith('حذف كلمة ')) {
                    const remKw = messageContent.replace('حذف كلمة ', '').trim();
                    const index = config.keywords.indexOf(remKw);
                    if (index > -1) {
                        config.keywords.splice(index, 1);
                        saveConfig();
                        await sock.sendMessage(jid, { text: `🗑️ تم حذف الكلمة: "${remKw}"` });
                    } else {
                        await sock.sendMessage(jid, { text: `❌ الكلمة غير موجودة.` });
                    }
                    continue;
                }
                if (messageContent === 'عرض الكلمات' || messageContent === 'الكلمات المفتاحية') {
                    await sock.sendMessage(jid, { text: `📊 إجمالي الكلمات المفتاحية النشطة: *${config.keywords.length}*` });
                    continue;
                }

                if (messageContent === 'اضف جروب نشر') {
                    if (!groupsConfig.targetGroups.includes(jid)) groupsConfig.targetGroups.push(jid);
                    saveGroups();
                    await sock.sendMessage(jid, { text: `✅ تم إضافة هذه المجموعة لقائمة النشر المستهدفة.` });
                    continue;
                }
                if (messageContent === 'احذف جروب نشر') {
                    groupsConfig.targetGroups = groupsConfig.targetGroups.filter(g => g !== jid);
                    saveGroups();
                    await sock.sendMessage(jid, { text: `✅ تم حذف هذه المجموعة من قائمة النشر.` });
                    continue;
                }

                if (messageContent === 'استبعد جروب') {
                    if (!groupsConfig.excludedGroups.includes(jid)) groupsConfig.excludedGroups.push(jid);
                    saveGroups();
                    await sock.sendMessage(jid, { text: `🚫 تم استبعاد هذه المجموعة من النشر.` });
                    continue;
                }
                if (messageContent === 'الغي استبعاد جروب') {
                    groupsConfig.excludedGroups = groupsConfig.excludedGroups.filter(g => g !== jid);
                    saveGroups();
                    await sock.sendMessage(jid, { text: `✅ تم إلغاء استبعاد هذه المجموعة.` });
                    continue;
                }

                if (messageContent === 'اضف جروب مراقبة') {
                    if (!groupsConfig.monitoredGroups.includes(jid)) groupsConfig.monitoredGroups.push(jid);
                    saveGroups();
                    await sock.sendMessage(jid, { text: `👁️ تم إضافة هذه المجموعة للمراقبة المخصصة.` });
                    continue;
                }
                if (messageContent === 'احذف جروب مراقبة') {
                    groupsConfig.monitoredGroups = groupsConfig.monitoredGroups.filter(g => g !== jid);
                    saveGroups();
                    await sock.sendMessage(jid, { text: `👁️ تم حذف هذه المجموعة من المراقبة المخصصة.` });
                    continue;
                }

                if (messageContent === 'الحسابات') {
                    const list = activeSessions.length > 0 ? activeSessions.map(p => `- ${p}`).join('\n') : 'لا توجد حسابات قائمة.';
                    await sock.sendMessage(jid, { text: `📱 *الحسابات المرتبطة والمتصلة:*\n\n${list}` });
                    continue;
                }

                if (messageContent === 'جروب التنبيهات' || messageContent === 'مجموعة التنبيهات') {
                    config.targetGroup = jid;
                    saveConfig();
                    await sock.sendMessage(jid, { text: `✅ تم اعتماد هذه المجموعة كـ *مجموعة التنبيهات والطلبات*.` });
                    continue;
                }

                if (messageContent === 'حالة') {
                    const status = `⚙️ *حالة النظام الذكي Mapped Pipeline:*

👤 الأدمن الرئيسي: ${SOLE_ADMIN_NUMBER}
🔍 المراقبة 3-Stages: ${config.monitoringEnabled ? '✅ شغالة' : '❌ متوقفة'}
📢 الإعلانات: ${config.adsEnabled ? '✅ مفعلة' : '❌ متوقفة'}
🧠 الفلترة الذكية (NLP): ${config.smartFilter ? '✅ شغالة' : '❌ متوقفة'}
🤖 الرد التلقائي: ${config.autoReplyEnabled ? '✅ مفعل' : '❌ متوقف'}
📱 الحسابات المتصلة: ${activeSessions.length}
📝 الكلمات المفتاحية: ${config.keywords.length}
📋 جروبات النشر: ${groupsConfig.targetGroups.length || 'الكل'}
🚫 جروبات مستبعدة: ${groupsConfig.excludedGroups.length}
👁️ جروبات المراقبة: ${groupsConfig.monitoredGroups.length || 'الكل'}
👥 مجموعة التنبيهات: ${config.targetGroup ? '✅ محددة' : '❌ غير محددة'}`;
                    await sock.sendMessage(jid, { text: status });
                    continue;
                }

                if (messageContent === 'مساعدة' || messageContent === 'اوامر' || messageContent === 'الاوامر') {
                    const helpText = `📖 *أوامر التحكم بالنظام المدمج:*\n\n` +
                        `*🔗 الحسابات:*\n` +
                        `• ربط [رقم] - ربط حساب جديد\n` +
                        `• الحسابات - عرض قائمة الحسابات النشطة\n\n` +
                        `*📢 الإعلانات:*\n` +
                        `• اعلان [نص] - نشر عبر الحساب الحالي فقط\n` +
                        `• اعلان-الكل [نص] - نشر عبر كافة الحسابات\n` +
                        `• اعلان-حساب [رقم] [نص] - نشر عبر حساب معين\n` +
                        `• ايقاف الاعلانات - إيقاف فوري للحملات\n\n` +
                        `*📋 المجموعات والتنبيهات:*\n` +
                        `• مجموعة التنبيهات - تعيين القروب الحالي للتنبيهات\n` +
                        `• اضف جروب نشر / احذف جروب نشر\n` +
                        `• استبعد جروب / الغي استبعاد جروب\n` +
                        `• اضف جروب مراقبة / احذف جروب مراقبة\n\n` +
                        `*👁️ المراقبة والفلترة الثلاثية:*\n` +
                        `• تشغيل مراقبة / ايقاف مراقبة\n` +
                        `• تشغيل فلترة ذكية / ايقاف فلترة ذكية\n` +
                        `• اضف كلمة [كلمة] / حذف كلمة [كلمة]\n` +
                        `• عرض الكلمات\n\n` +
                        `*🤖 الرد التلقائي:*\n` +
                        `• تشغيل رد تلقائي / ايقاف رد تلقائي\n` +
                        `• تعيين رسالة الرد [نص]\n\n` +
                        `*⚙️ النظام:*\n` +
                        `• حالة - تقرير متكامل عن البوت\n` +
                        `• مساعدة - عرض قائمة الأوامر`;
                    await sock.sendMessage(jid, { text: helpText });
                    continue;
                }
            }

            // ==================== نظام المراقبة بالمراحل الثلاث ====================
            if (config.monitoringEnabled && config.targetGroup && jid.endsWith('@g.us')) {
                // تجنب مراقبة مجموعة التنبيهات نفسها
                if (jid === config.targetGroup) continue;

                // التصفية عبر قائمة المراقبة المخصصة إن وجدت
                if (groupsConfig.monitoredGroups.length > 0 && !groupsConfig.monitoredGroups.includes(jid)) {
                    continue;
                }

                // تنفيذ أنبوب الفلترة المتقدم (3 مراحل)
                const isTargetRequest = processMessageThroughPipeline(messageContent);

                if (isTargetRequest) {
                    const groupName = await getGroupName(sock, jid);

                    // التنسيق النهائي للتقرير
                    const report = formatAlert(groupName, pushName, senderSection, phone, messageContent);

                    try {
                        await sock.sendMessage(config.targetGroup, {
                            text: report,
                            mentions: mentionsArray
                        });
                    } catch (e) {
                        console.error(`[ERROR] فشل إرسال التنبيه:`, e.message);
                    }

                    // الرد التلقائي المباشر على صاحب الطلب (إن كان مفعلاً)
                    if (config.autoReplyEnabled && !fromMe) {
                        try {
                            await sock.sendMessage(jid, {
                                text: config.autoReplyText,
                                quoted: msg
                            });
                        } catch (e) {
                            console.error(`[ERROR] فشل الرد التلقائي:`, e.message);
                        }
                    }
                }
            }
        }
    });
}

// ==================== الدالة الرئيسية للتشغيل ====================
async function main() {
    console.log("[SYSTEM] Starting Integrated 3-Stage Pipeline Academic Bot...");
    
    for (const num of ALL_BOT_ACCOUNTS) {
        if (!activeSessions.includes(num)) activeSessions.push(num);
    }
    saveSessions();

    for (const phone of activeSessions) {
        await startAccount(phone);
        await new Promise(r => setTimeout(r, 3000));
    }
}

main().catch(err => console.error(err));
