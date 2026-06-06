from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import random
import string

# --- Configuration ---
TOKEN = '8765508457:AAHLzXj9JEMCbnIWfeov39bN75JrRZ9JcfQ'
PRIMARY_ADMIN = 5145154527  # Your Telegram User ID
SUPPORT_USER = "@i6issiiiii"

# --- Database & Config ---
ADMIN_LIST = {PRIMARY_ADMIN}

# Base prices are stored strictly in USD inside the engine
PRODUCTS = {
    "Fluorite Hack 💎": {"1": 5.0, "7": 15.0, "30": 40.0},
    "Free Fire VIP 🔥": {"1": 3.0, "7": 10.0, "30": 25.0}
}

user_balances = {}  # Store balances in USD {user_id: float}
user_currencies = {}  # Selected currency mode {user_id: 'USD' or 'LOCAL'}
user_countries = {}  # Simulated country detected via initial check

# Fixed internal Exchange Rates (Base 1 USD to Local)
EXCHANGE_RATES = {
    "SA": {"symbol": "SAR", "rate": 3.75},   # Saudi Arabia
    "EG": {"symbol": "EGP", "rate": 47.0},   # Egypt
    "AE": {"symbol": "AED", "rate": 3.67},   # UAE
    "DZ": {"symbol": "DZD", "rate": 134.0},  # Algeria
    "IQ": {"symbol": "IQD", "rate": 1310.0}, # Iraq
    "DEFAULT": {"symbol": "EUR", "rate": 0.92} # Default fallback for other zones
}

active_coupons = {"CHARGE-10USD": 10.0, "CHARGE-50USD": 50.0}

fluorite_stock = {
    "Fluorite Hack 💎": {
        "1": ["FLUORITE-1DAY-XXXX"], "7": ["FLUORITE-7DAY-ZZZZ"], "30": ["FLUORITE-30DAY-AAAA"]
    },
    "Free Fire VIP 🔥": {
        "1": ["FF-1DAY-1111"], "7": ["FF-7DAY-2222"], "30": ["FF-30DAY-3333"]
    }
}

# States
admin_states = {}
user_states = {}
admin_view_mode = {}

# --- Helper Currency Functions ---
def get_user_currency_info(user_id):
    """Returns the currency symbol and rate factor for the user"""
    country = user_countries.get(user_id, "DEFAULT")
    mode = user_currencies.get(user_id, "USD")
    
    if mode == "USD":
        return "$", 1.0
    else:
        info = EXCHANGE_RATES.get(country, EXCHANGE_RATES["DEFAULT"])
        return info["symbol"], info["rate"]

def format_price(usd_amount, symbol, rate):
    """Converts and formats the currency cleanly"""
    local_amount = usd_amount * rate
    if symbol == "$":
        return f"{local_amount:.2f}$"
    return f"{local_amount:.2f} {symbol}"

# --- Keyboards ---
def get_admin_keyboard():
    keyboard = [
        [KeyboardButton("🎫 Generate New Coupon"), KeyboardButton("📦 Restock Cheat Keys")],
        [KeyboardButton("⚙️ Change Product Prices"), KeyboardButton("🛠️ Delete Mistaken Key")],
        [KeyboardButton("👥 Add New Admin ID"), KeyboardButton("📋 View System Analytics")],
        [KeyboardButton("👤 Switch to User Mode")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_user_keyboard(user_id):
    _, _ = get_user_currency_info(user_id)
    keyboard = [
        [KeyboardButton("🛒 Browse Premium Cheats"), KeyboardButton("💳 Redeem Coupon")],
        [KeyboardButton("💰 My Wallet"), KeyboardButton("💱 Switch Currency")],
    ]
    if user_id in ADMIN_LIST:
        keyboard.append([KeyboardButton("🔙 Back to Admin Panel")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_currency_preference_keyboard():
    keyboard = [
        [KeyboardButton("🟢 Local Country Currency"), KeyboardButton("💵 Standard USD ($)")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin_states[user_id] = None
    user_states[user_id] = None
    
    if user_id not in user_balances:
        user_balances[user_id] = 0.0

    # Auto-assign a random simulated Middle-East/North-African regional country code for localization demo
    if user_id not in user_countries:
        user_countries[user_id] = random.choice(["SA", "EG", "AE", "DZ", "IQ"])

    # --- Admin Dashboard Entry ---
    if user_id in ADMIN_LIST and admin_view_mode.get(user_id, 'admin') == 'admin':
        await update.message.reply_text(
            f"👑 **Welcome Back Commander! [Fluorite Master Dashboard]**\n\n"
            f"Manage licenses, edit prices, authorize co-admins, and monitor your shop live below 👇",
            reply_markup=get_admin_keyboard()
        )
        return

    # --- Prompt Currency Preference Selection on first login ---
    if user_id not in user_currencies:
        country_code = user_countries[user_id]
        local_sym = EXCHANGE_RATES.get(country_code, EXCHANGE_RATES["DEFAULT"])["symbol"]
        
        setup_msg = (
            f"🌍 **Currency Detection System**\n\n"
            f"We detected your region access profile. Would you prefer to browse our storefront products "
            f"and checkout using your **Local Currency ({local_sym})** or **Standard USD ($)**?"
        )
        await update.message.reply_text(setup_msg, reply_markup=get_currency_preference_keyboard())
        return

    await show_user_welcome(update, user_id)

async def show_user_welcome(update: Update, user_id: int):
    sym, rate = get_user_currency_info(user_id)
    bal_str = format_price(user_balances.get(user_id, 0.0), sym, rate)
    
    welcome_msg = (
        f"👋 **Welcome to the Elite Fluorite Keys Store!** ✨\n\n"
        f"🔒 **Access Status:** `Verified Customer`\n"
        f"💳 **Current Wallet Balance:** `{bal_str}`\n\n"
        f"To unlock our premium lethal cheats and secure your exclusive keys, please add balance to your wallet via a **Recharge Coupon Code**.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👑 **Official Live Sales & Support:** {SUPPORT_USER} 📲\n"
        f"💬 Contact the developer right now to clear your payment and secure your high-value voucher code! 💸💎\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ _Navigate your way to premium power using the buttons below!_"
    )
    await update.message.reply_text(welcome_msg, parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # --- [Handle Currency Choice Setup] ---
    if text in ["🟢 Local Country Currency", "💵 Standard USD ($)"]:
        user_currencies[user_id] = "LOCAL" if text == "🟢 Local Country Currency" else "USD"
        await update.message.reply_text("✅ Currency preference locked and successfully configured!", reply_markup=ReplyKeyboardRemove())
        await show_user_welcome(update, user_id)
        return

    # --- [Admin Control Protocol] ---
    if user_id in ADMIN_LIST and admin_view_mode.get(user_id, 'admin') == 'admin':
        if text == "🎫 Generate New Coupon":
            admin_states[user_id] = 'awaiting_coupon_val'
            await update.message.reply_text("💵 Enter voucher cash value in USD (Numbers only, e.g., 20):", reply_markup=ReplyKeyboardRemove())
            return
            
        elif text == "📦 Restock Cheat Keys":
            admin_states[user_id] = 'awaiting_key_add'
            msg = "⚙️ **Send the keys using this exact layout structure:**\n\n" \
                  "`Product Name | Days | License Key`\n\n" \
                  "💡 _Example:_\n`Fluorite Hack 💎 | 1 | FLUORITE-KEY-ABC123XYZ`"
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
            return

        elif text == "⚙️ Change Product Prices":
            admin_states[user_id] = 'awaiting_price_change'
            msg = "⚡ **To update a product price, send it using this format (Always enter value in USD):**\n\n" \
                  "`Product Name | Days | New Price In USD`\n\n" \
                  "📝 _Example:_\n`Fluorite Hack 💎 | 1 | 6.5`"
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
            return

        elif text == "🛠️ Delete Mistaken Key":
            admin_states[user_id] = 'awaiting_key_delete'
            await update.message.reply_text("🗑️ **To remove a specific key from stock, paste the exact key code below:**", reply_markup=ReplyKeyboardRemove())
            return

        elif text == "👥 Add New Admin ID":
            admin_states[user_id] = 'awaiting_admin_id'
            await update.message.reply_text("🆔 **Send the Telegram User ID of the person you want to promote to Admin:**", reply_markup=ReplyKeyboardRemove())
            return
            
        elif text == "📋 View System Analytics":
            msg = "🎫 **Active Coupons:**\n"
            for coup, val in active_coupons.items():
                msg += f"🔹 Code: `{coup}` | `{val}$` \n"
            msg += "\n💰 **Product Price List (Engine USD):**\n"
            for prod, prices in PRODUCTS.items():
                msg += f"💎 `{prod}` -> 1D: `{prices['1']}$` | 7D: `{prices['7']}$` | 30D: `{prices['30']}$` \n"
            msg += "\n📦 **Current Live Stock Statistics:**\n"
            for prod, days in fluorite_stock.items():
                msg += f"◽ {prod}:\n"
                for day, keys in days.items():
                    msg += f"   - {day} Day: ({len(keys)}) keys available.\n"
            msg += f"\n👑 **Authorized Admins Count:** `{len(ADMIN_LIST)}`"
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_admin_keyboard())
            return
            
        elif text == "👤 Switch to User Mode":
            admin_view_mode[user_id] = 'user'
            if user_id not in user_currencies: user_currencies[user_id] = "USD"
            await update.message.reply_text("🔄 Client simulation activated! Enjoy your shop testing experience.", reply_markup=get_user_keyboard(user_id))
            return

        # Executing Admin States
        state = admin_states.get(user_id)
        if state == 'awaiting_coupon_val':
            try:
                val = float(text)
                coupon_code = "FLUORITE-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                active_coupons[coupon_code] = val
                admin_states[user_id] = None
                await update.message.reply_text(f"✅ **Coupon Minted!**\n💵 Value: `{val}$`\n🎫 Code: `{coupon_code}`", parse_mode="Markdown", reply_markup=get_admin_keyboard())
            except ValueError:
                await update.message.reply_text("❌ Invalid number. Try again:")
            return
            
        elif state == 'awaiting_key_add':
            parts = text.split('|')
            if len(parts) == 3:
                p_name, p_days, p_key = parts[0].strip(), parts[1].strip(), parts[2].strip()
                if p_name in fluorite_stock and p_days in ["1", "7", "30"]:
                    fluorite_stock[p_name][p_days].append(p_key)
                    admin_states[user_id] = None
                    await update.message.reply_text(f"✅ Key added to stock successfully!", reply_markup=get_admin_keyboard())
                else:
                    await update.message.reply_text("❌ Product or day tier mismatch. Try again:")
            else:
                await update.message.reply_text("⚠️ Layout error. Use: `Product Name | Days | License Key`")
            return

        elif state == 'awaiting_price_change':
            parts = text.split('|')
            if len(parts) == 3:
                p_name, p_days, p_price = parts[0].strip(), parts[1].strip(), parts[2].strip()
                if p_name in PRODUCTS and p_days in ["1", "7", "30"]:
                    try:
                        PRODUCTS[p_name][p_days] = float(p_price)
                        admin_states[user_id] = None
                        await update.message.reply_text(f"✅ **Price Updated!**\n💎 `{p_name}` [{p_days} Day] set to `{p_price}$`", parse_mode="Markdown", reply_markup=get_admin_keyboard())
                    except ValueError:
                        await update.message.reply_text("❌ Price must be a valid number:")
                else:
                    await update.message.reply_text("❌ Product name or day tier not found in system.")
            else:
                await update.message.reply_text("⚠️ Use layout: `Product Name | Days | New Price`")
            return

        elif state == 'awaiting_key_delete':
            found = False
            for prod, days in fluorite_stock.items():
                for day, keys in days.items():
                    if text in keys:
                        keys.remove(text)
                        found = True
            admin_states[user_id] = None
            if found:
                await update.message.reply_text("🗑️ **Successfully deleted the mistaken key from stock!**", reply_markup=get_admin_keyboard())
            else:
                await update.message.reply_text("❌ Key was not found anywhere in active stock.", reply_markup=get_admin_keyboard())
            return

        elif state == 'awaiting_admin_id':
            try:
                new_admin = int(text)
                ADMIN_LIST.add(new_admin)
                admin_states[user_id] = None
                await update.message.reply_text(f"👑 **Promotion Success!** User ID `{new_admin}` is now an official Admin.", parse_mode="Markdown", reply_markup=get_admin_keyboard())
            except ValueError:
                await update.message.reply_text("❌ Telegram ID must be digits only. Enter a valid ID:")
            return

    # --- [Admin Escape Route] ---
    if user_id in ADMIN_LIST and text == "🔙 Back to Admin Panel":
        admin_view_mode[user_id] = 'admin'
        admin_states[user_id] = None
        user_states[user_id] = None
        await update.message.reply_text("👑 Controls restored. Back to HQ Operations.", reply_markup=get_admin_keyboard())
        return

    # --- [User Store Operations] ---
    sym, rate = get_user_currency_info(user_id)

    if text == "💱 Switch Currency":
        current_mode = user_currencies.get(user_id, "USD")
        user_currencies[user_id] = "USD" if current_mode == "LOCAL" else "LOCAL"
        new_sym, _ = get_user_currency_info(user_id)
        await update.message.reply_text(f"🔄 Currency successfully converted and switched to: **{new_sym}**", parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
        return

    elif text == "🛒 Browse Premium Cheats":
        msg = "🔥 **Exclusive Fluorite Mod Menu Portfolio:** 🔥\n\n"
        for prod, prices in PRODUCTS.items():
            p1 = format_price(prices['1'], sym, rate)
            p7 = format_price(prices['7'], sym, rate)
            p30 = format_price(prices['30'], sym, rate)
            
            msg += f"💎 **Software:** `{prod}`\n"
            msg += f"   ▫️ 1 Day Pass: `{p1}` \n"
            msg += f"   ▫️ 7 Day Pass: `{p7}` \n"
            msg += f"   ▫️ 30 Day Pass: `{p30}` \n"
            msg += f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += "🎯 **Instant Purchase Command:**\nDuplicate and send the exact template structure format below in one line:\n\n" \
               "`Buy | Product Name | Days`\n\n" \
               "📝 _Example:_ \n`Buy | Fluorite Hack 💎 | 1`"
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
        return
        
    elif text == "💳 Redeem Coupon":
        user_states[user_id] = 'entering_coupon'
        await update.message.reply_text("🎫 **Drop your active balance voucher code below to credit your account immediately:**", reply_markup=ReplyKeyboardRemove())
        return
        
    elif text == "💰 My Wallet":
        bal_str = format_price(user_balances.get(user_id, 0.0), sym, rate)
        await update.message.reply_text(f"👤 **Your Private Store Account Metrics:**\n\n💵 Spendable Funds: `{bal_str}` \n🎯 Currency View Profile: `{sym}` \n🎯 Account Manager: {SUPPORT_USER}", parse_mode="Markdown")
        return

    # Handling Coupon Redeeming
    if user_states.get(user_id) == 'entering_coupon':
        if text in active_coupons:
            amount_usd = active_coupons[text]
            user_balances[user_id] += amount_usd
            del active_coupons[text]  # Burn code
            user_states[user_id] = None
            
            credited_str = format_price(amount_usd, sym, rate)
            await update.message.reply_text(f"🎉 **Boom! Coupon Loaded Successfully.**\n💰 `{credited_str}` has been added to your live store wallet balance!", parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
        else:
            user_states[user_id] = None
            await update.message.reply_text("❌ **Invalid or expired voucher code!** Contact support if this is a mistake.", reply_markup=get_user_keyboard(user_id))
        return

    # Handling Automated Purchases
    if text.lower().startswith("buy"):
        parts = text.split('|')
        if len(parts) == 3:
            p_name, p_days = parts[1].strip(), parts[2].strip()
            
            if p_name in PRODUCTS and p_days in ["1", "7", "30"]:
                price_usd = PRODUCTS[p_name][p_days]
                current_bal_usd = user_balances.get(user_id, 0.0)
                
                if current_bal_usd >= price_usd:
                    if fluorite_stock[p_name][p_days]:
                        purchased_key = fluorite_stock[p_name][p_days].pop(0)
                        user_balances[user_id] -= price_usd
                        
                        success_msg = (
                            f"🎉 **Transaction Complete! Purchase Successful!** 🎉\n\n"
                            f"📦 **Here is your Fluorite Key License:**\n"
                            f"`{purchased_key}`\n\n"
                            f"🎮 _Inject your license, launch the game, and dominate the battleground!_"
                        )
                        await update.message.reply_text(success_msg, parse_mode="Markdown", reply_markup=get_user_keyboard(user_id))
                    else:
                        await update.message.reply_text(f"⚠️ **This tier is out of stock!** Contact {SUPPORT_USER} for an instant restock request.", reply_markup=get_user_keyboard(user_id))
                else:
                    needed_str = format_price(price_usd, sym, rate)
                    await update.message.reply_text(f"❌ **Funds Insufficient!** This item requires `{needed_str}`. Contact support {SUPPORT_USER} to add credits! ✨", reply_markup=get_user_keyboard(user_id))
            else:
                await update.message.reply_text("❌ Invalid product name or day configuration parameter.")
        else:
            await update.message.reply_text("⚠️ Faulty purchase structure. Send like this:\n`Buy | Product Name | Days`")
        return

    # Fallback response for unconfigured/unverified profiles
    if user_id not in user_currencies:
        await update.message.reply_text("⚙️ Please select your interface currency view using the buttons below:", reply_markup=get_currency_preference_keyboard())
    else:
        await update.message.reply_text("ℹ️ Please deploy the provided keyboard buttons below to manage products or checkouts.", reply_markup=get_user_keyboard(user_id))

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    
    print("🏪 Dynamic Multi-Currency Fluorite Store Online...")
    application.run_polling()
