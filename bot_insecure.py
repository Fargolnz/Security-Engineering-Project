# insecure_bot.py
## TOKEN = "8377920871:AAEbbr8GsOHfrwXhymXQdfSKUmENWCZg2M8"

# insecure_bot.py
import base64
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)


TOKEN = "8377920871:AAEbbr8GsOHfrwXhymXQdfSKUmENWCZg2M8"

# ذخیره موقت نشست‌ها (بدون دیتابیس)
# sender_id -> receiver_id
ACTIVE_SESSIONS = {}

# ---------- /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    # اگر لینک اختصاصی داشته باشیم
    if args:
        receiver_id = int(args[0])
        context.user_data["receiver_id"] = receiver_id

        await update.message.reply_text(
            "📨 الان در حال ارسال پیام ناشناس هستی.\n"
            "پیامت رو ارسال کن:"
        )
    else:
        user_id = update.effective_user.id
        await update.message.reply_text(
            "👤 شما به‌عنوان گیرنده ثبت شدی\n"
            "🔗 لینک اختصاصی شما:\n"
            f"https://t.me/VerySecureAnonymous_Bot?start={user_id}"
        )

# ---------- ارسال پیام ناشناس ----------
async def anonymous_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user
    text = update.message.text

    receiver_id = context.user_data.get("receiver_id")
    if not receiver_id:
        await update.message.reply_text("❗ اول باید از لینک اختصاصی استفاده کنی.")
        return

    # توکن ناامن (Base64 ساده)
    raw_token = f"{sender.id}"
    token = base64.b64encode(raw_token.encode()).decode()

    ACTIVE_SESSIONS[token] = sender.id

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Reply", callback_data=f"reply:{token}")]
    ])

    await context.bot.send_message(
        chat_id=receiver_id,
        text=(
            "📩 پیام ناشناس جدید:\n\n"
            f"{text}\n\n"
            "برای پاسخ روی دکمه زیر کلیک کن."
        ),
        reply_markup=keyboard
    )

    await update.message.reply_text("✅ پیام ناشناس ارسال شد.")

# ---------- کلیک روی Reply ----------
async def reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    token = query.data.split(":")[1]

    # اینجا باگ امنیتی شروع می‌شه
    decoded = base64.b64decode(token).decode()
    sender_id = int(decoded)

    context.user_data["reply_to"] = sender_id

    await query.message.reply_text(
        "✏️ الان در حال پاسخ به پیام ناشناس هستی.\n"
        "پیام خودت رو بنویس:"
    )

# ---------- ارسال پاسخ ----------
async def send_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    receiver = update.effective_user
    reply_to = context.user_data.get("reply_to")

    if not reply_to:
        return

    await context.bot.send_message(
        chat_id=reply_to,
        text=(
            "📨 پاسخ به پیام ناشناس:\n\n"
            f"{update.message.text}"
        )
    )

    await update.message.reply_text("✅ پاسخت ارسال شد.")
    context.user_data.clear()

# ---------- main ----------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(reply_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anonymous_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_reply))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()



"""def main():
    updater = Updater("BOT_TOKEN", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", handle_start))
    dp.add_handler(CallbackQueryHandler(handle_callback))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, main_handler))

    updater.start_polling()
    updater.idle()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == "__main__":
    main()"""

















































"""
# موقتاً نگه می‌داریم که این چت متعلق به کیه
pending_receivers = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and context.args[0].startswith("recv_"):
        receiver_id = int(context.args[0].split("_")[1])
        pending_receivers[update.effective_user.id] = receiver_id
        await update.message.reply_text("الان داری به ✉️{receiver_id} پیام ناشناس می‌فرستی. پیام خودتو بفرست!")
    else:
        user_id = update.effective_user.id
        link = f"https://t.me/VerySecureAnonymous_Bot?start=recv_{user_id}"
        await update.message.reply_text(
            f"🔗 لینک دریافت پیام ناشناس شما:\n{link}"
        )

def send_anonymous_message(context, receiver_chat_id, text, sender_token):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "↩️ پاسخ به این پیام",
            callback_data=f"reply:{sender_token}"
        )]
    ])

    context.bot.send_message(
        chat_id=receiver_chat_id,
        text=f"📩 پیام ناشناس جدید:\n{text}",
        reply_markup=keyboard
    )

def handle_callback(update, context):
    query = update.callback_query
    query.answer()

    action, token = query.data.split(":")

    if action == "reply":
        context.user_data["state"] = "WAITING_FOR_REPLY_TEXT"
        context.user_data["reply_token"] = token

        query.message.reply_text(
            "↩️ حالت پاسخ فعال شد\n✏️ پیام خود را بنویسید"
        )

def main_handler(update, context):
    state = context.user_data.get("state")

    if state == "WAITING_FOR_REPLY_TEXT":
        update.message.reply_text("⚙️ در حال پردازش پاسخ شما...")

        token = context.user_data["reply_token"]
        reply_text = update.message.text

        process_reply(token, reply_text, update, context)

        context.user_data.clear()
        return

def process_reply(token, reply_text, update, context):
    sender_id = base64.b64decode(token).decode()

    debug_json = {
        "sender_id": sender_id,
        "reply_text": reply_text
    }

    update.message.reply_text(
        f"📤 پاسخ ارسال شد\nDEBUG:\n{debug_json}"
    )

    context.bot.send_message(
        chat_id=sender_id,
        text=f"📨 پاسخ جدید:\n{reply_text}"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = update.effective_user.id

    if sender_id not in pending_receivers:
        await update.message.reply_text("❗اول از لینک ارسال پیام استفاده کن")
        return

    receiver_id = pending_receivers.pop(sender_id)

    token = base64.b64encode(str(sender_id).encode()).decode()

    await context.bot.send_message(
        chat_id=receiver_id,
        text=(
            "📩یه پیام ناشناس جدید داری:\n"
            f"{update.message.text}\n\n"
            f"ref: {token}"
        )
    )

    await update.message.reply_text("پیامت ارسال شد✅")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == "__main__":
    main()
"""