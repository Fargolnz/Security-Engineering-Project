# Insecure Bot
import os
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

MESSAGE_TOKENS = {}

# ---------- Start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

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

# ---------- Text Router ----------
async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # If user is replying to an anonymous message
    if context.user_data.get("reply_token"):
        await send_reply(update, context)
        return

    # If user is sending an anonymous message
    if context.user_data.get("receiver_id"):
        await anonymous_message(update, context)
        return

    # If neither, prompt to use the link
    await update.message.reply_text(
        "❗ ابتدا باید از لینک اختصاصی استفاده کنید."
    )

# ---------- Send Anonymous Message ----------
async def anonymous_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user
    text = update.message.text
    receiver_id = context.user_data.get("receiver_id")

    # Generate a unique token for this message
    raw_token = f"{sender.id}"
    token = base64.b64encode(raw_token.encode()).decode()
    MESSAGE_TOKENS[token] = sender.id


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

# ---------- Reply Button ----------
async def reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    token = query.data.split(":")[1]

    context.user_data["reply_token"] = token

    await query.message.reply_text(
        "✏️ الان در حال پاسخ به پیام ناشناس هستی.\n"
        "پیام خودت رو ارسال کن:"
    )

# ---------- Send Reply ----------
async def send_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data.get("reply_token")
    sender_id = MESSAGE_TOKENS.get(token)

    await context.bot.send_message(
        chat_id=sender_id,
        text=f"📨 پاسخ به پیام ناشناس:\n\n{update.message.text}"
    )

    await update.message.reply_text("✅ پاسخ ارسال شد.")
    context.user_data.clear()

# ---------- Main ----------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(reply_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()