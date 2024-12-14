from typing import Any

from dbt.artifacts.resources.v1.generic_test import TestConfig
from dbt.artifacts.resources.v1.unit_test_definition import UnitTestConfig
from dbt.contracts.results import RunResult, TestStatus  # type:ignore

from dbt_xray.model import XrayRunResult


def validate_jira_config(config: UnitTestConfig | TestConfig | Any) -> bool:
    if not config.get("jira"):
        return False
    if not config.get("jira", {}).get("test_key"):
        return False
    return True


def get_test_key(config: Any) -> str:
    return config.get("jira", {}).get("test_key", "")


def get_test_plan(config: Any) -> str:
    return config.get("jira", {}).get("test_plan", "")


def dbt_run_result_to_xray_run_result(result: RunResult, test_key: str) -> XrayRunResult:
    return XrayRunResult(
        test_key=test_key,
        status="pass" if result.status == TestStatus.Pass else "fail",
        execution_timestamp=result.timing[0].started_at,  # type: ignore
        execution_evidence=result.adapter_response,
    )
