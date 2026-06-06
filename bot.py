from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# --- الإعدادات ---
TOKEN = '8765508457:AAHLzXj9JEMCbnIWfeov39bN75JrRZ9JcfQ'
ADMIN_ID = 5145154527  # الـ ID الخاص بك كأدمن أساسي

# قائمة المستخدمين المصرح لهم (تبدأ بالأدمن تلقائياً)
authorized_users = {ADMIN_ID}

# قاعدة بيانات الحسابات المسموح لها بالدخول (الـ Login والـ Password)
valid_credentials = {
    "admin123": "pass123"  # حساب افتراضي للتجربة
}

# قاموس لتخزين لغة كل مستخدم (افتراضياً العربية)
user_languages = {}

# قاموس لحفظ حالة الأدمن المؤقتة (هل ينتظر إضافة حساب أو حذفه؟)
admin_states = {}

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # --- لوحة تحكم الأدمن ---
    if user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("➕ إضافة LOGIN و PASSWORD جديد", callback_data='admin_add')],
            [InlineKeyboardButton("❌ مسح وحظر LOGIN", callback_data='admin_delete')],
            [InlineKeyboardButton("📋 عرض الحسابات النشطة", callback_data='admin_list')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"🎯 **مرحباً بك يا أدمن! الـ ID الخاص بك هو:** `{user_id}`\n\n"
            f"👑 هذه هي لوحة التحكم الخاصة بك لإدارة صلاحيات البوت. اختر الإجراء المطلوبة من الأسفل 👇",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    # --- واجهة المستخدمين الأربعة لغات ---
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

async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data

    # --- معالجة كولباك اللغات للمستخدمين ---
    if data.startswith('lang_'):
        lang = data.split('_')[1]
        user_languages[user_id] = lang
        
        if user_id in authorized_users:
            text = MESSAGES[lang]['user_welcome']
        else:
            text = MESSAGES[lang]['unauthorized'].format(user_id=user_id)
        await query.edit_message_text(text, parse_mode="Markdown")
        
    # --- معالجة كولباك لوحة تحكم الأدمن ---
    elif user_id == ADMIN_ID:
        if data == 'admin_add':
            admin_states[user_id] = 'awaiting_add'
            await query.edit_message_text(
                "➕ **من فضلك أرسل الـ LOGIN والـ PASSWORD الجديدين مفصولين بمسافة.**\n\n"
                "مثال:\n`user55 pass99`", 
                parse_mode="Markdown"
            )
        elif data == 'admin_delete':
            admin_states[user_id] = 'awaiting_delete'
            await query.edit_message_text(
                "❌ **من فضلك أرسل اسم الـ LOGIN الذي تريد حذفه وحظره من البوت تماماً:**",
                parse_mode="Markdown"
            )
        elif data == 'admin_list':
            if not valid_credentials:
                text = "📋 لا توجد أي حسابات نشطة حالياً في قاعدة البيانات."
            else:
                text = "📋 **قائمة الحسابات النشطة والمتاحة حالياً:**\n\n"
                for log, pas in valid_credentials.items():
                    text += f"👤 LOGIN: `{log}`  |  🔑 PASSWORD: `{pas}`\n"
            
            # زر للعودة للوحة الرئيسية
            keyboard = [[InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_back')]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            
        elif data == 'admin_back':
            admin_states[user_id] = None
            keyboard = [
                [InlineKeyboardButton("➕ إضافة LOGIN و PASSWORD جديد", callback_data='admin_add')],
                [InlineKeyboardButton("❌ مسح وحظر LOGIN", callback_data='admin_delete')],
                [InlineKeyboardButton("📋 عرض الحسابات النشطة", callback_data='admin_list')]
            ]
            await query.edit_message_text("👑 لوحة تحكم الأدمن الرئيسية:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    lang = user_languages.get(user_id, 'ar')

    # --- منطق ومعالجة رسائل الأدمن ---
    if user_id == ADMIN_ID:
        state = admin_states.get(user_id)
        
        # 1. عند استقبال بيانات الإضافة
        if state == 'awaiting_add':
            parts = text.split()
            if len(parts) >= 2:
                new_login = parts[0]
                new_password = parts[1]
                valid_credentials[new_login] = new_password
                admin_states[user_id] = None # تصفير الحالة
                await update.message.reply_text(f"✅ تم حفظ الحساب بنجاح!\n👤 LOGIN: `{new_login}`\n🔑 PASSWORD: `{new_password}`", parse_mode="Markdown")
            else:
                await update.message.reply_text("⚠️ خطأ في الصيغة. يرجى إرسال الـ LOGIN والـ PASSWORD وبينهما مسافة فقط:")
            return
            
        # 2. عند استقبال طلب المسح والحظر
        elif state == 'awaiting_delete':
            if text in valid_credentials:
                del valid_credentials[text]
                admin_states[user_id] = None
                await update.message.reply_text(f"🗑️ تم مسح وحظر الـ LOGIN: `{text}` بنجاح ومنع تفعيله!", parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ هذا الـ LOGIN غير موجود في قاعدة البيانات للتأكيد. أرسل الاسم الصحيح:")
            return

    # --- إذا كان مستخدم عادي ومصرح له سابقاً ---
    if user_id in authorized_users:
        await update.message.reply_text(MESSAGES[lang]['active'])
        return

    # --- فحص محاولة تسجيل دخول المستخدم العادي (المطلوب سطرين) ---
    lines = text.split('\n')
    if len(lines) == 2:
        input_login = lines[0].strip()
        input_password = lines[1].strip()
        
        if input_login in valid_credentials and valid_credentials[input_login] == input_password:
            authorized_users.add(user_id)
            # لحماية الحساب من التداول (اختياري: يمسح الحساب بمجرد استخدامه لمرة واحدة)
            del valid_credentials[input_login] 
            await update.message.reply_text(MESSAGES[lang]['success'])
        else:
            await update.message.reply_text(MESSAGES[lang]['fail'])
    else:
        await update.message.reply_text(MESSAGES[lang]['fail'])

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(handle_callbacks))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    
    print("⚡ البوت يعمل بكفاءة مع لوحة تحكم الأدمن والأزرار التفاعلية ودعم 4 لغات...")
    application.run_polling()
