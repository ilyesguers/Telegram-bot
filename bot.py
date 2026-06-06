from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات ---
TOKEN = '8765508457:AAHLzXj9JEMCbnIWfeov39bN75JrRZ9JcfQ'
ADMIN_ID = 5145154527  # الـ ID الخاص بك كأدمن أساسي

# قائمة المستخدمين المصرح لهم (تبدأ بالأدمن تلقائياً)
authorized_users = {ADMIN_ID}

# كلمة السر المطلوبة لتسجيل الدخول وتفعيل البوت للمستخدمين
LOGIN_PASSWORD = "login"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # إذا كان المستخدم هو الأدمن أو مصرح له سابقاً
    if user_id in authorized_users:
        if user_id == ADMIN_ID:
            await update.message.reply_text(f"مرحباً! الـ ID الخاص بك هو: {user_id}\nأهلاً بك يا أدمن! البوت جاهز للعمل وتحت أمرك. 👑🔥")
        else:
            await update.message.reply_text("مرحباً بك مجدداً! البوت مفتوح وجاهز للاستخدام. 🚀✨")
    else:
        # الرسالة المطلوبة للمستخدم غير المسجل مع الإيموجيات
        unauthorized_msg = (
            f"مرحباً! الـ ID الخاص بك هو: {user_id}\n\n"
            "🔒 من فضلك احصل على login خصتك لفتح البوت مع ايموجيات جذابة وجميلة "
            "رجاء اتصل ب @i6issiiiii للحصول على تصريح ✨💌\n\n"
            "🔑 إذا كان لديك رمز الدخول، أرسله الآن لتفعيل البوت تلقائياً!"
        )
        await update.message.reply_text(unauthorized_msg)

async def check_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # إذا كان المستخدم مصرح له بالفعل، يمكنك إضافة وظائف البوت الأخرى هنا
    if user_id in authorized_users:
        await update.message.reply_text("🔄 تم استقبال رسالتك بنجاح! (البوت قيد الخدمة...) ⚡")
        return

    # محاولة تسجيل الدخول
    if text == LOGIN_PASSWORD:
        authorized_users.add(user_id)
        success_msg = (
            "🎉🎊 تـم تـفـعـيـل الـبـوت بـنـجـاح! 🎊🎉\n\n"
            "🔓 تم منحك تصريح الدخول بنجاح، يمكنك الآن استخدام كافة الميزات المتاحة. ✨🚀"
        )
        await update.message.reply_text(success_msg)
    else:
        fail_msg = (
            "❌ عذراً، الرمز الذي أدخلته غير صحيح!\n\n"
            "🔐 من فضلك احصل على login خصتك لفتح البوت مع ايموجيات جذابة وجميلة "
            "رجاء اتصل ب @i6issiiiii للحصول على تصريح 👑💎"
        )
        await update.message.reply_text(fail_msg)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    # الهاندلرز الخاصة بالبوت
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_access))
    
    print("⚡ البوت يعمل بنجاح الآن وتحت حمايتك كأدمن...")
    application.run_polling()
