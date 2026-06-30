
  create view "medical_warehouse"."public"."stg_cleaned_messages__dbt_tmp"
    
    
  as (
    

with raw_staging as (
    select * from "medical_warehouse"."public"."stg_telegram_messages"
)

select
    message_id,
    channel_name,
    message_date,
    message_text,
    views,
    forwards,
    has_media,
    -- Add safe text-length and word-count processing for NLP downstream tasks
    length(message_text) as character_count,
    array_length(regexp_split_to_array(trim(message_text), '\s+'), 1) as word_count
from raw_staging
-- Clean out empty updates or noise
where message_text is not null 
  and length(trim(message_text)) > 0
  );