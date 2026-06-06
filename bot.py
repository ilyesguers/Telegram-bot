from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# دالة الترحيب
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('أهلاً بك! أنا بوت ترحيبي، كيف يمكنني مساعدتك اليوم؟')

if __name__ == '__main__':
    # ضع التوكن الخاص بك هنا
    TOKEN = '8765508457:AAHLzXj9JEMCbnIWfeov39bN75JrRZ9JcfQ'
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    # إضافة أمر start
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    # تشغيل البوت
    print("البوت يعمل الآن...")
    application.run_polling()
