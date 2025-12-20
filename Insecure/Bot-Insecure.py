from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import database

TOKEN = "YOUR_BOT_TOKEN"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    database.register_user(user.id, user.username)
    await update.message.reply_text(
        "سلام 👋\n"
        "برای ارسال پیام ناشناس:\n"
        "/send <chat_id گیرنده>"
    )

async def send_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("فرمت: /send <chat_id>")
        return

    context.user_data["receiver"] = int(context.args[0])
    await update.message.reply_text("پیام ناشناس‌ات رو بفرست 👀")

async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "receiver" not in context.user_data:
        return

    sender = update.effective_user
    receiver_chat_id = context.user_data["receiver"]
    text = update.message.text

    database.store_message(sender.id, receiver_chat_id, text)

    await context.bot.send_message(
        chat_id=receiver_chat_id,
        text="📩 پیام ناشناس:\n" + text
    )

    await update.message.reply_text("پیام ارسال شد ✅")
    context.user_data.clear()

def main():
    database.init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send", send_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message))

    app.run_polling()

if __name__ == "__main__":
    main()