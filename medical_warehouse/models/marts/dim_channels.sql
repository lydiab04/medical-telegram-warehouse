{{ config(materialized='table') }}

with unique_channels as (
    select distinct channel_name
    from {{ ref('stg_telegram_messages') }}
)

select
    row_number() over (order by channel_name) as channel_key,
    channel_name,
    current_timestamp as date_added
from unique_channels