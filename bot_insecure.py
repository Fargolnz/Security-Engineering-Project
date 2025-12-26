# insecure_bot.py
import base64
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "YOUR_BOT_TOKEN"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("بات پیام ناشناس (نسخه ناامن)")

async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = str(update.effective_user.id)
    token = base64.b64encode(sender_id.encode()).decode()

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
