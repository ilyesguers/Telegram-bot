from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import random
import string
import json
import os

# --- Configurations ---
TOKEN = '8765508457:AAHLzXj9JEMCbnIWfeov39bN75JrRZ9JcfQ'
PRIMARY_ADMIN = 5145154527
SECONDARY_ADMIN = 8300889547  
SUPPORT_USER = "@i6issiiiii"
CHANNEL_ID = "@TQA_CHANNEL"  # معرف قناتك (SISI MODE) المربوطة بالبوت
BACKUP_FILE = "fluorite_backup.json"

# --- Database & Variables ---
ADMIN_LIST = {PRIMARY_ADMIN, SECONDARY_ADMIN}

# قاعدة بيانات الحسابات المسموح لها بالدخول
APPROVED_ACCOUNTS = {
    "demo_key": "pass123" 
}

# لتتبع مستخدمي البوت
all_bot_users = set()
authenticated_users = set()

PRODUCTS = {
    "Fluorite Hack 💎": {"1": 5.0, "7": 15.0, "30": 40.0},
    "Drip Hack 💧": {"1": 4.0, "7": 12.0, "30": 35.0}
}
user_balances = {}    
user_currencies = {}  
user_countries = {}   
active_coupons = {"CHARGE-10USD": 10.0, "CHARGE-50USD": 50.0}
fluorite_stock = {
    "Fluorite Hack 💎": {"1": ["FLUORITE-1DAY-XXXX"], "7": ["FLUORITE-7DAY-ZZZZ"], "30": ["FLUORITE-30DAY-AAAA"]},
    "Drip Hack 💧": {"1": ["DRIP-1DAY-1111"], "7": ["DRIP-7DAY-2222"], "30": ["DRIP-30DAY-3333"]}
}

# دالة إخفاء منتصف الأكواد
def mask_credential(text):
    if not text:
        return ""
    if ":" in text:
        parts = text.split(":", 1)
        return f"{mask_string(parts[0])}:{mask_string(parts[1])}"
    return mask_string(text)

def mask_string(s):
    s_len = len(s)
    if s_len <= 6:
        return s[0] + "****" + s[-1] if s_len > 1 else "****"
    return s[:4] + "*" * (s_len - 8) + s[-4:]

# --- Auto/Manual Backup System ---
def save_system_backup():
    backup_data = {
        "admins": list(ADMIN_LIST), "balances": user_balances, "currencies": user_currencies,
        "countries": user_countries, "coupons": active_coupons, "stock": fluorite_stock, 
        "products": PRODUCTS, "accounts": APPROVED_ACCOUNTS, "all_users": list(all_bot_users)
    }
    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=4)

def load_system_backup():
    global ADMIN_LIST, user_balances, user_currencies, user_countries, active_coupons, fluorite_stock, PRODUCTS, APPROVED_ACCOUNTS, all_bot_users
    if os.path.exists(BACKUP_FILE):
        try:
            with open(BACKUP_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                saved_admins = data.get("admins", [])
                ADMIN_LIST = set(saved_admins) | {PRIMARY_ADMIN, SECONDARY_ADMIN}
                user_balances = {int(k): v for k, v in data.get("balances", {}).items()}
                user_currencies = {int(k): v for k, v in data.get("currencies", {}).items()}
                user_countries = {int(k): v for k, v in data.get("countries", {}).items()}
                active_coupons = data.get("coupons", {})
                fluorite_stock = data.get("stock", {})
                PRODUCTS = data.get("products", PRODUCTS)
                APPROVED_ACCOUNTS = data.get("accounts", APPROVED_ACCOUNTS)
                all_bot_users = set(data.get("all_users", []))
        except Exception as e: print(f"Backup load failed: {e}")

load_system_backup()

EXCHANGE_RATES = {
    "SA": {"symbol": "SAR", "rate": 3.75},
    "EG": {"symbol": "EGP", "rate": 47.0},
    "AE": {"symbol": "AED", "rate": 3.67},
    "DZ": {"symbol": "DZD", "rate": 134.0},
    "IQ": {"symbol": "IQD", "rate": 1310.0},
    "DEFAULT": {"symbol": "$", "rate": 1.0}
}

admin_states, user_states, admin_view_mode = {}, {}, {}

def get_user_currency_info(user_id):
    country = user_countries.get(user_id, "DEFAULT")
    return ("$", 1.0) if user_currencies.get(user_id, "USD") == "USD" else (EXCHANGE_RATES.get(country, EXCHANGE_RATES["DEFAULT"])["symbol"], EXCHANGE_RATES.get(country, EXCHANGE_RATES["DEFAULT"])["rate"])

def format_price(usd_amount, symbol, rate):
    return f"{usd_amount * rate:.1f} $" if symbol == "$" else f"{usd_amount * rate:.1f} {symbol}"

# --- Keyboards ---
def get_admin_keyboard():
    # كيبورد الأدمن (كما هو، لم يتم تغييره)
    return ReplyKeyboardMarkup([
        [KeyboardButton("➕ Add Product"), KeyboardButton("❌ Delete Product")],
        [KeyboardButton("🎫 Mint Coupon"), KeyboardButton("📦 Add Keys")],
        [KeyboardButton("⚙️ Edit Prices"), KeyboardButton("🗑️ Delete Key")],
        [KeyboardButton("👥 Add Admin"), KeyboardButton("👤 Create Login Pass")],
        [KeyboardButton("📢 Broadcast")],
        [KeyboardButton("📊 Statistics"), KeyboardButton("💾 Save Backup")],
        [KeyboardButton("👤 View as User")]
    ], resize_keyboard=True)

def get_user_keyboard():
    # كيبورد المستخدم الجديد (تم استبداله بالأزرار الـ 3 الجديدة)
    keyboard = [
        [KeyboardButton("🩷 شراء مفتاح")],
        [KeyboardButton("💙 Support")],
        [KeyboardButton("🚪 log out")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    all_bot_users.add(user_id) 
    admin_states[user_id] = user_states[user_id] = None

    if user_id in ADMIN_LIST and admin_view_mode.get(user_id, 'admin') == 'admin':
        await update.message.reply_text("⚡ **Welcome back, Boss! Control Panel is ready:**", reply_markup=get_admin_keyboard())
        return

    # إذا كان المستخدم لم يسجل دخوله بعد
    if user_id not in authenticated_users and user_id not in ADMIN_LIST:
        user_states[user_id] = "awaiting_login_credentials"
        # واجهة الدخول الجديدة
        welcome_login_msg = (
            "Please send your credentials in the following format:\n\n"
            "`LOGIN`\n"
            "`PASSWORD`"
        )
        await update.message.reply_text(welcome_login_msg, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
        return

    # إذا كان المستخدم مسجل دخوله، نعرض واجهة الأزرار الـ 3 الجديدة
    if user_id not in user_countries: user_countries[user_id] = random.choice(["SA", "EG", "AE", "DZ", "IQ"])
    await show_user_welcome(update, user_id)

async def show_user_welcome(update: Update, user_id: int):
    # نعرض واجهة الأزرار الـ 3 الجديدة مع رسالة ترحيب
    msg = (
        "✅ **Access Granted! تم تسجيل الدخول بنجاح.**\n"
        "مرحباً بك في لوحة تحكم المستخدم."
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_user_keyboard())

# --- Inline Callback Hub (للمتجر) ---
async def shop_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if user_id not in authenticated_users and user_id not in ADMIN_LIST:
        return

    if data.startswith("shop_prod_"):
        prod = data.replace("shop_prod_", "")
        sym, rate = get_user_currency_info(user_id)
        
        buttons = []
        if prod in PRODUCTS:
            for d, price in PRODUCTS[prod].items():
                price_str = format_price(price, sym, rate)
                buttons.append([InlineKeyboardButton(f"⏳ {d} Day(s) - {price_str}", callback_data=f"buy_{prod}_{d}")])
        buttons.append([InlineKeyboardButton("🔙 Back to Shop", callback_data="reload_shop")])
        await query.edit_message_text(f"🛍️ **Product Plans for {prod}:**", reply_markup=InlineKeyboardMarkup(buttons))
        return

    if data == "reload_shop":
        buttons = [[InlineKeyboardButton(f"📦 {prod}", callback_data=f"shop_prod_{prod}")] for prod in PRODUCTS.keys()]
        await query.edit_message_text("🛒 **Welcome to our Shop!**", reply_markup=InlineKeyboardMarkup(buttons))
        return

    # ... بقية معالجة المتجر والشراء والأدمن (تبقى كما هي) ...
    if data.startswith("buy_"):
        # نفس منطق الشراء السابق...
        pass
    # ...

# --- Text Messaging Systems ---
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip() if update.message.text else ""
    all_bot_users.add(user_id)

    # التعامل مع محاولة تسجيل الدخول
    if user_id not in authenticated_users and user_id not in ADMIN_LIST:
        if user_states.get(user_id) == "awaiting_login_credentials":
            # التحقق من الصيغة (LOGIN PASSWORD)
            credentials = text.split()
            if len(credentials) == 2:
                input_key = credentials[0].strip()
                input_pass = credentials[1].strip()
                
                if APPROVED_ACCOUNTS.get(input_key) == input_pass:
                    authenticated_users.add(user_id)
                    user_states[user_id] = None
                    # بعد النجاح، نعرض واجهة الأزرار الـ 3 الجديدة
                    await show_user_welcome(update, user_id)
                    return
                else:
                    await update.message.reply_text("❌ **بيانات الدخول غير صحيحة!** يرجى المحاولة مرة أخرى.")
                    return
            else:
                await update.message.reply_text("⚠️ يرجى إرسال الـ LOGIN ثم الـ PASSWORD بنفس السطر.")
                return
        else:
            await update.message.reply_text("🔒 يرجى تسجيل الدخول أولاً.")
            return

    # --- Admin Backend Workspace (تبقى كما هي) ---
    if user_id in ADMIN_LIST and admin_view_mode.get(user_id, 'admin') == 'admin':
        # نفس منطق الأدمن السابق...
        # ...
        # (بقية كود الأدمن)
        pass 

    # --- User Frontend Operations (تم تحديثها للأزرار الـ 3) ---
    # زر "شراء مفتاح" (محدد بالوردي)
    if text == "🩷 شراء مفتاح":
        buttons = [[InlineKeyboardButton(f"📦 {prod}", callback_data=f"shop_prod_{prod}")] for prod in PRODUCTS.keys()]
        await update.message.reply_text("🛒 **Welcome to our Shop!**", reply_markup=InlineKeyboardMarkup(buttons))
        return
        
    # زر "Support" (محدد بالأزرق)
    elif text == "💙 Support":
        support_msg = (
            f"👑 **للحصول على تصريح الدخول أو أي مساعدة، تواصل معنا:**\n"
            f"➡️ **Admin Support:** {SUPPORT_USER} ✨"
        )
        await update.message.reply_text(support_msg, parse_mode="Markdown")
        return

    # زر "log out" (تسجيل الخروج)
    elif text == "🚪 log out":
        if user_id in authenticated_users:
            authenticated_users.remove(user_id)
        # بعد الخروج، نعرض واجهة الدخول مرة أخرى
        user_states[user_id] = "awaiting_login_credentials"
        welcome_login_msg = (
            "You have been logged out.\n"
            "Please send your credentials in the following format:\n\n"
            "`LOGIN`\n"
            "`PASSWORD`"
        )
        await update.message.reply_text(welcome_login_msg, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
        return

    # للتبديل بين وضع الأدمن والمستخدم (تبقى كما هي)
    if user_id in ADMIN_LIST and text == "🔙 Admin Panel":
        admin_view_mode[user_id] = 'admin'
        await update.message.reply_text("👑 Welcome back to the Management Room.", reply_markup=get_admin_keyboard())
        return
    if text == "👤 View as User" and user_id in ADMIN_LIST:
        admin_view_mode[user_id] = 'user'
        await show_user_welcome(update, user_id)
        return

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(shop_menu_callback))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_messages))
    print("🏪 Sisi Mode Bot is Running Smoothly...")
    application.run_polling()
