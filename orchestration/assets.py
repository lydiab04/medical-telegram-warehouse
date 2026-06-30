import os
import subprocess
from dagster import asset, Definitions
from dagster_dbt import dbt_assets, DbtCliResource

# Configure dbt project path
DBT_PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "medical_warehouse"))
dbt_resource = DbtCliResource(project_dir=DBT_PROJECT_DIR)

@asset(compute_kind="python")
def raw_telegram_data():
    """Runs the ingestion script to load raw JSON streams into PostgreSQL."""
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ingest_to_postgres.py"))
    # Use python executable relative to project structure
    result = subprocess.run([".\\venv\\Scripts\\python.exe", script_path], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Ingestion failed: {result.stderr}")
    return "Raw data successfully loaded"

@dbt_assets(manifest=os.path.join(DBT_PROJECT_DIR, "target", "manifest.json"))
def medical_warehouse_dbt_assets(context):
    """Executes dbt transformations on PostgreSQL."""
    os.environ["DBT_STATE_ENABLED"] = "false"
    yield from dbt_resource.cli(["run"], context=context).stream()

@asset(compute_kind="yolov8")
def yolov8_image_enrichment():
    """Triggers the object detection pipeline."""
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "object_detection_pipeline.py"))
    result = subprocess.run([".\\venv\\Scripts\\python.exe", script_path], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"YOLOv8 process failed: {result.stderr}")
    return "Computer vision logs updated"

# Use job definitions to explicitly enforce execution order (Pipeline Lineage)
from dagster import define_asset_job, AssetSelection

run_all_pipeline_assets = define_asset_job(
    name="medical_warehouse_pipeline",
    selection=AssetSelection.all()
)

defs = Definitions(
    assets=[raw_telegram_data, medical_warehouse_dbt_assets, yolov8_image_enrichment],
    resources={"dbt": dbt_resource},
    jobs=[run_all_pipeline_assets]
)