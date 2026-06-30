import os
import cv2
from ultralytics import YOLO
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "medical_warehouse"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD")
    )

def initialize_detection_table():
    """Creates the target schema table for computer vision metrics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detected_objects (
            detection_id SERIAL PRIMARY KEY,
            image_path VARCHAR(512),
            object_class VARCHAR(100),
            confidence FLOAT,
            box_coordinates TEXT
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def run_object_detection(image_dir):
    """Processes images through YOLOv8 and logs attributes to PostgreSQL."""
    # Load a lightweight pre-trained YOLOv8 model
    model = YOLO("yolov8n.pt")
    
    if not os.path.exists(image_dir):
        print(f"No image directory found at {image_dir}. Skipping vision tracking.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    for image_name in os.listdir(image_dir):
        if image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(image_dir, image_name)
            
            # Perform inference
            results = model(img_path)
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]
                    confidence = float(box.conf[0])
                    coords = box.xyxy[0].tolist() # [xmin, ymin, xmax, ymax]
                    
                    # Store metrics into the database
                    cursor.execute("""
                        INSERT INTO detected_objects (image_path, object_class, confidence, box_coordinates)
                        VALUES (%s, %s, %s, %s)
                    """, (img_path, class_name, confidence, str(coords)))
                    
    conn.commit()
    cursor.close()
    conn.close()
    print("Object detection pipeline successfully executed and logged.")

if __name__ == "__main__":
    initialize_detection_table()
    # Path where your scraper saves channel images
    image_folder_path = os.path.join(os.path.dirname(__file__), "data", "images")
    run_object_detection(image_folder_path)