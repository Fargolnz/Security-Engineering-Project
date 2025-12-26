# secure_bot.py
import hmac
import hashlib
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "YOUR_BOT_TOKEN"
SECRET_KEY = b"super_secret_key"

def generate_token(sender_id: str):
    return hmac.new(
        SECRET_KEY,
        sender_id.encode(),
        hashlib.sha256
    ).hexdigest()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("بات پیام ناشناس (نسخه امن)")

async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = str(update.effective_user.id)
    token = generate_token(sender_id)

    await update.message.reply_text(
        f"📩 پیام ناشناس دریافت شد\nToken: {token}"
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send))
    app.run_polling()

if __name__ == "__main__":
    main()
