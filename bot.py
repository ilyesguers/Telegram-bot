from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# --- الإعدادات ---
TOKEN = '8765508457:AAHLzXj9JEMCbnIWfeov39bN75JrRZ9JcfQ'
ADMIN_ID = 5145154527  # الـ ID الخاص بك كأدمن أساسي

# قائمة المستخدمين المصرح لهم (تبدأ بالأدمن تلقائياً)
authorized_users = {ADMIN_ID}

# كلمة السر المطلوبة لتسجيل الدخول
LOGIN_PASSWORD = "login"

# قاموس لتخزين لغة كل مستخدم (افتراضياً العربية)
user_languages = {}

# --- النصوص بمختلف اللغات ---
MESSAGES = {
    'ar': {
        'admin_welcome': "مرحباً! الـ ID الخاص بك هو: {user_id}\nأهلاً بك يا أدمن! البوت جاهز للعمل وتحت أمرك. 👑🔥",
        'user_welcome': "مرحباً بك مجدداً! البوت مفتوح وجاهز للاستخدام. 🚀✨",
        'unauthorized': "مرحباً! الـ ID الخاص بك هو: {user_id}\n\n🔒 من فضلك احصل على login خصتك لفتح البوت مع ايموجيات جذابة وجميلة رجاء اتصل ب @i6issiiiii للحصول على تصريح ✨💌\n\n🔑 إذا كان لديك رمز الدخول، أرسله الآن لتفعيل البوت تلقائياً!",
        'success': "🎉🎊 تـم تـفـعـيـل الـبـوت بـنـجـاح! 🎊🎉\n\n🔓 تم منحك تصريح الدخول بنجاح، يمكنك الآن استخدام كافة الميزات المتاحة. ✨🚀",
        'fail': "❌ عذراً، الرمز الذي أدخلته غير صحيح!\n\n🔐 من فضلك احصل على login خصتك لفتح البوت مع ايموجيات جذابة وجميلة رجاء اتصل ب @i6issiiiii للحصول على تصريح 👑💎",
        'active': "🔄 تم استقبال رسالتك بنجاح! (البوت قيد الخدمة...) ⚡"
    },
    'en': {
        'admin_welcome': "Hello! Your ID is: {user_id}\nWelcome back Admin! The bot is fully active and ready. 👑🔥",
        'user_welcome': "Welcome back! The bot is unlocked and ready for use. 🚀✨",
        'unauthorized': "Hello! Your ID is: {user_id}\n\n🔒 Please get your login to open the bot with attractive and beautiful emojis, please contact @i6issiiiii to get authorization ✨💌\n\n🔑 If you have the access code, send it now to activate!",
        'success': "🎉🎊 Bot activated successfully! 🎊🎉\n\n🔓 Access granted, you can now use all the features. ✨🚀",
        'fail': "❌ Sorry, the code you entered is incorrect!\n\n🔐 Please get your login to open the bot with attractive and beautiful emojis, please contact @i6issiiiii to get authorization 👑💎",
        'active': "🔄 Message received successfully! (Bot is in service...) ⚡"
    },
    'hi': { # الهندية
        'admin_welcome': "नमस्ते! आपकी आईडी है: {user_id}\nस्वागत है एडमिन! बोट पूरी तरह से सक्रिय है। 👑🔥",
        'user_welcome': "आपका स्वागत है! बोट अनलॉक है और उपयोग के लिए तैयार है। 🚀✨",
        'unauthorized': "नमस्ते! आपकी आईडी है: {user_id}\n\n🔒 आकर्षक और सुंदर इमोजी के साथ बोट को खोलने के लिए कृपया अपना लॉगिन प्राप्त करें, अनुमति प्राप्त करने के लिए कृपया @i6issiiiii से संपर्क करें ✨💌\n\n🔑 यदि आपके पास एक्सेस कोड है, तो सक्रिय करने के लिए इसे अभी भेजें!",
        'success': "🎉🎊 बोट सफलतापूर्वक सक्रिय हो गया! 🎊🎉\n\n🔓 पहुंच प्रदान की गई, अब आप सभी सुविधाओं का उपयोग कर सकते हैं। ✨🚀",
        'fail': "❌ क्षमा करें, आपके द्वारा दर्ज किया गया कोड गलत है!\n\n🔐 आकर्षक और सुंदर इमोजी के साथ बोट को खोलने के लिए कृपया अपना लॉगिन प्राप्त करें, अनुमति प्राप्त करने के लिए कृपया @i6issiiiii से संपर्क करें 👑💎",
        'active': "🔄 संदेश सफलतापूर्वक प्राप्त हुआ! (बोट सेवा में है...) ⚡"
    },
    'vi': { # الفيتنامية
        'admin_welcome': "Xin chào! ID của bạn là: {user_id}\nChào mừng Admin trở lại! Bot đã sẵn sàng hoạt động. 👑🔥",
        'user_welcome': "Chào mừng trở lại! Bot đã mở khóa và sẵn sàng sử dụng. 🚀✨",
        'unauthorized': "Xin chào! ID của bạn là: {user_id}\n\n🔒 Vui lòng nhận login của bạn để mở bot với các biểu tượng cảm xúc hấp dẫn và đẹp mắt, vui lòng liên hệ @i6issiiiii để được cấp phép ✨💌\n\n🔑 Nếu bạn có mã truy cập, hãy gửi nó ngay bây giờ để kích hoạt!",
        'success': "🎉🎊 Bot đã được kích hoạt thành công! 🎊🎉\n\n🔓 Quyền truy cập đã được cấp, giờ bạn có thể sử dụng mọi tính năng. ✨🚀",
        'fail': "❌ Xin lỗi, mã bạn nhập không chính xác!\n\n🔐 Vui lòng nhận login của bạn để mở bot với các biểu tượng cảm xúc hấp dẫn và đẹp mắt, vui lòng liên hệ @i6issiiiii để được cấp phép 👑💎",
        'active': "🔄 Đã nhận tin nhắn thành công! (Bot đang hoạt động...) ⚡"
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # إرسال قائمة اختيار اللغات فوراً عند الضغط على start
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
    lang = query.data.split('_')[1] # استخراج رمز اللغة (ar, en, hi, vi)
    
    # حفظ لغة المستخدم
    user_languages[user_id] = lang
    
    # التحقق من الصلاحيات بعد اختيار اللغة
    if user_id in authorized_users:
        if user_id == ADMIN_ID:
            text = MESSAGES[lang]['admin_welcome'].format(user_id=user_id)
        else:
            text = MESSAGES[lang]['user_welcome']
        await query.edit_message_text(text)
    else:
        text = MESSAGES[lang]['unauthorized'].format(user_id=user_id)
        await query.edit_message_text(text)

async def check_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # تحديد لغة المستخدم (العربية كافتراضية إذا لم يختار لغة بعد)
    lang = user_languages.get(user_id, 'ar')
    
    # إذا كان المستخدم مصرح له بالفعل
    if user_id in authorized_users:
        await update.message.reply_text(MESSAGES[lang]['active'])
        return

    # محاولة تسجيل الدخول
    if text == LOGIN_PASSWORD:
        authorized_users.add(user_id)
        await update.message.reply_text(MESSAGES[lang]['success'])
    else:
        await update.message.reply_text(MESSAGES[lang]['fail'])

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    # الهاندلرز الخاصة بالبوت
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(language_choice, pattern='^lang_'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_access))
    
    print("⚡ البوت يعمل بنجاح مع دعم 4 لغات وتحت حمايتك كأدمن...")
    application.run_polling()
