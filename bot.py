from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import random
import string
import json
import os

# --- Configurations ---
TOKEN = '8765508457:AAHLzXj9JEMCbnIWfeov39bN75JrRZ9JcfQ'
PRIMARY_ADMIN = 5145154527
SUPPORT_USER = "@i6issiiiii"
BACKUP_FILE = "fluorite_backup.json"

# --- Database ---
ADMIN_LIST = {PRIMARY_ADMIN}
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

# --- Auto/Manual Backup System ---
def save_system_backup():
    backup_data = {
        "admins": list(ADMIN_LIST), "balances": user_balances, "currencies": user_currencies,
        "countries": user_countries, "coupons": active_coupons, "stock": fluorite_stock, "products": PRODUCTS
    }
    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=4)

def load_system_backup():
    global ADMIN_LIST, user_balances, user_currencies, user_countries, active_coupons, fluorite_stock, PRODUCTS
    if os.path.exists(BACKUP_FILE):
        try:
            with open(BACKUP_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                ADMIN_LIST = set(data.get("admins", [PRIMARY_ADMIN]))
                user_balances = {int(k): v for k, v in data.get("balances", {}).items()}
                user_currencies = {int(k): v for k, v in data.get("currencies", {}).items()}
                user_countries = {int(k): v for k, v in data.get("countries", {}).items()}
                active_coupons = data.get("coupons", {})
                fluorite_stock = data.get("stock", {})
                PRODUCTS = data.get("products", PRODUCTS)
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
    return ReplyKeyboardMarkup([
        [KeyboardButton("🎫 Mint Coupon"), KeyboardButton("📦 Add Keys")],
        [KeyboardButton("⚙️ Edit Prices"), KeyboardButton("🗑️ Delete Key")],
        [KeyboardButton("👥 Add Admin"), KeyboardButton("📊 Statistics")],
        [KeyboardButton("💾 Save Backup"), KeyboardButton("👤 View as User")]
    ], resize_keyboard=True)

def get_user_keyboard(user_id):
    bal_str = format_price(user_balances.get(user_id, 0.0), *get_user_currency_info(user_id))
    keyboard = [
        [KeyboardButton("🛒 Shop"), KeyboardButton("💳 Add Funds")],
        [KeyboardButton(f"💰 Wallet [{bal_str}]"), KeyboardButton("💱 Currency")],
        [KeyboardButton("💬 Support")]
    ]
    if user_id in ADMIN_LIST:
        keyboard.insert(0, [KeyboardButton("🔙 Admin Panel")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- Start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin_states[user_id] = user_states[user_id] = None
    if user_id not in user_balances: user_balances[user_id] = 0.0
    if user_id not in user_countries: user_countries[user_id] = random.choice(["SA", "EG", "AE", "DZ", "IQ"])

    if user_id in ADMIN_LIST and admin_view_mode.get(user_id, 'admin') == 'admin':
        await update.message.reply_text("⚡ **Welcome back, Boss! Control Panel is ready:**", reply_markup=get_admin_keyboard())
        return

    if user_id not in user_currencies:
        sym = EXCHANGE_RATES.get(user_countries[user_id], EXCHANGE_RATES["DEFAULT"])["symbol"]
        await update.message.reply_text(f"🌍 **Currency Choice**\n\nDo you want to see prices in your **Local Currency ({sym})** or **USD ($)**?", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🟢 My Currency"), KeyboardButton("💵 USD ($)")]], resize_keyboard=True))
        return

    await show_user_welcome(update, user_id)

async def show_user_welcome(update: Update, user_id: int):
    bal_str = format_price(user_balances.get(user_id, 0.0), *get_user_currency_info(user_id))
    msg = (
        f"👋 **Hello friend! Welcome to our store!** ✨\n\n"
        f"💳 **Your Balance:** `{bal_str}`\n\n"
        f"Feel free to check our products below. If you want to add funds or get login keys, click support:\n"
        f"👑 **Support Desk:** {SUPPORT_USER} ✨"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))

# --- Simple Inline Clicks Hub ---
async def shop_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    # User Store Buying
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

    # Super Simple Step-by-Step Keys Adding (Admin)
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

    # Super Simple Step-by-Step Price Customization (Admin)
    if data.startswith("adm_prc_"):
        prod = data.replace("adm_prc_", "")
        context.user_data["adm_prod"] = prod
        buttons = [[InlineKeyboardButton(f"⚙️ Edit {d} Day Price", callback_data=f"adm_p_dur_{d}")] for d in PRODUCTS[prod].keys()]
        await query.edit_message_text(f"⚙️ Modifying rates for **{prod}**\nSelect plan duration:", reply_markup=InlineKeyboardMarkup(buttons))
        return

    if data.startswith("adm_p_dur_"):
        dur = data.replace("adm_p_dur_", "")
        context.user_data["adm_dur"] = dur
        admin_states[user_id] = "awaiting_raw_price"
        await query.edit_message_text(f"💵 Please send the **New Price in USD ($)** for this plan (numbers only):")
        return

# --- Text Messaging Systems ---
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if text in ["🟢 My Currency", "💵 USD ($)"]:
        user_currencies[user_id] = "LOCAL" if "My" in text else "USD"
        save_system_backup()
        await show_user_welcome(update, user_id)
        return

    # --- Admin Interactive Panel ---
    if user_id in ADMIN_LIST and admin_view_mode.get(user_id, 'admin') == 'admin':
        if text == "🎫 Mint Coupon":
            admin_states[user_id] = 'await_coup'
            await update.message.reply_text("💵 Enter coupon value in USD (numbers only):", reply_markup=ReplyKeyboardRemove())
            return

        elif text == "📦 Add Keys":
            buttons = [[InlineKeyboardButton(prod, callback_data=f"adm_add_{prod}")] for prod in PRODUCTS.keys()]
            await update.message.reply_text("📦 **Select target product to load stock:**", reply_markup=InlineKeyboardMarkup(buttons))
            return

        elif text == "⚙️ Edit Prices":
            buttons = [[InlineKeyboardButton(prod, callback_data=f"adm_prc_{prod}")] for prod in PRODUCTS.keys()]
            await update.message.reply_text("⚙️ **Select product to adjust price:**", reply_markup=InlineKeyboardMarkup(buttons))
            return

        elif text == "🗑️ Delete Key":
            admin_states[user_id] = 'await_del'
            await update.message.reply_text("Paste the code you want to remove from stock:", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "👥 Add Admin":
            admin_states[user_id] = 'await_adm'
            await update.message.reply_text("Send the Telegram ID of the new admin:", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "📊 Statistics":
            msg = "🎫 **Active Coupons:** " + ", ".join([f"`{k}: {v}$`" for k,v in active_coupons.items()]) + "\n\n📦 **Current Stock:**\n"
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
            if user_id not in user_currencies: user_currencies[user_id] = "USD"
            await update.message.reply_text("🔄 Switched to User View simulation.", reply_markup=get_user_keyboard(user_id))
            return

        # Simple Processing States
        state = admin_states.get(user_id)
        if state == 'await_coup':
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
            
            if p_name in fluorite_stock and p_days in fluorite_stock[p_name]:
                fluorite_stock[p_name][p_days].extend(input_keys)
                save_system_backup()
                await update.message.reply_text(f"✅ Loaded {len(input_keys)} keys to **{p_name} ({p_days} Days)** successfully!", reply_markup=get_admin_keyboard())
            else: await update.message.reply_text("⚠️ Processing error, please try again.", reply_markup=get_admin_keyboard())
            admin_states[user_id] = None; return

        elif state == 'awaiting_raw_price':
            p_name = context.user_data.get("adm_prod")
            p_days = context.user_data.get("adm_dur")
            try:
                new_val = float(text)
                PRODUCTS[p_name][p_days] = new_val
                save_system_backup()
                await update.message.reply_text(f"✅ Price updated! **{p_name} ({p_days}D)** is now `{new_val}$`", reply_markup=get_admin_keyboard())
            except: await update.message.reply_text("❌ Numerical digits only. Update failed.", reply_markup=get_admin_keyboard())
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

    # --- User Frontend Operations ---
    sym, rate = get_user_currency_info(user_id)

    if text == "💱 Currency":
        user_currencies[user_id] = "USD" if user_currencies.get(user_id, "USD") == "LOCAL" else "LOCAL"
        save_system_backup()
        new_sym, _ = get_user_currency_info(user_id)
        await update.message.reply_text(f"🔄 Currency display changed to **{new_sym}**", parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
        return
        
    elif text == "🛒 Shop":
        # All products listed cleanly on one page
        shop_msg = "🛒 **CHEATS CATALOGUE** 🛒\n\n"
        inline_buttons = []
        
        for prod_name, durations in PRODUCTS.items():
            shop_msg += f"🔹 **{prod_name}**\n"
            row_buttons = []
            for days, price in durations.items():
                price_str = format_price(price, sym, rate)
                shop_msg += f" ▫️ {days} Day(s) → `{price_str}`\n"
                btn_label = f"{prod_name.split()[0]} [{days}D]"
                row_buttons.append(InlineKeyboardButton(btn_label, callback_data=f"buy_{prod_name}_{days}"))
            shop_msg += "\n"
            inline_buttons.append(row_buttons)
            
        await update.message.reply_text(shop_msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_buttons))
        return
        
    elif text == "💳 Add Funds":
        user_states[user_id] = 'ent_coup'
        await update.message.reply_text("🎫 Please send your coupon code here:", reply_markup=ReplyKeyboardRemove())
        return

    elif text == "💬 Support":
        await update.message.reply_text(f"👑 Need help or want a login profile? Text our agent here: {SUPPORT_USER} ✨")
        return
        
    elif text.startswith("💰 Wallet"):
        bal_str = format_price(user_balances.get(user_id, 0.0), sym, rate)
        await update.message.reply_text(f"👤 **Your Account Status:**\n\n💵 Funds: `{bal_str}`\n🌐 Currency: `{sym}`\n👑 Support desk: {SUPPORT_USER}", parse_mode="Markdown")
        return

    # Coupon shifting
    if user_states.get(user_id) == 'ent_coup':
        user_states[user_id] = None
        if text in active_coupons:
            amt = active_coupons[text]
            user_balances[user_id] += amt
            del active_coupons[text]
            save_system_backup()
            await update.message.reply_text(f"🎉 Sweet! +`{format_price(amt, sym, rate)}` added to your wallet!", parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
        else: await update.message.reply_text("❌ Code is incorrect or already used.", reply_markup=get_user_keyboard(user_id))
        return

    # User Checkout Confirmation
    if user_states.get(user_id) == "awaiting_checkout_confirm":
        user_states[user_id] = None
        if text.lower() == "ok":
            p_name = context.user_data.get("selected_product")
            p_days = context.user_data.get("selected_days")
            price = PRODUCTS[p_name][p_days]
            
            if user_balances.get(user_id, 0.0) >= price:
                if fluorite_stock[p_name][p_days]:
                    key = fluorite_stock[p_name][p_days].pop(0)
                    user_balances[user_id] -= price
                    save_system_backup()
                    await update.message.reply_text(f"🎉 **Awesome! Purchase successful:**\n\n`{key}`\n\nHave fun using it! ✨", parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
                else: await update.message.reply_text(f"⚠️ Oh no! We are out of stock. Please ask {SUPPORT_USER}", reply_markup=get_user_keyboard(user_id))
            else: await update.message.reply_text(f"❌ Your balance is not enough. You need {format_price(price, sym, rate)} to buy this item.", reply_markup=get_user_keyboard(user_id))
        else:
            await update.message.reply_text("❌ **Order cancelled.** Feel free to explore again whenever you like!", reply_markup=get_user_keyboard(user_id))
        return

    # Admin DB restoration file catcher
    if update.message.document and user_id in ADMIN_LIST and admin_view_mode.get(user_id, 'admin') == 'admin':
        if update.message.document.file_name == BACKUP_FILE:
            file_obj = await context.bot.get_file(update.message.document.file_id)
            await file_obj.download_to_drive(custom_path=BACKUP_FILE)
            load_system_backup()
            await update.message.reply_text("⚡ **Database file recovered and synced perfectly!**", reply_markup=get_admin_keyboard())
            return

    if user_balances.get(user_id, 0.0) == 0 and user_id not in ADMIN_LIST:
        await update.message.reply_text(f"👋 **Shop Locked**\n\nPlease add some funds first to start shopping.\n👑 **Support for top-up / login:** {SUPPORT_USER}", parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
    else: await update.message.reply_text("ℹ️ Please use the menu buttons to control.", reply_markup=get_user_keyboard(user_id))

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(shop_menu_callback))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_messages))
    print("🏪 Super Simple One-Page Store running successfully...")
    application.run_polling()
