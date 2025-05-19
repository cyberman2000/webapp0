from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler
from flask import Flask, request, jsonify
from tonclient.client import TonClient
from tonweb import TonWeb
import sqlite3
import requests
# ==================== تنظیمات ====================
BOT_TOKEN = "8019556090:AAGkPCm5-EKNN_vajujlIqwq2hSeYUJt7Oc"
WEB_APP_URL = "https://Sasane1010.pythonanywhere.com"  # مثل Render یا Railway
CHANNEL_USERNAME = "@bot_MakerTelegram"

# ==================== دیتابیس ====================
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            wallet_address TEXT,
            ton_balance REAL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

TONCENTER_API = "https://toncenter.com/api/v2/sendBoc "
API_KEY = "your_api_key"

def send_ton(wallet_address, amount_in_nano):
    payload = {
        "boc": generate_transfer_boc(wallet_address, amount_in_nano)
    }
    headers = {"X-API-Key": API_KEY}
    response = requests.post(TONCENTER_API, json=payload, headers=headers)
    return response.json()

def get_balance(user_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT ton_balance FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def add_ton(user_id, amount):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, ton_balance) VALUES (?, ?)", (user_id, 0))
    c.execute("UPDATE users SET ton_balance = ton_balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def set_wallet(user_id, address):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET wallet_address = ? WHERE user_id = ?", (address, user_id))
    conn.commit()
    conn.close()

# ==================== دستور استارت ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔥 بزن بریم", web_app={"url": f"{WEB_APP_URL}?user_id={user_id}"})],
    [InlineKeyboardButton("💼 اتصال به کیف پول", web_app={"url": f"https://your-webapp-url.com/connect-wallet?user_id= {user_id}"})],
    [InlineKeyboardButton("💰 موجودی", callback_data="balance")]
    ])

    await update.message.reply_text(f"""
👋 سلام {user.first_name}!

به ربات گیم خوش آمدی!
هر بار بازی، جایزه‌ای در انتظار توست.

🔹 موجودی: {get_balance(user_id):.2f} TON
    """, reply_markup=keyboard)

# ==================== مدیریت کلیک دکمه ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    user_id = user.id
    data = query.data

    if data == "wallet":
        wallet = get_wallet(user_id)
        text = f"👛 آدرس کیف پول: {wallet}" if wallet else "⚠️ کیف پولی متصل نشده است."
        await query.answer()
        await query.edit_message_text(text)

    elif data == "balance":
        await query.answer()
        await query.edit_message_text(f"🔸 موجودی شما: {get_balance(user_id):.2f} TON")

# ==================== دریافت نتیجه بازی از طریق وب هوک ====================
async def receive_prize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(context.args[0])
    prize = float(context.args[1])

    add_ton(user_id, prize)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ بله، متصل کن", callback_data=f"connect_{user_id}_{prize}")],
        [InlineKeyboardButton("❌ خیر", callback_data="no")]
    ])

    await update.message.reply_text(f"""
🎉 جایزه شما: {prize:.2f} TON

آیا مایلید این مبلغ به کیف پولتان منتقل شود؟
    """, reply_markup=keyboard)

# ==================== پاسخ به سوال اتصال کیف پول ====================
api_app = Flask(__name__)

@api_app.route("/api/wallet", methods=["POST"])
def save_wallet():
    data = request.json
    user_id = data["user_id"]
    wallet = data["wallet_address"]

    set_wallet(user_id, wallet)

    return jsonify({"status": "success"})

async def connect_wallet_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data

    if data.startswith("connect_"):
        _, user_id, prize = data.split("_")
        user_id = int(user_id)
        prize = float(prize)

        await query.answer()
        await query.edit_message_text("📌 لطفاً آدرس کیف پول خود را ارسال کنید:")

        context.user_data["awaiting_wallet"] = {"user_id": user_id, "prize": prize}

    elif data == "no":
        await query.answer("❌ جایزه شما نگه داشته شد.")

# ==================== دریافت آدرس کیف پول ====================
async def handle_wallet_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "awaiting_wallet" not in context.user_data:
        return

    wallet = update.message.text.strip()
    data = context.user_data["awaiting_wallet"]
    user_id = data["user_id"]

    set_wallet(user_id, wallet)
    del context.user_data["awaiting_wallet"]

    await update.message.reply_text("✅ کیف پول متصل شد!")

async def verify_wallet_signature(address, signature):
    # اعتبارسنجی امضای دیجیتال
    # مثلاً با Tonweb یا Tonkeeper API
    pass
# ==================== اجرای ربات ====================
if __name__ == '__main__':
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("prize", receive_prize))
    app.add_handler(CallbackQueryHandler(connect_wallet_prompt))
    app.add_handler(MessageHandler(None, handle_wallet_input))

    print("🎮 ربات گیم در حال اجرا است...")
    app.run_polling()