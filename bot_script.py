import requests
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


# Function to scrape individual torrent download page
def scrape_torrent_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the "Torrent Download" button/link (you may need to adjust the selector)
    torrent_link = None
    download_button = soup.find('a', {'class': 'btn-download'})  # Assuming this is the button's class
    if download_button and download_button.get('href'):
        torrent_link = download_button['href']
    
    return torrent_link

# Function to scrape search results page
def scrape_search_results(search_query):
    search_url = f"https://pornrips.to/?s={search_query}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the links to the individual torrent pages from the search results
    torrent_links = []
    for a_tag in soup.find_all('a', href=True):
        if '/torrents/' in a_tag['href']:  # Only consider links that lead to individual torrent pages
            torrent_page_url = a_tag['href']
            torrent_link = scrape_torrent_page(torrent_page_url)  # Scrape the torrent page for the actual torrent file link
            if torrent_link:
                torrent_links.append(torrent_link)

    return torrent_links

# Function to send torrents to Telegram
def send_torrent(update, context):
    query = update.message.text  # Get the query from the user message
    torrent_links = scrape_search_results(query)

    if torrent_links:
        message = "\n".join([f"Found torrent: {link}" for link in torrent_links])
    else:
        message = "No torrents found!"

    update.message.reply_text(message)

# Set up the bot
def start(update, context):
    update.message.reply_text('Hello! Send a search query and I\'ll find torrents for you.')

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Command Handlers
    dispatcher.add_handler(CommandHandler('start', start))

    # Message handler for normal text messages (to trigger search)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, send_torrent))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
