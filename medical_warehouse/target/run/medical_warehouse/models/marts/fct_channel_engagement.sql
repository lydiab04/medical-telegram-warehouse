
  
    

  create  table "medical_warehouse"."public"."fct_channel_engagement__dbt_tmp"
  
  
    as
  
  (
    

with cleaned_data as (
    select * from "medical_warehouse"."public"."stg_cleaned_messages"
)

select
    channel_name,
    count(message_id) as total_messages,
    sum(views) as total_views,
    sum(forwards) as total_forwards,
    round(avg(character_count), 2) as avg_character_count,
    round(avg(word_count), 2) as avg_word_count
from cleaned_data
group by channel_name
  );
  