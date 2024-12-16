{{
    config(
        tags=['unit-test', 'key:IGDP-71'],
    )
}}
{% call dbt_unit_testing.test("stg_user_events", "Shall fail the given scenario") %}
    {% call dbt_unit_testing.mock_source("landing_tables", "user_events") %}
        select
            'us-east-1' as region_id,
            'user-1f' as user_id,
            '1.0.1' as client_version,
            'login' as event_type,
            '{ "success": true }' :: jsonb as event_data,
            '2020-01-01 00:00:00' :: timestamp as event_timestamp,
            'abc123de' as event_id,
            '2020-01-01 00:00:00' :: timestamp as received_at
    {% endcall %}
    {% call dbt_unit_testing.expect() %}
        select
            'different-region' as region_id,
            'different-user' as user_id,
            'different-client-version' as client_version,
            'different-event-type' as event_type,
            '{}' :: jsonb as event_data,
            '2020-01-01 00:00:00' :: timestamp as event_timestamp,
            'fgh456ij' as event_id,
            '2020-01-01 00:00:00' :: timestamp as received_at,
            '2020-01-01 00:00:00' :: timestamp as dbt_run_started_at
    {% endcall %}
{% endcall %}