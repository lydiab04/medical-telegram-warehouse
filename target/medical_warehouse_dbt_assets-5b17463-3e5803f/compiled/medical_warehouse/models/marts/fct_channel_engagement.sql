

with staging_data as (
    select
        channel_name,
        message_id,
        message_date,
        message_length,
        views,
        forwards,
        has_media
    from "medical_warehouse"."public"."stg_telegram_messages"
)

select
    channel_name,
    count(message_id) as total_messages,
    sum(views) as total_views,
    sum(forwards) as total_forwards,
    -- Calculate averages safely
    round(avg(views), 2) as avg_views_per_post,
    round(avg(forwards), 2) as avg_forwards_per_post,
    -- Count how many messages included images/media
    sum(case when has_media = 1 then 1 else 0 end) as total_media_messages
from staging_data
group by channel_name