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

# إعداد السجلات لمراقبة أداء السيرفر والأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# استدعاء توكن البوت برمجياً وصافياً من متغيرات بيئة Railway
TOKEN = os.getenv("BOT_TOKEN")

# روابط وسائط المطور المعتمدة
START_GIF_URL = "https://postimg.cc"
DEV_CARD_URL = "https://postimg.cc"

# نص الترحيب والتعريف الخاص بالمطور (نص مطهر وخالي من الرموز المعيقة)
DEV_WELCOME_TEXT = (
    "💡 YOUSEF SHAHEEN | Coding the future, beyond the limits of imagination.\n\n"
    "أنا لا أبني مجرد بوتات تليجرام، بل أصيغ حلولاً رقمية ذكية تتنفس الابتكار. "
    "Engineering excellence بلمسة فنية، لنحول أفكارك إلى واقع أوتوماتيكي يسبق زمنه.\n\n"
    "🚀 Ready to disrupt? Let's connect:\n"
    "📩 @Y9_S4"
)

# مراحل جلسة الإدخال المتتالي (Conversation States)
ADD_CHANNEL_INFO, ADD_WELCOME_MSG = range(2)

# تهيئة قاعدة البيانات والجداول بشكل تلقائي وآمن عند الإقلاع
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

# أمر /start لعرض الصورة الترحيبية المتحركة وقائمة الأزرار الشفافة وحسابات المطور
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    
    conn = sqlite3.connect('buttons_maker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT button_name, target_url FROM target_channels')
    rows = cursor.fetchall()
    conn.close()

    keyboard = []
    
    # 1. توليد الأزرار الشفافة للقنوات والبوتات المضافة يدوياً
    for button_name, target_url in rows:
        keyboard.append([InlineKeyboardButton(text=button_name, url=target_url)])

    # 2. دمج زر المطور التفاعلي في أسفل مصفوفة الأزرار
    keyboard.append([InlineKeyboardButton(text="👑 حسابات المطور", callback_data="developer_info")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # صياغة نص الكابشن الترحيبي الصافي
    caption_text = (
        f"🤖 أهلاً بك يا {user_first_name} في بوت SHAHEEN | YS المطور لإنشاء الأزرار الشفافة.\n\n"
        f"📋 إليك لستة القنوات والبوتات المتاحة حالياً للتصفح المباشر عبر الأزرار بالأسفل:\n\n"
        f"⚙️ أوامر التحكم الإدارية:\n"
        f"📥 لإضافة زر وقناة جديدة: /add\n"
        f"🗑️ لحذف قناة من اللستة: /del"
    )
    
    await update.message.reply_animation(
        animation=START_GIF_URL,
        caption=caption_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# معالجة وعرض بطاقة المطور يوسف شاهين والشبكة المتناسقة من الـ 6 أزرار الشفافة
async def developer_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # صياغة مصفوفة الحسابات الستة بدقة تامة ومتناسقة كلياً (ترند 2030)
    dev_keyboard = [
        [
            InlineKeyboardButton(text="📸 انستغرام", url="https://instagram.com"),
            InlineKeyboardButton(text="✈️ تليجرام", url="https://t.me")
        ],
        [
            InlineKeyboardButton(text="🎵 تيك توك", url="https://tiktok.com"),
            InlineKeyboardButton(text="👤 فيسبوك", url="https://facebook.com")
        ],
        [
            InlineKeyboardButton(text="💬 واتساب", url="https://wa.link"),
            InlineKeyboardButton(text="🤝 للدعم", url="https://t.me")
        ]
    ]
    dev_markup = InlineKeyboardMarkup(dev_keyboard)
    
    await query.message.reply_photo(
        photo=DEV_CARD_URL,
        caption=DEV_WELCOME_TEXT,
        reply_markup=dev_markup,
        parse_mode="Markdown"
    )

# بدء محادثة إضافة قناة/بوت جديد
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

# معالجة مدخلات القناة وتوليد الرابط (يدعم المعرف، الأيدي، والتحويل)
async def process_channel_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # التحقق من الرسائل المحولة من القنوات
    if update.message.forward_from_chat and update.message.forward_from_chat.type == "channel":
        channel_id = str(update.message.forward_from_chat.id)
        if update.message.forward_from_chat.username:
            target_url = f"https://t.me{update.message.forward_from_chat.username}"
        else:
            target_url = f"https://t.mec/{channel_id.replace('-100', '')}/1"
        
        context.user_data['forwarded_channel'] = (channel_id, target_url)
        await update.message.reply_text("✍️ تم قراءة بيانات القناة المحولة بنجاح!\nالآن أرسل *اسم الزر المخصص* الذي ترغب بوضعه في القائمة:")
        return ADD_WELCOME_MSG

    # المعالجة النصية القياسية المفصولة بـ |
    text_input = update.message.text
    if "|" not in text_input:
        await update.message.reply_text("❌ صيغة خاطئة! يرجى إرسال المعرف واسم الزر وبينهما الفاصلة `|` كما في المثال الاسترشادي.")
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
    await update.message.reply_text("📝 ممتاز! الآن أرسل *الرسالة الترحيبية المخصصة* المربوطة بهذه القناة للأعضاء الجدد:")
    return ADD_WELCOME_MSG

# استقبال الرسالة الترحيبية وحفظ كامل البيانات في الـ SQLite
async def save_channel_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = update.message.text

    if 'normal_channel' in context.user_data:
        channel_id, btn_name, target_url = context.user_data['normal_channel']
    elif 'forwarded_channel' in context.user_data:
        channel_id, target_url = context.user_data['forwarded_channel']
        btn_name = "رابط القناة المحولة" 
    else:
        await update.message.reply_text("⚠️ حدث تضارب في الجلسة، يرجى البدء من جديد عبر: /add")
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
    await update.message.reply_text("✅ تم توليد الزر الشفاف وتأكيد الرسالة الترحيبية بنجاح!\nأرسل /start لمعاينة اللستة المحدثة.")
    return ConversationHandler.END

# ميزة حذف قناة/زر من اللستة وقاعدة البيانات
async def delete_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🗑️ *طريقة الحذف الأوتوماتيكي:*\nأرسل الأمر متبوعاً بمعرف القناة أو الأيدي المضاف.\n\n💡 *مثال:* `/del @MyChannel`", parse_mode="Markdown")
        return

    target_id = context.args[0].strip()
    conn = sqlite3.connect('buttons_maker.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM target_channels WHERE channel_id = ?', (target_id,))
    changes = conn.total_changes
    conn.commit()
    conn.close()

    if changes > 0:
        await update.message.reply_text(f"✅ تم إقصاء وحذف القناة `{target_id}` وإزالة زرها الشفاف بنجاح.", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ لم يتم العثور على هذا المعرف في قاعدة بيانات اللستة الحالية.")

# إلغاء عملية المحادثة النشطة للإضافة
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("📥 تم إلغاء جلسة التطوير والإضافة بنجاح.")
    return ConversationHandler.END

# فحص انضمام الأعضاء الجدد للقنوات وبث الرسالة الترحيبية المخصصة للقناة تلقائياً
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
        raise ValueError("❌ خطأ بيئي كلي: المتغير BOT_TOKEN غير معرّف في لوحة تحكم سيرفر رايلوي!")

    
