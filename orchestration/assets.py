import os
import subprocess
from dagster import asset, Definitions
from dagster_dbt import dbt_assets, DbtCliResource

DBT_PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "medical_warehouse"))
dbt_resource = DbtCliResource(project_dir=DBT_PROJECT_DIR)

@asset(compute_kind="python")
def raw_telegram_data():
    """Asset 1: Python Ingestion Engine."""
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ingest_to_postgres.py"))
    result = subprocess.run([".\\venv\\Scripts\\python.exe", script_path], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Ingestion critical failure: {result.stderr}")
    return "Raw ingestion step passed."

@asset(compute_kind="yolov8", deps=[raw_telegram_data])
def yolov8_image_enrichment():
    """Asset 2: Computer Vision Pipeline (Populates public.detected_objects table)."""
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "object_detection_pipeline.py"))
    result = subprocess.run([".\\venv\\Scripts\\python.exe", script_path], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"YOLOv8 pipeline dropped frames: {result.stderr}")
    return "Object detection logs populated."

@dbt_assets(manifest=os.path.join(DBT_PROJECT_DIR, "target", "manifest.json"))
def medical_warehouse_dbt_assets(context, yolov8_image_enrichment):
    """Asset 3: Coordinates Staging, Marts, and Enriched Vision Tables."""
    os.environ["DBT_STATE_ENABLED"] = "false"
    yield from dbt_resource.cli(["run"], context=context).stream()

defs = Definitions(
    assets=[raw_telegram_data, yolov8_image_enrichment, medical_warehouse_dbt_assets],
    resources={"dbt": dbt_resource}
)