import os
import json
from datetime import datetime
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from loguru import logger

# Force log directory and configuration at startup
os.makedirs("logs", exist_ok=True)
logger.add("logs/scraper.log", rotation="10 MB", retention="10 days", level="INFO")

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# Clean channel handles (no @ symbols for easier file paths)
channels = [
    "CheMed123",
    "lobelia4cosmetics",
    "tikvahpharma"
]

client = TelegramClient('session', api_id, api_hash)

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    json_folder = f"data/raw/telegram_messages/{today}"
    os.makedirs(json_folder, exist_ok=True)

    logger.info("Starting Telegram Client and initiating data pipeline...")

    with client:
        for channel in channels:
            logger.info(f"Scraping channel: {channel}...")
            messages_data = []
            
            image_folder = f"data/raw/images/{channel}"
            os.makedirs(image_folder, exist_ok=True)

            try:
                for message in client.iter_messages(channel, limit=500):
                    has_media = message.photo is not None
                    
                    data = {
                        "message_id": message.id,
                        "channel_name": channel,
                        "message_date": str(message.date),
                        "message_text": message.text if message.text else "",
                        "views": message.views if message.views else 0,
                        "forwards": message.forwards if message.forwards else 0,
                        "has_media": has_media
                    }
                    messages_data.append(data)

                    if has_media:
                        image_path = f"{image_folder}/{message.id}.jpg"
                        if not os.path.exists(image_path):
                            client.download_media(message, image_path)

                filename = f"{json_folder}/{channel}.json"
                with open(filename, "w", encoding="utf8") as f:
                    json.dump(messages_data, f, ensure_ascii=False, indent=4)
                
                logger.info(f"Successfully scraped {len(messages_data)} messages from {channel}.")

            except Exception as e:
                logger.error(f"Failed to scrape channel {channel}: {str(e)}")

if __name__ == "__main__":
    main()