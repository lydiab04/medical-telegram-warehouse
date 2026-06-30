

with raw_dates as (
    select distinct cast(message_date as date) as full_date
    from "medical_warehouse"."public"."stg_telegram_messages"
    where message_date is not null
)

select
    cast(to_char(full_date, 'YYYYMMDD') as integer) as date_key,
    full_date,
    extract(day from full_date) as day,
    extract(month from full_date) as month,
    extract(year from full_date) as year,
    to_char(full_date, 'Day') as day_of_week
from raw_dates