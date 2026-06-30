{{ config(materialized='table') }}

with messages as (
    select * from {{ ref('stg_cleaned_messages') }}
),
channels as (
    select * from {{ ref('dim_channels') }}
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