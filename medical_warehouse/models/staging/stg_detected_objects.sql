{{ config(materialized='view') }}

select
    detection_id,
    image_path,
    -- Extract message ID from the file path if named like 'msg_1001.jpg', or keep as reference
    object_class,
    confidence,
    box_coordinates
from {{ source('public', 'detected_objects') }}