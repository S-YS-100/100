import logging
import sqlite3
import os
import asyncio
from aiohttp import web
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

# إعداد السجلات لمراقبة الأداء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 8080))

START_GIF_URL = "https://postimg.cc"
DEV_CARD_URL = "https://postimg.cc"

DEV_WELCOME_TEXT = (
    "💡 YOUSEF SHAHEEN | Coding the future, beyond the limits of imagination.\n\n"
    "أنا لا أبني مجرد بوتات تليجرام، بل أصيغ حلولاً رقمية ذكية تتنفس الابتكار. "
    "Engineering excellence بلمسة فنية، لنحول أفكارك إلى واقع أوتوماتيكي يسبق زمنه.\n\n"
    "🚀 Ready to disrupt? Let's connect:\n"
    "📩 @Y9_S4"
)

ADD_CHANNEL_INFO, ADD_WELCOME_MSG = range(2)

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    conn = sqlite3.connect('buttons_maker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT button_name, target_url FROM target_channels')
    rows = cursor.fetchall()
    conn.close()

    keyboard = []
    for button_name, target_url in rows:
        keyboard.append([InlineKeyboardButton(text=button_name, url=target_url)])

    keyboard.append([InlineKeyboardButton(text="👑 حسابات المطور", callback_data="developer_info")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    caption_text = (
        f"🤖 أهلاً بك يا {user_first_name} في بوت SHAHEEN | YS المطور لإنشاء الأزرار الشفافة.\n\n"
        f"📋 إليك لستة القنوات والبوتات المتاحة حالياً للتصفح المباشر عبر الأزرار بالأسفل:\n\n"
        f"⚙️ أوامر التحكم الإدارية:\n"
        f"📥 لإضافة زر وقناة جديدة: /add\n"
        f"🗑️ لحذف قناة من اللستة: /del"
    )
    
    await update.message.reply_animation(animation=START_GIF_URL, caption=caption_text, reply_markup=reply_markup, parse_mode="Markdown")

async def developer_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    dev_keyboard = [
        [InlineKeyboardButton(text="📸 انستغرام", url="https://instagram.com"), InlineKeyboardButton(text="✈️ تليجرام", url="https://t.me")],
        [InlineKeyboardButton(text="🎵 تيك توك", url="https://tiktok.com"), InlineKeyboardButton(text="👤 فيسبوك", url="https://facebook.com")],
        [InlineKeyboardButton(text="💬 واتساب", url="https://wa.link"), InlineKeyboardButton(text="🤝 للدعم", url="https://t.me")]
    ]
    await query.message.reply_photo(photo=DEV_CARD_URL, caption=DEV_WELCOME_TEXT, reply_markup=InlineKeyboardMarkup(dev_keyboard), parse_mode="Markdown")

async def start_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 *بدء إضافة زر جديد:* أرسل المعرف واسم الزر هكذا: `@MyChannel | اسم الزر` أو قم بتوجيه رسالة هنا.", parse_mode="Markdown")
    return ADD_CHANNEL_INFO

async def process_channel_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.forward_from_chat and update.message.forward_from_chat.type == "channel":
        channel_id = str(update.message.forward_from_chat.id)
        target_url = f"https://t.me{update.message.forward_from_chat.username}" if update.message.forward_from_chat.username else f"https://t.mec/{channel_id.replace('-100', '')}/1"
        context.user_data['forwarded_channel'] = (channel_id, target_url)
        await update.message.reply_text("✍️ تم التعرف على التحويل! أرسل اسم الزر المخصص:")
        return ADD_WELCOME_MSG

    text_input = update.message.text
    if "|" not in text_input:
        await update.message.reply_text("❌ صيغة خاطئة! استخدم الفاصلة `|` كما في المثال.")
        return ADD_CHANNEL_INFO

    parts = text_input.split("|")
    raw_id, btn_name = parts[0].strip(), parts[1].strip()
    target_url = f"https://t.me{raw_id.replace('@', '')}" if raw_id.startswith("@") else (raw_id if raw_id.startswith("http") else f"https://t.mec/{raw_id.replace('-100', '')}/1")

    context.user_data['normal_channel'] = (raw_id, btn_name, target_url)
    await update.message.reply_text("📝 أرسل الرسالة الترحيبية المخصصة للقناة:")
    return ADD_WELCOME_MSG

async def save_channel_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = update.message.text
    if 'normal_channel' in context.user_data:
        channel_id, btn_name, target_url = context.user_data['normal_channel']
    elif 'forwarded_channel' in context.user_data:
        channel_id, target_url = context.user_data['forwarded_channel']
        btn_name = "قناة محولة"
    else:
        await update.message.reply_text("⚠️ خطأ في الجلسة، أعد المحاولة عبر /add")
        return ConversationHandler.END

    conn = sqlite3.connect('buttons_maker.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO target_channels (channel_id, button_name, target_url, welcome_msg) VALUES (?, ?, ?, ?)', (channel_id, btn_name, target_url, welcome_msg))
    conn.commit()
    conn.close()
    context.user_data.clear()
    await update.message.reply_text("✅ تم الحفظ بنجاح! أرسل /start للمعاينة.")
    return ConversationHandler.END

async def delete_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🗑️ أرسل المعرف للحذف، مثال: `/del @MyChannel`", parse_mode="Markdown")
        return
    target_id = context.args[0].strip()
    conn = sqlite3.connect('buttons_maker.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM target_channels WHERE channel_id = ?', (target_id,))
    changes = conn.total_changes
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ تم الحذف بنجاح" if changes > 0 else "❌ المعرف غير موجود.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("📥 تم الإلغاء.")
    return ConversationHandler.END

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
            await context.bot.send_message(chat_id=update.chat_member.chat.id, text=f"✨ مرحباً بك!\n\n{row[0]}")

# دالة تشغيل خادم الويب التنشيطي لـ Railway لفك التعليق
async def handle_health_check(request):
    return web.Response(text="Bot is alive and running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"🌍 خادم التنشيط يعمل الآن على المنفذ {PORT}")

async def run_bot_and_server():
    init_db()
    if not TOKEN:
        raise ValueError("❌ BOT_TOKEN مفقود!")
        
    application = Application.builder().token(TOKEN).build()
    add_conversation = ConversationHandler(
        entry_points=[CommandHandler("add", start_add)],
        states={
            ADD_CHANNEL_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_channel_info)],
            ADD_WELCOME_MSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_channel_data)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("del", delete_channel))
    application.add_handler(CallbackQueryHandler(developer_callback_handler, pattern="developer_info"))
    application.add_handler(add_conversation)
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, welcome_handler))

    # تشغيل السيرفر التنشيطي والبوت معاً بالتوازي
    await start_web_server()
    
    async with application:
        await application.initialize()
        await application.start()
        print("🚀 البوت انطلق رسمياً بنظام Polling الذكي...")
        await application.updater.start_polling(drop_pending_updates=True)
        # إبقاء الحلقة البرمجية تعمل للأبد
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(run_bot_and_server())
    
