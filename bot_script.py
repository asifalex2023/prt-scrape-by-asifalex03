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

    # Check if the response is valid
    if response.status_code != 200:
        print(f"Error fetching torrent page: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Debug: Print the entire HTML of the torrent page
    print(f"Torrent Page HTML for {url}:", soup.prettify()[:500])  # Print the first 500 chars

    # Find the "Torrent Download" button/link (you may need to adjust the selector)
    download_button = soup.find('a', {'class': 'btn-download'})  # Adjust based on actual class or element

    # Debug: Check if the download button is found
    if download_button:
        print("Download button found:", download_button.get('href'))
        return download_button['href']
    else:
        print("Download button not found on this page.")
        return None


# Function to scrape search results page
def scrape_search_results(search_query):
    search_url = f"https://pornrips.to/?s={search_query}"
    response = requests.get(search_url)
    
    # Check if the response is valid
    if response.status_code != 200:
        print(f"Error fetching search results: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Debug: Print the entire HTML of the search results
    print("Search Results Page HTML:", soup.prettify()[:500])  # Print the first 500 chars

    # Find the links to the individual torrent pages from the search results
    torrent_links = []
    for a_tag in soup.find_all('a', href=True):
        link = a_tag['href']
        # Debug: Print the found 'a' tag href
        print("Found a tag:", link)

        # Filter links that are more likely to be individual torrent pages (not category, RSS, etc.)
        if '/torrents/' in link:  # Only consider links that lead to individual torrent pages
            print(f"Found torrent page link: {link}")
            torrent_page_url = link
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
