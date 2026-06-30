
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select total_views
from "medical_warehouse"."public"."fct_channel_engagement"
where total_views is null



  
  
      
    ) dbt_internal_test