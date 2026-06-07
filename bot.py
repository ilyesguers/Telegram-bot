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
CHANNEL_ID = "@TQA_CHANNEL"  
BACKUP_FILE = "fluorite_backup.json"

# --- Database & Variables ---
ADMIN_LIST = {PRIMARY_ADMIN, SECONDARY_ADMIN}

APPROVED_ACCOUNTS = {
    "demo_key": "pass123" 
}

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

# --- Keyboards (Converted to Reply Keyboards) ---
def get_admin_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("➕ Add Product"), KeyboardButton("❌ Delete Product")],
        [KeyboardButton("🎫 Mint Coupon"), KeyboardButton("📦 Add Keys")],
        [KeyboardButton("⚙️ Edit Prices"), KeyboardButton("🗑️ Delete Key")],
        [KeyboardButton("👥 Add Admin"), KeyboardButton("👤 Create Login Pass")],
        [KeyboardButton("📢 Broadcast"), KeyboardButton("🪄 Fake Sale Promo")],
        [KeyboardButton("📊 Statistics"), KeyboardButton("💾 Save Backup")],
        [KeyboardButton("👤 View as User")]
    ], resize_keyboard=True)

def get_user_keyboard():
    # ترتيب الأزرار كما طلبت في الصورة
    return ReplyKeyboardMarkup([
        [KeyboardButton(" Buy Key 🔑")],
        [KeyboardButton(" Support "), KeyboardButton(" Log out 🚪")],
        [KeyboardButton("➡️ Next")]
    ], resize_keyboard=True)

def get_user_keyboard_page2():
    return ReplyKeyboardMarkup([
        [KeyboardButton("👤 My Profile"), KeyboardButton("🎫 Redeem Coupon")],
        [KeyboardButton("🔄 Reset Fluorite")],
        [KeyboardButton("🔙 Back")]
    ], resize_keyboard=True)

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    all_bot_users.add(user_id) 
    admin_states[user_id] = user_states[user_id] = None

    if user_id in ADMIN_LIST and admin_view_mode.get(user_id, 'admin') == 'admin':
        await update.message.reply_text("⚡ **Welcome back, Boss! Control Panel is ready:**", reply_markup=get_admin_keyboard())
        return

    if user_id not in authenticated_users and user_id not in ADMIN_LIST:
        user_states[user_id] = "awaiting_login_credentials"
        welcome_login_msg = (
            "Please send your credentials in the following format:\n\n"
            "`LOGIN`\n"
            "`PASSWORD`"
        )
        await update.message.reply_text(welcome_login_msg, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
        return

    if user_id not in user_countries: user_countries[user_id] = random.choice(["SA", "EG", "AE", "DZ", "IQ"])
    await show_user_welcome(update, user_id)

async def show_user_welcome(update: Update, user_id: int):
    msg = "✅ **Access Granted! Logged in successfully.**\nWelcome to your User Dashboard."
    if update.message:
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_user_keyboard())
    elif update.callback_query:
        await update.callback_query.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_user_keyboard())

# --- Inline Callback Hub (For Shop only) ---
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
        await query.edit_message_text(f"🛍️ **Product Plans for {prod}:**\n\nChoose your preferred duration package below:", reply_markup=InlineKeyboardMarkup(buttons))
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
            f"🌸 To confirm purchase, send the word: **`ok`**"
        )
        await query.edit_message_text(checkout_msg, parse_mode="Markdown")
        return

    # Admin Inline Options
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

    # Login Check
    if user_id not in authenticated_users and user_id not in ADMIN_LIST:
        if user_states.get(user_id) == "awaiting_login_credentials":
            credentials = text.split()
            if len(credentials) == 2:
                input_key = credentials[0].strip()
                input_pass = credentials[1].strip()
                
                if APPROVED_ACCOUNTS.get(input_key) == input_pass:
                    authenticated_users.add(user_id)
                    user_states[user_id] = None
                    await show_user_welcome(update, user_id)
                    return
                else:
                    await update.message.reply_text("❌ **Invalid Credentials!** Please try again.")
                    return
            else:
                await update.message.reply_text("⚠️ Please send LOGIN and PASSWORD on the same line, separated by a space.")
                return
        else:
            await update.message.reply_text("🔒 Please send `/start` to log in first.")
            return

    # --- Admin Backend Workspace ---
    if user_id in ADMIN_LIST and admin_view_mode.get(user_id, 'admin') == 'admin':
        if text == "➕ Add Product":
            admin_states[user_id] = 'await_new_prod_name'
            await update.message.reply_text("📝 Enter the name of the new product/cheat to add:", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "❌ Delete Product":
            buttons = [[InlineKeyboardButton(f"🗑️ Delete {prod}", callback_data=f"adm_del_p_{prod}")] for prod in PRODUCTS.keys()]
            await update.message.reply_text("⚠️ **Select product to delete permanently:**", reply_markup=InlineKeyboardMarkup(buttons))
            return
        elif text == "🎫 Mint Coupon":
            admin_states[user_id] = 'await_coup'
            await update.message.reply_text("💵 Enter coupon value in USD (numbers only):", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "📦 Add Keys":
            buttons = [[InlineKeyboardButton(prod, callback_data=f"adm_add_{prod}")] for prod in PRODUCTS.keys()]
            await update.message.reply_text("📦 **Select target product to load stock:**", reply_markup=InlineKeyboardMarkup(buttons))
            return
        elif text == "⚙️ Edit Prices":
            buttons = [[InlineKeyboardButton(prod, callback_data=f"adm_prc_{prod}")] for prod in PRODUCTS.keys()]
            admin_markup = InlineKeyboardMarkup(buttons)
            await update.message.reply_text("⚙️ **Select a product to edit its current plan prices:**", reply_markup=admin_markup)
            custom_plan_btn = [[InlineKeyboardButton("➕ Add New Custom Daily Plan", callback_data="adm_add_custom_day")]]
            await update.message.reply_text("✨ **Or add a completely new standalone plan to any product:**", reply_markup=InlineKeyboardMarkup(custom_plan_btn))
            return
        elif text == "🗑️ Delete Key":
            admin_states[user_id] = 'await_del'
            await update.message.reply_text("Paste the code you want to remove from stock:", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "👥 Add Admin":
            admin_states[user_id] = 'await_adm'
            await update.message.reply_text("Send the Telegram ID of the new admin:", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "👤 Create Login Pass":
            admin_states[user_id] = 'await_create_user_account'
            await update.message.reply_text("📝 Send the new client account in this format:\n`loginkey:password`", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "📢 Broadcast":
            admin_states[user_id] = 'await_broadcast_message'
            await update.message.reply_text("📝 **Send the message you want to broadcast to the channel and all bot users now:**", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "🪄 Fake Sale Promo":
            admin_states[user_id] = 'await_fake_sale_confirmation'
            await update.message.reply_text("⚠️ **Action Confirmation:**\nPlease type `Confirm` to generate and post a fake purchase notification in the channel immediately:", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "📊 Statistics":
            msg = f"🎫 **Active Coupons:** {', '.join([f'`{k}: {v}$`' for k,v in active_coupons.items()])}\n👥 **Total Authorized Accounts:** `{len(APPROVED_ACCOUNTS)}` accounts\n📢 **Total Bot Observers:** `{len(all_bot_users)}` users\n\n📦 **Current Stock:**\n"
            for p, d in fluorite_stock.items():
                msg += f"🔹 `{p}` -> " + " | ".join([f"Day {k}: ({len(v)})" for k,v in d.items()]) + "\n"
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_admin_keyboard())
            return
        elif text == "💾 Save Backup":
            save_system_backup()
            await update.message.reply_document(document=open(BACKUP_FILE, 'rb'), filename=BACKUP_FILE, caption="📥 **Database backup file successfully created!**", reply_markup=get_admin_keyboard())
            return
        elif text == "👤 View as User":
            admin_view_mode[user_id] = 'user'
            authenticated_users.add(user_id)
            if user_id not in user_currencies: user_currencies[user_id] = "USD"
            await update.message.reply_text("🔄 Switched to User View simulation.")
            await show_user_welcome(update, user_id)
            return

        # Processing Admin Input States
        state = admin_states.get(user_id)
        if state == 'await_fake_sale_confirmation':
            admin_states[user_id] = None
            if text.lower() == "confirm":
                raw_fake_16_code = generate_random_16_code()
                masked_fake_code = mask_credential(raw_fake_16_code)
                attractive_fake_msg = (
                    f"🔥 **NEW SUCCESSFUL PURCHASE!** 🔥\n\n"
                    f"⚡ **SOMEONE JUST BOUGHT A FLUORITE CODE NOW!** ⚡\n"
                    f"📈 **STORE IS ON FIRE!** 📈\n\n"
                    f"🤝 *Thank you for your endless trust in us! We promise to always deliver the latest updates and the absolute best tools for you!* ✨💎\n\n"
                    f"📥 **The code obtained by the user:**\n"
                    f"👉 `{masked_fake_code}` 🚀"
                )
                try:
                    await context.bot.send_message(chat_id=CHANNEL_ID, text=attractive_fake_msg, parse_mode="Markdown")
                    await update.message.reply_text("✅ **[Success]** Notification posted in the channel successfully!", reply_markup=get_admin_keyboard())
                except Exception as e:
                    await update.message.reply_text(f"❌ Confirmed but failed to send to channel. Error: {e}", reply_markup=get_admin_keyboard())
            else:
                await update.message.reply_text("❌ Action cancelled, the word you entered is not `Confirm`.", reply_markup=get_admin_keyboard())
            return

        elif state == 'await_broadcast_message':
            admin_states[user_id] = None
            success_count = fail_count = 0
            await update.message.reply_text(f"⏳ Broadcasting to channel and {len(all_bot_users)} users...")
            try:
                await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
                channel_status = "✅ Successfully posted to the channel!"
            except Exception as e: channel_status = f"❌ Failed to post to channel. Error: {e}"
                
            for u_id in list(all_bot_users):
                try:
                    await context.bot.send_message(chat_id=u_id, text=text)
                    success_count += 1
                except: fail_count += 1
            
            report_msg = f"📢 **Broadcast Completed!**\n\n📺 **Channel Status:**\n{channel_status}\n\n👥 **Direct Messages Status:**\n✅ Delivered to: `{success_count}` users.\n❌ Failed to send to: `{fail_count}` users."
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
                await update.message.reply_text(f"✅ **Client Pass created successfully!**\n👤 Login Key: `{u.strip()}`\n🔑 Password: `{p.strip()}`", parse_mode="Markdown", reply_markup=get_admin_keyboard())
            else:
                await update.message.reply_text("❌ Wrong format, not created. You must use `loginkey:password`", reply_markup=get_admin_keyboard())
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

    if user_id in ADMIN_LIST and text == "🔙 Admin Panel":
        admin_view_mode[user_id] = 'admin'
        await update.message.reply_text("👑 Welcome back to the Management Room.", reply_markup=get_admin_keyboard())
        return

    # --- User Frontend Text Inputs (Reply Keyboards Logic) ---
    sym, rate = get_user_currency_info(user_id)

    # User Button Clicks
    if text == "🩷 Buy Key 🩷":
        buttons = [[InlineKeyboardButton(f"📦 {prod}", callback_data=f"shop_prod_{prod}")] for prod in PRODUCTS.keys()]
        await update.message.reply_text("🛒 **Welcome to our Shop!**\n\nChoose the product you want to buy:", reply_markup=InlineKeyboardMarkup(buttons))
        return

    elif text == "💙 Support 💙":
        support_msg = f"👑 **For any help or inquiries, contact our support:**\n➡️ **Admin Support:** {SUPPORT_USER} ✨"
        await update.message.reply_text(support_msg, parse_mode="Markdown")
        return

    elif text == "🚪 Log out 🚪":
        if user_id in authenticated_users:
            authenticated_users.remove(user_id)
        user_states[user_id] = "awaiting_login_credentials"
        welcome_login_msg = "You have been logged out.\nPlease send your credentials in the following format:\n\n`LOGIN`\n`PASSWORD`"
        await update.message.reply_text(welcome_login_msg, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
        return

    elif text == "➡️ Next":
        await update.message.reply_text("⚙️ **More Options:**", reply_markup=get_user_keyboard_page2())
        return

    elif text == "🔙 Back":
        await show_user_welcome(update, user_id)
        return

    elif text == "👤 My Profile":
        bal_str = format_price(user_balances.get(user_id, 0.0), sym, rate)
        msg = f"👤 **My Profile**\n\n🆔 **Your ID:** `{user_id}`\n💵 **Balance:** `{bal_str}`"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    elif text == "🎫 Redeem Coupon":
        user_states[user_id] = 'ent_coup'
        await update.message.reply_text("🎫 **Please send your coupon code now:**\n\n(Send any other text to cancel)", parse_mode="Markdown")
        return

    elif text == "🔄 Reset Fluorite":
        await update.message.reply_text("🔄 **Reset Fluorite feature is currently empty (Under Development).**")
        return

    # Processing Coupon Input
    if user_states.get(user_id) == 'ent_coup':
        user_states[user_id] = None
        if text in active_coupons:
            amt = active_coupons[text]
            if user_id not in user_balances: user_balances[user_id] = 0.0
            user_balances[user_id] += amt
            del active_coupons[text]
            save_system_backup()
            sym, rate = get_user_currency_info(user_id)
            await update.message.reply_text(f"🎉 **Success!**\nAdded +`{format_price(amt, sym, rate)}` to your balance!", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ **Invalid or already used coupon code.**")
        return

    # Processing Checkout Confirmation
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
                    await update.message.reply_text(f"🎉 **Awesome! Purchase successful:**\n\n`{masked_output}`\n\nHave fun using it! ✨", parse_mode="Markdown")
                else: 
                    await update.message.reply_text(f"⚠️ Oh no! We are out of stock. Please ask {SUPPORT_USER}")
            else: 
                await update.message.reply_text(f"❌ Your balance is not enough.")
        else:
            await update.message.reply_text("❌ **Order cancelled.**")
        return

    if update.message.document and user_id in ADMIN_LIST and admin_view_mode.get(user_id, 'admin') == 'admin':
        if update.message.document.file_name == BACKUP_FILE:
            file_obj = await context.bot.get_file(update.message.document.file_id)
            await file_obj.download_to_drive(custom_path=BACKUP_FILE)
            load_system_backup()
            await update.message.reply_text("⚡ **Database file recovered!**", reply_markup=get_admin_keyboard())
            return

    if text and user_id not in ADMIN_LIST: 
        await update.message.reply_text("ℹ️ Please use the menu buttons below to navigate.")

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

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(handling_inject_callbacks, pattern="^(adm_add_custom_day|inject_day_to_.*)$"))
    application.add_handler(CallbackQueryHandler(shop_menu_callback))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_messages))
    print("🏪 Private Wholesale Store Running Smoothly...")
    application.run_polling()
