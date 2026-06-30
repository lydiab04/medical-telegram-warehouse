import os
import json
import pandas as pd
from psycopg2 import connect
from dotenv import load_dotenv

# Force load the .env file explicitly from the same directory as this script
script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(script_dir, '.env'))

def get_db_connection():
    """Establishes a modular connection instance to the PostgreSQL backend."""
    return connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "medical_warehouse"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD")
    )

def parse_raw_telegram_json(file_path):
    """Parses raw JSON message arrays from the Data Lake Bronze layer."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Target source file not found at: {file_path}")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('messages', [])

def transform_to_dataframe(messages, channel_name):
    """Normalizes raw unstructured message keys into a clean Pandas DataFrame (Silver Layer)."""
    parsed_records = []
    for msg in messages:
        if msg.get('type') == 'message':
            parsed_records.append({
                'message_id': msg.get('id'),
                'channel_name': channel_name,
                'message_date': msg.get('date'),
                'message_text': msg.get('text'),
                'views': msg.get('views', 0),
                'forwards': msg.get('forwards', 0),
                'has_media': 1 if msg.get('media_type') or msg.get('photo') else 0
            })
    return pd.DataFrame(parsed_records)

def load_dataframe_to_postgres(df, table_name="raw_messages"):
    """Pipes the curated structured array straight into PostgreSQL staging tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Simple incremental table setup
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            message_id BIGINT,
            channel_name VARCHAR(255),
            message_date TIMESTAMP,
            message_text TEXT,
            views INT,
            forwards INT,
            has_media INT
        );
    """)
    conn.commit()
    
    # Bulk insertion logic
    for _, row in df.iterrows():
        cursor.execute(f"""
            INSERT INTO {table_name} (message_id, channel_name, message_date, message_text, views, forwards, has_media)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (row['message_id'], row['channel_name'], row['message_date'], row['message_text'], row['views'], row['forwards'], row['has_media']))
        
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Successfully loaded {len(df)} records into target table: {table_name}")

if __name__ == "__main__":
    # Look for data inside the local directory structure dynamically
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_sample_file = os.path.join(script_dir, "data", "raw_channel_data.json")
    
    # Alternative fallback check: if you have your JSON file named differently or directly in root
    if not os.path.exists(target_sample_file):
        # Look for any json file in a 'data' folder or root
        target_sample_file = os.path.join(script_dir, "raw_channel_data.json")

    print(f"Attempting to read data asset from: {target_sample_file}")
    
    try:
        raw_payload = parse_raw_telegram_json(target_sample_file)
        clean_df = transform_to_dataframe(raw_payload, channel_name="medical_channel_one")
        load_dataframe_to_postgres(clean_df)
    except Exception as e:
        print(f"Ingestion pipeline execution failed: {e}")