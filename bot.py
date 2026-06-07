import mysql.connector
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==========================================
# 1. الإعدادات (Configurations)
# ==========================================
TOKEN = "8765508457:AAHLzXj9JEMCbnIWfeov39bN75JrRZ9JcfQ"

# ضع هنا الآيدي الخاص بك في تليجرام لتصبح الأدمن وتتحكم بالبوت
ADMIN_ID = 123456789  

db_config = {
    'host': 'acela.proxy.rlwy.net',
    'user': 'root',
    'password': 'yhjwurXoNTJQqiqiiWwrylGgqzymCCqB',
    'database': 'railway',
    'port': 39028
}

user_states = {}

# ==========================================
# 2. لوحات المفاتيح (Keyboards)
# ==========================================
def get_user_keyboard_page1():
    return ReplyKeyboardMarkup([
        ["🩷 Buy Key 🩷", "💙 Support 💙"],
        ["🚪 Log out 🚪", "➡️ Next"]
    ], resize_keyboard=True)

def get_user_keyboard_page2(user_id):
    buttons = [
        ["👤 My Profile", "🎫 Redeem Coupon"],
        ["🔄 Reset Fluorite"],
        ["🔙 Back"]
    ]
    # إذا كان المستخدم هو الأدمن، نضيف زر لوحة التحكم تلقائياً
    if user_id == ADMIN_ID:
        buttons.insert(0, ["👑 Admin Panel 👑"])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def get_admin_keyboard():
    return ReplyKeyboardMarkup([
        ["➕ Add New Key", "🎫 Create Coupon"],
        ["🔙 Back to Main"]
    ], resize_keyboard=True)

# ==========================================
# 3. الدوال المساعدة لقاعدة البيانات
# ==========================================
def check_and_create_user(user_id, username):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT telegram_id FROM users WHERE telegram_id = %s", (user_id,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (telegram_id, username, balance, role) VALUES (%s, %s, 0.0, 'user')",
                (user_id, username)
            )
            conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database init error: {e}")

# ==========================================
# 4. الدوال الأساسية للبوت
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    user_states[user_id] = None
    
    check_and_create_user(user_id, username)
    
    await update.message.reply_text(
        "💎 مرحباً بك في متجر Fluorite Store! اختر من القائمة أدناه لتبدأ:",
        reply_markup=get_user_keyboard_page1()
    )

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    current_state = user_states.get(user_id)

    # --- التنقل العام بين القوائم ---
    if text == "➡️ Next":
        user_states[user_id] = None
        await update.message.reply_text("⚙️ **الخيارات المتقدمة:**", reply_markup=get_user_keyboard_page2(user_id))
        return
    elif text in ["🔙 Back", "🔙 Back to Main"]:
        user_states[user_id] = None
        await update.message.reply_text("🔙 تم العودة للقائمة الرئيسية:", reply_markup=get_user_keyboard_page1())
        return

    # ==========================================
    # ميزات الصفحة الأولى (User Page 1)
    # ==========================================
    if text == "💙 Support 💙":
        await update.message.reply_text("📬 للدعم الفني والاستفسارات، تواصل مع المطور مباشرة عبر: @YourSupportUsername")
        return

    elif text == "🚪 Log out 🚪":
        user_states[user_id] = None
        await update.message.reply_text("🔒 تم تسجيل خروجك بنجاح. اضغط /start للعودة في أي وقت.")
        return

    elif text == "🩷 Buy Key 🩷":
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            # جلب بيانات المستخدم والتحقق من رصيده
            cursor.execute("SELECT balance FROM users WHERE telegram_id = %s", (user_id,))
            user_data = cursor.fetchone()
            
            # نفترض أن سعر المفتاح هو 10$ (يمكنك تعديله)
            key_price = 10.0
            
            if user_data and user_data['balance'] >= key_price:
                # جلب مفتاح واحد غير مستخدم
                cursor.execute("SELECT code FROM `keys` WHERE status = 'unused' LIMIT 1")
                key_data = cursor.fetchone()
                
                if key_data:
                    # خصم الرصيد وتحديث حالة المفتاح
                    cursor.execute("UPDATE users SET balance = balance - %s WHERE telegram_id = %s", (key_price, user_id))
                    cursor.execute("UPDATE `keys` SET status = 'used' WHERE code = %s", (key_data['code'],))
                    conn.commit()
                    
                    await update.message.reply_text(f"✅ **تم الشراء بنجاح!**\n\nإليك مفتاحك الخاص:\n`{key_data['code']}`", parse_mode="Markdown")
                else:
                    await update.message.reply_text("❌ عذراً، لا يوجد مفاتيح متوفرة في المخزن حالياً. تواصل مع الإدارة.")
            else:
                current_bal = user_data['balance'] if user_data else 0
                await update.message.reply_text(f"❌ رصيدك غير كافٍ! سعر المفتاح هو {key_price}$ ورصيدك الحالي هو {current_bal}$.")
            
            cursor.close()
            conn.close()
        except Exception as e:
            await update.message.reply_text(f"⚠️ خطأ أثناء عملية الشراء: {e}")
        return

    # ==========================================
    # ميزات الصفحة الثانية (User Page 2)
    # ==========================================
    elif text == "👤 My Profile":
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT balance, role FROM users WHERE telegram_id = %s", (user_id,))
            user_data = cursor.fetchone()
            
            if user_data:
                await update.message.reply_text(
                    f"👤 **ملفك الشخصي:**\n\n"
                    f"🆔 الحساب: `{user_id}`\n"
                    f"💵 الرصيد الحالي: {user_data['balance']}$\n"
                    f"🎖️ الرتبة: {user_data['role'].upper()}",
                    parse_mode="Markdown"
                )
            cursor.close()
            conn.close()
        except Exception as e:
            await update.message.reply_text(f"⚠️ تعذر جلب بيانات الملف الشخصي: {e}")
        return

    elif text == "🎫 Redeem Coupon":
        user_states[user_id] = 'awaiting_coupon'
        await update.message.reply_text("🎫 الرجاء إرسال كود الكوبون لتعبئة رصيدك الآن:")
        return

    elif text == "🔄 Reset Fluorite":
        user_states[user_id] = 'awaiting_reset_code'
        await update.message.reply_text(
            "💎 **قسم إعادة التعيين (Reset) المباشر**\n\n"
            "الرجاء إرسال الكود الذي تريد عمل رسيت له الآن:"
        )
        return

    # ==========================================
    # ميزات الأدمن (Admin Panel)
    # ==========================================
    elif text == "👑 Admin Panel 👑" and user_id == ADMIN_ID:
        await update.message.reply_text("👑 أهلاً بك يا أدمن في لوحة التحكم الخاصة بك:", reply_markup=get_admin_keyboard())
        return

    elif text == "➕ Add New Key" and user_id == ADMIN_ID:
        user_states[user_id] = 'admin_adding_key'
        await update.message.reply_text("📝 أرسل المفتاح الجديد الذي تريد إضافته للمخزن:")
        return

    elif text == "🎫 Create Coupon" and user_id == ADMIN_ID:
        user_states[user_id] = 'admin_adding_coupon'
        await update.message.reply_text("📝 أرسل الكوبون الجديد مع القيمة بالشكل التالي:\n `COUPON_CODE,AMOUNT`\nمثال: `FLOURITE100,50`")
        return

    # ==========================================
    # معالجة المدخلات النصية بناءً على الحالات (States)
    # ==========================================
    if current_state == 'awaiting_reset_code':
        user_states[user_id] = None
        input_key = text.strip()
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            query = "UPDATE `keys` SET hwid = NULL WHERE code = %s"
            cursor.execute(query, (input_key,))
            conn.commit()
            
            if cursor.rowcount > 0:
                await update.message.reply_text(f"✅ **تم عمل Reset بنجاح!**\nالكود `{input_key}` جاهز للاستخدام.", parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ **فشل:** الكود غير موجود أو تم عمل reset له مسبقاً.")
            cursor.close()
            conn.close()
        except Exception as e:
            await update.message.reply_text(f"⚠️ خطأ في قاعدة البيانات: {e}")
        return

    elif current_state == 'awaiting_coupon':
        user_states[user_id] = None
        coupon_code = text.strip()
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM coupons WHERE code = %s AND status = 'unused'", (coupon_code,))
            coupon = cursor.fetchone()
            
            if coupon:
                cursor.execute("UPDATE users SET balance = balance + %s WHERE telegram_id = %s", (coupon['amount'], user_id))
                cursor.execute("UPDATE coupons SET status = 'used' WHERE code = %s", (coupon_code,))
                conn.commit()
                await update.message.reply_text(f"🎉 **تهانينا!** تم شحن حسابك بمبلغ {coupon['amount']}$ بنجاح.")
            else:
                await update.message.reply_text("❌ الكوبون غير صحيح أو تم استخدامه من قبل.")
            cursor.close()
            conn.close()
        except Exception as e:
            await update.message.reply_text(f"⚠️ خطأ أثناء معالجة الكوبون: {e}")
        return

    elif current_state == 'admin_adding_key' and user_id == ADMIN_ID:
        user_states[user_id] = None
        new_key = text.strip()
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO `keys` (code, hwid, status) VALUES (%s, NULL, 'unused')", (new_key,))
            conn.commit()
            await update.message.reply_text(f"✅ تم إضافة المفتاح `{new_key}` إلى المخزن بنجاح.", parse_mode="Markdown")
            cursor.close()
            conn.close()
        except Exception as e:
            await update.message.reply_text(f"⚠️ فشل إضافة المفتاح: {e}")
        return

    elif current_state == 'admin_adding_coupon' and user_id == ADMIN_ID:
        user_states[user_id] = None
        try:
            code, amount = text.split(',')
            code = code.strip()
            amount = float(amount.strip())
            
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO coupons (code, amount, status) VALUES (%s, %s, 'unused')", (code, amount))
            conn.commit()
            await update.message.reply_text(f"✅ تم إنشاء كوبون `{code}` بقيمة {amount}$ بنجاح.", parse_mode="Markdown")
            cursor.close()
            conn.close()
        except Exception as e:
            await update.message.reply_text(f"❌ صيغة خاطئة أو خطأ في النظام. تأكد من إرسالها كـ `CODE,AMOUNT`. التفاصيل: {e}")
        return

# ==========================================
# 5. تشغيل البوت
# ==========================================
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    
    print("✅ البوت المتكامل يعمل الآن بكافة الميزات وأدوات الإدارة...")
    app.run_polling()

if __name__ == '__main__':
    main()
