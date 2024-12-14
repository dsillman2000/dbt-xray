select
    region_id,
    user_id,
    client_version,
    event_type,
    event_data,
    event_timestamp,
    event_id,
    received_at,
    '{{ dbt_run_started_at() }}' :: timestamp as dbt_run_started_at
from {{ dbt_unit_testing.source('landing_tables', 'user_events') }}
