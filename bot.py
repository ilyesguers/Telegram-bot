from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telethon import TelegramClient, events
from telegram.ext import Application
import random
import string
import json
import os
import asyncio

# --- Configurations ---
TOKEN = '8765508457:AAHLzXj9JEMCbnIWfeov39bN75JrRZ9JcfQ'
PRIMARY_ADMIN = 5145154527
SECONDARY_ADMIN = 8300889547  
SUPPORT_USER = "@i6issiiiii"
CHANNEL_ID = "@TQA_CHANNEL"  

# --- Telethon Configurations ---
API_ID = 26481531
API_HASH = '8d8ea2b8bde9b22bb7f4b6de905bd3f7'
TARGET_BOT = '@FlouriteReseller_bot'
DRIP_RESET_BOT = '@ResetDrip_bot'

client = TelegramClient('bot_session', API_ID, API_HASH)
pending_requests = {}

BACKUP_FILE = "fluorite_backup.json"

# --- Database & Variables ---
ADMIN_LIST = {PRIMARY_ADMIN, SECONDARY_ADMIN}
APPROVED_ACCOUNTS = {"demo_key": "pass123"}
all_bot_users = set()
authenticated_users = set()

PRODUCTS = {
    "Fluorite Hack 💎": {"1": 5.0, "7": 15.0, "30": 40.0},
    "Drip Hack 💧": {"1": 4.0, "7": 12.0, "30": 35.0}
}
user_balances, user_currencies, user_countries = {}, {}, {}
active_coupons = {"CHARGE-10USD": 10.0, "CHARGE-50USD": 50.0}
fluorite_stock = {
    "Fluorite Hack 💎": {"1": ["FLUORITE-1DAY-XXXX"], "7": ["FLUORITE-7DAY-ZZZZ"], "30": ["FLUORITE-30DAY-AAAA"]},
    "Drip Hack 💧": {"1": ["DRIP-1DAY-1111"], "7": ["DRIP-7DAY-2222"], "30": ["DRIP-30DAY-3333"]}
}

def mask_credential(text):
    if not text: return ""
    if ":" in text:
        parts = text.split(":", 1)
        return f"{mask_string(parts[0])}:{mask_string(parts[1])}"
    return mask_string(text)

def mask_string(s):
    s_len = len(s)
    if s_len <= 6: return s[0] + "****" + s[-1] if s_len > 1 else "****"
    return s[:4] + "*" * (s_len - 8) + s[-4:]

def generate_random_16_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

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
                ADMIN_LIST = set(data.get("admins", [])) | {PRIMARY_ADMIN, SECONDARY_ADMIN}
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
    "SA": {"symbol": "SAR", "rate": 3.75}, "EG": {"symbol": "EGP", "rate": 47.0},
    "AE": {"symbol": "AED", "rate": 3.67}, "DZ": {"symbol": "DZD", "rate": 134.0},
    "IQ": {"symbol": "IQD", "rate": 1310.0}, "DEFAULT": {"symbol": "$", "rate": 1.0}
}

admin_states, user_states, admin_view_mode = {}, {}, {}

def get_user_currency_info(user_id):
    country = user_countries.get(user_id, "DEFAULT")
    return ("$", 1.0) if user_currencies.get(user_id, "USD") == "USD" else (EXCHANGE_RATES.get(country, EXCHANGE_RATES["DEFAULT"])["symbol"], EXCHANGE_RATES.get(country, EXCHANGE_RATES["DEFAULT"])["rate"])

def format_price(usd_amount, symbol, rate):
    return f"{usd_amount * rate:.1f} $" if symbol == "$" else f"{usd_amount * rate:.1f} {symbol}"

# --- NEW Keyboards (Renamed to break old cache) ---
def get_admin_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("➕ Add New Product"), KeyboardButton("❌ Remove Product")],
        [KeyboardButton("🎫 Create Coupon"), KeyboardButton("📦 Load Keys")],
        [KeyboardButton("⚙️ Modify Prices"), KeyboardButton("🗑️ Erase Key")],
        [KeyboardButton("👥 Manage Admins"), KeyboardButton("👤 New Login Pass")],
        [KeyboardButton("📢 Send Broadcast"), KeyboardButton("🪄 Trigger Fake Sale")],
        [KeyboardButton("📊 System Stats"), KeyboardButton("💾 Manual Backup")],
        [KeyboardButton("👤 Enter User Mode")]
    ], resize_keyboard=True)

def get_user_keyboard(user_id):
    bal_str = format_price(user_balances.get(user_id, 0.0), *get_user_currency_info(user_id))
    keyboard = [
        [KeyboardButton("🛒 Wholesale Shop"), KeyboardButton("💳 Top-up Balance")],
        [KeyboardButton(f"💰 My Wallet [{bal_str}]"), KeyboardButton("💱 Switch Currency")],
        [KeyboardButton("🔄 Reset Drip Key"), KeyboardButton("📁 Drip File Check")],
        [KeyboardButton("💬 Live Support")]
    ]
    if user_id in ADMIN_LIST:
        keyboard.insert(0, [KeyboardButton("🔙 Return to Admin")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    all_bot_users.add(user_id) 
    admin_states[user_id] = user_states[user_id] = None

    if user_id not in user_balances: user_balances[user_id] = 0.0
    if user_id not in user_countries: user_countries[user_id] = random.choice(["SA", "EG", "AE", "DZ", "IQ"])

    if user_id in ADMIN_LIST and admin_view_mode.get(user_id, 'admin') == 'admin':
        await update.message.reply_text("⚡ **Welcome back, Boss! Control Panel is ready:**", reply_markup=get_admin_keyboard())
        return

    if user_id not in authenticated_users and user_id not in ADMIN_LIST:
        user_states[user_id] = "awaiting_login_credentials"
        welcome_secure_msg = (
            "🔒 **مرحباً بك في متجر الجملة السري والحصري!**\n"
            "✨ *هذا البوت محمي ومخصص للأعضاء المصرح لهم فقط بأسعار رخيصة جداً.*\n\n"
            "💬 **الرجاء إرسال تفاصيل الدخول الخاصة بك بالصيغة التالية:**\n"
            "👉 `loginkey:password`\n\n"
            f"👑 **To get your private access pass, contact support:**\n"
            f"➡️ **Contact Admin:** {SUPPORT_USER} ✨"
        )
        await update.message.reply_text(welcome_secure_msg, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
        return

    if user_id not in user_currencies:
        sym = EXCHANGE_RATES.get(user_countries[user_id], EXCHANGE_RATES["DEFAULT"])["symbol"]
        await update.message.reply_text(f"🌍 **Currency Choice**\n\nDo you want to see prices in your **Local Currency ({sym})** or **USD ($)**?", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🟢 My Currency"), KeyboardButton("💵 USD ($)")]], resize_keyboard=True))
        return

    await show_user_welcome(update, user_id)

async def show_user_welcome(update: Update, user_id: int):
    bal_str = format_price(user_balances.get(user_id, 0.0), *get_user_currency_info(user_id))
    msg = (
        f"👋 **Access Granted! Welcome to our wholesale store!** ✨\n\n"
        f"💳 **Your Balance:** `{bal_str}`\n\n"
        f"Enjoy our specially discounted prices below.\n"
        f"👑 **Support Desk:** {SUPPORT_USER} ✨"
    )
    # The new keyboard will overwrite the old stuck ones!
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))

# --- Fluorite Reset Command ---
async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in authenticated_users and user_id not in ADMIN_LIST: return
    
    if not context.args:
        await update.message.reply_text("❌ **Please provide the 16-character code.**\nExample: `/reset ABCDEFGHIJKLMNOP`", parse_mode="Markdown")
        return
        
    code = context.args[0].strip()
    if not client.is_connected(): await client.connect()
    
    await client.send_message(TARGET_BOT, f"/fluorite {code}")
    pending_requests[user_id] = {"type": "fluorite"}
    await update.message.reply_text("⏳ **Reset request sent!** Waiting for response...", parse_mode="Markdown")

# --- Inline Callback Hub ---
async def shop_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if user_id not in authenticated_users and user_id not in ADMIN_LIST: return

    if data.startswith("shop_prod_"):
        prod = data.replace("shop_prod_", "")
        sym, rate = get_user_currency_info(user_id)
        buttons = []
        if prod in PRODUCTS:
            for d, price in PRODUCTS[prod].items():
                price_str = format_price(price, sym, rate)
                buttons.append([InlineKeyboardButton(f"⏳ {d} Day(s) - {price_str}", callback_data=f"buy_{prod}_{d}")])
        buttons.append([InlineKeyboardButton("🔙 Back to Shop", callback_data="reload_shop")])
        await query.edit_message_text(f"🛍️ **Product Plans for {prod}:**\n\nChoose your preferred duration package below:", reply_markup=InlineKeyboardMarkup(buttons))
        return

    if data == "reload_shop":
        buttons = [[InlineKeyboardButton(f"📦 {prod}", callback_data=f"shop_prod_{prod}")] for prod in PRODUCTS.keys()]
        await query.edit_message_text("🛒 **Welcome to our Shop!**\n\nSelect a product category to view plans:", reply_markup=InlineKeyboardMarkup(buttons))
        return

    if data.startswith("buy_"):
        parts = data.split("_")
        selected_prod = parts[1]
        selected_days = parts[2]
        context.user_data["selected_product"] = selected_prod
        context.user_data["selected_days"] = selected_days
        
        price_usd = PRODUCTS[selected_prod][selected_days]
        sym, rate = get_user_currency_info(user_id)
        price_str = format_price(price_usd, sym, rate)
        
        user_states[user_id] = "awaiting_checkout_confirm"
        checkout_msg = (
            f"🛍️ **Your Order Summary**\n\n"
            f"📦 **Product:** `{selected_prod}`\n"
            f"⏱️ **Duration:** `{selected_days} Day(s)`\n"
            f"💵 **Price:** `{price_str}`\n\n"
            f"🌸 To confirm your order, reply with the word: **`ok`**"
        )
        await query.edit_message_text(checkout_msg, parse_mode="Markdown")
        return

    if data.startswith("adm_add_"):
        prod = data.replace("adm_add_", "")
        context.user_data["adm_prod"] = prod
        buttons = [[InlineKeyboardButton(f"📅 {d} Day(s)", callback_data=f"adm_dur_{d}")] for d in PRODUCTS[prod].keys()]
        await query.edit_message_text(f"📦 Adding keys for **{prod}**\nSelect duration plan:", reply_markup=InlineKeyboardMarkup(buttons))
        return

    if data.startswith("adm_dur_"):
        dur = data.replace("adm_dur_", "")
        context.user_data["adm_dur"] = dur
        admin_states[user_id] = "awaiting_raw_keys"
        await query.edit_message_text(f"📝 **Almost done!**\nNow send the keys/codes (You can paste one or multiple lines):")
        return

    if data.startswith("adm_prc_"):
        prod = data.replace("adm_prc_", "")
        context.user_data["adm_prod"] = prod
        buttons = [[InlineKeyboardButton(f"⚙️ Edit {d} Day Price", callback_data=f"adm_p_dur_{d}")] for d in PRODUCTS[prod].keys()]
        await query.edit_message_text(f"⚙️ Modifying rates for **{prod}**\nSelect a duration plan to edit:", reply_markup=InlineKeyboardMarkup(buttons))
        return

    if data.startswith("adm_p_dur_"):
        dur = data.replace("adm_p_dur_", "")
        context.user_data["adm_dur"] = dur
        admin_states[user_id] = "awaiting_raw_price"
        await query.edit_message_text(f"💵 Please send the **New Price in USD ($)** for this plan (numbers only):")
        return

    if data.startswith("adm_del_p_"):
        prod = data.replace("adm_del_p_", "")
        if prod in PRODUCTS: del PRODUCTS[prod]
        if prod in fluorite_stock: del fluorite_stock[prod]
        save_system_backup()
        await query.edit_message_text(f"✅ Product **{prod}** has been completely deleted from store.")
        return

# --- Text Messaging Systems ---
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip() if update.message.text else ""
    all_bot_users.add(user_id)

    # Document Handling (For File Check & Backup Restore)
    if update.message.document:
        if user_states.get(user_id) == "awaiting_drip_file":
            user_states[user_id] = None
            file = await context.bot.get_file(update.message.document.file_id)
            path = f"temp_{update.message.document.file_name}"
            await file.download_to_drive(path)
            
            if not client.is_connected(): await client.connect()
            await client.send_file(DRIP_RESET_BOT, path)
            os.remove(path)
            
            pending_requests[user_id] = {"type": "drip"}
            await update.message.reply_text("⏳ **File sent!** Waiting for check results...", parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
            return
            
        elif user_id in ADMIN_LIST and admin_view_mode.get(user_id, 'admin') == 'admin':
            if update.message.document.file_name == BACKUP_FILE:
                file_obj = await context.bot.get_file(update.message.document.file_id)
                await file_obj.download_to_drive(custom_path=BACKUP_FILE)
                load_system_backup()
                await update.message.reply_text("⚡ **Database file recovered!**", reply_markup=get_admin_keyboard())
                return
        return

    # Authentication Handling
    if user_id not in authenticated_users and user_id not in ADMIN_LIST:
        if user_states.get(user_id) == "awaiting_login_credentials":
            if ":" in text:
                input_key, input_pass = text.split(":", 1)
                if APPROVED_ACCOUNTS.get(input_key.strip()) == input_pass.strip():
                    authenticated_users.add(user_id)
                    user_states[user_id] = None
                    await update.message.reply_text("🎉 **Access Granted / تم تفعيل دخولك بنجاح!**")
                    if user_id not in user_currencies:
                        sym = EXCHANGE_RATES.get(user_countries[user_id], EXCHANGE_RATES["DEFAULT"])["symbol"]
                        await update.message.reply_text(f"🌍 **Currency Choice**\n\nDo you want to see prices in your **Local Currency ({sym})** or **USD ($)**?", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🟢 My Currency"), KeyboardButton("💵 USD ($)")]], resize_keyboard=True))
                    else:
                        await show_user_welcome(update, user_id)
                    return
                else:
                    await update.message.reply_text("❌ **Invalid Login Key or Password!** بيانات الدخول غير صحيحة، يرجى إعادة المحاولة.")
                    return
            else:
                await update.message.reply_text("⚠️ صيغة الإرسال خاطئة، أرسل الحساب هكذا فقط:\n`loginkey:password`")
                return
        else:
            await update.message.reply_text("🔒 الرجاء كتابة `/start` لتسجيل الدخول أولاً.")
            return

    if text in ["🟢 My Currency", "💵 USD ($)"]:
        user_currencies[user_id] = "LOCAL" if "My" in text else "USD"
        save_system_backup()
        await show_user_welcome(update, user_id)
        return

    # --- Admin Backend Workspace (Exact Matches to New Names) ---
    if user_id in ADMIN_LIST and admin_view_mode.get(user_id, 'admin') == 'admin':
        if text == "➕ Add New Product":
            admin_states[user_id] = 'await_new_prod_name'
            await update.message.reply_text("📝 Enter the name of the new product/cheat to add:", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "❌ Remove Product":
            buttons = [[InlineKeyboardButton(f"🗑️ Delete {prod}", callback_data=f"adm_del_p_{prod}")] for prod in PRODUCTS.keys()]
            await update.message.reply_text("⚠️ **Select product to delete permanently:**", reply_markup=InlineKeyboardMarkup(buttons))
            return
        elif text == "🎫 Create Coupon":
            admin_states[user_id] = 'await_coup'
            await update.message.reply_text("💵 Enter coupon value in USD (numbers only):", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "📦 Load Keys":
            buttons = [[InlineKeyboardButton(prod, callback_data=f"adm_add_{prod}")] for prod in PRODUCTS.keys()]
            await update.message.reply_text("📦 **Select target product to load stock:**", reply_markup=InlineKeyboardMarkup(buttons))
            return
        elif text == "⚙️ Modify Prices":
            buttons = [[InlineKeyboardButton(prod, callback_data=f"adm_prc_{prod}")] for prod in PRODUCTS.keys()]
            admin_markup = InlineKeyboardMarkup(buttons)
            await update.message.reply_text("⚙️ **Select a product to edit its current plan prices:**", reply_markup=admin_markup)
            custom_plan_btn = [[InlineKeyboardButton("➕ Add New Custom Daily Plan", callback_data="adm_add_custom_day")]]
            await update.message.reply_text("✨ **Or add a completely new standalone plan to any product:**", reply_markup=InlineKeyboardMarkup(custom_plan_btn))
            return
        elif text == "🗑️ Erase Key":
            admin_states[user_id] = 'await_del'
            await update.message.reply_text("Paste the code you want to remove from stock:", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "👥 Manage Admins":
            admin_states[user_id] = 'await_adm'
            await update.message.reply_text("Send the Telegram ID of the new admin:", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "👤 New Login Pass":
            admin_states[user_id] = 'await_create_user_account'
            await update.message.reply_text("📝 أرسل الحساب الجديد للزبون بالصيغة التالية:\n`loginkey:password`", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "📢 Send Broadcast":
            admin_states[user_id] = 'await_broadcast_message'
            await update.message.reply_text("📝 **أرسل الآن الرسالة التي تريد تعميمها ونشرها في القناة ولجميع مستخدمي البوت:**", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "🪄 Trigger Fake Sale":
            admin_states[user_id] = 'await_fake_sale_confirmation'
            await update.message.reply_text("⚠️ **تأكيد الإجراء:**\nالرجاء كتابة كلمة `تأكيد` لإنشاء ونشر إشعار الشراء الوهمي في القناة فوراً:", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "📊 System Stats":
            msg = f"🎫 **Active Coupons:** {', '.join([f'`{k}: {v}$`' for k,v in active_coupons.items()])}\n👥 **Total Authorized Accounts:** `{len(APPROVED_ACCOUNTS)}` accounts\n📢 **Total Bot Observers:** `{len(all_bot_users)}` users\n\n📦 **Current Stock:**\n"
            for p, d in fluorite_stock.items():
                msg += f"🔹 `{p}` -> " + " | ".join([f"Day {k}: ({len(v)})" for k,v in d.items()]) + "\n"
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_admin_keyboard())
            return
        elif text == "💾 Manual Backup":
            save_system_backup()
            await update.message.reply_document(document=open(BACKUP_FILE, 'rb'), filename=BACKUP_FILE, caption="📥 **Database backup file successfully created!**", reply_markup=get_admin_keyboard())
            return
        elif text == "👤 Enter User Mode":
            admin_view_mode[user_id] = 'user'
            authenticated_users.add(user_id)
            if user_id not in user_currencies: user_currencies[user_id] = "USD"
            await update.message.reply_text("🔄 Switched to User View simulation.", reply_markup=get_user_keyboard(user_id))
            return

        # Processing Admin Input States
        state = admin_states.get(user_id)
        if state == 'await_fake_sale_confirmation':
            admin_states[user_id] = None
            if text == "تأكيد":
                raw_fake_16_code = generate_random_16_code()
                masked_fake_code = mask_credential(raw_fake_16_code)
                attractive_fake_msg = (
                    f"🔥 **NEW SUCCESSFUL PURCHASE!** 🔥\n\n"
                    f"⚡ **SOMEONE JUST BOUGHT A CODE NOW!** ⚡\n"
                    f"📈 **STORE IS ON FIRE!** 📈\n\n"
                    f"🤝 *Thank you for your endless trust in us! We promise to always deliver the latest updates and the absolute best tools for you!* ✨💎\n\n"
                    f"📥 **The code obtained by the user:**\n"
                    f"👉 `{masked_fake_code}` 🚀"
                )
                try:
                    await context.bot.send_message(chat_id=CHANNEL_ID, text=attractive_fake_msg, parse_mode="Markdown")
                    await update.message.reply_text("✅ **[نجاح]** تم نشر الإشعار المشتعل في القناة بنجاح!", reply_markup=get_admin_keyboard())
                except Exception as e:
                    await update.message.reply_text(f"❌ تم التأكيد لكن فشل الإرسال للقناة (تأكد من صلاحيات البوت). الخطأ: {e}", reply_markup=get_admin_keyboard())
            else: await update.message.reply_text("❌ إلغاء الإجراء، الكلمة التي أدخلتها ليست `تأكيد`.", reply_markup=get_admin_keyboard())
            return
        elif state == 'await_broadcast_message':
            admin_states[user_id] = None
            success_count = fail_count = 0
            await update.message.reply_text(f"⏳ جاري النشر في القناة وبدء النشر الجماعي لـ {len(all_bot_users)} مستخدم...")
            try:
                await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
                channel_status = "✅ تم النشر في القناة بنجاح!"
            except Exception as e: channel_status = f"❌ فشل النشر في القناة. الخطأ: {e}"
            for u_id in list(all_bot_users):
                try:
                    await context.bot.send_message(chat_id=u_id, text=text)
                    success_count += 1
                except: fail_count += 1
            report_msg = f"📢 **تم انتهاء عملية الإذاعة الجماعية!**\n\n📺 **حالة القناة:**\n{channel_status}\n\n👥 **حالة المشتركين في الخاص:**\n✅ تم التسليم لـ: `{success_count}` مستخدم.\n❌ فشل الإرسال لـ: `{fail_count}` مستخدم."
            await update.message.reply_text(report_msg, parse_mode="Markdown", reply_markup=get_admin_keyboard())
            return
        elif state == 'await_new_prod_name':
            PRODUCTS[text] = {}
            fluorite_stock[text] = {}
            save_system_backup()
            await update.message.reply_text(f"✅ Product **{text}** created successfully!", reply_markup=get_admin_keyboard())
            admin_states[user_id] = None; return
        elif state == 'await_create_user_account':
            if ":" in text:
                u, p = text.split(":", 1)
                APPROVED_ACCOUNTS[u.strip()] = p.strip()
                save_system_backup()
                await update.message.reply_text(f"✅ **تم إنشاء تصريح العميل بنجاح!**\n👤 الـ Login Key: `{u.strip()}`\n🔑 الـ Password: `{p.strip()}`", parse_mode="Markdown", reply_markup=get_admin_keyboard())
            else: await update.message.reply_text("❌ صيغة خاطئة، لم يتم الإنشاء. يجب استخدام `loginkey:password`", reply_markup=get_admin_keyboard())
            admin_states[user_id] = None; return
        elif state == 'awaiting_custom_day_name':
            context.user_data["custom_inject_day"] = text
            buttons = [[InlineKeyboardButton(prod, callback_data=f"inject_day_to_{prod}")] for prod in PRODUCTS.keys()]
            await update.message.reply_text(f"⏱️ Plan duration set to `{text}` Days.\nNow select which product category to assign this plan to:", reply_markup=InlineKeyboardMarkup(buttons))
            admin_states[user_id] = None; return
        elif state == 'awaiting_raw_price':
            p_name = context.user_data.get("adm_prod")
            p_days = context.user_data.get("adm_dur")
            try:
                new_val = float(text)
                if p_name in PRODUCTS:
                    PRODUCTS[p_name][p_days] = new_val
                    if p_name not in fluorite_stock: fluorite_stock[p_name] = {}
                    if p_days not in fluorite_stock[p_name]: fluorite_stock[p_name][p_days] = []
                    save_system_backup()
                    await update.message.reply_text(f"✅ Price updated! **{p_name} ({p_days}D)** is now `{new_val}$`", reply_markup=get_admin_keyboard())
                else: await update.message.reply_text("❌ Error: Product not found.", reply_markup=get_admin_keyboard())
            except: await update.message.reply_text("❌ Numerical digits only.", reply_markup=get_admin_keyboard())
            admin_states[user_id] = None; return
        elif state == 'awaiting_custom_inject_price':
            p_name = context.user_data.get("adm_prod")
            p_days = context.user_data.get("custom_inject_day")
            try:
                new_val = float(text)
                if p_name not in PRODUCTS: PRODUCTS[p_name] = {}
                PRODUCTS[p_name][p_days] = new_val
                if p_name not in fluorite_stock: fluorite_stock[p_name] = {}
                if p_days not in fluorite_stock[p_name]: fluorite_stock[p_name][p_days] = []
                save_system_backup()
                await update.message.reply_text(f"✅ Custom daily plan injected perfectly!", reply_markup=get_admin_keyboard())
            except: await update.message.reply_text("❌ Invalid price digits.", reply_markup=get_admin_keyboard())
            admin_states[user_id] = None; return
        elif state == 'await_coup':
            try:
                val = float(text)
                code = "FL-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                active_coupons[code] = val
                save_system_backup()
                await update.message.reply_text(f"✅ **Coupon created:** `{code}` (`{val}$`)", parse_mode="Markdown", reply_markup=get_admin_keyboard())
            except: await update.message.reply_text("Error, numbers only.", reply_markup=get_admin_keyboard())
            admin_states[user_id] = None; return
        elif state == 'awaiting_raw_keys':
            p_name = context.user_data.get("adm_prod")
            p_days = context.user_data.get("adm_dur")
            input_keys = [line.strip() for line in text.split('\n') if line.strip()]
            if p_name in fluorite_stock:
                if p_days not in fluorite_stock[p_name]: fluorite_stock[p_name][p_days] = []
                fluorite_stock[p_name][p_days].extend(input_keys)
                save_system_backup()
                await update.message.reply_text(f"✅ Loaded {len(input_keys)} keys successfully!", reply_markup=get_admin_keyboard())
            else: await update.message.reply_text("⚠️ Processing error.", reply_markup=get_admin_keyboard())
            admin_states[user_id] = None; return
        elif state == 'await_del':
            f = False
            for pr, dy in fluorite_stock.items():
                for d, k in dy.items():
                    if text in k: k.remove(text); f = True
            save_system_backup()
            await update.message.reply_text("✅ Key removed." if f else "❌ Key not found.", reply_markup=get_admin_keyboard())
            admin_states[user_id] = None; return
        elif state == 'await_adm':
            try: ADMIN_LIST.add(int(text)); save_system_backup(); await update.message.reply_text("👑 Admin added successfully.", reply_markup=get_admin_keyboard())
            except: await update.message.reply_text("Invalid ID.", reply_markup=get_admin_keyboard())
            admin_states[user_id] = None; return

    if user_id in ADMIN_LIST and text == "🔙 Return to Admin":
        admin_view_mode[user_id] = 'admin'
        await update.message.reply_text("👑 Welcome back to the Management Room.", reply_markup=get_admin_keyboard())
        return

    # --- User Frontend Operations ---
    sym, rate = get_user_currency_info(user_id)

    if text == "💱 Switch Currency":
        user_currencies[user_id] = "USD" if user_currencies.get(user_id, "USD") == "LOCAL" else "LOCAL"
        save_system_backup()
        new_sym, _ = get_user_currency_info(user_id)
        await update.message.reply_text(f"🔄 Currency display changed to **{new_sym}**", parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
        return
        
    elif text == "🛒 Wholesale Shop":
        buttons = [[InlineKeyboardButton(f"📦 {prod}", callback_data=f"shop_prod_{prod}")] for prod in PRODUCTS.keys()]
        await update.message.reply_text("🛒 **Welcome to our Shop!**\n\nSelect a product category to view plans:", reply_markup=InlineKeyboardMarkup(buttons))
        return
        
    elif text == "💳 Top-up Balance":
        user_states[user_id] = 'ent_coup'
        await update.message.reply_text("🎫 Please send your coupon code here:", reply_markup=ReplyKeyboardRemove())
        return

    elif text == "💬 Live Support":
        await update.message.reply_text(f"👑 Need help or want a login profile? Text our agent here: {SUPPORT_USER} ✨")
        return
        
    elif text.startswith("💰 My Wallet"):
        bal_str = format_price(user_balances.get(user_id, 0.0), sym, rate)
        await update.message.reply_text(f"👤 **Your Account Status:**\n\n💵 Funds: `{bal_str}`\n🌐 Currency: `{sym}`", parse_mode="Markdown")
        return
        
    # --- Reset Features Handling ---
    elif text == "🔄 Reset Drip Key":
        user_states[user_id] = "awaiting_drip_code"
        await update.message.reply_text("📝 **Please send your 10-digit DRIP code:**", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
        return

    elif text == "📁 Drip File Check":
        user_states[user_id] = "awaiting_drip_file"
        await update.message.reply_text("📁 **Please upload the file you want to check:**", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
        return

    if user_states.get(user_id) == "awaiting_drip_code":
        user_states[user_id] = None
        if not text.isdigit() or len(text) != 10:
            await update.message.reply_text("❌ **Invalid code!** Must be exactly 10 digits.", parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
            return
            
        if not client.is_connected(): await client.connect()
        await client.send_message(DRIP_RESET_BOT, text)
        pending_requests[user_id] = {"type": "drip"}
        await update.message.reply_text("⏳ **DRIP code sent!** Waiting for response...", parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
        return

    if user_states.get(user_id) == 'ent_coup':
        user_states[user_id] = None
        if text in active_coupons:
            amt = active_coupons[text]
            user_balances[user_id] += amt
            del active_coupons[text]
            save_system_backup()
            await update.message.reply_text(f"🎉 Sweet! +`{format_price(amt, sym, rate)}` added to your wallet!", parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
        else: await update.message.reply_text("❌ Code is incorrect.", reply_markup=get_user_keyboard(user_id))
        return

    if user_states.get(user_id) == "awaiting_checkout_confirm":
        user_states[user_id] = None
        if text.lower() == "ok":
            p_name = context.user_data.get("selected_product")
            p_days = context.user_data.get("selected_days")
            price = PRODUCTS.get(p_name, {}).get(p_days, 0.0)
            
            if user_balances.get(user_id, 0.0) >= price:
                if fluorite_stock.get(p_name, {}).get(p_days):
                    raw_key = fluorite_stock[p_name][p_days].pop(0)
                    user_balances[user_id] -= price
                    save_system_backup()
                    masked_output = mask_credential(raw_key)
                    await update.message.reply_text(f"🎉 **Awesome! Purchase successful:**\n\n`{masked_output}`\n\nHave fun using it! ✨", parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
                else: await update.message.reply_text(f"⚠️ Oh no! We are out of stock. Please ask {SUPPORT_USER}", reply_markup=get_user_keyboard(user_id))
            else: await update.message.reply_text(f"❌ Your balance is not enough.", reply_markup=get_user_keyboard(user_id))
        else:
            await update.message.reply_text("❌ **Order cancelled.**", reply_markup=get_user_keyboard(user_id))
        return

    if user_balances.get(user_id, 0.0) == 0 and user_id not in ADMIN_LIST:
        await update.message.reply_text(f"👋 **Shop Locked**\n\nPlease add some funds first to start shopping.\n👑 **Support for top-up / login:** {SUPPORT_USER}", parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
    else: 
        if text and text not in ["🟢 My Currency", "💵 USD ($)"]: 
            await update.message.reply_text("ℹ️ Please use the menu buttons to control.", reply_markup=get_user_keyboard(user_id))

# --- Custom Add Plan Callback Handler ---
async def handling_inject_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    
    if data == "adm_add_custom_day":
        if user_id not in ADMIN_LIST: return
        admin_states[user_id] = "awaiting_custom_day_name"
        await query.edit_message_text("⏱️ Send the number of days for the new custom plan:")
        return
        
    if data.startswith("inject_day_to_"):
        prod_target = data.replace("inject_day_to_", "")
        context.user_data["adm_prod"] = prod_target
        admin_states[user_id] = "awaiting_custom_inject_price"
        await query.edit_message_text(f"💵 Perfect! Now send the **Price in USD ($)**:")
        return

# --- Telethon Post Init & Event Handler ---
@client.on(events.NewMessage())
async def handle_telethon_response(event):
    global application # Accessing the global application object safely
    sender = await event.get_sender()
    if not sender or not getattr(sender, 'username', None): return
    username = sender.username.lower()
    drip_bot = DRIP_RESET_BOT.replace("@", "").lower()
    target_bot = TARGET_BOT.replace("@", "").lower()

    if username not in [drip_bot, target_bot]: return

    to_delete = []
    for uid, data in pending_requests.items():
        if username == drip_bot and data["type"] == "drip":
            if event.message.file:
                path = await event.message.download_media()
                await application.bot.send_document(chat_id=uid, document=open(path, 'rb'), caption="✅ **File Check Complete**", parse_mode="Markdown")
                os.remove(path)
            else:
                await application.bot.send_message(chat_id=uid, text=f"📥 **DRIP Response:**\n`{event.message.message}`", parse_mode="Markdown")
            to_delete.append(uid)

        elif username == target_bot and data["type"] == "fluorite":
            await application.bot.send_message(chat_id=uid, text=f"📥 **Response:**\n`{event.message.message}`", parse_mode="Markdown")
            to_delete.append(uid)
            
    for uid in to_delete:
        del pending_requests[uid]

async def post_init(app: Application):
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("⚠️ Telethon is not authorized! You must login manually via python-telethon first.")
        else:
            print("✅ Telethon Client connected successfully inside the bot!")
    except Exception as e:
        print(f"❌ Telethon Connection Failed: {e}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('reset', reset_cmd))
    application.add_handler(CallbackQueryHandler(handling_inject_callbacks, pattern="^(adm_add_custom_day|inject_day_to_.*)$"))
    application.add_handler(CallbackQueryHandler(shop_menu_callback))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_messages))
    print("🏪 Private Wholesale Store Running Smoothly...")
    application.run_polling()
