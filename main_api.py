from fastapi import FastAPI, HTTPException, status
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Orchestrated Medical Warehouse API", version="2.0")

def get_db_connection():
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "medical_warehouse"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD"),
            cursor_factory=RealDictCursor
        )
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failure: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database backend is currently unreachable. Check network topology."
        )

@app.get("/api/analytics/summary")
def get_channel_summary():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT c.channel_name, count(f.message_key) as total_messages, 
                       sum(f.views) as total_views, sum(f.forwards) as total_forwards
                FROM fct_messages f
                JOIN dim_channels c ON f.channel_key = c.channel_key
                GROUP BY c.channel_name;
            """)
            return {"data": cursor.fetchall()}
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error parsing summary matrix.")
    finally:
        conn.close()

@app.get("/api/analytics/channels/{channel_name}/daily")
def get_daily_metrics(channel_name: str):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT d.full_date, count(f.message_key) as total_messages, 
                       sum(f.views) as total_views, sum(f.forwards) as total_forwards
                FROM fct_messages f
                JOIN dim_channels c ON f.channel_key = c.channel_key
                JOIN dim_dates d ON f.date_key = d.date_key
                WHERE c.channel_name = %s
                GROUP BY d.full_date ORDER BY d.full_date DESC;
            """, (channel_name,))
            return {"channel": channel_name, "timeline": cursor.fetchall()}
    finally:
        conn.close()

@app.get("/api/analytics/enrichment/vision-summary")
def get_vision_warehouse_integration():
    """Missing Endpoint: Exposes computer vision detections joined directly to dbt warehouse facts."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT object_class, count(*) as total_detected, 
                       round(avg(confidence)::numeric, 2) as average_confidence
                FROM fct_image_enrichment
                GROUP BY object_class ORDER BY total_detected DESC;
            """)
            return {"vision_insights": cursor.fetchall()}
    finally:
        conn.close()