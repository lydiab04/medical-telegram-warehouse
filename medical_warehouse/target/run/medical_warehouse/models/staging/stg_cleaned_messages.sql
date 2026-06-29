
    
    create view main."stg_cleaned_messages" as
    

with raw_data as (
    select
        message_id,
        channel_name,
        message_date,
        message_text,
        coalesce(views, 0) as views,
        coalesce(forwards, 0) as forwards,
        has_media
    from main."stg_telegram_messages"
)

select
    message_id,
    channel_name,
    message_date,
    -- Basic text cleaning: strip trailing white spaces and force lowercase for consistency
    lower(trim(message_text)) as cleaned_text,
    length(message_text) as character_count,
    -- Feature engineering: calculate the word count using space separation
    (length(trim(message_text)) - length(replace(trim(message_text), ' ', '')) + 1) as word_count,
    views,
    forwards,
    has_media
where message_text is not null 
  and message_text != ''
  and length(trim(message_text)) > 5  -- Filter out empty or meaningless single-word alerts;