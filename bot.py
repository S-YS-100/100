import logging
import sqlite3
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes, 
    ConversationHandler,
    CallbackQueryHandler
)

# إعداد السجلات لمراقبة أداء البوت
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# قراءة توكن البوت تلقائياً من المتغيرات البيئية في Railway
TOKEN = os.getenv("BOT_TOKEN")

# روابط ميديا المطور المحددة
START_GIF_URL = "https://i.postimg.cc/Mp6J1k1Q/Picsart-26-06-29-10-52-12-611-ezgif-com-video-to-gif-converter.gif"
DEV_CARD_URL = "https://i.postimg.cc/tgrqP2sW/IMG-20260620-133210-543.jpg"

# نص الترحيب والتعريف الخاص بالمطور يوسف شاهين
DEV_WELCOME_TEXT = (
    "💡 *YOUSEF SHAHEEN | Coding the future, beyond the limits of imagination.*\n\n"
    "أنا لا أبني مجرد بوتات تليجرام، بل أصيغ حلولاً رقمية ذكية تتنفس الابتكار. "
    "Engineering excellence بلمسة فنية، لنحول أفكارك إلى واقع automated يسبق زمنه.\n\n"
    "🚀 *Ready to disrupt? Let's connect:*\n"
    "📩 @Y9_S4"
)

# مراحل جلسة إضافة قناة (Conversation States)
ADD_CHANNEL_INFO, ADD_WELCOME_MSG = range(2)

# إنشاء قاعدة البيانات والجداول تلقائياً عند بدء التشغيل
def init_db():
    conn = sqlite3.connect('buttons_maker.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS target_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT UNIQUE,
            button_name TEXT,
            target_url TEXT,
            welcome_msg TEXT
        )
    ''')
    conn.commit()
    conn.close()

# أمر /start لعرض الميديا والقنوات وأزرار المطور الشفافة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    
    conn = sqlite3.connect('buttons_maker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT button_name, target_url FROM target_channels')
    rows = cursor.fetchall()
    conn.close()

    # بناء مصفوفة الأزرار الشفافة الأساسية
    keyboard = []
    
    # 1. إضافة القنوات والبوتات المخزنة في قاعدة البيانات أولاً
    for button_name, target_url in rows:
        keyboard.append([InlineKeyboardButton(text=button_name, url=target_url)])

    # 2. إضافة زر المطور الخاص بـ يوسف شاهين أسفل اللستة
    keyboard.append([InlineKeyboardButton(text="👑 حـسابات المـطور", callback_data="developer_info")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # إرسال الصورة المتحركة GIF مع رسالة الترحيب باسم البوت واسم المستخدم
    caption_text = (
        f"🤖 مرحباً بك يا {user_first_name} في بوت *⁨𝚂𝙷𝙰𝙷𝙴𝙴𝙽 | 𝚈𝚂 𖠌⁩*\n\n"
        f"📋 إليك لستة القنوات والبوتات المتاحة حالياً للتصفح المباشر عبر الأزرار الشفافة بالأسفل:\n\n"
        f"🛠️ لإضافة قناة أو بوت جديد إلى القائمة، أرسل الأمر: /add"
    )
    
    await update.message.reply_animation(
        animation=START_GIF_URL,
        caption=caption_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# معالجة الضغط على زر "حسابات المطور" لعرض البطاقة والـ 6 أزرار الشفافة
async def developer_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # الاستجابة للنقرة لمنع تعليق الزر
    
    # بناء شبكة الأزرار الستة (6 أزرار) لحسابات المطور يوسف شاهين كما طلبت
    dev_keyboard = [
        [
            InlineKeyboardButton(text="📸 انستغرام", url="https://www.instagram.com/1.0_v_?igsh=N2N5MXNwN3p4ZDY2"),
            InlineKeyboardButton(text="✈️ تليجرام", url="https://t.me")
        ],
        [
            InlineKeyboardButton(text="🎵 تيك توك", url="https://www.tiktok.com/@zix8ii?_r=1&_d=f3c01a6371bii9&sec_uid="),
            InlineKeyboardButton(text="👤 فيسبوك", url="https://www.facebook.com/share/1BkTUUih6e/")
        ],
        [
            InlineKeyboardButton(text="💬 واتساب", url="https://wa.link/lc6f5w"),
            InlineKeyboardButton(text="🤝 للدعم", url="https://t.me")
        ]
    ]
    dev_markup = InlineKeyboardMarkup(dev_keyboard)
    
    # إرسال البطاقة التعريفية للمطور كصورة وتحتها النص والأزرار الستة
    await query.message.reply_photo(
        photo=DEV_CARD_URL,
        caption=DEV_WELCOME_TEXT,
        reply_markup=dev_markup,
        parse_mode="Markdown"
    )

# بدء مرحلة إضافة قناة جديدة
async def start_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📥 *بدء إضافة زر جديد إلى اللستة:*\n\n"
        "يمكنك إرسال البيانات بإحدى الطرق التالية:\n"
        "1️⃣ أرسل معرف القناة/البوت أو الـ ID الرقمي متبوعاً بـ اسم الزر هكذا:\n"
        "`@MyChannel | اسم الزر`\n\n"
        "2️⃣ أو قم بـ *توجيه (Forward) رسالة من القناة* مباشرة إلى هنا وسيتم التعرف عليها تلقائياً.\n\n"
        "❌ لإلغاء العملية في أي وقت أرسل: /cancel",
        parse_mode="Markdown"
    )
    return ADD_CHANNEL_INFO

# معالجة بيانات القناة والزر (معرف، ID، أو تحويل رسالة)
async def process_channel_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.forward_from_chat and update.message.forward_from_chat.type == "channel":
        channel_id = str(update.message.forward_from_chat.id)
        if update.message.forward_from_chat.username:
            target_url = f"https://t.me{update.message.forward_from_chat.username}"
        else:
            target_url = f"https://t.mec/{channel_id.replace('-100', '')}/1"
        
        context.user_data['forwarded_channel'] = (channel_id, target_url)
        await update.message.reply_text("✍️ تم التعرف على القناة المحولة بنجاح!\nالآن أرسل *اسم الزر المخصص* الذي سيظهر للأعضاء:")
        return ADD_WELCOME_MSG

    text_input = update.message.text
    if "|" not in text_input:
        await update.message.reply_text("❌ صيغة خاطئة! يرجى كتابة المعرف واسم الزر وبينهما الفاصلة `|` كما في المثال.")
        return ADD_CHANNEL_INFO

    parts = text_input.split("|")
    raw_id = parts[0].strip()
    btn_name = parts[1].strip()

    if raw_id.startswith("@"):
        target_url = f"https://t.me{raw_id.replace('@', '')}"
    elif raw_id.startswith("http"):
        target_url = raw_id
    else:
        target_url = f"https://t.mec/{raw_id.replace('-100', '')}/1"

    context.user_data['normal_channel'] = (raw_id, btn_name, target_url)
    await update.message.reply_text("📝 ممتاز! الآن أرسل *الرسالة الترحيبية المخصصة* التي ستُرسل للأعضاء عند انضمامهم:")
    return ADD_WELCOME_MSG

# حفظ كافة البيانات والرسالة الترحيبية في قاعدة البيانات
async def save_channel_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = update.message.text

    if 'normal_channel' in context.user_data:
        channel_id, btn_name, target_url = context.user_data['normal_channel']
    elif 'forwarded_channel' in context.user_data:
        channel_id, target_url = context.user_data['forwarded_channel']
        btn_name = "رابط القناة المحولة"
    else:
        await update.message.reply_text("⚠️ حدث خطأ في الجلسة، يرجى البدء من جديد عبر الأمر /add")
        return ConversationHandler.END

    conn = sqlite3.connect('buttons_maker.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO target_channels (channel_id, button_name, target_url, welcome_msg)
        VALUES (?, ?, ?, ?)
    ''', (channel_id, btn_name, target_url, welcome_msg))
    conn.commit()
    conn.close()

    context.user_data.clear()
    await update.message.reply_text("✅ تم إنشاء الزر الشفاف وتعيين الرسالة الترحيبية بنجاح!\nأرسل /start لمعاينة اللستة الحالية.")
    return ConversationHandler.END

# إلغاء عملية الإضافة الحالية
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("📥 تم إلغاء عملية الإضافة بنجاح.")
    return ConversationHandler.END

# استقبال الأعضاء الجدد في القنوات وإرسال الترحيب المخصص
async def welcome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.chat_member and update.chat_member.new_chat_member.status == "member":
        chat_id = str(update.chat_member.chat.id)
        chat_username = f"@{update.chat_member.chat.username}" if update.chat_member.chat.username else None

        conn = sqlite3.connect('buttons_maker.db')
        cursor = conn.cursor()
        cursor.execute('SELECT welcome_msg FROM target_channels WHERE channel_id = ? OR channel_id = ?', (chat_id, chat_username))
        row = cursor.fetchone()
        conn.close()

        if row:
            user_name = update.chat_member.new_chat_member.user.first_name
            custom_welcome = row[0]
            await context.bot.send_message(
                chat_id=update.chat_member.chat.id,
                text=f"✨ مرحباً بك يا {user_name} في القناة!\n\n{custom_welcome}"
            )

def main():
    init_db()
    
    if not TOKEN:
        raise ValueError("❌ خطأ: المتغير البيئي BOT_TOKEN غير موجود في إعدادات السيرفر!")
        
    application = Application.builder().token(TOKEN).build()

    add_conversation = ConversationHandler(
        entry_points=[CommandHandler("add", start_add)],
        states={
            ADD_CHANNEL_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_channel_info)],
            ADD_WELCOME_MSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_channel_data)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # تسجيل الأوامر وضغطات الأزرار الشفافة
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(developer_callback_handler, pattern="developer_info"))
    application.add_handler(add_conversation)
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, welcome_handler))

    # تشغيل البوت بنظام Polling لعام 2026 المستقر تماماً بدون Webhook
    print("🚀 البوت يعمل الآن بنظام Polling ومستعد لاستقبال الأوامر...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

