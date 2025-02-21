from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Function to send a message to Telegram
async def start(update: Update, context):
    await update.message.reply_text("Hello! Send a search query and I'll find torrents for you.")

async def send_torrent(update: Update, context):
    query = update.message.text  # Get the query from the user message
    torrent_links = scrape_search_results(query)

    if torrent_links:
        message = "\n".join([f"Found torrent: {link}" for link in torrent_links])
    else:
        message = "No torrents found!"

    await update.message.reply_text(message)

# Main function to run the bot
def main():
    application = Application.builder().token(TOKEN).build()

    # Set up handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_torrent))

    application.run_polling()

if __name__ == '__main__':
    main()
