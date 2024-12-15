from typing import Any

from dbt.artifacts.resources.v1.generic_test import TestConfig
from dbt.artifacts.resources.v1.unit_test_definition import UnitTestConfig
from dbt.contracts.results import RunResult, TestStatus  # type:ignore

from dbt_xray.model import XrayRunResult


def validate_jira_config(config: UnitTestConfig | TestConfig | Any) -> bool:
    return bool(next((tag for tag in config.tags if tag.startswith("key:")), None))


def get_test_key(config: UnitTestConfig | TestConfig | Any) -> str | None:
    if key := next((tag for tag in config.tags if tag.startswith("key:")), None):
        return key.split(":", maxsplit=1)[1]


def get_test_plan(config: UnitTestConfig | TestConfig | Any) -> str | None:
    if plan := next((tag for tag in config.tags if tag.startswith("plan:")), None):
        return plan.split(":", maxsplit=1)[1]
