
  create view "medical_warehouse"."public"."stg_telegram_messages__dbt_tmp"
    
    
  as (
    select
    message_id,
    channel_name,
    cast(message_date as timestamp) as message_date,
    message_text,
    length(message_text) as message_length,
    views,
    forwards,
    has_media
from raw_messages
where message_text is not null and message_text != ''
  );