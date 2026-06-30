
  
    

  create  table "medical_warehouse"."public"."fct_messages__dbt_tmp"
  
  
    as
  
  (
    

with messages as (
    select * from "medical_warehouse"."public"."stg_cleaned_messages"
),
channels as (
    select * from "medical_warehouse"."public"."dim_channels"
)

select
    m.message_id as message_key,
    c.channel_key,
    cast(to_char(m.message_date, 'YYYYMMDD') as integer) as date_key,
    m.views,
    m.forwards,
    m.character_count,
    m.word_count,
    m.has_media
from messages m
join channels c on m.channel_name = c.channel_name
  );
  