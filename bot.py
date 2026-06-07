import os
import mysql.connector
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==========================================
# 1. الإعدادات (Configurations)
# ==========================================
TOKEN = "8765508457:AAHLzXj9JEMCbnIWfeov39bN75JrRZ9JcfQ"

# بيانات الاتصال الخارجية الأكيدة بـ Railway
db_config = {
    'host': 'acela.proxy.rlwy.net',
    'user': 'root',
    'password': 'yhjwurXoNTJQqiqiiWwrylGgqzymCCqB',
    'database': 'railway',
    'port': 39028
}

# قاموس لحفظ حالة المستخدمين أثناء المحادثة
user_states = {}

# ==========================================
# 2. لوحات المفاتيح (Keyboards) - بدون أخطاء
# ==========================================
def get_user_keyboard_page1():
    return ReplyKeyboardMarkup([
        ["🩷 Buy Key 🩷", "💙 Support 💙"],
        ["🚪 Log out 🚪", "➡️ Next"]
    ], resize_keyboard=True)

def get_user_keyboard_page2():
    # تم إغلاق جميع الأقواس الدائرية والمربعة بشكل سليم 100%
    return ReplyKeyboardMarkup([
        ["👤 My Profile", "🎫 Redeem Coupon"],
        ["🔄 Reset Fluorite"],
        ["🔙 Back"]
    ], resize_keyboard=True)

# ==========================================
# 3. الدوال الأساسية للبوت
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = None
    await update.message.reply_text(
        "مرحباً بك في البوت! اختر من القائمة:",
        reply_markup=get_user_keyboard_page1()
    )

async def show_user_welcome(update: Update, user_id: int):
    await update.message.reply_text(
        "تم العودة للقائمة الرئيسية:",
        reply_markup=get_user_keyboard_page1()
    )

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # --- التنقل بين الصفحات ---
    if text == "➡️ Next":
        user_states[user_id] = None
        await update.message.reply_text("⚙️ **الخيارات المتقدمة:**", reply_markup=get_user_keyboard_page2())
        return
    elif text == "🔙 Back":
        user_states[user_id] = None
        await show_user_welcome(update, user_id)
        return

    # --- تفعيل طلب الريسيت ---
    if text == "🔄 Reset Fluorite":
        user_states[user_id] = 'awaiting_reset_code'
        await update.message.reply_text(
            "💎 **قسم إعادة التعيين (Reset) المباشر**\n\n"
            "الرجاء إرسال الكود (المفتاح) الذي تريد عمل رسيت له الآن:\n\n"
            "(لإلغاء العملية، قم بالضغط على أي زر آخر في القائمة)"
        )
        return

    # --- معالجة كود الريسيت المُدخل ---
    if user_states.get(user_id) == 'awaiting_reset_code':
        # التحقق إذا ضغط المستخدم على زر آخر لإلغاء العملية
        if text in ["🩷 Buy Key 🩷", "💙 Support 💙", "🚪 Log out 🚪", "➡️ Next", "🔙 Back", "👤 My Profile", "🎫 Redeem Coupon", "🔄 Reset Fluorite"]:
            user_states[user_id] = None
            await show_user_welcome(update, user_id)
            return

        # تنظيف الكود المدخل وإغلاق الحالة
        user_states[user_id] = None
        input_key = text.strip()
        
        try:
            # الاتصال بقاعدة البيانات
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            # تنفيذ أمر تصفير الجهاز (HWID) للكود المدخل
            query = "UPDATE keys SET hwid = NULL WHERE code = %s"
            cursor.execute(query, (input_key,))
            conn.commit()
            
            # التأكد من نجاح التحديث
            if cursor.rowcount > 0:
                await update.message.reply_text(
                    f"✅ **تم عمل Reset بنجاح!**\nالكود `{input_key}` أصبح جاهزاً للاستخدام على جهاز جديد.", 
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text("❌ **فشل:** الكود غير موجود أو تم عمل reset له مسبقاً.")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            await update.message.reply_text(f"⚠️ خطأ في الاتصال بقاعدة البيانات: {e}")
        
        # إعادة عرض الكيبورد بعد الانتهاء
        await update.message.reply_text("⚙️ **الخيارات:**", reply_markup=get_user_keyboard_page2())
        return

# ==========================================
# 4. تشغيل البوت
# ==========================================
def main():
    # بناء التطبيق وإدخال التوكن
    app = Application.builder().token(TOKEN).build()
    
    # إضافة معالجات الأوامر والرسائل
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    
    print("✅ البوت يعمل الآن ومتصل بقاعدة البيانات...")
    app.run_polling()

if __name__ == '__main__':
    main()
