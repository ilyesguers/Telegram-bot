from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import random
import string
import json
import os
import mysql.connector

# بيانات الاتصال الخارجية الصحيحة بناءً على الرابط الذي أرسلته
db_config = {
    'host': 'acela.proxy.rlwy.net',
    'user': 'root',
    'password': 'yhjwurXoNTJQqiqiiWwrylGgqzymCCqB',
    'database': 'railway',
    'port': 39028
}

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
    return ReplyKeyboardMarkup([
        [KeyboardButton("🩷 Buy Key 🩷")],
        [KeyboardButton("💙 Support 💙"), KeyboardButton("🚪 Log out 🚪")],
        [KeyboardButton("➡️ Next")]
    ], resize
