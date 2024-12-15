from pprint import pprint

import click
from dbt.cli.main import dbtRunner
from dbt.contracts.graph.manifest import Manifest
from dbt.contracts.results import RunExecutionResult  # type: ignore

from dbt_xray import callbacks, params, utils
from dbt_xray.model import XrayRunResult


@click.group()
@click.pass_context
def cli(ctx: click.Context):
    """A plugin for dbt that provides additional functionality for managing and running tests."""
    pass


@cli.command()
@params.test_plan
@params.test_key
@params.quiet
@click.pass_context
def ls(ctx: click.Context, test_plan: str | None, test_key: str | None, quiet: bool = False) -> dict[str, str]:
    """List all test nodes in the project meeting the selection criteria."""
    runner = dbtRunner()
    manifest: Manifest = runner.invoke(["parse"]).result  # type: ignore
    native_unit_tests = {} if not hasattr(manifest, "unit_tests") else manifest.unit_tests
    jira_native_unit_tests = {k: v for k, v in native_unit_tests.items() if utils.validate_jira_config(v.config)}
    equal_experts_unit_tests = {k: v for k, v in manifest.nodes.items() if "unit-test" in v.config.tags}
    jira_equal_experts_unit_tests = {
        k: v for k, v in equal_experts_unit_tests.items() if utils.validate_jira_config(v.config)
    }
    jira_unit_tests = {**jira_native_unit_tests, **jira_equal_experts_unit_tests}
    selected = jira_unit_tests
    if test_plan:
        selected = {k: v for k, v in jira_unit_tests.items() if utils.get_test_plan(v.config) == test_plan}
    elif test_key:
        test_keys = test_key.split(",")
        selected = {k: v for k, v in jira_unit_tests.items() if utils.get_test_key(v.config) in test_keys}
    test_name_to_key: dict[str, str] = {}
    for k, v in selected.items():
        if not (test_key := utils.get_test_key(v.config)):
            raise ValueError(f"Test {k} does not have a key tag!")
        test_name_to_key[v.unique_id] = test_key
        if not quiet:
            print(f"{test_key}: {k}")
    return test_name_to_key


@cli.command()
@params.test_plan
@params.test_key
@click.pass_context
def run(ctx: click.Context, test_plan: str | None, test_key: str | None):
    """Run all test nodes in the project meeting the selection criteria."""
    selected: dict[str, str] = ctx.invoke(ls, test_plan=test_plan, test_key=test_key, quiet=True)
    collection = callbacks.XrayTestResultsCollection(_lookup=selected)
    runner = dbtRunner(callbacks=collection.callbacks())
    if not selected:
        print("Nothing to do!")
        return
    for test_name, test_key in selected.items():
        print(f"Running test for {test_key}: {test_name}")
        runner.invoke(["test"], select=[f"tag:key:{test_key}"]).result  # type: ignore
    results: list[XrayRunResult] = [collection._test_results[k] for k in selected.keys()]
    return results
