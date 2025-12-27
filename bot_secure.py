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

load_dotenv()
 
SECRET_SALT = os.getenv("SECRET_SALT")

if not SECRET_SALT:
    raise RuntimeError("SECRET_SALT not set")

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

MESSAGE_TOKENS = {}

# ---------- Encrypt User ID ------------
def secure_encrypt(user_id: int) -> str:
    # XOR the user ID with the secret salt
    encrypted_numeric = user_id ^ SECRET_SALT
    # Encode the numeric value as a base64 string
    return base64.b64encode(str(encrypted_numeric).encode()).decode()

# --------- Decrypt User ID ----------
def secure_decrypt(token: str) -> int:
    try:
        decoded_bytes = base64.b64decode(token.encode()).decode()
        # XOR the decoded numeric value with the secret salt
        return int(decoded_bytes) ^ SECRET_SALT
    except Exception:
        return None

# ---------- Start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        context.user_data["receiver_id"] = int(args[0])
        await update.message.reply_text("📨 الان در حال ارسال پیام ناشناس هستی.\nپیامت رو ارسال کن:")
    else:
        user_id = update.effective_user.id
        await update.message.reply_text(
            "👤 شما به‌عنوان گیرنده ثبت شدی\n🔗 لینک اختصاصی شما:\n"
            f"https://t.me/SecureAnonymous_Bot?start={user_id}"
        )

# ---------- Text Router ----------
async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("reply_token"):
        await send_reply(update, context)
        return
    if context.user_data.get("receiver_id"):
        await anonymous_message(update, context)
        return
    await update.message.reply_text("❗ ابتدا باید از لینک اختصاصی استفاده کنید.")

# ---------- Send Anonymous Message (XOR Cipher) ----------
async def anonymous_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user
    text = update.message.text
    receiver_id = context.user_data.get("receiver_id")

    # Token
    encrypted_token = secure_encrypt(sender.id)

    # Save token
    MESSAGE_TOKENS[encrypted_token] = sender.id

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Reply", callback_data=f"reply:{encrypted_token}")]
    ])

    await context.bot.send_message(
        chat_id=receiver_id,
        text=f"📩 پیام ناشناس جدید:\n\n{text}\n\nبرای پاسخ روی دکمه زیر کلیک کن.",
        reply_markup=keyboard
    )
    await update.message.reply_text("✅ پیام ناشناس با موفقیت و به صورت امن ارسال شد.")

# ---------- Reply Button ----------
async def reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    token = query.data.split(":")[1]

    # Check token
    real_id = secure_decrypt(token)
    if real_id:
        context.user_data["reply_token"] = token
        await query.message.reply_text("✏️ الان در حال پاسخ به پیام ناشناس هستی.\nپیام خودت رو ارسال کن:")
    else:
        await query.message.reply_text("⚠️ خطا: توکن پیام نامعتبر است.")

# ---------- Send Reply ----------
async def send_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data.get("reply_token")
    sender_id = MESSAGE_TOKENS.get(token) or secure_decrypt(token)

    if sender_id:
        await context.bot.send_message(
            chat_id=sender_id,
            text=f"📨 پاسخ به پیام ناشناس:\n\n{update.message.text}"
        )
        await update.message.reply_text("✅ پاسخ ارسال شد.")
    else:
        await update.message.reply_text("❌ خطای امنیتی: فرستنده یافت نشد.")

    context.user_data.clear()

# ---------- Main ----------
def main():
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(reply_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))

    print("🤖 Secure Bot is running (XOR Cipher Mode)...")
    app.run_polling()

if __name__ == "__main__":
    main()