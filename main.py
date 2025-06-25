import os
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Enhanced environment variable loading with debugging
print("\n" + "="*40)
print("STARTING BOT - ENVIRONMENT CHECK")
print("="*40 + "\n")

# Debug: Print all available environment variables
print("Available environment variables:")
for key, value in os.environ.items():
    if any(k in key.lower() for k in ['bot', 'channel', 'token']):
        print(f"{key}: {'*' * len(value) if 'token' in key.lower() else value}")

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

print("\n" + "="*40)
print(f"BOT_TOKEN: {'SET' if BOT_TOKEN else 'NOT SET'}")
print(f"CHANNEL_ID: {CHANNEL_ID if CHANNEL_ID else 'NOT SET'}")
print("="*40 + "\n")

if not BOT_TOKEN or not CHANNEL_ID:
    error_msg = """
    ERROR: Missing required environment variables!
    Please ensure these are set in Render:
    1. BOT_TOKEN - Your Telegram bot token from @BotFather
    2. CHANNEL_ID - Your channel ID (including -100 prefix)
    """
    print(error_msg)
    sys.exit(1)

# Sample files data structure
CATEGORIES = {
    "study": {
        "name": "📁 Study Materials",
        "files": {
            "math_guide": {"name": "📕 Math Guide", "message_id": 101},
            "physics_notes": {"name": "📗 Physics Notes", "message_id": 102},
        },
    },
    "crypto": {
        "name": "📁 Crypto PDFs",
        "files": {
            "bitcoin_whitepaper": {"name": "📄 Bitcoin Whitepaper", "message_id": 201},
            "ethereum_guide": {"name": "📄 Ethereum Guide", "message_id": 202},
        },
    },
    "apk": {
        "name": "📁 APK Files",
        "files": {
            "tool_app": {"name": "🛠️ Useful Tool", "message_id": 301},
            "game_app": {"name": "🎮 Fun Game", "message_id": 302},
        },
    },
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send menu with categories when /start is issued."""
    keyboard = [
        [InlineKeyboardButton(cat["name"], callback_data=cat_id)]
        for cat_id, cat in CATEGORIES.items()
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose a category:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses."""
    query = update.callback_query
    await query.answer()
    
    if query.data in CATEGORIES:
        category = CATEGORIES[query.data]
        keyboard = [
            [InlineKeyboardButton(file["name"], callback_data=f"file_{query.data}_{file_id}")]
            for file_id, file in category["files"].items()
        ]
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"Category: {category['name']}\nSelect a file:",
            reply_markup=reply_markup
        )
    elif query.data.startswith("file_"):
        _, category_id, file_id = query.data.split("_", 2)
        file_data = CATEGORIES[category_id]["files"][file_id]
        
        try:
            await context.bot.copy_message(
                chat_id=query.from_user.id,
                from_chat_id=int(CHANNEL_ID),
                message_id=file_data["message_id"]
            )
            print(f"Sent file {file_id} to user {query.from_user.id}")
        except Exception as e:
            error_msg = f"Failed to send file: {str(e)}"
            print(error_msg)
            await query.edit_message_text("❌ Failed to send file. Please try again later.")
    elif query.data == "back":
        keyboard = [
            [InlineKeyboardButton(cat["name"], callback_data=cat_id)]
            for cat_id, cat in CATEGORIES.items()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Please choose a category:",
            reply_markup=reply_markup
        )

def main() -> None:
    """Start the bot."""
    print("\n" + "="*40)
    print("INITIALIZING BOT APPLICATION")
    print("="*40 + "\n")
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button))
        
        print("Bot is running...")
        application.run_polling()
    except Exception as e:
        print(f"FATAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
