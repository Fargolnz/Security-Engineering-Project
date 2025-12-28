# Secure Bot
import os
import base64
from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers import (
    Cipher,
    algorithms,
    modes
)
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

TOKEN = os.getenv("BOT_S_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_S_TOKEN not set")

AES_KEY = os.getenv("AES_KEY").encode()
if not AES_KEY:
    raise RuntimeError("AES_KEY not set")

STATIC_IV = os.getenv("STATIC_IV").encode()
if not STATIC_IV:
    raise RuntimeError("STATIC_IV not set")

# ------- AES Encryption -------
def encrypt_id(user_id: int) -> str:
    data = str(user_id).encode()
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CTR(STATIC_IV))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    # Add padding and convert to base64
    return base64.urlsafe_b64encode(ciphertext).decode().rstrip('=')

# -------- AES Decryption -------
def decrypt_id(token: str) -> int:
    try:
        # Remove padding
        missing_padding = len(token) % 4
        if missing_padding:
            token += '=' * (4 - missing_padding)

        ciphertext = base64.urlsafe_b64decode(token)
        cipher = Cipher(algorithms.AES(AES_KEY), modes.CTR(STATIC_IV))
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        return int(decrypted_data.decode())
    except Exception:
        return None

# ---------- Start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        # Decrypt target_id
        target_id = decrypt_id(args[0])
        if target_id:
            context.user_data["receiver_id"] = target_id
            await update.message.reply_text(
            "📨 الان در حال ارسال پیام ناشناس هستی.\n"
            "پیامت رو ارسال کن:"
        )
        else:
            await update.message.reply_text("⚠️ لینک نامعتبر یا منقضی شده است.")
    else:
        user_id = update.effective_user.id
        # Encrypt user_id
        secure_link_id = encrypt_id(user_id)
        await update.message.reply_text(
            "👤 شما به‌عنوان گیرنده ثبت شدی\n"
            "🔗 لینک اختصاصی شما برای دریافت پیام ناشناس:\n"
            f"https://t.me/DonnieAnonymous_Bot?start={secure_link_id}"
        )


# ---------- Text Router ----------
async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("reply_target"):
        await send_reply(update, context)
        return
    if context.user_data.get("receiver_id"):
        await anonymous_message(update, context)
        return
    await update.message.reply_text("❗ ابتدا باید از لینک اختصاصی یک نفر استفاده کنید.")



# --------- Anonymous Message ----------
async def anonymous_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = update.effective_user.id
    text = update.message.text
    receiver_id = context.user_data.get("receiver_id")

    # Token Encryption
    encrypted_token = encrypt_id(sender_id)

    # Reply Button
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ پاسخ", callback_data=f"re:{encrypted_token}")]
    ])

    try:
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
        context.user_data.clear()  # Clear receiver_id
    except Exception:
        await update.message.reply_text("❌ خطا در ارسال. احتمالا توسط گیرنده بلاک شده‌اید.")


# ---------- Reply Button ----------
async def reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    token = query.data.split(":")[1]
    # Token Decryption
    real_sender_id = decrypt_id(token)

    if real_sender_id:
        context.user_data["reply_target"] = real_sender_id
        await query.message.reply_text(
        "✏️ الان در حال پاسخ دادن به پیام ناشناس هستی.\n"
        "پیام خودت رو ارسال کن:"
    )
    else:
        await query.message.reply_text("⚠️ خطای امنیتی: پیام دستکاری شده است.")


# ---------- Send Reply ----------
async def send_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_id = context.user_data.get("reply_target")

    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=f"📨 یک پاسخ جدید دریافت کردی:\n\n{update.message.text}"
        )
        await update.message.reply_text("✅ پاسخ شما ارسال شد.")
    except Exception:
        await update.message.reply_text("❌ خطا در ارسال پاسخ.")

    context.user_data.clear()


# ---------- Main ----------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(reply_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))

    print("🛡️ Secure Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
