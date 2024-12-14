from pprint import pprint

import click
from dbt.cli.main import dbtRunner
from dbt.contracts.graph.manifest import Manifest
from dbt.contracts.results import RunExecutionResult  # type: ignore

from dbt_xray import params, utils
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
def ls(ctx: click.Context, test_plan: str | None, test_key: str | None, quiet: bool = False):
    """List all test nodes in the project meeting the selection criteria."""
    runner = dbtRunner()
    manifest: Manifest = runner.invoke(["parse"]).result  # type: ignore
    native_unit_tests = {} if not hasattr(manifest, "unit_tests") else manifest.unit_tests
    jira_native_unit_tests = {k: v for k, v in native_unit_tests.items() if utils.validate_jira_config(v.config)}
    equal_experts_unit_tests = {k: v for k, v in manifest.nodes.items() if "unit-test" in v.config.get("tags", [])}
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
    for k, v in selected.items():
        ticket = utils.get_test_key(v.config)
        if not quiet:
            print(f"{ticket}: {k}")
    return selected


@cli.command()
@params.test_plan
@params.test_key
@click.pass_context
def run(ctx: click.Context, test_plan: str | None, test_key: str | None):
    """Run all test nodes in the project meeting the selection criteria."""
    selected = ctx.invoke(ls, test_plan=test_plan, test_key=test_key, quiet=True)
    runner = dbtRunner()
    if not selected:
        print("Nothing to do!")
        return
    results: list[XrayRunResult] = []
    for k, v in selected.items():
        ticket = utils.get_test_key(v.config)
        print(f"Running test for {ticket}: {k}")
        is_equal_experts = "unit-test" in v.config.get("tags", [])
        result: RunExecutionResult
        if is_equal_experts:
            result = runner.invoke(["test", "--select", "tag:unit-test,{}".format(v.name)]).result  # type: ignore
        else:
            result = runner.invoke(["test", "--select", "{},{}".format(v.model, v.name)]).result  # type: ignore
        results.append(utils.dbt_run_result_to_xray_run_result(result.results[0], ticket))
    pprint(results)
    return results
