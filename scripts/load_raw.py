import os
import json
import sqlite3
from loguru import logger

logger.add("logs/data_loader.log", rotation="5 MB")

def load_json_to_sqlite():
    # 1. Open a local database file (Creates it automatically, no passwords!)
    db_path = "medical_db.sqlite"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    logger.info(f"Connected to local SQLite database at {db_path}")

    # 2. Create the destination table layout
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telegram_messages (
        message_id INTEGER,
        channel_name TEXT,
        message_date TEXT,
        message_text TEXT,
        views INTEGER,
        forwards INTEGER,
        has_media BOOLEAN
    );
    """)
    
    data_lake_folder = "data/raw/telegram_messages"
    if not os.path.exists(data_lake_folder):
        logger.warning("Data lake folder not found. Run the scraper first.")
        return

    # 3. Read JSON files and insert data rows
    inserted_count = 0
    for root, dirs, files in os.walk(data_lake_folder):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                logger.info(f"Loading files from: {file_path}")
                
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        messages = json.load(f)
                    except Exception as e:
                        logger.error(f"Failed to parse {file}: {str(e)}")
                        continue

                    for msg in messages:
                        cursor.execute("""
                        INSERT INTO telegram_messages (
                            message_id, channel_name, message_date, message_text, views, forwards, has_media
                        ) VALUES (?, ?, ?, ?, ?, ?, ?);
                        """, (
                            msg["message_id"],
                            msg["channel_name"],
                            msg["message_date"],
                            msg["message_text"],
                            msg["views"],
                            msg["forwards"],
                            msg["has_media"]
                        ))
                        inserted_count += 1

    conn.commit()
    cursor.close()
    conn.close()
    logger.success(f"Successfully loaded {inserted_count} rows into the SQLite database!")

if __name__ == "__main__":
    load_json_to_sqlite()