import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# Function to save the torrent links to a text file
def save_torrent_links(torrent_links, filename="torrent_links.txt"):
    with open(filename, 'w') as file:
        for link in torrent_links:
            file.write(f"{link}\n")

# Function to handle the '/start' command
async def start(update: Update, context):
    await update.message.reply_text("Hello! Send a search query and I'll find torrents for you.")

# Function to handle torrent search and saving results to a text file
async def send_torrent(update: Update, context):
    query = update.message.text  # Get the query from the user message
    torrent_links = scrape_search_results(query)

    if torrent_links:
        # Save the results to a text file
        save_torrent_links(torrent_links)
        message = f"Found {len(torrent_links)} torrents. Links saved to 'torrent_links.txt'."
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
