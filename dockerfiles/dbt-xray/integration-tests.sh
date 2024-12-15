cd /project/integration_tests
poetry run dbt run --empty

cd /project
poetry run pytest -sv tests/test_integration.py
