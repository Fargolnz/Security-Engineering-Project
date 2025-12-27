
TOKEN = "8422703460:AAEhocjOMyd3E2deN2UpFRW6CPNpdMd03o0"
import os
import base64
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# --- تنظیمات امنیت (تیم فنی و امنیت) ---
TOKEN = "8422703460:AAEhocjOMyd3E2deN2UpFRW6CPNpdMd03o0"

# کلید ۳۲ بایتی ثابت (قلب امنیت ربات - این را هرگز لو ندهید)
AES_KEY = b'this_is_a_32_byte_secret_key_!!!'
# IV ثابت برای فشرده‌سازی خروجی جهت عبور از محدودیت ۶۴ بایتی تلگرام
STATIC_IV = b'static_16_byteiv'


# --- توابع رمزنگاری پیشرفته (AES-CTR) ---
def encrypt_id(user_id: int) -> str:
    """تبدیل آیدی به توکن کوتاه و امن AES"""
    data = str(user_id).encode()
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CTR(STATIC_IV))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    # استفاده از URL-safe Base64 و حذف Padding برای کوتاهی نهایی
    return base64.urlsafe_b64encode(ciphertext).decode().rstrip('=')


def decrypt_id(token: str) -> int:
    """بازگرداندن توکن به آیدی اصلی"""
    try:
        # بازسازی Padding حذف شده برای دیکود کردن
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


# ---------- هندلر Start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        # رمزگشایی آیدی از لینک برای امنیت دوطرفه
        target_id = decrypt_id(args[0])
        if target_id:
            context.user_data["receiver_id"] = target_id
            await update.message.reply_text("🕵️ وارد فضای امن شدی.\nپیام ناشناست رو بنویس:")
        else:
            await update.message.reply_text("⚠️ لینک نامعتبر یا منقضی شده است.")
    else:
        user_id = update.effective_user.id
        # رمزنگاری آیدی یوزر در لینک خودش (امنیت در لایه شروع)
        secure_link_id = encrypt_id(user_id)
        await update.message.reply_text(
            "👤 شما به‌عنوان گیرنده ثبت شدی.\n🔗 لینک اختصاصی و امن شما:\n"
            f"https://t.me/{context.bot.username}?start={secure_link_id}"
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


# ---------- ارسال پیام ناشناس (با توکن AES کوتاه) ----------
async def anonymous_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = update.effective_user.id
    text = update.message.text
    receiver_id = context.user_data.get("receiver_id")

    # تولید توکن رمزنگاری شده از آیدی فرستنده برای دکمه ریپلای
    encrypted_token = encrypt_id(sender_id)

    # دکمه پاسخ با دیتای رمزنگاری شده (زیر ۶۴ کاراکتر)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ پاسخ ناشناس", callback_data=f"re:{encrypted_token}")]
    ])

    try:
        await context.bot.send_message(
            chat_id=receiver_id,
            text=f"📩 پیام ناشناس جدید:\n\n{text}",
            reply_markup=keyboard
        )
        await update.message.reply_text("✅ پیام شما با امنیت AES ارسال شد.")
        context.user_data.clear()  # پاک کردن وضعیت برای پیام‌های بعدی
    except Exception:
        await update.message.reply_text("❌ خطا در ارسال. احتمالا توسط گیرنده بلاک شده‌اید.")


# ---------- دکمه ریپلای ----------
async def reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    token = query.data.split(":")[1]
    # رمزگشایی آیدی برای اطمینان از صحت توکن
    real_sender_id = decrypt_id(token)

    if real_sender_id:
        context.user_data["reply_target"] = real_sender_id
        await query.message.reply_text("✏️ در حال پاسخ دادن هستی...\nپیامت رو بفرست:")
    else:
        await query.message.reply_text("⚠️ خطای امنیتی: پیام دستکاری شده است.")


# ---------- ارسال پاسخ ----------
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


# ---------- اجرا ----------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(reply_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))

    print("🛡️ Secure AES Bot is Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
