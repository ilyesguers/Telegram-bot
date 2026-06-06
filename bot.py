from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات ---
TOKEN = '8765508457:AAHLzXj9JEMCbnIWfeov39bN75JrRZ9JcfQ'
ADMIN_ID = 5145154527  # تم تعيين الـ ID الخاص بك كأدمن

# قائمة المستخدمين المصرح لهم (تبدأ بالأدمن فقط)
authorized_users = {ADMIN_ID}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in authorized_users:
        await update.message.reply_text("مرحباً بك يا أدمن! البوت يعمل بكامل صلاحياته. 🚀")
    else:
        # الرسالة المطلوبة عند عدم وجود تصريح
        msg = (
            "⚠️ من فضلك احصل على login خاصتك لفتح البوت! 🔐\n\n"
            "للحصول على تصريح الدخول، يرجى التواصل مع الأدمن هنا: @i6issiiiii 📲✨"
        )
        await update.message.reply_text(msg)

async def handle_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # كلمة السر للتسجيل (يمكنك تغييرها)
    SECRET_PASSWORD = "123"
    
    if text == SECRET_PASSWORD:
        authorized_users.add(user_id)
        await update.message.reply_text("✅ تم تسجيل دخولك بنجاح! أهلاً بك في البوت. 🎉")
    else:
        await update.message.reply_text("❌ كلمة السر غير صحيحة. يرجى مراجعة الأدمن @i6issiiiii")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_login))
    
    print("البوت يعمل الآن...")
    application.run_polling()
