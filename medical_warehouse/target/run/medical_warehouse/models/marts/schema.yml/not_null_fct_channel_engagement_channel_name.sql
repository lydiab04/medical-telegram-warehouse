
    select
      count(*) as failures,
      case when count(*) != 0
        then 'true' else 'false' end as should_warn,
      case when count(*) != 0
        then 'true' else 'false' end as should_error
    from (
      
    
  
    
    



select channel_name
from main."fct_channel_engagement"
where channel_name is null



  
  
      
    ) dbt_internal_test