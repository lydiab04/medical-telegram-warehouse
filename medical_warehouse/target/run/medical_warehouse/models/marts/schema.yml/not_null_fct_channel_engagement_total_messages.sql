
    select
      count(*) as failures,
      case when count(*) != 0
        then 'true' else 'false' end as should_warn,
      case when count(*) != 0
        then 'true' else 'false' end as should_error
    from (
      
    
  
    
    



select total_messages
from main."fct_channel_engagement"
where total_messages is null



  
  
      
    ) dbt_internal_test