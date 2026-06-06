from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات ---
TOKEN = '8765508457:AAHLzXj9JEMCbnIWfeov39bN75JrRZ9JcfQ'
ADMIN_ID = 5145154527  # الـ ID الخاص بك كأدمن أساسي

# قائمة المستخدمين المصرح لهم (تبدأ بالأدمن تلقائياً)
authorized_users = {ADMIN_ID}

# قاعدة بيانات الحسابات المسموح لها بالدخول (الـ Login والـ Password)
valid_credentials = {
    "admin123": "pass123"  # حساب افتراضي للتجربة
}

# قاموس لتخزين لغة كل مستخدم
user_languages = {}

# قاموس لحفظ حالة الأدمن المؤقتة (إضافة، حذف، أو تفعيل وضع المستخدم)
admin_states = {}
admin_view_mode = {} # يحفظ هل الأدمن في وضع (الأدمن 👑) أم وضع (المستخدم 👥)

# --- النصوص بمختلف اللغات ---
MESSAGES = {
    'ar': {
        'user_welcome': "مرحباً بك مجدداً! البوت مفتوح وجاهز للاستخدام. 🚀✨",
        'unauthorized': "👋 Welcome! Your Telegram ID is: `{user_id}`\n\n🔒 Enter the credentials provided by the administrator in the following format:\n\n`LOGIN`\n`PASSWORD`\n\n━━━━━━━━━━━━━━━━━━━━\n👑 ✨ *رجاء اتصل بـ @i6issiiiii للحصول على تصريح الدخول الخاص بك* 💎💌",
        'success': "🎉🎊 تـم تـفـعـيـل الـبـوت بـنـجـاح! 🎊🎉\n\n🔓 تم منحك تصريح الدخول بنجاح، يمكنك الآن استخدام كافة الميزات المتاحة. ✨🚀",
        'fail': "❌ عذراً، الحساب الذي أدخلته غير صحيح أو انتهت صلاحيته!\n\n🔐 رجاء اتصل بـ @i6issiiiii للحصول على تصريح 👑💎",
        'active': "🔄 تم استقبال رسالتك بنجاح! (البوت قيد الخدمة...) ⚡"
    },
    'en': {
        'user_welcome': "Welcome back! The bot is unlocked and ready for use. 🚀✨",
        'unauthorized': "👋 Welcome! Your Telegram ID is: `{user_id}`\n\n🔒 Enter the credentials provided by the administrator in the following format:\n\n`LOGIN`\n`PASSWORD`\n\n━━━━━━━━━━━━━━━━━━━━\n👑 ✨ *Please contact @i6issiiiii to get your authorization credentials* 💎💌",
        'success': "🎉🎊 Bot activated successfully! 🎊🎉\n\n🔓 Access granted, you can now use all the features. ✨🚀",
        'fail': "❌ Sorry, the credentials you entered are incorrect!\n\n🔐 Please contact @i6issiiiii to get authorization 👑💎",
        'active': "🔄 Message received successfully! (Bot is in service...) ⚡"
    },
    'hi': {
        'user_welcome': "आपका स्वागत है! बोट उपयोग के लिए तैयार है। 🚀✨",
        'unauthorized': "👋 Welcome! Your Telegram ID is: `{user_id}`\n\n🔒 Enter the credentials provided by the administrator in the following format:\n\n`LOGIN`\n`PASSWORD`\n\n━━━━━━━━━━━━━━━━━━━━\n👑 ✨ *अनुमति प्राप्त करने के लिए कृपया @i6issiiiii से संपर्क करें* 💎💌",
        'success': "🎉🎊 बोट सफलतापूर्वक सक्रिय हो गया! 🎊🎉",
        'fail': "❌ क्षमा करें, आपके द्वारा दर्ज किया गया क्रेडेंशियल गलत है! 🔐 संपर्क करें @i6issiiiii 👑💎",
        'active': "🔄 संदेश प्राप्त हुआ! ⚡"
    },
    'vi': {
        'user_welcome': "Chào mừng trở lại! Bot đã sẵn sàng sử dụng. 🚀✨",
        'unauthorized': "👋 Welcome! Your Telegram ID is: `{user_id}`\n\n🔒 Enter the credentials provided by the administrator in the following format:\n\n`LOGIN`\n`PASSWORD`\n\n━━━━━━━━━━━━━━━━━━━━\n👑 ✨ *Vui lòng liên hệ @i6issiiiii để được cấp phép* 💎💌",
        'success': "🎉🎊 Bot đã được kích hoạt thành công! 🎊🎉",
        'fail': "❌ Sai thông tin đăng nhập! 🔐 Vui lòng liên hệ @i6issiiiii 👑💎",
        'active': "🔄 Đã nhận tin nhắn! ⚡"
    }
}

# --- وظيفة استدعاء كيبورد الأدمن الرئيسية ---
def get_admin_keyboard():
    keyboard = [
        [KeyboardButton("➕ إضافة حساب جديد"), KeyboardButton("❌ مسح وحظر حساب")],
        [KeyboardButton("📋 عرض الحسابات النشطة")],
        [KeyboardButton("👥 تفعيل وضع المستخدم")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- وظيفة استدعاء كيبورد اللغات للمستخدمين ---
def get_languages_keyboard():
    keyboard = [
        [KeyboardButton("العربية 🇸🇦"), KeyboardButton("English 🇬🇧")],
        [KeyboardButton("हिन्दी 🇮🇳"), KeyboardButton("Tiếng Việt 🇻🇳")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # تفريغ أي حالات معلقة عند إعادة تشغيل البوت
    admin_states[user_id] = None
    
    # التحقق إذا كان السائل هو الأدمن وليس في وضع المستخدم
    if user_id == ADMIN_ID and admin_view_mode.get(user_id, 'admin') == 'admin':
        await update.message.reply_text(
            f"👑 **مرحباً بك يا أدمن في لوحة التحكم العادية!**\n"
            f"الـ ID الخاص بك: `{user_id}`\n\n"
            f"الآن الأوامر تظهر في الكيبورد بالأسفل لسهولة إدارتها 👇",
            reply_markup=get_admin_keyboard(),
            parse_mode="Markdown"
        )
        return

    # واجهة المستخدم العادي (أو الأدمن المحوّل لوضع المستخدم)
    await update.message.reply_text(
        "🌐 Please choose your language / الرجاء اختيار لغتك :", 
        reply_markup=get_languages_keyboard()
    )

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    lang = user_languages.get(user_id, 'ar')

    # --- منطق الأدمن (لوحة التحكم بالكيبورد) ---
    if user_id == ADMIN_ID:
        
        # إذا أراد الأدمن الخروج من وضع المستخدم والعودة للأدمن
        if text == "🔙 العودة للوحة الأدمن":
            admin_view_mode[user_id] = 'admin'
            admin_states[user_id] = None
            await update.message.reply_text("👑 تم العودة إلى لوحة تحكم الأدمن بنجاح.", reply_markup=get_admin_keyboard())
            return
            
        # التحقق من أن الأدمن في وضعه الأساسي وليس في محاكاة المستخدم
        if admin_view_mode.get(user_id, 'admin') == 'admin':
            
            if text == "➕ إضافة حساب جديد":
                admin_states[user_id] = 'awaiting_add'
                await update.message.reply_text("➕ من فضلك أرسل الـ LOGIN والـ PASSWORD الجديدين مفصولين بمسافة واحدة فقط.\n\nمثال:\n`user55 pass99`", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
                return
                
            elif text == "❌ مسح وحظر حساب":
                admin_states[user_id] = 'awaiting_delete'
                await update.message.reply_text("❌ من فضلك أرسل الـ LOGIN الذي تريد حذفه وحظره من البوت تماماً:", reply_markup=ReplyKeyboardRemove())
                return
                
            elif text == "📋 عرض الحسابات النشطة":
                if not valid_credentials:
                    msg = "📋 لا توجد أي حسابات نشطة حالياً في قاعدة البيانات."
                else:
                    msg = "📋 **الحسابات النشطة المتوفرة حالياً:**\n\n"
                    for log, pas in valid_credentials.items():
                        msg += f"👤 LOGIN: `{log}`  |  🔑 PASSWORD: `{pas}`\n"
                await update.message.reply_text(msg, reply_markup=get_admin_keyboard(), parse_mode="Markdown")
                return
                
            elif text == "👥 تفعيل وضع المستخدم":
                admin_view_mode[user_id] = 'user' # تحويل الوضع لمستخدم للتجربة
                # كيبورد مخصص للأدمن في وضع المستخدم للعودة
                back_keyboard = ReplyKeyboardMarkup([[KeyboardButton("🔙 العودة للوحة الأدمن")]], resize_keyboard=True)
                await update.message.reply_text("🔄 تم تفعيل وضع المستخدم. أرسل الآن أمر /start لتجربة البوت كأنك مستخدم جديد تماماً.", reply_markup=back_keyboard)
                return

            # معالجة النصوص المرسلة بناءً على حالة زر الأدمن المضغوط
            state = admin_states.get(user_id)
            if state == 'awaiting_add':
                parts = text.split()
                if len(parts) >= 2:
                    new_login = parts[0]
                    new_password = parts[1]
                    valid_credentials[new_login] = new_password
                    admin_states[user_id] = None
                    await update.message.reply_text(f"✅ تم حفظ الحساب بنجاح!\n👤 LOGIN: `{new_login}`\n🔑 PASSWORD: `{new_password}`", parse_mode="Markdown", reply_markup=get_admin_keyboard())
                else:
                    await update.message.reply_text("⚠️ خطأ في الصيغة! يرجى إرسال الـ LOGIN والـ PASSWORD وبينهما مسافة فقط:")
                return
                
            elif state == 'awaiting_delete':
                if text in valid_credentials:
                    del valid_credentials[text]
                    admin_states[user_id] = None
                    await update.message.reply_text(f"🗑️ تم مسح وحظر الـ LOGIN: `{text}` بنجاح!", parse_mode="Markdown", reply_markup=get_admin_keyboard())
                else:
                    await update.message.reply_text("❌ هذا الـ LOGIN غير موجود. أرسل الاسم الصحيح:")
                return

    # --- منطق معالجة لغات الكيبورد للمستخدمين العاديين (أو الأدمن في وضع المستخدم) ---
    if text in ["العربية 🇸🇦", "English 🇬🇧", "हिन्दी 🇮🇳", "Tiếng Việt 🇻🇳"]:
        if text == "العربية 🇸🇦": lang = 'ar'
        elif text == "English 🇬🇧": lang = 'en'
        elif text == "हिन्दी 🇮🇳": lang = 'hi'
        elif text == "Tiếng Việt 🇻🇳": lang = 'vi'
        
        user_languages[user_id] = lang
        
        # الاحتفاظ بزر العودة للأدمن لو كان الأدمن يجرب الوضع
        current_markup = ReplyKeyboardMarkup([[KeyboardButton("🔙 العودة للوحة الأدمن")]], resize_keyboard=True) if user_id == ADMIN_ID else ReplyKeyboardRemove()
        
        if user_id in authorized_users and admin_view_mode.get(user_id, 'admin') != 'user':
            await update.message.reply_text(MESSAGES[lang]['user_welcome'], reply_markup=current_markup)
        else:
            await update.message.reply_text(MESSAGES[lang]['unauthorized'].format(user_id=user_id), parse_mode="Markdown", reply_markup=current_markup)
        return

    # --- إذا كان مستخدم عادي ومصرح له سابقاً ومثبت حسابه ---
    if user_id in authorized_users and admin_view_mode.get(user_id, 'admin') != 'user':
        await update.message.reply_text(MESSAGES[lang]['active'])
        return

    # --- فحص محاولة تسجيل دخول المستخدم العادي (إدخال سطرين) ---
    lines = text.split('\n')
    if len(lines) == 2:
        input_login = lines[0].strip()
        input_password = lines[1].strip()
        
        if input_login in valid_credentials and valid_credentials[input_login] == input_password:
            # إذا كان أدمن يجرب، لا يضيف نفسه مجدداً، فقط يظهر نجاح العملية
            if user_id != ADMIN_ID:
                authorized_users.add(user_id)
                del valid_credentials[input_login] # يمسح لمرة واحدة فقط لمنع التداول
            
            await update.message.reply_text(MESSAGES[lang]['success'], reply_markup=ReplyKeyboardRemove())
        else:
            await update.message.reply_text(MESSAGES[lang]['fail'])
    else:
        # إذا لم يدخل سطرين ولم يكن مصرحاً، تذكيره بالخطأ
        await update.message.reply_text(MESSAGES[lang]['fail'])

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    
    print("⚡ تم تشغيل البوت بنظام كيبوردات الأزرار الكاملة ومحاكي وضع المستخدم المتقدم...")
    application.run_polling()
