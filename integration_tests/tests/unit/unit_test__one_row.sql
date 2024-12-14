{{
    config(
        tags=['unit-test'],
        jira={
            "test_key": "IGDP-14",
        }
    )
}}
{% call dbt_unit_testing.test("stg_user_events", "Shall properly handle a single row") %}
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
            'us-east-1' as region_id,
            'user-1f' as user_id,
            '1.0.1' as client_version,
            'login' as event_type,
            '{ "success": true }' :: jsonb as event_data,
            '2020-01-01 00:00:00' :: timestamp as event_timestamp,
            'abc123de' as event_id,
            '2020-01-01 00:00:00' :: timestamp as received_at,
            '{{ dbt_run_started_at() }}' :: timestamp as dbt_run_started_at
    {% endcall %}
{% endcall %}