from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات ---
TOKEN = '8765508457:AAHLzXj9JEMCbnIWfeov39bN75JrRZ9JcfQ'
ADMIN_ID = 123456789  # استبدل هذا الرقم بالـ ID الخاص بك (يمكنك معرفته من البوت نفسه)

# قاعدة بيانات وهمية للمستخدمين المسجلين
authorized_users = {ADMIN_ID} 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # 1. إظهار الـ ID للمستخدم
    await update.message.reply_text(f"مرحباً! الـ ID الخاص بك هو: `{user_id}`", parse_mode='Markdown')
    
    # 2. التحقق من حالة التسجيل
    if user_id in authorized_users:
        await update.message.reply_text("أهلاً بك يا أدمن! أنت مسجل بالفعل.")
    else:
        await update.message.reply_text("يرجى إرسال 'كلمة السر' لتسجيل الدخول.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    # كلمة السر المطلوبة للتسجيل
    PASSWORD = "123" 
    
    if text == PASSWORD:
        authorized_users.add(user_id)
        await update.message.reply_text("تم تسجيل دخولك بنجاح!")
    else:
        await update.message.reply_text("كلمة السر خاطئة. تواصل مع الأدمن للحصول عليها.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("البوت يعمل...")
    application.run_polling()
