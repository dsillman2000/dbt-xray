from typing import Any, Literal

from dbt.artifacts.resources.v1.config import TestConfig

try:
    from dbt.artifacts.resources.v1.unit_test_definition import (
        UnitTestConfig,
        UnitTestDefinition,
    )
except ModuleNotFoundError:
    from dbt.artifacts.resources.v1.config import TestConfig as UnitTestConfig
    from dbt.artifacts.resources.v1.singular_test import (
        SingularTest as UnitTestDefinition,
    )

from dbt.cli.main import dbtRunner
from dbt.contracts.graph.manifest import Manifest
from dbt.contracts.graph.nodes import TestNode

from dbt_xray.model import XrayRunResult

try:
    from dbt_common.events.functions import fire_event
    from dbt_common.events.types import Note
except ModuleNotFoundError:
    from dbt.events.functions import fire_event  # type: ignore
    from dbt.events.types import Note  # type: ignore

UnitTestNode = UnitTestDefinition | TestNode


def validate_jira_config(config: UnitTestConfig | TestConfig | Any) -> bool:
    return bool(next((tag for tag in config.tags if tag.startswith("key:")), None))


def get_test_key(config: UnitTestConfig | TestConfig | Any) -> str | None:
    if key := next((tag for tag in config.tags if tag.startswith("key:")), None):
        return key.split(":", maxsplit=1)[1]


def get_test_plans(config: UnitTestConfig | TestConfig | Any) -> list[str]:
    return [tag.split(":", maxsplit=1)[1] for tag in config.tags if tag.startswith("plan:")]


def _candidate_nodes(manifest: Manifest) -> dict[str, UnitTestNode]:
    native_unit_tests = {} if not hasattr(manifest, "unit_tests") else manifest.unit_tests
    equal_experts_tests = {
        k: v for k, v in manifest.nodes.items() if (v.resource_type == "test" and "unit-test" in v.config.tags)
    }  # type: ignore
    return {**native_unit_tests, **equal_experts_tests}


def find_test_by_test_key(manifest: Manifest, test_key: str) -> UnitTestNode:
    result = next((node for node in _candidate_nodes(manifest).values() if get_test_key(node.config) == test_key), None)
    if not result:
        raise ValueError(f"Test with key {test_key} not found!")
    return result


def find_tests_by_test_plan(manifest: Manifest, test_plan: str) -> dict[str, UnitTestNode]:
    results = {}
    for node in _candidate_nodes(manifest).values():
        if test_plan in get_test_plans(node.config) and isinstance(node, UnitTestNode):
            assert (test_key := get_test_key(node.config)), f"Test {node.unique_id} does not have a key tag!"
            results[test_key] = node
    return results


def find_all_tests(manifest: Manifest) -> dict[str, UnitTestNode]:
    nodes = {k: v for k, v in _candidate_nodes(manifest).items() if validate_jira_config(v.config)}
    return {test_key: node for node in nodes.values() if (test_key := get_test_key(node.config))}


def run_test_by_test_key(runner: dbtRunner, test_key: str):
    runner.invoke(["test", "-s", "tag:key:" + test_key])


def run_tests_by_test_keys(runner: dbtRunner, test_keys: list[str], mode: Literal["bulk", "serial"] = "bulk"):
    match mode:
        case "serial":
            for test_key in test_keys:
                run_test_by_test_key(runner, test_key)
        case "bulk":
            selects = " ".join([f"tag:key:{key}" for key in test_keys])
            runner.invoke(["test", "-s", selects])


def dbt_log_note(message: str):
    fire_event(Note(msg=message))
