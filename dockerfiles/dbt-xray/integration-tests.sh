cd /project/integration_tests
poetry run dbt run --empty

poetry run dbt-xray ls
poetry run dbt-xray ls --test-key IGDP-14
poetry run dbt-xray ls --test-key IGDP-13,IGDP-14
poetry run dbt-xray ls --test-plan IGDP-28
poetry run dbt-xray run
poetry run dbt-xray run --test-key IGDP-14
poetry run dbt-xray run --test-key IGDP-13,IGDP-14
poetry run dbt-xray run --test-plan IGDP-28
