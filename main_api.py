from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="Medical Telegram Warehouse Analytics API", version="1.0")

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "medical_warehouse"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        cursor_factory=RealDictCursor
    )

@app.get("/")
def read_root():
    return {"status": "online", "message": "Medical Warehouse API layer active"}

@app.get("/api/analytics/summary")
def get_channel_summary():
    """Exposes core aggregate data metrics directly out of our dbt Star Schema."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            c.channel_name,
            count(f.message_key) as total_messages,
            sum(f.views) as total_views,
            sum(f.forwards) as total_forwards
        FROM fct_messages f
        JOIN dim_channels c ON f.channel_key = c.channel_key
        GROUP BY c.channel_name;
    """)
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"data": records}

@app.get("/api/analytics/detections")
def get_object_detections():
    """Exposes YOLOv8 object detection analytics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT object_class, confidence, image_path FROM detected_objects ORDER BY confidence DESC LIMIT 50;")
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"detections": records}