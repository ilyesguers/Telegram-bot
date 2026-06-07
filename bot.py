from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import random
import string
import json
import os

# --- Configuration ---
TOKEN = '8765508457:AAHLzXj9JEMCbnIWfeov39bN75JrRZ9JcfQ'
PRIMARY_ADMIN = 5145154527
SUPPORT_USER = "@i6issiiiii"
BACKUP_FILE = "fluorite_backup.json"

# --- Database Structures ---
ADMIN_LIST = {PRIMARY_ADMIN}
PRODUCTS = {
    "Fluorite Hack 💎": {"1": 5.0, "7": 15.0, "30": 40.0},
    "Free Fire VIP 🔥": {"1": 3.0, "7": 10.0, "30": 25.0}
}
user_balances = {}    # {user_id: float}
user_currencies = {}  # {user_id: 'USD'/'LOCAL'}
user_countries = {}   # {user_id: 'SA'/'EG' etc}
active_coupons = {"CHARGE-10USD": 10.0, "CHARGE-50USD": 50.0}
fluorite_stock = {
    "Fluorite Hack 💎": {"1": ["FLUORITE-1DAY-XXXX"], "7": ["FLUORITE-7DAY-ZZZZ"], "30": ["FLUORITE-30DAY-AAAA"]},
    "Free Fire VIP 🔥": {"1": ["FF-1DAY-1111"], "7": ["FF-7DAY-2222"], "30": ["FF-30DAY-3333"]}
}

# --- Backup System Core Engine ---
def save_system_backup():
    """Compiles database variables into a secure local JSON file"""
    backup_data = {
        "admins": list(ADMIN_LIST),
        "balances": user_balances,
        "currencies": user_currencies,
        "countries": user_countries,
        "coupons": active_coupons,
        "stock": fluorite_stock,
        "products": PRODUCTS
    }
    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=4)

def load_system_backup():
    """Restores database states from local JSON backup file if exists"""
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
        except Exception as e:
            print(f"Backup load failed: {e}")

# Load active memory state on boot up
load_system_backup()

EXCHANGE_RATES = {
    "SA": {"symbol": "SAR", "rate": 3.75},
    "EG": {"symbol": "EGP", "rate": 47.0},
    "AE": {"symbol": "AED", "rate": 3.67},
    "DZ": {"symbol": "DZD", "rate": 134.0},
    "IQ": {"symbol": "IQD", "rate": 1310.0},
    "DEFAULT": {"symbol": "EUR", "rate": 0.92}
}

admin_states, user_states, admin_view_mode = {}, {}, {}

def get_user_currency_info(user_id):
    country = user_countries.get(user_id, "DEFAULT")
    return ("$", 1.0) if user_currencies.get(user_id, "USD") == "USD" else (EXCHANGE_RATES.get(country, EXCHANGE_RATES["DEFAULT"])["symbol"], EXCHANGE_RATES.get(country, EXCHANGE_RATES["DEFAULT"])["rate"])

def format_price(usd_amount, symbol, rate):
    return f"{usd_amount * rate:.2f}$" if symbol == "$" else f"{usd_amount * rate:.2f} {symbol}"

# --- Ultra-Sleek Dynamic Keyboards ---
def get_admin_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🎫 Mint Coupon"), KeyboardButton("📦 Add Keys")],
        [KeyboardButton("⚙️ Edit Prices"), KeyboardButton("🗑️ Erase Key")],
        [KeyboardButton("👥 Add Admin"), KeyboardButton("📊 System Stats")],
        [KeyboardButton("💾 Backup Database"), KeyboardButton("👤 User View")]
    ], resize_keyboard=True)

def get_user_keyboard(user_id):
    bal_str = format_price(user_balances.get(user_id, 0.0), *get_user_currency_info(user_id))
    keyboard = [
        [KeyboardButton("🛒 STOREFRONT"), KeyboardButton("💳 REDEEM")],
        [KeyboardButton(f"💰 WALLET [{bal_str}]"), KeyboardButton("💱 CURRENCY")]
    ]
    if user_id in ADMIN_LIST:
        keyboard.append([KeyboardButton("🔙 ADMIN HQ")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin_states[user_id] = user_states[user_id] = None
    if user_id not in user_balances: user_balances[user_id] = 0.0
    if user_id not in user_countries: user_countries[user_id] = random.choice(["SA", "EG", "AE", "DZ", "IQ"])

    if user_id in ADMIN_LIST and admin_view_mode.get(user_id, 'admin') == 'admin':
        await update.message.reply_text("⚡ **Fluorite Central HQ Active.**\nDeploy management arrays below:", parse_mode="Markdown", reply_markup=get_admin_keyboard())
        return

    if user_id not in user_currencies:
        sym = EXCHANGE_RATES.get(user_countries[user_id], EXCHANGE_RATES["DEFAULT"])["symbol"]
        await update.message.reply_text(f"🌍 **Currency Setup**\n\nDisplay prices in your local **{sym}** currency or standard **USD ($)**?", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🟢 Local Currency"), KeyboardButton("💵 Standard USD")]], resize_keyboard=True))
        return

    await show_user_welcome(update, user_id)

async def show_user_welcome(update: Update, user_id: int):
    bal_str = format_price(user_balances.get(user_id, 0.0), *get_user_currency_info(user_id))
    msg = (
        f"🔥 **WELCOME TO FLUORITE ELITE** 🔥\n\n"
        f"🔒 **Status:** `Restricted / Unverified`\n"
        f"💳 **Balance:** `{bal_str}`\n\n"
        f"Unlock lethal premium cheats instantly. Buy a voucher from our official desk to fund your wallet.\n\n"
        f"👑 **Live Desk:** {SUPPORT_USER} 📲"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if text in ["🟢 Local Currency", "💵 Standard USD"]:
        user_currencies[user_id] = "LOCAL" if "Local" in text else "USD"
        save_system_backup()
        await show_user_welcome(update, user_id)
        return

    # --- Admin Master Execution Protocols ---
    if user_id in ADMIN_LIST and admin_view_mode.get(user_id, 'admin') == 'admin':
        if text == "🎫 Mint Coupon":
            admin_states[user_id] = 'await_coup'
            await update.message.reply_text("💵 Enter cash value in USD (Numbers only):", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "📦 Add Keys":
            admin_states[user_id] = 'await_key'
            await update.message.reply_text("Format: `Product Name | Days | License Key`", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "⚙️ Edit Prices":
            admin_states[user_id] = 'await_price'
            await update.message.reply_text("Format: `Product Name | Days | New USD Price`", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "🗑️ Erase Key":
            admin_states[user_id] = 'await_del'
            await update.message.reply_text("Paste the exact key to wipe out from stock:", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "👥 Add Admin":
            admin_states[user_id] = 'await_adm'
            await update.message.reply_text("Send Telegram User ID to promote:", reply_markup=ReplyKeyboardRemove())
            return
        elif text == "📊 System Stats":
            msg = "🎫 **Coupons:** " + ", ".join([f"`{k}: {v}$`" for k,v in active_coupons.items()]) + "\n\n📦 **Live Stock:**\n"
            for p, d in fluorite_stock.items():
                msg += f"🔹 `{p}` -> " + " | ".join([f"{k}D: ({len(v)})" for k,v in d.items()]) + "\n"
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_admin_keyboard())
            return
        elif text == "💾 Backup Database":
            save_system_backup()
            await update.message.reply_document(document=open(BACKUP_FILE, 'rb'), filename=BACKUP_FILE, caption="📥 **Fluorite Core Database Backup Secured Successfully!**", parse_mode="Markdown")
            return
        elif text == "👤 User View":
            admin_view_mode[user_id] = 'user'
            if user_id not in user_currencies: user_currencies[user_id] = "USD"
            await update.message.reply_text("🔄 Simulation Mode Online.", reply_markup=get_user_keyboard(user_id))
            return

        state = admin_states.get(user_id)
        if state == 'await_coup':
            try:
                val = float(text)
                code = "FL-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                active_coupons[code] = val
                save_system_backup()
                await update.message.reply_text(f"✅ **Minted:** `{code}` (`{val}$`)", parse_mode="Markdown", reply_markup=get_admin_keyboard())
            except: await update.message.reply_text("Error. Send number only:", reply_markup=get_admin_keyboard())
            admin_states[user_id] = None
            return
        elif state == 'await_key':
            p = text.split('|')
            if len(p) == 3 and p[0].strip() in fluorite_stock and p[1].strip() in ["1", "7", "30"]:
                fluorite_stock[p[0].strip()][p[1].strip()].append(p[2].strip())
                save_system_backup()
                await update.message.reply_text("✅ Loaded.", reply_markup=get_admin_keyboard())
            else: await update.message.reply_text("Format error or mismatch.", reply_markup=get_admin_keyboard())
            admin_states[user_id] = None
            return
        elif state == 'await_price':
            p = text.split('|')
            if len(p) == 3 and p[0].strip() in PRODUCTS and p[1].strip() in ["1", "7", "30"]:
                try: 
                    PRODUCTS[p[0].strip()][p[1].strip()] = float(p[2].strip())
                    save_system_backup()
                    await update.message.reply_text("✅ Price Updated.", reply_markup=get_admin_keyboard())
                except: await update.message.reply_text("Invalid price.")
            else: await update.message.reply_text("Error.")
            admin_states[user_id] = None
            return
        elif state == 'await_del':
            f = False
            for pr, dy in fluorite_stock.items():
                for d, k in dy.items():
                    if text in k: k.remove(text); f = True
            save_system_backup()
            await update.message.reply_text("✅ Wiped out." if f else "❌ Not found.", reply_markup=get_admin_keyboard())
            admin_states[user_id] = None
            return
        elif state == 'await_adm':
            try: ADMIN_LIST.add(int(text)); save_system_backup(); await update.message.reply_text("👑 Added.", reply_markup=get_admin_keyboard())
            except: await update.message.reply_text("Invalid ID.", reply_markup=get_admin_keyboard())
            admin_states[user_id] = None
            return

    if user_id in ADMIN_LIST and text == "🔙 ADMIN HQ":
        admin_view_mode[user_id] = 'admin'
        await update.message.reply_text("👑 Restored HQ Operations.", reply_markup=get_admin_keyboard())
        return

    # --- User Frontend Operations ---
    sym, rate = get_user_currency_info(user_id)

    if text == "💱 CURRENCY":
        user_currencies[user_id] = "USD" if user_currencies.get(user_id, "USD") == "LOCAL" else "LOCAL"
        save_system_backup()
        new_sym, _ = get_user_currency_info(user_id)
        await update.message.reply_text(f"🔄 Switched view to **{new_sym}**", parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
        return
    elif text == "🛒 STOREFRONT":
        msg = "🔥 **PREMIUM CHEAT PORTFOLIO** 🔥\n\n"
        for p, pr in PRODUCTS.items():
            msg += f"💎 `{p}`\n ▫️ 1D: `{format_price(pr['1'], sym, rate)}` | 7D: `{format_price(pr['7'], sym, rate)}` | 30D: `{format_price(pr['30'], sym, rate)}`\n"
        msg += "\n🎯 **Instant Checkout Command:**\n`Buy | Product Name | Days`"
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
        return
    elif text == "💳 REDEEM":
        user_states[user_id] = 'ent_coup'
        await update.message.reply_text("🎫 Paste your balance voucher code:", reply_markup=ReplyKeyboardRemove())
        return
    elif text.startswith("💰 WALLET"):
        bal_str = format_price(user_balances.get(user_id, 0.0), sym, rate)
        await update.message.reply_text(f"👤 **PROFILE METRICS**\n\n💵 Funds: `{bal_str}`\n🌐 Rate Profile: `{sym}`\n👑 Desk: {SUPPORT_USER}", parse_mode="Markdown")
        return

    if user_states.get(user_id) == 'ent_coup':
        user_states[user_id] = None
        if text in active_coupons:
            amt = active_coupons[text]
            user_balances[user_id] += amt
            del active_coupons[text]
            save_system_backup()
            await update.message.reply_text(f"🎉 Loaded +`{format_price(amt, sym, rate)}`!", parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
        else: await update.message.reply_text("❌ Invalid code.", reply_markup=get_user_keyboard(user_id))
        return

    if text.lower().startswith("buy"):
        p = text.split('|')
        if len(p) == 3 and p[1].strip() in PRODUCTS and p[2].strip() in ["1", "7", "30"]:
            p_name, p_days = p[1].strip(), p[2].strip()
            price = PRODUCTS[p_name][p_days]
            if user_balances.get(user_id, 0.0) >= price:
                if fluorite_stock[p_name][p_days]:
                    key = fluorite_stock[p_name][p_days].pop(0)
                    user_balances[user_id] -= price
                    save_system_backup()
                    await update.message.reply_text(f"🎉 **Success! License Generated:**\n`{key}`\n\nInject & Dominate!", parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
                else: await update.message.reply_text(f"⚠️ Out of stock! Ping {SUPPORT_USER}", reply_markup=get_user_keyboard(user_id))
            else: await update.message.reply_text(f"❌ Insufficient funds. Needs {format_price(price, sym, rate)}", reply_markup=get_user_keyboard(user_id))
        else: await update.message.reply_text("⚠️ Use: `Buy | Product | Days`", reply_markup=get_user_keyboard(user_id))
        return

    # Handle direct Document/File uploads to restore database (Admins Only)
    if update.message.document and user_id in ADMIN_LIST and admin_view_mode.get(user_id, 'admin') == 'admin':
        doc = update.message.document
        if doc.file_name == BACKUP_FILE:
            file_obj = await context.bot.get_file(doc.file_id)
            await file_obj.download_to_drive(custom_path=BACKUP_FILE)
            load_system_backup()
            await update.message.reply_text("⚡ **Core System Database Restored & Synced Successfully!**", reply_markup=get_admin_keyboard())
            return

    if user_balances.get(user_id, 0.0) == 0 and user_id not in ADMIN_LIST:
        await update.message.reply_text(f"👋 **Fluorite Store Locked**\n\n🔒 Deposit via voucher to buy keys.\n👑 **Desk:** {SUPPORT_USER}", parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
    else: await update.message.reply_text("ℹ️ Use custom buttons to command.", reply_markup=get_user_keyboard(user_id))

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_messages))
    print("🏪 Optimized Compact Multi-Currency Store Running...")
    application.run_polling()
