{{ config(materialized='table') }}

with detections as (
    select * from {{ ref('stg_detected_objects') }}
),
messages as (
    select * from {{ ref('fct_messages') }}
)

select
    d.detection_id,
    m.message_key,
    d.object_class,
    d.confidence,
    d.box_coordinates
from detections d
-- Joins based on image matching logic used in your pipeline
join messages m on d.image_path like '%' || m.message_key || '%'