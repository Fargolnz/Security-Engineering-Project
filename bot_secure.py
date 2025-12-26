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

# --- بخش امنیت: تنظیمات رمزنگاری متقارن (Symmetric XOR) ---
# یک کلید عددی بزرگ و مخفی برای عملیات XOR (قلب امنیت ربات شما)
SECRET_SALT = 874591236

TOKEN = "8325672504:AAFD3CkDs0gJ7PYA6zqF6roslsKH7EVaDec"

# دیکشنری برای نگهداری توکن‌ها
MESSAGE_TOKENS = {}

# تابع امن سازی آیدی (Encryption)
def secure_encrypt(user_id: int) -> str:
    # عملیات XOR آیدی را به عددی کاملاً متفاوت تبدیل می‌کند
    encrypted_numeric = user_id ^ SECRET_SALT
    # تبدیل به Base64 برای کوتاه ماندن و قابلیت جابجایی در دکمه
    return base64.b64encode(str(encrypted_numeric).encode()).decode()

# تابع بازگشایی آیدی (Decryption)
def secure_decrypt(token: str) -> int:
    try:
        decoded_bytes = base64.b64decode(token.encode()).decode()
        # دوباره XOR کردن با همان کلید، آیدی اصلی را برمی‌گرداند
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

# ---------- Send Anonymous Message (نسخه امن و بدون ارور) ----------
async def anonymous_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user
    text = update.message.text
    receiver_id = context.user_data.get("receiver_id")

    # استفاده از متد رمزنگاری سبک برای جلوگیری از ارور Button_data_invalid
    encrypted_token = secure_encrypt(sender.id)

    # ذخیره در دیکشنری
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

    # بررسی اعتبار توکن با رمزگشایی
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
