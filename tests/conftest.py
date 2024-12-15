from pathlib import Path

import pytest
from dbt.cli.main import dbtRunner

INTEGRATION_TESTS_DIR = Path(__file__).parent.parent / "integration_tests"


@pytest.fixture(autouse=True)
def dbt_project_dir(monkeypatch: pytest.MonkeyPatch):
    with monkeypatch.context() as m:
        m.setenv("DBT_PROJECT_DIR", str(INTEGRATION_TESTS_DIR))
        m.chdir(INTEGRATION_TESTS_DIR)
        yield
