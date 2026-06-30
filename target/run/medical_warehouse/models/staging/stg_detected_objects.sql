
  create view "medical_warehouse"."public"."stg_detected_objects__dbt_tmp"
    
    
  as (
    

select
    detection_id,
    image_path,
    -- Extract message ID from the file path if named like 'msg_1001.jpg', or keep as reference
    object_class,
    confidence,
    box_coordinates
from "medical_warehouse"."public"."detected_objects"
  );