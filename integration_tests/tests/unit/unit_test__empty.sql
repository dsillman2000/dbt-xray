{{
    config(
        tags=['unit-test', 'key:IGDP-15', 'plan:IGDP-28'],
    )
}}
{% call dbt_unit_testing.test("stg_user_events", "Shall handle an empty row correctly") %}
    {% call dbt_unit_testing.mock_source("landing_tables", "user_events") %}
        select
            null as region_id,
            null as user_id,
            null as client_version,
            null as event_type,
            null as event_data,
            null as event_timestamp,
            null as event_id,
            null as received_at
        where 1=0
    {% endcall %}
    {% call dbt_unit_testing.expect_no_rows() %}{% endcall %}
{% endcall %}