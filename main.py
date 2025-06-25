import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not BOT_TOKEN or not CHANNEL_ID:
    raise ValueError("Please set BOT_TOKEN and CHANNEL_ID environment variables")

# Sample files data structure (you can modify this)
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
    """Send a message with the inline keyboard when the command /start is issued."""
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
    
    # Check if the callback is for a category
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
    # Check if the callback is for a file
    elif query.data.startswith("file_"):
        _, category_id, file_id = query.data.split("_", 2)
        file_data = CATEGORIES[category_id]["files"][file_id]
        
        try:
            await context.bot.copy_message(
                chat_id=query.from_user.id,
                from_chat_id=int(CHANNEL_ID),
                message_id=file_data["message_id"]
            )
        except Exception as e:
            await query.edit_message_text("❌ Failed to send file. Please try again later.")
            print(f"Error sending file: {e}")
    # Handle back button
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
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()