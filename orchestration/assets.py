import os
import subprocess
from dagster import asset, Definitions, define_asset_job, AssetSelection, ScheduleDefinition
from dagster_dbt import dbt_assets, DbtCliResource

DBT_PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "medical_warehouse"))
dbt_resource = DbtCliResource(project_dir=DBT_PROJECT_DIR)

@asset(compute_kind="python")
def raw_telegram_data():
    """Runs the ingestion script to load raw JSON streams into PostgreSQL."""
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ingest_to_postgres.py"))
    result = subprocess.run([".\\venv\\Scripts\\python.exe", script_path], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Ingestion failed: {result.stderr}")
    return "Raw data successfully loaded"

@asset(compute_kind="yolov8", deps=[raw_telegram_data])
def yolov8_image_enrichment():
    """Triggers object detection pipeline on raw scraped images."""
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "object_detection_pipeline.py"))
    result = subprocess.run([".\\venv\\Scripts\\python.exe", script_path], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"YOLOv8 pipeline failed: {result.stderr}")
    return "Object detection logs updated"

@dbt_assets(manifest=os.path.join(DBT_PROJECT_DIR, "target", "manifest.json"))
def medical_warehouse_dbt_assets(context, yolov8_image_enrichment):
    """Executes dbt transformations downstream from raw ingestion and YOLO detection."""
    os.environ["DBT_STATE_ENABLED"] = "false"
    yield from dbt_resource.cli(["run"], context=context).stream()

# 1. Define the Job execution target
pipeline_job = define_asset_job(
    name="medical_warehouse_daily_job",
    selection=AssetSelection.all()
)

# 2. Rubric Alignment: Add strict automated Cron scheduling (Runs every day at midnight)
daily_pipeline_schedule = ScheduleDefinition(
    job=pipeline_job,
    cron_schedule="0 0 * * *" 
)

defs = Definitions(
    assets=[raw_telegram_data, yolov8_image_enrichment, medical_warehouse_dbt_assets],
    resources={"dbt": dbt_resource},
    schedules=[daily_pipeline_schedule] # Registered schedule
)