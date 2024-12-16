from pprint import pprint
from typing import Literal

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
def ls(
    ctx: click.Context, test_plan: str | None, test_key: str | None, quiet: bool = False
) -> dict[str, utils.UnitTestNode]:
    """List all test nodes in the project meeting the selection criteria."""
    runner = dbtRunner()
    manifest: Manifest = runner.invoke(["parse"]).result  # type: ignore
    nodes: dict[str, utils.UnitTestNode] = {}
    match test_plan, test_key:
        case None, None:
            nodes = utils.find_all_tests(manifest)
        case None, key:
            if "," in key:
                nodes = {k: utils.find_test_by_test_key(manifest, k) for k in key.split(",")}
            else:
                nodes = {key: utils.find_test_by_test_key(manifest, key)}
        case plan, None:
            nodes = utils.find_tests_by_test_plan(manifest, plan)
        case _:
            raise ValueError("Cannot specify both test plan and test key!")
    if not quiet:
        print("\n".join([f"{k}: {v.unique_id}" for k, v in nodes.items()]))
    return nodes


@cli.command()
@params.test_plan
@params.test_key
@params.mode
@click.pass_context
def run(ctx: click.Context, test_plan: str | None, test_key: str | None, mode: Literal["bulk", "serial"] = "bulk"):
    """Run all test nodes in the project meeting the selection criteria."""
    selected: dict[str, utils.UnitTestNode] = ctx.invoke(ls, test_plan=test_plan, test_key=test_key, quiet=True)
    lookup: dict[str, str] = {v.unique_id: utils.get_test_key(v.config) for k, v in selected.items()}  # type: ignore
    collection = callbacks.XrayTestResultsCollection(_lookup=lookup)
    runner = dbtRunner(callbacks=collection.callbacks())
    if not selected:
        utils.dbt_log_note("Nothing to do!")
        return
    utils.run_tests_by_test_keys(runner, list(selected.keys()), mode=mode)
    results: list[XrayRunResult] = [collection._test_results[k] for k in selected.keys()]
    return results
