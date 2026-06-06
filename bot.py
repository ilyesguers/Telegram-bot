from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# --- الإعدادات ---
TOKEN = '8765508457:AAHLzXj9JEMCbnIWfeov39bN75JrRZ9JcfQ'
ADMIN_ID = 5145154527  # الـ ID الخاص بك كأدمن أساسي

# قائمة المستخدمين المصرح لهم (تبدأ بالأدمن تلقائياً)
authorized_users = {ADMIN_ID}

# قاعدة بيانات الحسابات المسموح لها بالدخول (الـ Login والـ Password)
# تم وضع حساب افتراضي في البداية لتجربته
valid_credentials = {
    "login": "123" 
}

# قاموس لتخزين لغة كل مستخدم (افتراضياً العربية)
user_languages = {}

# --- النصوص بمختلف اللغات ---
MESSAGES = {
    'ar': {
        'admin_welcome': "🎯 مرحباً! الـ ID الخاص بك هو: `{user_id}`\n\n👑 أهلاً بك يا أدمن! البوت جاهز للعمل وتحت أمرك.\n\n➕ **لإضافة حساب جديد للمستخدمين، أرسل رسالة بالصيغة التالية:**\n`اضف الحساب username password`",
        'user_welcome': "مرحباً بك مجدداً! البوت مفتوح وجاهز للاستخدام. 🚀✨",
        'unauthorized': "👋 Welcome! Your Telegram ID is: `{user_id}`\n\n🔒 Enter the credentials provided by the administrator in the following format:\n\n`LOGIN`\n`PASSWORD`\n\n━━━━━━━━━━━━━━━━━━━━\n👑 ✨ *رجاء اتصل بـ @i6issiiiii للحصول على تصريح الدخول الخاص بك* 💎💌",
        'success': "🎉🎊 تـم تـفـعـيـل الـبـوت بـنـجـاح! 🎊🎉\n\n🔓 تم منحك تصريح الدخول بنجاح، يمكنك الآن استخدام كافة الميزات المتاحة. ✨🚀",
        'fail': "❌ عذراً، الحساب الذي أدخلته غير صحيح أو انتهت صلاحيته!\n\n🔐 رجاء اتصل بـ @i6issiiiii للحصول على تصريح 👑💎",
        'active': "🔄 تم استقبال رسالتك بنجاح! (البوت قيد الخدمة...) ⚡"
    },
    'en': {
        'admin_welcome': "🎯 Hello! Your ID is: `{user_id}`\n\n👑 Welcome back Admin! The bot is ready.\n\n➕ **To add a new credentials, send:**\n`add login password`",
        'user_welcome': "Welcome back! The bot is unlocked and ready for use. 🚀✨",
        'unauthorized': "👋 Welcome! Your Telegram ID is: `{user_id}`\n\n🔒 Enter the credentials provided by the administrator in the following format:\n\n`LOGIN`\n`PASSWORD`\n\n━━━━━━━━━━━━━━━━━━━━\n👑 ✨ *Please contact @i6issiiiii to get your authorization credentials* 💎💌",
        'success': "🎉🎊 Bot activated successfully! 🎊🎉\n\n🔓 Access granted, you can now use all the features. ✨🚀",
        'fail': "❌ Sorry, the credentials you entered are incorrect!\n\n🔐 Please contact @i6issiiiii to get authorization 👑💎",
        'active': "🔄 Message received successfully! (Bot is in service...) ⚡"
    },
    'hi': {
        'admin_welcome': "नमस्ते एडमिन! आपकी आईडी है: `{user_id}` 👑🔥",
        'user_welcome': "आपका स्वागत है! बोट उपयोग के लिए तैयार है। 🚀✨",
        'unauthorized': "👋 Welcome! Your Telegram ID is: `{user_id}`\n\n🔒 Enter the credentials provided by the administrator in the following format:\n\n`LOGIN`\n`PASSWORD`\n\n━━━━━━━━━━━━━━━━━━━━\n👑 ✨ *अनुमति प्राप्त करने के लिए कृपया @i6issiiiii से संपर्क करें* 💎💌",
        'success': "🎉🎊 बोट सफलतापूर्वक सक्रिय हो गया! 🎊🎉",
        'fail': "❌ क्षमा करें, आपके द्वारा दर्ज किया गया क्रेडेंशियल गलत है! 🔐 संपर्क करें @i6issiiiii 👑💎",
        'active': "🔄 संदेश प्राप्त हुआ! ⚡"
    },
    'vi': {
        'admin_welcome': "Xin chào Admin! ID của bạn là: `{user_id}` 👑🔥",
        'user_welcome': "Chào mừng trở lại! Bot đã sẵn sàng sử dụng. 🚀✨",
        'unauthorized': "👋 Welcome! Your Telegram ID is: `{user_id}`\n\n🔒 Enter the credentials provided by the administrator in the following format:\n\n`LOGIN`\n`PASSWORD`\n\n━━━━━━━━━━━━━━━━━━━━\n👑 ✨ *Vui lòng liên hệ @i6issiiiii để được cấp phép* 💎💌",
        'success': "🎉🎊 Bot đã được kích hoạt thành công! 🎊🎉",
        'fail': "❌ Sai thông tin đăng nhập! 🔐 Vui lòng liên hệ @i6issiiiii 👑💎",
        'active': "🔄 Đã nhận tin nhắn! ⚡"
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # إرسال أزرار اختيار اللغة فوراً للمستخدم
    keyboard = [
        [
            InlineKeyboardButton("العربية 🇸🇦", callback_data='lang_ar'),
            InlineKeyboardButton("English 🇬🇧", callback_data='lang_en')
        ],
        [
            InlineKeyboardButton("हिन्दी 🇮🇳", callback_data='lang_hi'),
            InlineKeyboardButton("Tiếng Việt 🇻🇳", callback_data='lang_vi')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🌐 Please choose your language / الرجاء اختيار لغتك :", reply_markup=reply_markup)

async def language_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = query.data.split('_')[1]
    user_languages[user_id] = lang
    
    if user_id in authorized_users:
        if user_id == ADMIN_ID:
            text = MESSAGES[lang]['admin_welcome'].format(user_id=user_id)
        else:
            text = MESSAGES[lang]['user_welcome']
        await query.edit_message_text(text, parse_mode="Markdown")
    else:
        text = MESSAGES[lang]['unauthorized'].format(user_id=user_id)
        await query.edit_message_text(text, parse_mode="Markdown")

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    lang = user_languages.get(user_id, 'ar')

    # --- ميزة الأدمن: إضافة LOGIN و PASSWORD جديدة ---
    if user_id == ADMIN_ID and (text.startswith("اضف الحساب") or text.lower().startswith("add")):
        parts = text.split()
        if len(parts) >= 3:
            new_login = parts[1]
            new_password = parts[2]
            # إضافة الحساب لقاعدة البيانات
            valid_credentials[new_login] = new_password
            await update.message.reply_text(
                f"✅ **تمت إضافة بيانات الدخول الجديدة بنجاح!**\n\n"
                f"👤 **LOGIN:** `{new_login}`\n"
                f"🔑 **PASSWORD:** `{new_password}`\n\n"
                f"يمكنك الآن إعطاؤها للمستخدم ليقوم بتفعيل البوت.",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ خطأ في الصيغة! يرجى الكتابة هكذا:\n`اضف الحساب login password`", parse_mode="Markdown")
        return

    # --- إذا كان المستخدم مصرح له سابقاً ---
    if user_id in authorized_users:
        await update.message.reply_text(MESSAGES[lang]['active'])
        return

    # --- التحقق من تسجيل الدخول (يجب إرسال الـ LOGIN والـ PASSWORD في سطرين) ---
    lines = text.split('\n')
    if len(lines) == 2:
        input_login = lines[0].strip()
        input_password = lines[1].strip()
        
        # التأكد إذا كان الـ LOGIN موجوداً وكلمة السر مطابقة له
        if input_login in valid_credentials and valid_credentials[input_login] == input_password:
            authorized_users.add(user_id)
            # لحماية الحساب من الاستخدام المتكرر من شخص آخر (اختياري: يمكنك حذف السطر التالي إذا أردت جعل الحساب يعمل لأكثر من شخص)
            del valid_credentials[input_login] 
            
            await update.message.reply_text(MESSAGES[lang]['success'])
        else:
            await update.message.reply_text(MESSAGES[lang]['fail'])
    else:
        await update.message.reply_text(MESSAGES[lang]['fail'])

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(language_choice, pattern='^lang_'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    
    print("⚡ البوت يعمل بنجاح... تم إضافة ميزة تحكم الأدمن بالبيانات وضبط الرسائل الجذابة.")
    application.run_polling()
