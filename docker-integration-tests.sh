docker compose exec dbt-xray bash -c "cd /project && poetry run pytest -sv tests/test_integration.py"
